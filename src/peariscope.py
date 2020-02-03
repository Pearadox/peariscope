#!/usr/bin/env python3

import json
import time
import sys
import ntcore
import numpy as np
import cv2
import time
import subprocess
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
BGR_RED = (0, 0, 255)
BGR_GRN = (0, 255, 0)
BGR_BLU = (255, 0, 0)
BGR_YEL = (0, 255, 255)

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
    script = '/home/pi/peariscope/src/ringlight_on.py'
    command = 'sudo {} {} {} {} 2>/dev/null'.format(script, red, grn, blu)
    rc = subprocess.call(command, shell=True) # Run the script in the shell

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
    image = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)

    # Create output stream for sending processed images
    output_stream = inst.putVideo('Peariscope', camera_width, camera_height)

    # Use network tables to receive configuration and publish results
    nt = networktables.NetworkTables.getTable('Peariscope')
    time.sleep(1) # Wait for network tables to start

    '''
    # Set all configuration values if not set already
    for key, value in DEFAULT_VALS.items():
        print(key, value)
        if nt.getNumber(key, None) == None:
            nt.putNumber(key, value)
    '''

    # Set all configuration values
    for key, value in DEFAULT_VALS.items():
        print(key, value)
        nt.putNumber(key, value)

    # Set ringlight to initial color
    red = nt.getNumber('led_red', None)
    grn = nt.getNumber('led_grn', None)
    blu = nt.getNumber('led_blu', None)
    ringlight_on(red, grn, blu)

    #
    # Image Loop (process each image from the camera)
    #

    current_time = time.time()
    while True: # Forever loop
        start_time = current_time

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
        frame_time, image = sink.grabFrame(image)

        # If there is an error then notify the output and skip this iteration
        if frame_time == 0:
            output_stream.notifyError(sink.getError())
            continue

        # Publish the image size
        image_height, image_width = image.shape[:2]
        nt.putNumber('image_height', image_height)
        nt.putNumber('image_width', image_width)

        # Segment the image based on hue, saturation, and value ranges
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        binary_image = cv2.inRange(hsv_image,
            (min_hue, min_sat, min_val), (max_hue, max_sat, max_val))

        # Opening (remove any small noise objects)
        #binary_image = cv2.erode(binary_image, None, iterations=1)
        #binary_image = cv2.dilate(binary_image, None, iterations=1)

        # Closing (fill in any gaps)
        binary_image = cv2.dilate(binary_image, None, iterations=2)
        binary_image = cv2.erode(binary_image, None, iterations=2)

        #
        # Contour Loop (process each object in the image)
        #

        # Find contours in the binary image
        _, contour_list, _ = cv2.findContours(binary_image,
             mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

        # Initialize arrays of results
        x_list = [] # X-coordinates of found reflectors
        y_list = [] # Y-coordinates of found reflectors
        
        pos_list = []
        dist_list = []
        angle_list = []

        # For each contour of every object...
        for contour in contour_list:

            # Color in the contour so we know it was seen
            cv2.drawContours(image, [contour], 0, color=BGR_BLU, thickness=-1)

            # Compute the area of the contour
            area = cv2.contourArea(contour)

            # Compute the bounding box of the contour
            x, y, w, h = cv2.boundingRect(contour)
            center_x = int(x + w/2)
            center_y = int(y + h/2)

            # Compute the ratio of the bounding box
            ratio = w / h * 1.0

            # Draw the bounding box
            image = cv2.rectangle(image, (x,y), (x+w, y+h), BGR_RED, 1)

            # Compute the fill of the contour
            fill = area / (h * w * 1.0)

            # Keep only the contours we want
            corners = cv2.convexHull(contour)
            
            if (50 < area < 2000) and (0 < fill < 0.15) and (ratio > 1.3) and len(corners) == 4:

                # Color in the successful contour
                cv2.drawContours(image, [contour], 0, color=BGR_YEL, thickness=-1)

                # Draw the bounding box
                image = cv2.rectangle(image, (x,y), (x+w, y+h), BGR_YEL, 1)

                # Draw a circle to mark the center
                cv2.circle(image, center=(center_x, center_y),
                    radius=2, color=BGR_YEL, thickness=-1)

                # Add to the lists of results
                x_list.append(center_x)
                y_list.append(center_y)
                
                _, rvec, tvec = cv2.solvePnP(TARGET_POINTS, corners, camera_matrix, distortion_coeffs)
                rot, _ = cv2.Rodrigues(rvec)
                
                x = tvec[0][0]
                y = tvec[1][0]
                z = tvec[2][0]
                
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
        x_list_pct = [(x-image_width/2)/(image_width/2)*100 for x in x_list]
        y_list_pct = [(y-image_height/2)/(image_height/2)*100 for y in y_list]
        x_list_pct = [round(x, 1) for x in x_list_pct]
        y_list_pct = [round(y, 1) for y in y_list_pct]
        nt.putNumberArray('x_list_pct', x_list_pct)
        nt.putNumberArray('y_list_pct', y_list_pct)

        # Draw crosshairs on the image
        image_center_x = int(image_width/2)
        image_center_y = int(image_height/2)
        cv2.line(image, (image_center_x, 0), (image_center_x, image_height-1), BGR_YEL, 1)
        cv2.line(image, (0, image_center_y), (image_width-1, image_center_y), BGR_YEL, 1)

        # Display the marked-up image on a separate output stream
        output_stream.putFrame(image)

        # Compute the elapsed time and FPS
        current_time = time.time()
        elapsed_time = current_time - start_time
        fps = 1/elapsed_time
        nt.putNumber('elapsed_time', elapsed_time)
        nt.putNumber('fps', fps)
        
        

#######################
# End Peariscope Code #
#######################

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        configFile = sys.argv[1]

    # read configuration
    if not readConfig():
        sys.exit(1)

    # start NetworkTables
    ntinst = networktables.NetworkTablesInstance.getDefault()
    if server:
        print("Setting up NetworkTables server")
        ntinst.startServer()
    else:
        print("Setting up NetworkTables client for team {}".format(team))
        ntinst.startClientTeam(team)

    # start cameras
    for config in cameraConfigs:
        camera, inst = startCamera(config)
        cameras.append(camera)
        insts.append(inst)

    # start switched cameras
    for config in switchedCameraConfigs:
        startSwitchedCamera(config)

    # Peariscope uses only the first (non-switched) camera and its instance
    peariscope(cameras[0], insts[0])

