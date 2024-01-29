import rasterio
import matplotlib.pyplot as plt
import cv2
import numpy as np

def segment_contours(image_path, contour_channel=5, display_channels=[5,4,2], min_contour_area=10, max_contour_area=2000):
    with rasterio.open(image_path) as src:
        # Read the selected channel for contour segmentation
        contour_band = src.read(contour_channel)

        # Ensure contour band is 2D (grayscale)
        if contour_band.ndim > 2:
            contour_band = contour_band[0]  # Take the first band if it's not already 2D

        # Convert the contour band to 8-bit without normalization
        contour_band_8bit = (contour_band / contour_band.max() * 255).astype('uint8')

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_image = clahe.apply(contour_band_8bit)

        # Apply Adaptive Thresholding
        adaptive_thresh = cv2.adaptiveThreshold(clahe_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 10)
        
        if np.mean(adaptive_thresh) > 127:
            adaptive_thresh = cv2.bitwise_not(adaptive_thresh)

        # Find contours
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area
        contours = [contour for contour in contours if min_contour_area < cv2.contourArea(contour) < max_contour_area]

        # # Display binary image
        # plt.imshow(adaptive_thresh, cmap='gray')
        # plt.title("Adaptive Threshold Image")
        # plt.axis('off')
        # plt.show()

        # Read and normalize display bands
        display_bands = src.read(display_channels)
        normalized_display_bands = [(band - np.min(band)) / (np.max(band) - np.min(band)) for band in display_bands]
        display_image = np.dstack(normalized_display_bands)
        display_image_8bit = (display_image * 255).astype('uint8')

        # Create a canvas for drawing contours
        contour_canvas = np.zeros_like(display_image_8bit)

        # Draw contours
        cv2.drawContours(contour_canvas, contours, -1, (255, 0, 0), 1)

        # # Display image with contours
        # plt.imshow(contour_canvas)
        # plt.title("Contours")
        # plt.axis('off')
        # plt.show()

        # Overlay contours on display image
        result_image = cv2.addWeighted(display_image_8bit, 1, contour_canvas, 0.5, 0)

        # Display result
        plt.imshow(result_image)
        plt.title("Result with Contours")
        plt.axis('off')
        plt.show()

        return contours

# Use the function
segment_contours('test.TIF')
