import json
import time
import numpy as np
import cv2

from networktables import NetworkTables

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)

def peariscope(camera, inst):
    print("Peariscope by Pearadox Robotics Team 5414")
    print("Info", camera.getInfo())
    print("Path", camera.getPath())

    config = json.loads(camera.getConfigJson())
    height = config["height"]
    width = config["width"]
    fps = config["fps"]
    print("height {} width {} fps {}".format(height, width, fps))

    # Capture images from the camera
    sink = inst.getVideo()

    # Preallocate space for new color images
    image = np.zeros(shape=(height, width, 3), dtype=np.uint8)

    # Use network table to publish camera data
    nt = NetworkTables.getTable("Peariscope")

    # Send processed images back to the dashboard
    output_stream = inst.putVideo("Peariscope", width, height)

    # Peariscope Loop Code (process each image)
    current_time = time.time()
    while True:
        start_time = current_time

        # Grab a frame from the camera and put it in the source image
        frame_time, image = sink.grabFrame(image)

        # If there is an error then notify the output and skip the iteration
        if frame_time == 0:
            output_stream.notifyError(sink.getError())
            continue

        process_image(image, nt, output_stream)

        current_time = time.time()
        elapsed_time = current_time - start_time
        nt.putNumber("elapsed_time", elapsed_time)
        nt.putNumber("fps", 1/elapsed_time)

def process_image(image, nt, output_stream):
    image_height, image_width = image.shape[:2]
    nt.putNumberArray("image_size", [image_height, image_width])

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Smooth (blur) the image to reduce high frequency noise
    blur_img = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Compute the minimum and maximum pixel values [0, 255]
    (min_val, max_val, _, _) = cv2.minMaxLoc(blur_img)
    nt.putNumberArray("min_max_val", [min_val, max_val])

    # Threshold the image to reveal the brightest regions in the blurred image
    binary_image = cv2.threshold(blur_img, 200, 255, cv2.THRESH_BINARY)[1]

    # Remove any small blobs of noise using a series of erosions and dilations
    blob_img = cv2.erode(binary_image, None, iterations=2)
    blob_img = cv2.dilate(blob_img, None, iterations=4)

    # Perform a connected component analysis on the thresholded image
    connectivity = 4 # Choose 4 or 8 for connectivity type
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        blob_img, connectivity, cv2.CV_32S)

    # Examine each blob
    x_list = []
    y_list = []
    for i in range(num_labels):
        # Ignore this label if it is the background
        if i == 0:
            continue

        # Get features of the blob
        blob_area  = stats[i, cv2.CC_STAT_AREA]
        box_left   = stats[i, cv2.CC_STAT_LEFT]
        box_top    = stats[i, cv2.CC_STAT_TOP]
        box_width  = stats[i, cv2.CC_STAT_WIDTH]
        box_height = stats[i, cv2.CC_STAT_HEIGHT]
        box_bottom = box_top + box_height
        box_right  = box_left + box_width
        centroid_x, centroid_y = centroids[i]

        # Ignore blobs that are too big
        if box_height < image_height/2 and box_width < image_width/2:
            color = GREEN
            # Add the centroid to the list of detections
            x_list.append(centroid_x)
            y_list.append(centroid_y)
        else:
            color = RED

        # Draw a circle to mark the centroid of the reflector blob
        center = (int(centroid_x), int(centroid_y)) # Center of the circle
        radius = 2
        cv2.circle(image, center, radius, color, -1)

        # Draw a rectangle to mark the bounding box of the reflector blob
        line_thickness = 2
        cv2.rectangle(image, (box_left, box_top), (box_right, box_bottom), color, line_thickness)

    # Draw crosshairs on the image
    image_center_x = int(image_width/2)
    image_center_y = int(image_height/2)
    cv2.line(image, (image_center_x, 0), (image_center_x, image_height-1), YELLOW, 1)
    cv2.line(image, (0, image_center_y), (image_width-1, image_center_y), YELLOW, 1)

    # Give the output stream a new image to display
    output_stream.putFrame(image)

    # Output the lists of x and y coordinates for the blobs
    nt.putNumberArray("x_list", x_list)
    nt.putNumberArray("y_list", y_list)

    # Compute the coordinates as percentage distances from image center
    # for x (horizontal), 0 is center,  -100 is image left, 100 is image right
    # for y (vertical), 0 is center, -100 is image top, 100 is image bottom
    x_list_pct = [(x-image_width/2)/(image_width/2)*100 for x in x_list]
    y_list_pct = [(y-image_height/2)/(image_height/2)*100 for y in y_list]
    nt.putNumberArray("x_list_pct", x_list_pct)
    nt.putNumberArray("y_list_pct", y_list_pct)
