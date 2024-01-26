import rasterio
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time

def segment_and_classify(image_path, chunk_size=256, overlap=32, manual_threshold=50):
    with rasterio.open(image_path) as src:
        # Read all bands or specific bands you're interested in
        # For example, reading all bands: image_data = src.read()
        # For specific bands (e.g., bands 2, 4, 7): image_data = src.read([2, 4, 7])
        image_data = src.read()

        # Assume band 3 is used for contouring as before
        image = image_data[2]  # Band 3 for example
        
        #contour segmentation
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

        print(contours)

        # Classification logic:
        def classify_segment(segment_stats):
            # Define your classification logic here
            # For example, based on mean value of the band data:
            b1 = np.mean(segment_band_values[0])
            b4 = np.mean(segment_band_values[3])
            b7 = np.mean(segment_band_values[6])

            #one band 
            normalized_diff = (b4-b7)/(b4+b7)
            nara_threshold = .075672
            threshold_std = 3*.007612

            if normalized_diff <= nara_threshold + threshold_std and normalized_diff >= nara_threshold - threshold_std:
                return '!Nara'
            else:
                return 'Non !Nara'

        # Iterate through each contour and classify
        classified_contours = []
        for contour in all_contours:
            # Create a mask for the current contour
            mask = np.zeros(image.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, color=255, thickness=-1)

            # Extract band data for the current segment
            segment_band_values = [band[mask == 255] for band in image_data]

            # Classify the segment based on band values
            segment_class = classify_segment(segment_band_values)
            
            # Store the contour and its classification
            classified_contours.append((contour, segment_class))

        print(classified_contours)
        
        # Visualization or further processing
        # For example, visualizing the classified contours with different colors:
        display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)  # Convert to BGR format for visualization
        colors = {'!Nara': (255, 0, 0), 'Non !Nara': (0, 255, 0)}  # Define colors for each class
        for contour, segment_class in classified_contours:
            cv2.drawContours(display_image, [contour], -1, colors[segment_class], 2)

        # Display the result using matplotlib
        plt.imshow(display_image)
        plt.show()

start_time = time.time()
# Call the function with the specified parameters
segment_and_classify('test.tif', chunk_size=256, overlap=32, manual_threshold=70)
end_time = time.time()
print(f"The process took {end_time - start_time} seconds.")
