import rasterio
import matplotlib.pyplot as plt
import cv2
import numpy as np
from shapely.geometry import Point, Polygon, MultiPoint


def classify_segment(contour, src, classifiers):
    # get contour data
    image_data=src.read()
    image = src.read(1)
    mask = np.zeros(image.shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, color=255, thickness=-1)

    # remove contours with very long shapes (via square bounding box)
    rect = MultiPoint(np.squeeze(contour)).envelope
    polygon = Polygon(np.squeeze(contour))
    x, y = rect.exterior.coords.xy
    # get length of bounding box edges
    edge_length = (Point(x[0], y[0]).distance(Point(x[1], y[1])), Point(x[1], y[1]).distance(Point(x[2], y[2])))
    # get length of polygon as the longest edge of the bounding box
    square = max(edge_length)**2
    if polygon.area < 0.1*square:
        return False

    # Extract band data for the current segment
    segment_band_values = [band[mask == 255] for band in image_data]

    # Define your classification logic here
    # For example, based on mean value of the band data:
    b1 = np.median(segment_band_values[0])
    b2 = np.median(segment_band_values[1])
    b3 = np.median(segment_band_values[2])
    b4 = np.median(segment_band_values[3])
    b5 = np.median(segment_band_values[3])
    b6 = np.median(segment_band_values[5])
    b7 = np.median(segment_band_values[6])
    b8 = np.median(segment_band_values[7])
    bands = [b1,b2,b3,b4,b5,b6,b7,b8]

    # apply each given classifier
    for i in range(len(classifiers)):
        bpos = bands[classifiers[i][0]-1]
        bneg = bands[classifiers[i][1]-1]
        normalized_diff = (bpos-bneg)/(bpos+bneg)
        threshold_low = classifiers[i][2]
        threshold_high = classifiers[i][3]
        if normalized_diff < threshold_low or normalized_diff > threshold_high:
            return False # didn't pass a portion of the classifier
    
    return True


    # deprecated hardcoded classifier (left for reference in comments)

    # normalized_diff = (b7-b1)/(b7+b1)
    # nara_threshold = 0.3061
    # threshold_std = 2*.007612

    # if normalized_diff >= nara_threshold - threshold_std:
    #     normalized_diff = (b4-b1)/(b4+b1)
    #     nara_threshold = 0.1951
    #     threshold_std = .12
    #     # threshold_std = .05
    #     if normalized_diff <= nara_threshold + threshold_std and normalized_diff >= nara_threshold - threshold_std:
    #         return True
        
    # return False
