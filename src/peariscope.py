import json
import numpy as np
import cv2
import networktables
import time
import subprocess

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
    'max_hue' : 70,
    'min_sat' : 0,
    'max_sat' : 255,
    'min_val' : 40,
    'max_val' : 255,
}

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

    # Create sink for capturing images from the camera video stream
    sink = inst.getVideo()

    # Preallocate space for new color images
    image = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)

    # Create output stream for sending processed images
    output_stream = inst.putVideo('Peariscope', camera_width, camera_height)

    # Use network tables to receive configuration and publish results
    nt = networktables.NetworkTables.getTable('Peariscope')
    time.sleep(1) # Wait for network tables to start

    # Set all configuration values if not set already
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
        binary_image = cv2.dilate(binary_image, None, iterations=1)
        binary_image = cv2.erode(binary_image, None, iterations=1)

        #
        # Contour Loop (process each object in the image)
        #

        # Find contours in the binary image
        _, contour_list, _ = cv2.findContours(binary_image,
             mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

        # Initialize arrays of results
        x_list = [] # X-coordinates of found reflectors
        y_list = [] # Y-coordinates of found reflectors

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

            # Keep only the contours we want
            if (100 < area < 2750) and (25 < w < 250) and (w > h * 1.25):

                # Color in the successful contour
                cv2.drawContours(image, [contour], 0, color=BGR_YEL, thickness=-1)

                # Draw the bounding box
                image = cv2.rectangle(image, (x,y), (x+w, y+h), BGR_RED, 1)

                # Draw a circle to mark the center
                cv2.circle(image, center=(center_x, center_y),
                    radius=2, color=BGR_YEL, thickness=-1)

                # Print the features of this contour
                #print("area", area, "height", h, "width", w)

                # Add to the lists of results
                x_list.append(center_x)
                y_list.append(center_y)

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

