# All Credit goes to Github user JackToaster (Discord: A Toaster#9900) for providing this script

import argparse
import numpy as np
import cv2

parser = argparse.ArgumentParser(description='Calibrate a camera')
parser.add_argument('--resolution', '-r', nargs=2)
parser.add_argument('--camera', '-c', default=0)
parser.add_argument('--gridsize', '-g', default=0.0254)  # Default to 1 inch grid
parser.add_argument('--output', '-o')

parsed = parser.parse_args()

CAMERA_MATRIX_NAME = 'camera_matrix'
DISTORTION_COEFFICIENTS_NAME = 'distortion_coefficients'

WRITE_PATH = parsed.output

GRID_SQUARE_SIZE = float(parsed.gridsize)

RESOLUTION = tuple([int(res) for res in parsed.resolution])

# Create video capture
cap = cv2.VideoCapture(int(parsed.camera))

cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION[1])

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Scale to real grid size
objp = np.multiply(objp, GRID_SQUARE_SIZE)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

ret, img = cap.read()
if not ret:
    raise Exception('Camera input failed to read')
h, w = img.shape[:2]

print('Searching for calibration checkerboard. Press q to calibrate once enough samples (usually 20-50) have been recorded.')

while True:
    _, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7, 6), None)
    # If found, add object points, image points (after refining them)
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        # Draw and display the corners
        cv2.drawChessboardCorners(img, (7, 6), corners2, ret)
        cv2.putText(img, 'Calibrating - ' + str(len(objpoints)) + ' samples - press Q to stop', (5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        cv2.putText(img, 'Press Y/N to accept/reject sample', (5, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 255))
        cv2.imshow('img', img)
        key = cv2.waitKey(5000)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('y'):
            objpoints.append(objp)
            imgpoints.append(corners2)
    else:
        cv2.putText(img, 'Calibrating - ' + str(len(objpoints)) + ' samples - press Q to stop', (5, 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

print('Computing camera calibration parameters. This may take a minute...')
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print('camera_matrix = np.' + repr(mtx))
print('distortion_coefficients = np.' + repr(dist))

print('Saving to ' + WRITE_PATH)


def write_calibration_file(path: str, camera_matrix, distortion_coefficients):
    fs = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    fs.write(CAMERA_MATRIX_NAME, camera_matrix)
    fs.write(DISTORTION_COEFFICIENTS_NAME, distortion_coefficients)


write_calibration_file(WRITE_PATH, mtx, dist)

# Calculate how accurate the calibration was (Reprojection error)
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error

print("reprojection_error = {}".format(mean_error/len(objpoints)))

print('Showing undistorted image. Press q to exit.')

new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

while True:
    _, img = cap.read()
    # undistort
    dst = cv2.undistort(img, mtx, dist, None, new_camera_mtx)
    # crop the image
    # x, y, w, h = roi
    # dst = dst[y:y + h, x:x + w]

    cv2.putText(dst, 'Undistorted', (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (0, 0, 255))
    cv2.imshow('img', dst)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break