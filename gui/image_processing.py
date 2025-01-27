import cv2
import numpy as np

def adjust_contrast_brightness(image, alpha=1.5, beta=0):
    """
    Adjust contrast and brightness.
    - alpha: Contrast factor. (>1 increases contrast)
    - beta: Brightness offset. (positive or negative)
    """
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted


def denoise_image(image):
    """Reduce noise in the image."""
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


def fast_denoise(image):
    """Apply a fast denoising technique using Gaussian Blur."""
    # Only apply blur to darker areas
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)  # Adjust kernel size as needed
    return blurred_image


def fast_median_denoise(image):
    """Apply a fast median blur to the image."""
    return cv2.medianBlur(image, 3)  # Use a small kernel for speed


def gamma_correction(image, gamma=1.2):
    """Apply gamma correction to brighten or darken the image."""
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)


def gamma_correction_denoise(image, gamma=1.2):
    """Reduce noise by applying gamma correction."""
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)


def sharpen_image(image):
    """Apply a sharpening filter to the image."""
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(image, -1, kernel)
    return sharpened


def process_image(image):
    # image = adjust_contrast_brightness(image, alpha=1.5, beta=20)
    # image = denoise_image(image) # --> Too slow
    # image = gamma_correction(image)
    image = gamma_correction_denoise(image)
    # image = fast_denoise(image) 
    # image = fast_median_denoise(image)
    image = sharpen_image(image)

    return image
