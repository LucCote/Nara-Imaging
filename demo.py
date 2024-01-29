import rasterio
import numpy as np
from metrics import get_metrics
from segment import segment_contours
# from contour import segment_contours
from analyze import classify_segment


FILENAME = "AOI2.TIF"

def display_image(src, contours, labels, display_channels=[5,4,2]):
   # Read and normalize display bands
    display_bands = src.read(display_channels)
    normalized_display_bands = [(band - np.min(band)) / (np.max(band) - np.min(band)) for band in display_bands]
    display_image = np.dstack(normalized_display_bands)
    display_image_8bit = (display_image * 255).astype('uint8')

    # Create a canvas for drawing contours
    contour_canvas = np.zeros_like(display_image_8bit)

    # Draw contours
    colors = {0: (0,255,0), 1: (255,0,0), 2:(255,0,255), 3:(0,0,255)}  # Define colors for each class
    for i in range(len(contours)):
        cv2.drawContours(display_image_8bit, [contours[i]], -1, colors[labels[i]], 2)

    # Overlay contours on display image
    result_image = cv2.addWeighted(display_image_8bit, 1, contour_canvas, 0.5, 0)

    # Display result
    plt.imshow(result_image)
    plt.title("Result with Contours")
    plt.axis('off')
    plt.show()

src = rasterio.open('AOI2.TIF')
contours = segment_contours('AOI2.TIF',8)
print(contours)
labels = np.zeros(len(contours))
for i in range(len(contours)):
  labels[i] = classify_segment(contours[i],src)
print(labels)
print(get_metrics(src,contours,labels,"test_sheet.csv"))
