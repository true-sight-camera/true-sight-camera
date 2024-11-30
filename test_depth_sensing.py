import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load calibration data
data = np.load("calibration_data.npz")
mtx_left, dist_left = data["mtx_left"], data["dist_left"]
mtx_right, dist_right = data["mtx_right"], data["dist_right"]
R, T = data["R"], data["T"]

# Load stereo images
img_left = cv2.imread("left_image.jpg")
img_right = cv2.imread("right_image.jpg")

# Step 1: Rectify Images
h, w = img_left.shape[:2]
R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
    mtx_left, dist_left, mtx_right, dist_right, (w, h), R, T, alpha=0
)

map1_left, map2_left = cv2.initUndistortRectifyMap(mtx_left, dist_left, R1, P1, (w, h), cv2.CV_16SC2)
map1_right, map2_right = cv2.initUndistortRectifyMap(mtx_right, dist_right, R2, P2, (w, h), cv2.CV_16SC2)

rectified_left = cv2.remap(img_left, map1_left, map2_left, cv2.INTER_LINEAR)
rectified_right = cv2.remap(img_right, map1_right, map2_right, cv2.INTER_LINEAR)

cv2.imwrite("rectified_left.jpg", rectified_left)
cv2.imwrite("rectified_right.jpg", rectified_right)

cv2.imshow("Rectified Left", rectified_left)
cv2.imshow("Rectified Right", rectified_right)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Step 2: Generate Disparity Map
gray_left = cv2.cvtColor(rectified_left, cv2.COLOR_BGR2GRAY)
gray_right = cv2.cvtColor(rectified_right, cv2.COLOR_BGR2GRAY)

stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)
disparity = stereo.compute(gray_left, gray_right).astype(np.float32) / 16.0
disparity_normalized = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)

cv2.imwrite("disparity.jpg", disparity_normalized)
cv2.imshow("Disparity", disparity_normalized)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Step 3: Calculate Depth
baseline = 0.1  # Baseline in meters
focal_length = mtx_left[0, 0]  # Focal length from calibration

disparity[disparity <= 0] = 1e-6  # Avoid division by zero
depth = (baseline * focal_length) / disparity
depth_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)

cv2.imwrite("depth.jpg", depth_normalized)
cv2.imshow("Depth Map", depth_normalized)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optional: Visualize Depth Map with Matplotlib
plt.imshow(depth, cmap="plasma")
plt.colorbar()
plt.title("Depth Map")
plt.show()
