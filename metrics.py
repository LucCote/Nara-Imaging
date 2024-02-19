import numpy as np
import rasterio
from shapely.geometry import Point, Polygon
import csv
import cv2
from pyproj import Transformer

# load nara point data
def load_coords(src):
  band1 = src.read(1)
  height = band1.shape[0]
  width = band1.shape[1]
  cols, rows = np.meshgrid(np.arange(width), np.arange(height))
  xs, ys = rasterio.transform.xy(src.transform, rows, cols)
  transformer = Transformer.from_crs("epsg:32733","epsg:4326")
  # print("TRANSFORM:",transformer.transform(7419231, 478181))
  for i in range(len(xs)):
    for j in range(len(xs[i])):
      newp = transformer.transform(xs[i][j], ys[i][j])
      xs[i][j] = newp[0]
      ys[i][j] = newp[1]
  lons= np.array(xs)
  lats = np.array(ys)
  return lats, lons

def load_points(file):
  points = []
  with open(file) as csvfile:
      reader = csv.reader(csvfile)
      next(reader, None)  # skip the headers
      for row in reader:
          points.append((float(row[1]),float(row[0])))
  return points

def transform_shape(shape, lats, longs):
  new_shape = np.copy(shape).astype('float64')
  for i in range(len(shape)):
    new_shape[i][0] = lats[shape[i][1]][shape[i][0]]
    new_shape[i][1] = longs[shape[i][1]][shape[i][0]]
  return new_shape

def point_in_shape(shape, point):
  pointS = Point(point)
  polygon = Polygon(shape)
  if polygon.contains(pointS):
    return True
  return polygon.exterior.distance(pointS) < 1e-4

def get_metrics(src, contour_shapes, contour_tags, truth_file):
  lats, longs = load_coords(src)
  true_loc = load_points(truth_file)
  # print(lats,longs,true_loc)
  true_pos = 0
  false_pos = 0
  true_neg = 0
  false_neg = 0
  true_tags = [False for shape in contour_shapes]
  metric_labels = [0 for shape in contour_shapes]
  false_pos_s = ""
  false_neg_s = ""
  true_pos_s = ""
  true_neg_s = ""
  for i in range(len(contour_shapes)):
     shape = contour_shapes[i]
     shape = np.squeeze(shape)
     tag = contour_tags[i]
     coords_shape = transform_shape(shape, lats, longs)
     for point in true_loc:
        if point_in_shape(coords_shape, point):
          true_tags[i] = True
          break
     if tag and true_tags[i]:
      true_pos += 1
      image_data=src.read()
      image = src.read(1)
      mask = np.zeros(image.shape, dtype=np.uint8)
      cv2.drawContours(mask, [contour_shapes[i]], -1, color=255, thickness=-1)
      segment_band_values = [band[mask == 255] for band in image_data]
      arr = []
      for j in range(0,8):
        arr.append(np.median(segment_band_values[j]))
      true_pos_s+=", ".join(str(num) for num in arr) + "\n"
     elif tag and not true_tags[i]:
      false_pos += 1
      
      image_data=src.read()
      image = src.read(1)
      mask = np.zeros(image.shape, dtype=np.uint8)
      cv2.drawContours(mask, [contour_shapes[i]], -1, color=255, thickness=-1)
      segment_band_values = [band[mask == 255] for band in image_data]
      arr = []
      for j in range(0,8):
        arr.append(np.median(segment_band_values[j]))
      false_pos_s+=", ".join(str(num) for num in arr) + "\n"
      metric_labels[i] = 1
     elif not tag and not true_tags[i]:
      image_data=src.read()
      image = src.read(1)
      mask = np.zeros(image.shape, dtype=np.uint8)
      cv2.drawContours(mask, [contour_shapes[i]], -1, color=255, thickness=-1)
      segment_band_values = [band[mask == 255] for band in image_data]
      arr = []
      for j in range(0,8):
        arr.append(np.median(segment_band_values[j]))
      true_neg_s+=", ".join(str(num) for num in arr) + "\n"

      true_neg += 1
      metric_labels[i] = 2
     elif not tag and true_tags[i]:

      image_data=src.read()
      image = src.read(1)
      mask = np.zeros(image.shape, dtype=np.uint8)
      cv2.drawContours(mask, [contour_shapes[i]], -1, color=255, thickness=-1)
      segment_band_values = [band[mask == 255] for band in image_data]
      arr = []
      for j in range(0,8):
        arr.append(np.median(segment_band_values[j]))
      false_neg_s+=", ".join(str(num) for num in arr) + "\n"

      false_neg += 1
      metric_labels[i] = 3
  with open("false_neg.csv", "w") as text_file:
    text_file.write(false_neg_s)
  with open("false_pos.csv", "w") as text_file:
    text_file.write(false_pos_s)
  with open("true_neg.csv", "w") as text_file:
    text_file.write(true_neg_s)
  with open("true_pos.csv", "w") as text_file:
    text_file.write(true_pos_s)
  return true_pos, false_pos, true_neg, false_neg, metric_labels

def segment_contours(image_path, contour_channel, min_contour_area=60, max_contour_area=5000):
    with rasterio.open(image_path) as src:
        # Read the selected channel for contour segmentation
        contours = []
        for i in range(1,9):
          contour_band = src.read(contour_channel)

          # Normalize the contour band
          normalized_contour_band = (contour_band - np.min(contour_band)) / (np.max(contour_band) - np.min(contour_band))

          # Convert the normalized contour band to 8-bit
          contour_band_8bit = (normalized_contour_band * 255).astype('uint8')

          # Apply Otsu's thresholding
          _, binary_image = cv2.threshold(contour_band_8bit, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

          # Find contours on the binary image
          contours2, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

          # Filter contours by area
          contours += [contour for contour in contours2 if min_contour_area < cv2.contourArea(contour) < max_contour_area]

        return contours

if __name__ == "__main__":
  src = rasterio.open('test_download.TIF')
  contours = segment_contours('test_download.TIF', 4)
  print("found", len(contours))
  tags = [False for ele in contours]
  print(get_metrics(src, contours, tags, 'test_sheet.csv'))


  
