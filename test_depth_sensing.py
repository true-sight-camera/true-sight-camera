import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# Load and preprocess the images
left_image = cv.imread("test_images/left_image.png", cv.IMREAD_GRAYSCALE)
right_image = cv.imread("test_images/right_image.png", cv.IMREAD_GRAYSCALE)

# Align the left image (adjust based on observed misalignment)
x_offset = 0.06
y_offset = 0
rows, cols = right_image.shape
translation_matrix = np.float32([[1, 0, x_offset], [0, 1, y_offset]])

# Define broader parameter ranges
num_disparities_range = [16 * i for i in range(1, 6)]  # Test 16, 32, 48, 64, 80
block_size_range = [3, 5, 7, 9, 11, 13]  # Test more block sizes
uniqueness_ratio_range = [5, 10]  # Test broader uniqueness ratios

# Collect all parameter combinations
parameter_combinations = [
    (nd, bs, ur)
    for nd in num_disparities_range
    for bs in block_size_range
    for ur in uniqueness_ratio_range
    if bs % 2 != 0  # Skip invalid configurations
]

# Pagination settings
results_per_page = 6
total_pages = (len(parameter_combinations) + results_per_page - 1) // results_per_page

# Function to display a single page of results
def display_page(page_number):
    start_idx = page_number * results_per_page
    end_idx = start_idx + results_per_page
    combinations_to_display = parameter_combinations[start_idx:end_idx]

    # Set up subplots
    cols = 3  # Number of columns per page
    rows = (len(combinations_to_display) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 5))

    # Flatten axes for easier handling
    axes = axes.flatten()

    # Display results
    for idx, (num_disparities, block_size, uniqueness_ratio) in enumerate(combinations_to_display):
        # Create StereoSGBM with current parameters
        stereo = cv.StereoSGBM_create(
            minDisparity=0,
            numDisparities=num_disparities,
            blockSize=block_size,
            P1=8 * 1 * block_size ** 2,
            P2=32 * 1 * block_size ** 2,
            disp12MaxDiff=1,
            uniquenessRatio=uniqueness_ratio,
            speckleWindowSize=50,
            speckleRange=2,
            preFilterCap=63,
            mode=cv.STEREO_SGBM_MODE_HH
        )

        # Compute disparity map
        depth = stereo.compute(left_image, right_image).astype(np.float32) / 16.0

        # Normalize and convert to 8-bit for visualization
        depth_normalized = cv.normalize(depth, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
        depth_normalized = np.uint8(depth_normalized)

        # Plot the result
        ax = axes[idx]
        ax.imshow(depth_normalized, cmap='gray')
        ax.set_title(f"nd={num_disparities}, bs={block_size}, ur={uniqueness_ratio}", fontsize=10)
        ax.axis('off')

    # Hide any unused axes
    for idx in range(len(combinations_to_display), len(axes)):
        axes[idx].axis('off')

    # Add page title
    fig.suptitle(f"StereoSGBM Results (Page {page_number + 1}/{total_pages})", fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()

# Display all pages one by one
for page in range(total_pages):
    display_page(page)

# testing specific ones
# import numpy as np
# import cv2 as cv
# from matplotlib import pyplot as plt

# # Load and preprocess the images
# left_image = cv.imread("left_cam.png", cv.IMREAD_GRAYSCALE)
# right_image = cv.imread("right_cam.png", cv.IMREAD_GRAYSCALE)

# # Align the left image (adjust based on observed misalignment)
# x_offset = 0
# y_offset = 63
# rows, cols = right_image.shape
# translation_matrix = np.float32([[1, 0, x_offset], [0, 1, y_offset]])
# left_image = cv.warpAffine(left_image, translation_matrix, (cols, rows))

# # Equalize histograms for better contrast
# left_image = cv.equalizeHist(left_image)
# right_image = cv.equalizeHist(right_image)

# # Parameter combinations to test
# parameter_combinations = [
#     (16, 3, 10),
#     (32, 5, 10),
#     (16, 9, 10),
#     (32, 11, 10),
#     (48, 3, 5),
#     (48, 11, 10),
#     (64, 5, 10),
#     (64, 11, 5),
#     (80, 5, 5),
#     (80, 11, 10)
# ]

# # Set up subplots
# cols = 3  # Number of columns in the grid
# rows = (len(parameter_combinations) + cols - 1) // cols  # Calculate rows dynamically
# fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 5))

# # Flatten axes for easier handling
# axes = axes.flatten()

# # Loop through the parameter combinations
# for idx, (num_disparities, block_size, uniqueness_ratio) in enumerate(parameter_combinations):
#     # Create StereoSGBM with current parameters
#     stereo = cv.StereoSGBM_create(
#         minDisparity=0,
#         numDisparities=num_disparities,
#         blockSize=block_size,
#         P1=8 * 1 * block_size ** 2,
#         P2=32 * 1 * block_size ** 2,
#         disp12MaxDiff=1,
#         uniquenessRatio=uniqueness_ratio,
#         speckleWindowSize=50,
#         speckleRange=2,
#         preFilterCap=63,
#         mode=cv.STEREO_SGBM_MODE_SGBM_3WAY
#     )

#     # Compute disparity map
#     depth = stereo.compute(left_image, right_image).astype(np.float32) / 16.0

#     # Normalize and convert to 8-bit for visualization
#     depth_normalized = cv.normalize(depth, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
#     depth_normalized = np.uint8(depth_normalized)

#     # Plot the result
#     ax = axes[idx]
#     ax.imshow(depth_normalized, cmap='gray')
#     ax.set_title(f"nd={num_disparities}, bs={block_size}, ur={uniqueness_ratio}", fontsize=10, y=-0.2)
#     ax.axis('off')

# # Hide any unused axes
# for idx in range(len(parameter_combinations), len(axes)):
#     axes[idx].axis('off')

# # Add spacing between images
# fig.suptitle("Comparison of Selected StereoSGBM Parameter Combinations", fontsize=16)
# plt.tight_layout(pad=3.0, w_pad=2.0, h_pad=2.5)  # Adjust padding
# plt.subplots_adjust(top=0.9, bottom=0.05)  # Adjust top and bottom spacing
# plt.show()

