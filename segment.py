import rasterio
import matplotlib.pyplot as plt
import cv2
import numpy as np

def segment_contours(image_path, contour_channels = [7,8, 5], display_channels = [5,4, 2], min_contour_area=1, max_contour_area=5000):
    with rasterio.open(image_path) as src:
        # Read the selected channels for contour segmentation
        contour_bands = src.read(contour_channels)

        # Combine the contour bands to create a grayscale image
        combined_contour_band = np.mean(contour_bands, axis=0)

        # Normalize the combined contour band
        normalized_contour_band = (combined_contour_band - np.min(combined_contour_band)) / (np.max(combined_contour_band) - np.min(combined_contour_band))

        # Convert the normalized contour band to 8-bit
        contour_band_8bit = (normalized_contour_band * 255).astype('uint8')

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_image = clahe.apply(contour_band_8bit)

        # Apply edge detection to enhance features
        edges = cv2.Canny(clahe_image, 100, 200)

        # Combine edge detection result with CLAHE image
        combined_image = cv2.bitwise_or(clahe_image, edges)


        # Apply Otsu's thresholding
        _, binary_image = cv2.threshold(combined_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area
        contours = [contour for contour in contours if min_contour_area < cv2.contourArea(contour) < max_contour_area]

        # # Print number of contours
        # print(f"Number of contours found: {len(contours)}")

        # # Display binary image
        # plt.imshow(binary_image, cmap='gray')
        # plt.title("Binary Image")
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

# Call the function with contour channels and display channels
segment_contours('19OCT11091449-M2AS_R1C1-012529890010_01_P002.TIF', [7,8, 5], [5, 4, 2])
