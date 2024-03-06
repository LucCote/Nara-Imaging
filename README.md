# Automated !Nara Melon Identification Project

## Installation (Mac)
 1. [Download](https://github.com/LucCote/Nara-Imaging/archive/refs/heads/main.zip) and unzip or clone this repository
 2. Open the terminal application from Finder and navigate to the downloaded repository folder
    - Example naviagtion command may be ```cd Downloads/Nara-Imaging-main```
 3. Install the required python libraries using the command ```pip install -r requirements.txt```
 4. Launch the user interface by running the command ```python ctkUI.py```

## Installation (Windows)

### Python Installation
1. Go to your Start menu (lower left Windows icon), type "Microsoft Store", select the link to open the store.
2. Once the store is open, select Search from the upper-right menu and enter "Python". Select any version above 3.9 Python from the results under Apps (recommend the most recent). Once you've determined which version you would like to install, select Get.
3. Once Python has completed the downloading and installation process, open Windows PowerShell using the Start menu (lower left Windows icon). Once PowerShell is open, enter the command ```Python --version``` to confirm that Python3 has installed on your machine. Also confirm that pip is installed with the command ```pip --version ```

 ### VS Code Installation
 1. To install VS Code, download VS Code for Windows: https://code.visualstudio.com.
 2. To connect VS Code and Python, search for Python in the extensions menu (Ctrl+Shift+X) and install.
 3. Once you've installed the Python extension, select a Python 3 interpreter by opening the Command Palette (Ctrl+Shift+P), start typing the command Python: Select Interpreter to search, then select the command.
 4. To open the terminal in VS Code, select View > Terminal, or alternatively use the shortcut Ctrl+` (using the backtick character). The default terminal is PowerShell.
 5. [Download](https://github.com/LucCote/Nara-Imaging/archive/refs/heads/main.zip) and unzip or clone this repository
 6. Inside your VS Code terminal, open Python by simply entering the command: python
 7. Navigate to the downloaded repository folder
    - Example naviagtion command may be ```os.chdir(Downloads/Nara-Imaging-main)```
 8. Install the required python libraries using the command ```pip install -r requirements.txt```
    - If this does not work, then try to individually download using... 
 10. Launch the user interface by running the command ```python ctkUI.py```


## Usage
1. Launch the UI as described in the installation steps.
2. Load a WorldView 2 multispectral tiff image (must include all 8 bands) to analyze using the "Upload TIF File" button located at the top of the screen
   - Click [here](https://github.com/LucCote/Nara-Imaging/raw/main/demo_data.zip) to download an image and a channel mask that can be used to run the algorithm and test its functionality
   - The image should then be displayed in the center of the screen
3. (Optional) Select a polygon shapefile mask which outlines the boundaries of rivers in the uploaded images using the "Upload Channel Mask Shapefile" button. This step enables the usage of separate classifiers for finding !Nara plants within a river channel and outside the river channel
   - This shapefile polygon must use latitude and longitude coordinates (WGS84)
4. Analyze the image for !Nara plants by pressing the "Find !Nara" button at the bottom of the screen
   - Note: this step may take some time to run, especially on large images
   - One can also toggle the option to search for !Nara outside the channel mask uploaded in step 3
5. After the analysis is complete download a shape file containing the outlines the found !Nara plants or a CSV containing the coordinates of centroids using the buttons below the "Find !Nara" button

## Classifier Settings
The advanced settings page enables the user to adjust the classifier values. The way in which the software classifies contours is through the use of a 2-band normalized difference schema where we check if the difference between two bands scaled by their sum is within a certain value threshold. In the advanced settings, the bands used in classification in addition to the lower and upper thresholds can be adjusted to specific image conditions as the researcher sees fit. After every new image upload the settings will reset to default. 

## Other Thoughts
- In order to minimize runtime, we recommend to clip images before inputting into our algorithm
  - An alternative option is to put a channel mask as described above 

## Additional Help
For additional help for windows installation see: https://learn.microsoft.com/en-us/windows/python/beginners 
Questions can also be directed to jonathan.w.chipman@dartmouth.edu 

