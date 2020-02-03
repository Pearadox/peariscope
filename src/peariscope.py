#!/usr/bin/env python3

import sys
import time
import subprocess
import json
import numpy as np
import cv2
import networktables
import peariscope.src.multiCameraServer as mcs

# Define some colors (BGR)
BGR_BLACK = (0, 0, 0)
BGR_WHITE = (255, 255, 255)
BGR_RED = (0, 0, 255)
BGR_GREEN = (2, 222, 132) # Alien armpit
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

def ringlight_on(red, grn, blu):
    print("Setting ringlights to", red, grn, blu)
    script = 'peariscope/src/ringlight_on.py'
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
    print('camera_height: {}, camera_width: {}, fps: {}'.format(camera_height, camera_width, camera_fps))

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

        # Opening (remove any small noise objects)
        #binary_img = cv2.erode(binary_img, None, iterations=1)
        #binary_img = cv2.dilate(binary_img, None, iterations=1)

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

            # Draw rotated rectangle
            cv2.drawContours(output_img, [np.int0(cv2.boxPoints(rect))], 0, BGR_YELLOW, 2)

            # Ratio of long side to short side of rotated rectangle
            ratio = rect_long / rect_short

            # Compute the fill of the contour
            fill = area / (rect_long * rect_short)

            print("area {:.2f} long {:.2f} short {:.2f} angle {:.2f} ratio {:.2f} fill {:.2f}".format(
                area, rect_long, rect_short, rect_angle, ratio, fill))

            # Keep only the contours we want
            if (50 < area < 2000) and (ratio > 1.3) and (0 < fill < 0.15):

                # Color in the successful contour
                cv2.drawContours(output_img, [contour], 0, color=BGR_GREEN, thickness=-1)

                # Draw a circle to mark the center
                cv2.circle(output_img, center=(int(rect_x), int(rect_y)), radius=3, color=BGR_YELLOW, thickness=-1)

                # Add to the lists of results
                x_list.append(rect_x)
                y_list.append(rect_y)

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

