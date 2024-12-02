import cv2 as cv
import numpy as np

# Load the images
left_image = cv.imread("left_cam.png", cv.IMREAD_GRAYSCALE)
right_image = cv.imread("right_cam.png", cv.IMREAD_GRAYSCALE)

# Define translation offsets (tweak these values based on observed misalignment)
x_offset = -325  # Positive: Move right; Negative: Move left
y_offset = 63 # Positive: Move down; Negative: Move up

# Create the translation matrix
rows, cols = right_image.shape
translation_matrix = np.float32([[1, 0, x_offset], [0, 1, y_offset]])

# Apply the translation to align the left image
aligned_left = cv.warpAffine(left_image, translation_matrix, (cols, rows))

# Verify alignment by overlaying the images
overlay = cv.addWeighted(aligned_left, 0.5, right_image, 0.5, 0)

# Display the images
# cv.imshow("Original Left Image", left_image)
# cv.imshow("Right Image", right_image)
cv.imshow("Aligned Left Image", aligned_left)
cv.imshow("Overlay", overlay)
cv.waitKey(0)
cv.destroyAllWindows()
