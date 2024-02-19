import rasterio
import numpy as np
from metrics import get_metrics, load_coords, transform_shape
from segment import segment_contours
from analyze import classify_segment
import matplotlib.pyplot as plt
import cv2
from output import write_shape
import fiona
from shapely.geometry import shape, Polygon


FILENAME = "testing_image.tif"

def display_image(src, contours, labels, display_channels=[5,4,2]):
   # Read and normalize display bands
    display_bands = src.read(display_channels)
    normalized_display_bands = [(band - np.min(band)) / (np.max(band) - np.min(band)) for band in display_bands]
    display_image = np.dstack(normalized_display_bands)
    display_image_8bit = (display_image * 255).astype('uint8')

    # Create a canvas for drawing contours
    contour_canvas = np.zeros_like(display_image_8bit)

    # Draw contours
    colors = {0: (0,255,0), 1: (255,0,0), 2:(0,255,255), 3:(255, 165, 0)}  # Define colors for each class
    for i in range(len(contours)):
        if labels[i] == 2:
           continue
        cv2.drawContours(display_image_8bit, [contours[i]], -1, colors[labels[i]], 2)

    # Overlay contours on display image
    result_image = cv2.addWeighted(display_image_8bit, 1, contour_canvas, 0.5, 0)

    # Display result
    plt.imshow(result_image)
    plt.title("Result with Contours")
    plt.axis('off')
    plt.show()

def read_shapefile(file):
  geometries = []
  # Open the shapefile
  with fiona.open(file) as shapefile:
      # Iterate over the records
      for record in shapefile:
          
          # Get the geometry from the record
          geometry = shape(record['geometry'])
          geometries.append(geometry)
  return geometries


# channel_masks = read_shapefile("test_mask_2.shp")

src = rasterio.open(FILENAME)

contours = segment_contours(FILENAME,5)

# lats,longs = load_coords(src)

# toremove = []
# for i in range(len(contours)):
#   contour = np.squeeze(contours[i])
#   coords_shape = Polygon(transform_shape(contour, lats, longs))
#   found = False
#   for mask in channel_masks:
#     if coords_shape.intersects(mask):
#        found = True
#        break
#   if not found:
#      toremove.append(i)

filtered_contours = contours
# for idx, ele in enumerate(contours): 
#   # checking if element not present in index list
#   if idx not in toremove:
#       filtered_contours.append(ele)

labels = np.zeros(len(filtered_contours))
for i in range(len(filtered_contours)):
  labels[i] = classify_segment(filtered_contours[i],src)



true_pos, false_pos, true_neg, false_neg, metric_labels = get_metrics(src,filtered_contours,labels,"channel_testing_data.csv")
print(true_pos, false_pos, true_neg, false_neg)

display_image(src,filtered_contours,metric_labels)

write_shape(filtered_contours, labels, src)

# Visualization or further processing
# For example, visualizing the classified contours with different colors:
# image = src.read(3)
# display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)  # Convert to BGR format for visualization
# colors = {True: (0,255,0), False: (255,0,0)}  # Define colors for each class
# for i in range(len(contours)):
#     cv2.drawContours(display_image, [contours[i]], -1, colors[labels[i]], 2)

# # Display the result using matplotlib
# plt.imshow(display_image)
# plt.show()
