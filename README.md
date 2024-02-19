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
   - Sample Image is included within GIT Repository and will need to be unzipped.
3. (Optional) Select a polygon shapefile mask which outlines the boundaries of rivers in the uploaded images. This step enables the usage of separate classifiers for finding !Nara plants within a river channel and outside the river channel.
