#!/usr/bin/env python3

import sys
import time
import subprocess
import json
import numpy as np
import cv2
import networktables
import math

from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer

configFile = "/boot/frc.json"

class CameraConfig: pass

team = None
server = False
cameraConfigs = []
switchedCameraConfigs = []
cameras = []
insts = []

def parseError(str):
    """Report parse error."""
    print("config error in '" + configFile + "': " + str, file=sys.stderr)

def readCameraConfig(config):
    """Read single camera configuration."""
    cam = CameraConfig()

    # name
    try:
        cam.name = config["name"]
    except KeyError:
        parseError("could not read camera name")
        return False

    # path
    try:
        cam.path = config["path"]
    except KeyError:
        parseError("camera '{}': could not read path".format(cam.name))
        return False

    # stream properties
    cam.streamConfig = config.get("stream")

    cam.config = config

    cameraConfigs.append(cam)
    return True

def readCalibrationFile(path: str):
    fs = cv2.FileStorage(path, cv2.FileStorage_READ)
    if fs.isOpened():
        cam_mat = fs.getNode(CAMERA_MATRIX_NAME).mat()
        dist_coeff = fs.getNode(DISTORTION_COEFFICIENTS_NAME).mat()
        return cam_mat, dist_coeff
    else:
        raise ValueError(
            "Specified calibration file does not exist or cannot be opened"
        )

def readSwitchedCameraConfig(config):
    """Read single switched camera configuration."""
    cam = CameraConfig()

    # name
    try:
        cam.name = config["name"]
    except KeyError:
        parseError("could not read switched camera name")
        return False

    # path
    try:
        cam.key = config["key"]
    except KeyError:
        parseError("switched camera '{}': could not read key".format(cam.name))
        return False

    switchedCameraConfigs.append(cam)
    return True

def readConfig():
    """Read configuration file."""
    global team
    global server

    # parse file
    try:
        with open(configFile, "rt", encoding="utf-8") as f:
            j = json.load(f)
    except OSError as err:
        print("could not open '{}': {}".format(configFile, err), file=sys.stderr)
        return False

    # top level must be an object
    if not isinstance(j, dict):
        parseError("must be JSON object")
        return False

    # team number
    try:
        team = j["team"]
    except KeyError:
        parseError("could not read team number")
        return False

    # ntmode (optional)
    if "ntmode" in j:
        str = j["ntmode"]
        if str.lower() == "client":
            server = False
        elif str.lower() == "server":
            server = True
        else:
            parseError("could not understand ntmode value '{}'".format(str))

    # cameras
    try:
        cameras = j["cameras"]
    except KeyError:
        parseError("could not read cameras")
        return False
    for camera in cameras:
        if not readCameraConfig(camera):
            return False

    # switched cameras
    if "switched cameras" in j:
        for camera in j["switched cameras"]:
            if not readSwitchedCameraConfig(camera):
                return False

    return True

def startCamera(config):
    """Start running the camera."""
    print("Starting camera '{}' on {}".format(config.name, config.path))
    inst = CameraServer.getInstance()
    camera = UsbCamera(config.name, config.path)
    server = inst.startAutomaticCapture(camera=camera, return_server=True)

    camera.setConfigJson(json.dumps(config.config))
    camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

    if config.streamConfig is not None:
        server.setConfigJson(json.dumps(config.streamConfig))

    return camera, inst

def startSwitchedCamera(config):
    """Start running the switched camera."""
    print("Starting switched camera '{}' on {}".format(config.name, config.key))
    server = CameraServer.getInstance().addSwitchedCamera(config.name)

    def listener(fromobj, key, value, isNew):
        if isinstance(value, float):
            i = int(value)
            if i >= 0 and i < len(cameras):
              server.setSource(cameras[i])
        elif isinstance(value, str):
            for i in range(len(cameraConfigs)):
                if value == cameraConfigs[i].name:
                    server.setSource(cameras[i])
                    break

    networktables.NetworkTablesInstance.getDefault().getEntry(config.key).addListener(
        listener,
        ntcore.constants.NT_NOTIFY_IMMEDIATE |
        ntcore.constants.NT_NOTIFY_NEW |
        ntcore.constants.NT_NOTIFY_UPDATE)

    return server

#########################
# Start Peariscope Code #
#########################

# Define some colors (BGR)
BGR_BLACK = (0, 0, 0)
BGR_WHITE = (255, 255, 255)
BGR_RED = (0, 0, 255)
BGR_GREEN = (0, 255, 0)
BGR_BLUE = (255, 0, 0)
BGR_YELLOW = (0, 255, 255)

# Define default parameters
DEFAULT_VALS = {
    'led_red' : 0,
    'led_grn' : 255,
    'led_blu' : 0,
    'min_hue' : 55,
    'max_hue' : 65,
    'min_sat' : 255,
    'max_sat' : 255,
    'min_val' : 40,
    'max_val' : 255,
}

TARGET_POINTS = np.array(
    [
        [-0.498475, 0.0, 0.0],  # Top left
        [0.498475, 0.0, 0.0],  # Top right
        [-0.2492375, -0.4318, 0.0],  # Bottom left
        [0.2492375, -0.4318, 0.0],  # Bottom right
    ]
)

def ringlight_on(red, grn, blu):
    print("Setting ringlights to", red, grn, blu)
    script = 'peariscope/src/ringlight_on.py'
    command = 'sudo {} {} {} {} 2>/dev/null'.format(script, red, grn, blu)
    rc = subprocess.call(command, shell=True) # Run the script in the shell

def get_temperature():
    result = subprocess.check_output(['vcgencmd', 'measure_temp'])
    temperature = float(result.decode('UTF-8')[5:][:-3])
    return temperature

def peariscope(camera, inst):

    #
    # Setup (runs only once)
    #

    print('Peariscope by Pearadox Robotics Team 5414')
    print('Info', camera.getInfo())
    print('Path', camera.getPath())

    # Load FRC configuration file (/boot/frc.json)
    config = json.loads(camera.getConfigJson())
    camera_height = config['height']
    camera_width = config['width']
    camera_fps = config['fps']
    print('camera_height: {}, camera_width: {}, fps: {}'.format(
        camera_height, camera_width, camera_fps))
    
    camera_matrix, distortion_coeffs = readCalibrationFile('./calibration/')

    # Create sink for capturing images from the camera video stream
    sink = inst.getVideo()

    # Preallocate space for new color images
    input_img = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)

    # Create output stream for sending processed images
    output_stream = inst.putVideo('Peariscope', camera_width, camera_height)

    # Use network tables to receive configuration and publish results
    nt = networktables.NetworkTables.getTable('Peariscope')
    time.sleep(1) # Wait for network tables to start

    # Set all configuration parameters if not set already
    for key, value in DEFAULT_VALS.items():
        print(key, value)
        if nt.getNumber(key, None) == None:
            nt.putNumber(key, value)

    # Set ringlight to initial color
    red = nt.getNumber('led_red', None)
    grn = nt.getNumber('led_grn', None)
    blu = nt.getNumber('led_blu', None)
    ringlight_on(red, grn, blu)

    #
    # Image Loop (runs for each image from the camera)
    #

    current_time = time.time()
    while True: # Forever loop
        start_time = current_time

        # Publish the temperature of the pi
        nt.putNumber('temperature', get_temperature())

        # Get configuration values for LED lights
        led_red = nt.getNumber('led_red', None)
        led_grn = nt.getNumber('led_grn', None)
        led_blu = nt.getNumber('led_blu', None)

        # Get configuration values for color detection
        min_hue = nt.getNumber('min_hue', None)
        max_hue = nt.getNumber('max_hue', None)
        min_sat = nt.getNumber('min_sat', None)
        max_sat = nt.getNumber('max_sat', None)
        min_val = nt.getNumber('min_val', None)
        max_val = nt.getNumber('max_val', None)

        # Ringlight control (only if changes are requested)
        if led_red != red or led_grn != grn or led_blu != blu:
            red, grn, blu = led_red, led_grn, led_blu
            ringlight_on(red, grn, blu)

        # Grab a frame from the camera and store it in the preallocated space
        frame_time, input_img = sink.grabFrame(input_img)

        # If there is an error then notify the output and skip this iteration
        if frame_time == 0:
            output_stream.notifyError(sink.getError())
            continue

        # Publish the image size
        img_height, img_width = input_img.shape[:2]
        nt.putNumber('image_height', img_height)
        nt.putNumber('image_width', img_width)
        img_center_x = int(img_width/2)
        img_center_y = int(img_height/2)

        # Segment the image based on hue, saturation, and value ranges
        hsv_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)
        binary_img = cv2.inRange(hsv_img, (min_hue, min_sat, min_val), (max_hue, max_sat, max_val))

        # Closing (fill in any gaps)
        binary_img = cv2.dilate(binary_img, None, iterations=2)
        binary_img = cv2.erode(binary_img, None, iterations=2)

        # Create an output image for display
        output_img = np.zeros_like(input_img)
        output_img[:] = BGR_BLUE

        # Find contours in the binary image
        _, contour_list, _ = cv2.findContours(binary_img, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

        #
        # Contour Loop (runs for each contour in the image)
        #

        # Initialize arrays of results
        x_list = [] # X-coordinates of found reflectors
        y_list = [] # Y-coordinates of found reflectors
        
        pos_list = []
        dist_list = []
        angle_list = []

        # For each contour of every object...
        for contour in contour_list:

            # Color in the contour so we know it was seen
            cv2.drawContours(output_img, [contour], 0, color=BGR_RED, thickness=-1)

            # Compute the area of the contour
            area = cv2.contourArea(contour)
            if area < 10:
                continue # Immediately eliminate small contours

            # Compute the rotated rectangle surrounding the contour
            rect = cv2.minAreaRect(contour)
            rect_center, rect_size, rect_angle = rect
            rect_x, rect_y = rect_center
            rect_width, rect_height = rect_size
            rect_angle = -rect_angle # Horizontal is 0 degrees, CCW is positive
            if rect_width >= rect_height:
                rect_long, rect_short = rect_width, rect_height
            else:
                rect_long, rect_short = rect_height, rect_width
                rect_angle += 90
            # Keep the angle between -90 and +90 degrees
            if rect_angle > 90:
                rect_angle -= 180

            # Ratio of long side to short side of rotated rectangle
            ratio = rect_long / rect_short

            # Compute the fill of the contour
            fill = area / (rect_long * rect_short)

            # Keep only the contours we want
            corners = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            
            if (50 < area < 2000) and (0 < fill < 0.15) and (ratio > 1.3) and len(corners) == 4:

                # Color in the successful contour
                cv2.drawContours(output_img, [contour], 0, color=BGR_GREEN, thickness=-1)

                # Draw rotated rectangle
                cv2.drawContours(output_img, [np.int0(cv2.boxPoints(rect))], 0, BGR_YELLOW, 2)

                # Draw a circle to mark the center
                cv2.circle(output_img, center=(int(rect_x), int(rect_y)), radius=3, color=BGR_YELLOW, thickness=-1)

                # Add to the lists of results
                x_list.append(center_x)
                y_list.append(center_y)
                
                _, rvec, tvec = cv2.solvePnP(TARGET_POINTS, corners, camera_matrix, distortion_coeffs)
                rot, _ = cv2.Rodrigues(rvec)
                
                angle1 = math.atan2(x, y)
                rot_t = rot.transpose()
                pzero_world = np.matmul(rot_t, -tvec)
                angle2 = math.atan2(pzero_world[0][0], pzero_world[2][0])
                
                pos_list.append([x, y, z])
                dist_list.append(math.sqrt(x**2 + z**2))   
                angle_list.append([angle1, angle2])         

                print("GOOD:", "area", area, "height", h, "width", w, "fill", fill, "ratio", ratio)
            else:
                print("bad:", "area", area, "height", h, "width", w, "fill", fill, "ratio", ratio)

        #
        # Outputs
        #

        # Output the results
        nt.putNumberArray('x_list', x_list)
        nt.putNumberArray('y_list', y_list)

        # Compute the coordinates as percentage distances from image center
        # for x (horizontal), 0 is center, -100 is image left, 100 is image right
        # for y (vertical), 0 is center, -100 is image top, 100 is image bottom
        x_list_pct = [(x-img_width/2)/(img_width/2)*100 for x in x_list]
        y_list_pct = [(y-img_height/2)/(img_height/2)*100 for y in y_list]
        x_list_pct = [round(x, 1) for x in x_list_pct]
        y_list_pct = [round(y, 1) for y in y_list_pct]
        nt.putNumberArray('x_list_pct', x_list_pct)
        nt.putNumberArray('y_list_pct', y_list_pct)

        # Draw crosshairs on the image
        cv2.line(output_img, (img_center_x, 0), (img_center_x, img_height-1), BGR_YELLOW, 1)
        cv2.line(output_img, (0, img_center_y), (img_width-1, img_center_y), BGR_YELLOW, 1)

        # Display the marked-up image on a separate output stream
        output_stream.putFrame(output_img)

        # Compute the elapsed time and FPS
        current_time = time.time()
        elapsed_time = current_time - start_time
        fps = 1/elapsed_time
        nt.putNumber('elapsed_time', elapsed_time)
        nt.putNumber('fps', fps)
        
        

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        mcs.configFile = sys.argv[1]

    mcs.init()
    print("Peariscope", "team", mcs.team, "server", mcs.server, "configFile", mcs.configFile)

    # Peariscope uses only the first (non-switched) camera and its instance
    peariscope(mcs.cameras[0], mcs.insts[0])
