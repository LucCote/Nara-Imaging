# Automated !Nara Melon Identification Project

## Installation (Mac)
 1. [Download](https://github.com/LucCote/Nara-Imaging/archive/refs/heads/main.zip) and unzip or clone this repository
 2. Open terminal application and navigate to the downloaded repository folder
    - Example naviagtion command may be ```cd Downloads/Nara-Imaging-main```
 3. Install the required python libraries using the command ```pip install -r requirements.txt```
 4. Launch the user interface by running the command ```python ctkUI.py```

## Usage
1. Launch the UI as described in the installation steps.
2. Load a WorldView 2 multispectral tiff image (must include all 8 bands) to analyze using the "Upload TIF File" button located at the top of the screen
   - The image should then be displayed in the center of the screen
3. (Optional) Select a polygon shapefile mask which outlines the boundaries of rivers in the uploaded images using the "Upload Channel Mask Shapefile" button. This step enables the usage of separate classifiers for finding !Nara plants within a river channel and outside the river channel
   - This shapefile polygon must use latitude and longitude coordinates (WGS84)
4. Analyze the image for !Nara plants by pressing the "Find !Nara" button at the bottom of the screen
   - Note: this step may take some time to run, especially on large images
   - One can also toggle the option to search for !Nara outside the channel mask uploaded in step 3.
5. After the analysis is complete download a shape file containing the outlines the found !Nara plants or a CSV containing the coordinates of centroids using the buttons below the "Find !Nara" button

## Classifier Settings
The advanced settings page enables the user to adjust the classifier values. The way in which the software classifies contours is through the use of a 2-band mnormalized difference schema where we check if the difference between two bands scaled by their sum is within a certain value threshold. In the advanced settings the bands used in classification in addition to the lower and upper thresholds can be adjusted to specific image conditions as the researcher sees fit.
