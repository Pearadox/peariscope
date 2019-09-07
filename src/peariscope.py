import json
import time
import numpy as np
import cv2

from networktables import NetworkTables

# Define colors (BGR)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)

# Configuration parameter defaults
MIN_REFLECTOR_WIDTH = 0
MAX_REFLECTOR_WIDTH = 1000
MIN_REFLECTOR_LENGTH = 0
MAX_REFLECTOR_LENGTH = 1000

def peariscope(camera, inst):

    #
    # Peariscope Setup Code
    #

    print('Peariscope by Pearadox Robotics Team 5414')
    print('Info', camera.getInfo())
    print('Path', camera.getPath())

    config = json.loads(camera.getConfigJson())
    camera_height = config['height']
    camera_width = config['width']
    camera_fps = config['fps']
    print('camera_height {} camera_width {} fps {}'.format(camera_height, camera_width, camera_fps))

    # Create sink for capturing images from the camera video stream
    sink = inst.getVideo()

    # Preallocate space for new color images
    image = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)

    # Create output stream for sending processed images back to the dashboard
    output_stream = inst.putVideo('Peariscope', camera_width, camera_height)

    # Use network table to receive configuration parameters and for publishing results
    nt = NetworkTables.getTable('Peariscope')

    # Set configuration parameters
    nt.putNumber('min_reflector_width', MIN_REFLECTOR_WIDTH)
    nt.putNumber('max_reflector_width', MAX_REFLECTOR_WIDTH)
    nt.putNumber('min_reflector_length', MIN_REFLECTOR_LENGTH)
    nt.putNumber('max_reflector_length', MAX_REFLECTOR_LENGTH)

    #
    # Peariscope Loop Code
    #

    current_time = time.time()
    while True: # Forever loop
        start_time = current_time

        # Grab a frame from the camera and store it in the preallocated space
        frame_time, image = sink.grabFrame(image)

        # If there is an error then notify the output and skip the iteration
        if frame_time == 0:
            output_stream.notifyError(sink.getError())
            continue

        # Compute and publish the image size
        image_height, image_width = image.shape[:2]
        nt.putNumber('image_height', image_height)
        nt.putNumber('image_width', image_width)

        # Process the image
        image = process_image(image, image_height, image_width, nt)

        # Draw crosshairs on the image
        image_center_x = int(image_width/2)
        image_center_y = int(image_height/2)
        cv2.line(image, (image_center_x, 0), (image_center_x, image_height-1), YELLOW, 1)
        cv2.line(image, (0, image_center_y), (image_width-1, image_center_y), YELLOW, 1)

        # Give the output stream the image to display
        output_stream.putFrame(image)

        # Compute elapsed time and FPS
        current_time = time.time()
        elapsed_time = current_time - start_time
        nt.putNumber('elapsed_time', elapsed_time)
        nt.putNumber('fps', 1/elapsed_time)

def process_image(image, image_height, image_width, nt):

    # Get configuration parameters
    min_reflector_width = nt.getNumber('min_reflector_width', MIN_REFLECTOR_WIDTH)
    max_reflector_width = nt.getNumber('max_reflector_width', MAX_REFLECTOR_WIDTH)
    min_reflector_length = nt.getNumber('min_reflector_length', MIN_REFLECTOR_LENGTH)
    max_reflector_length = nt.getNumber('max_reflector_length', MAX_REFLECTOR_LENGTH)

    #
    # Find Contours
    #

    # Convert the image from color to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Smooth (blur) the image to reduce high frequency noise
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Threshold the image to reveal the brightest regions in the blurred image
    binary_image = cv2.threshold(blurred_image, 200, 255, cv2.THRESH_BINARY)[1]

    # Remove any small blobs of noise using morphological filtering (erosions and dilations)
    binary_image = cv2.erode(binary_image, None, iterations=2)
    binary_image = cv2.dilate(binary_image, None, iterations=4)

    # Find contours in the binary image
    _, contours, _ = cv2.findContours(binary_image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

    #
    # Examine Contours
    #

    x_list = []
    y_list = []
    for index, cnt in enumerate(contours):

        # Draw the contour
        line_thickness = 2
        cv2.drawContours(image, [cnt], 0, RED, line_thickness)

        #
        # Contour Features
        #

        # Contour area
        cnt_area = cv2.contourArea(cnt)

        # Contour perimeter (arc length)
        cnt_perimeter = cv2.arcLength(cnt, True)

        # Contour centroid
        M = cv2.moments(cnt)
        cnt_x = int(M['m10']/M['m00'])
        cnt_y = int(M['m01']/M['m00'])

        # Contour solidity
        cnt_solidity = 100 * cnt_area / cv2.contourArea(cv2.convexHull(cnt))

        #
        # Rotated Features
        #

        # Find rotated rectangle surrounding the contour.
        # Returns a Box2D structure which contains following details:
        # (center (x,y), (width, height), angle of rotation)
        # width of rectangle becomes length (long side) of reflector
        # height of rectangle becomes width (short side) of reflector
        rect = cv2.minAreaRect(cnt)
        center, size, angle = rect
        rect_x, rect_y = center
        rect_length, rect_width = size
        rect_angle = -angle # horizontal is 0 degrees, CCW is positive

        # Make sure rectangle length is bigger than width
        if rect_width > rect_length:
            temp = rect_width
            rect_width = rect_length
            rect_length = temp
            rect_angle += 90

        # Keep the angle between -90 and +90 degrees
        if rect_angle > 90:
            rect_angle -= 180

        # Ratio of long side to short side of bounding rectangle
        rect_ratio = float(rect_length)/float(rect_width)

        #
        # Filter Contours
        #

        if not(min_reflector_width < rect_width < max_reflector_width):
            continue
        if not(min_reflector_length < rect_length <  max_reflector_length):
            continue

        #
        # Output Contours
        #

        # Draw the rotated rectangle
        box = np.int0(cv2.boxPoints(rect))
        image = cv2.drawContours(image, [box], 0, GREEN, line_thickness)

        # Draw a circle to mark the center of the rectangle
        radius = 2
        cv2.circle(image, (int(rect_x), int(rect_y)), radius, GREEN, -1)

        # Add the center to the list of detections
        x_list.append(rect_x)
        y_list.append(rect_y)

    # Output the lists of x and y coordinates of the reflectors
    x_list = [round(x, 1) for x in x_list]
    y_list = [round(y, 1) for y in y_list]
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

    return image
