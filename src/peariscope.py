import json
import time
import numpy as np
import cv2

from networktables import NetworkTables

# Define colors (BGR)
BGR_RED = (0, 0, 255)
BGR_GRN = (0, 255, 0)
BGR_BLU = (255, 0, 0)
BGR_YEL = (0, 255, 255)

def peariscope(camera, inst):

    #
    # Peariscope Setup Code
    #

    print('Peariscope by Pearadox Robotics Team 5414')
    print('Info', camera.getInfo())
    print('Path', camera.getPath())

    # Load FRC configuration file
    config = json.loads(camera.getConfigJson())
    camera_height = config['height']
    camera_width = config['width']
    camera_fps = config['fps']
    print('camera_height {} camera_width {} fps {}'.format(camera_height, camera_width, camera_fps))

    # Create sink for capturing images from the camera video stream
    sink = inst.getVideo()

    # Preallocate space for new color images
    image = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)

    # Create output stream for sending processed images
    output_stream = inst.putVideo('Peariscope', camera_width, camera_height)

    # Use network tables to receive configuration parameters and for publishing results
    nt = NetworkTables.getTable('Peariscope')
    time.sleep(1)

    # Set configuration parameters
    nt.putNumber('min_hue', 55)
    nt.putNumber('max_hue', 65)
    nt.putNumber('min_sat', 170)
    nt.putNumber('max_sat', 255)
    nt.putNumber('min_val', 100)
    nt.putNumber('max_val', 255)
    nt.putNumber('min_height', 6)
    nt.putNumber('max_height', 1000)
    nt.putNumber('min_width', 6)
    nt.putNumber('max_width', 1000)
    nt.putNumber('min_vert', 0)
    nt.putNumber('max_vert', 20)

    #
    # Peariscope Loop Code
    #

    current_time = time.time()
    while True: # Forever loop
        start_time = current_time

        # Get configuration parameters
        min_hue = nt.getNumber('min_hue', None)
        max_hue = nt.getNumber('max_hue', None)
        min_sat = nt.getNumber('min_sat', None)
        max_sat = nt.getNumber('max_sat', None)
        min_val = nt.getNumber('min_val', None)
        max_val = nt.getNumber('max_val', None)
        min_height = nt.getNumber('min_height', None)
        max_height = nt.getNumber('max_height', None)
        min_width = nt.getNumber('min_width', None)
        max_width = nt.getNumber('max_width', None)
        min_vert = nt.getNumber('min_vert', None)
        max_vert = nt.getNumber('max_vert', None)

        # Grab a frame from the camera and store it in the preallocated space
        frame_time, image = sink.grabFrame(image)

        # If there is an error then notify the output and skip the iteration
        if frame_time == 0:
            output_stream.notifyError(sink.getError())
            continue

        # Publish the image size
        image_height, image_width = image.shape[:2]
        nt.putNumber('image_height', image_height)
        nt.putNumber('image_width', image_width)

        # Segment the image based on hue, saturation, and value ranges
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        binary_image = cv2.inRange(hsv_image, (min_hue, min_sat, min_val), (max_hue, max_sat, max_val))

        # Remove any small blobs of noise using morphological filtering (erosions and dilations)
        binary_image = cv2.erode(binary_image, None, iterations=3)
        binary_image = cv2.dilate(binary_image, None, iterations=3)

        # Find contours in the binary image
        _, contour_list, _ = cv2.findContours(binary_image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

        #
        # Examine Contours
        #

        x_list = []
        y_list = []

        for contour in contour_list:

            # Contour size
            x, y, w, h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue # Forget this contour
            if (h < min_height or h > max_height):
                continue # Forget this contour

            # Vertex count
            num_vertex = len(contour)
            if (num_vertex < min_vert or num_vertex > max_vert):
                continue # Forget this contour

            # Draw the contour
            cv2.drawContours(image, [contour], 0, color=BGR_BLU, thickness=-1)

            # Contour centroid (center of mass)
            M = cv2.moments(contour)
            contour_x = int(M['m10']/M['m00'])
            contour_y = int(M['m01']/M['m00'])

            # Draw a circle to mark the center of the contour
            cv2.circle(image, center=(contour_x, contour_y), radius=3, color=BGR_RED, thickness=-1)

            # Draw crosshairs to mark the center of the contour
            cv2.line(image, (contour_x, 0), (contour_x, image_height-1), BGR_RED, 1)
            cv2.line(image, (0, contour_y), (image_width-1, contour_y), BGR_RED, 1)

            # Add the center to the list of detections
            x_list.append(contour_x)
            y_list.append(contour_y)

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

        # Draw crosshairs on the image
        image_center_x = int(image_width/2)
        image_center_y = int(image_height/2)
        cv2.line(image, (image_center_x, 0), (image_center_x, image_height-1), BGR_YEL, 1)
        cv2.line(image, (0, image_center_y), (image_width-1, image_center_y), BGR_YEL, 1)

        # Give the output stream the image to display
        output_stream.putFrame(image)

        # Compute elapsed time and FPS
        current_time = time.time()
        elapsed_time = current_time - start_time
        nt.putNumber('fps', 1/elapsed_time)

