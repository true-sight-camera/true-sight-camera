import cv2
import numpy as np

# Settings
chessboard_size = (8, 5)
square_size = 0.028  # Size of a square in meters
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Arrays to store 3D points and 2D image points
obj_points = []  # 3D points in real world
img_points_left = []  # 2D points in left camera
img_points_right = []  # 2D points in right camera

# Create object points for the chessboard
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size

# Detect chessboard corners
for i in range(1, 7):
    left = cv2.imread(f"calibration_images/left_{i}.png")
    right = cv2.imread(f"calibration_images/right_{i}.png")

    gray_left = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

    flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK
    ret_left, corners_left = cv2.findChessboardCorners(gray_left, chessboard_size, flags)
    ret_right, corners_right = cv2.findChessboardCorners(gray_right, chessboard_size, flags)

    if ret_left and ret_right:
        obj_points.append(objp)
        img_points_left.append(corners_left)
        img_points_right.append(corners_right)

# Camera calibration
ret_left, mtx_left, dist_left, _, _ = cv2.calibrateCamera(obj_points, img_points_left, gray_left.shape[::-1], None, None)
ret_right, mtx_right, dist_right, _, _ = cv2.calibrateCamera(obj_points, img_points_right, gray_right.shape[::-1], None, None)

# Stereo calibration
retval, _, _, _, _, R, T, _, _ = cv2.stereoCalibrate(
    obj_points, img_points_left, img_points_right, 
    mtx_left, dist_left, mtx_right, dist_right, 
    gray_left.shape[::-1], criteria=criteria, flags=cv2.CALIB_FIX_INTRINSIC
)

# Save calibration data
np.savez("calibration_data.npz", mtx_left=mtx_left, dist_left=dist_left, mtx_right=mtx_right, dist_right=dist_right, R=R, T=T)
