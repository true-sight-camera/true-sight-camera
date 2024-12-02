import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# Load and preprocess the images
left_image = cv.imread("left_cam.png", cv.IMREAD_GRAYSCALE)
right_image = cv.imread("right_cam.png", cv.IMREAD_GRAYSCALE)

# Align the left image (adjust based on observed misalignment)
x_offset = 0
y_offset = 63
rows, cols = right_image.shape
translation_matrix = np.float32([[1, 0, x_offset], [0, 1, y_offset]])
left_image = cv.warpAffine(left_image, translation_matrix, (cols, rows))

# Equalize histograms for better contrast
left_image = cv.equalizeHist(left_image)
right_image = cv.equalizeHist(right_image)

# StereoSGBM with selected parameters
stereo = cv.StereoSGBM_create(
    minDisparity=0,
    numDisparities=48,      # Selected value (must be a multiple of 16)
    blockSize=11,            # Selected value
    P1=8 * 1 * 11 ** 2,      # P1 based on blockSize
    P2=64 * 1 * 11 ** 2,     # P2 based on blockSize
    disp12MaxDiff=1,
    uniquenessRatio=7,      # Selected value
    speckleWindowSize=100,   # Default for noise removal
    speckleRange=2,         # Default for disparity variation
    preFilterCap=63,
    mode=cv.STEREO_SGBM_MODE_SGBM_3WAY  # High-quality mode
)

# Compute disparity map
depth = stereo.compute(left_image, right_image)

# Normalize the disparity map for visualization
depth_normalized = cv.normalize(depth, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
depth_normalized = np.uint8(depth_normalized)

depth_smoothed = cv.medianBlur(depth_normalized, 5)



# Display the final depth map
plt.figure(figsize=(10, 5))
plt.imshow(depth_smoothed, cmap='gray')
plt.title("Final Depth Map (bs=9, ur=5, nd=80)")
plt.colorbar()
plt.show()
