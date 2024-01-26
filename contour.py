import rasterio
import matplotlib.pyplot as plt
import cv2
import numpy as np

def segment_contours(image_path, chunk_size=256, overlap=32, manual_threshold=50):
    with rasterio.open(image_path) as src:
        #channels = [2,4,7]
        image = src.read(3)


        # Convert the image to 8-bit
        if image.dtype == 'uint16':
            image = (image / 256).astype('uint8')

        # Determine the number of chunks needed along each dimension
        num_chunks_x = image.shape[1] // chunk_size
        num_chunks_y = image.shape[0] // chunk_size

        all_contours = []

        # Process each chunk
        for i in range(num_chunks_y):
            for j in range(num_chunks_x):
                # Compute the region of interest with overlap to avoid edge effects
                x1 = max(j * chunk_size - overlap, 0)
                x2 = min((j + 1) * chunk_size + overlap, image.shape[1])
                y1 = max(i * chunk_size - overlap, 0)
                y2 = min((i + 1) * chunk_size + overlap, image.shape[0])
                
                chunk = image[y1:y2, x1:x2]

                # Thresholding to create a binary image
                # chunk: source image
                # manual_threshold: threshold value
                # 255: maxVal, color value to assign if pixel value less than the threshold value
                # cv2.THRESH_BINARY_INV: thresholding type, which sets the pixel to maxVal if it is below the threshold value
                _, binary_chunk = cv2.threshold(chunk, manual_threshold, 255, cv2.THRESH_BINARY_INV)

                # Find contours
                # binary_chunk: source binary image from which to find contours
                # cv2.RETR_EXTERNAL: contour retrieval mode, retrieves only the extreme outer contours
                # cv2.CHAIN_APPROX_SIMPLE: contour approximation method, compresses horizontal, vertical, and diagonal segments and leaves only their end points
                contours, _ = cv2.findContours(binary_chunk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Move the contour points to match the original image's coordinate space and store them
                for contour in contours:
                    contour[:, :, 0] += x1
                    contour[:, :, 1] += y1
                    all_contours.append(contour)

        # Create an output image to draw the contours on
        # Convert the original image to a 3-channel BGR image
        display_image = cv2.cvtColor(image, cv2.COLOR_BAYER_BG2BGR_EA)

        # Draw the contours on the output image
        # display_image: destination image
        # all_contours: list of all contours to draw
        # -1: indicates all contours are to be drawn
        # (255, 0, 0): red contours 
        # 2: thickness of the contours
        cv2.drawContours(display_image, all_contours, -1, (255, 0, 0), 2)

        # Display the result using matplotlib
        plt.imshow(display_image)
        plt.show()

# Call the function with the specified parameters
segment_contours('test.tif', chunk_size=256, overlap=32, manual_threshold=70)

