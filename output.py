import numpy as np
import rasterio
from shapely.geometry import Point, Polygon, mapping
import csv
import cv2
from pyproj import Transformer
import fiona

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

def transform_shape(shape, lats, longs):
  new_shape = np.copy(shape).astype('float64')
  for i in range(len(shape)):
    new_shape[i][0] = lats[shape[i][1]][shape[i][0]]
    new_shape[i][1] = longs[shape[i][1]][shape[i][0]]
  return new_shape


def get_center(contour, src):
    # print(contour)
    # polygon = Polygon(np.squeeze(contour))
    # if polygon.area < 0.0045*(polygon.length**2):
    #     return False
    lats, longs = load_coords(src)
    coords_shape = transform_shape(np.squeeze(contour), lats, longs)
    polygon = Polygon(coords_shape)
    center = polygon.centroid
    return center.x, center.y

def write_shape(file, contours, labels, src):
  # nara_coords = "latitude,longitude\n"
  lats, longs = load_coords(src)
  # Define a polygon feature geometry with one attribute
  schema = {
      'geometry': 'Polygon',
      'properties': {'id': 'int'},
  }
  # Write a new Shapefile
  with fiona.open(file, 'w', 'ESRI Shapefile', schema) as c:
    j = 0
    for i in range(len(contours)):
      if not labels[i]:
        continue
      contour = contours[i]
      coords_shape = transform_shape(np.squeeze(contour), lats, longs)
      polygon = Polygon(coords_shape)
      center = polygon.centroid
      # nara_coords+=str(center.y)+","+str(center.x)+"\n"
  
      ## If there are multiple geometries, put the "for" loop here
      c.write({
          'geometry': mapping(polygon),
          'properties': {'id': j},
      })
      j+=1

def write_csv(file,contours, labels, src):
  nara_coords = "latitude,longitude\n"
  lats, longs = load_coords(src)
  for i in range(len(contours)):
      if not labels[i]:
        continue
      contour = contours[i]
      coords_shape = transform_shape(np.squeeze(contour), lats, longs)
      polygon = Polygon(coords_shape)
      center = polygon.centroid
      nara_coords+=str(center.y)+","+str(center.x)+"\n"
  with open(file, "w") as text_file:
    text_file.write(nara_coords)
