import rasterio
import numpy as np
from metrics import get_metrics, segment_contours
# from contour import segment_contours
from analyze import classify_segment


src = rasterio.open('test_download.TIF')
contours = segment_contours('test_download.TIF', 4)
print(contours)
labels = np.zeros(len(contours))
for i in range(len(contours)):
  labels[i] = classify_segment(contours[i],src)
print(labels)
print(get_metrics(src,contours,labels,"test_sheet.csv"))
