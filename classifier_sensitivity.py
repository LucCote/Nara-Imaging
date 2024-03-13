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
files = ["nara_testing/test2.tif","nara_testing/test3.tif","nara_testing/test4.tif"]
metrics = ["nara_testing/test2.csv","nara_testing/test3.csv","nara_testing/test4.csv"]
masks = ["nara_testing/test2.shp","nara_testing/test3.shp","nara_testing/test4.shp"]
for j in range(2):
   for k in range(2):
      for l in range(-2,3):
        precision_rates = []
        recall_rates = []
        channel_classifiers = [[7,1,.3,100], [4,1,.12,.27]]
        mod = .01*l
        # mod = 0
        channel_classifiers[j][k+2] += mod

        for i in range(len(files)):
          file = files[i]
          metric = metrics[i]
          mask = masks[i]
          geometries = []
          with fiona.open(mask) as shapefile:
            # Iterate over the records
            for record in shapefile:
                # Get the geometry from the record
                geometry = shape(record['geometry'])
                geometries.append(geometry)

          src = rasterio.open(file)

          contours = segment_contours(file,5)
          lats,longs = load_coords(src)
          # filtered_contours = []
          # for i in range(len(contours)):
          #   coords_shape = Polygon(transform_shape(np.squeeze(contours[i]), lats, longs))
          #   found = False
          #   for geometry in geometries:
          #       if coords_shape.intersects(geometry):
          #           found = True
          #       break
          #   if found:
          #      filtered_contours.append(contours[i])
          channel_classifiers = [[7,1,.3,100], [4,1,.12,.27]]
          filtered_contours = contours
          # channel_classifiers = [[7,1,.28,100], [4,1,.12,.26]]
          labels = np.zeros(len(filtered_contours))
          for i in range(len(filtered_contours)):
            labels[i] = classify_segment(filtered_contours[i],src, channel_classifiers)


          true_pos, false_pos, true_neg, false_neg, metric_labels = get_metrics(src,filtered_contours,labels,metric)
          print(true_pos, false_pos, true_neg, false_neg)
          precision_rates.append(true_pos/(true_pos+false_pos))
          recall_rates.append(true_pos/(true_pos+false_neg))

          display_image(src,filtered_contours,metric_labels)

          # write_shape(filtered_contours, labels, src)
        print(channel_classifiers)
        print(recall_rates, sum(recall_rates)/len(files))
        print(precision_rates, sum(precision_rates)/len(files))
