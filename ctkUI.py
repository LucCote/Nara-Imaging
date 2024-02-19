import tkinter
import tkinter as tk
from tkinter import *
from PIL import ImageTk,Image
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import rasterio
import numpy as np
from metrics import get_metrics
from segment import segment_contours
# from contour import segment_contours
from analyze import classify_segment
import matplotlib.pyplot as plt
import cv2
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
import fiona
from shapely.geometry import shape, Polygon
from metrics import get_metrics, load_coords, transform_shape
from output import write_csv, write_shape


fig = None
ax = None
im = None
canvas = None
src = None
filename = None
masks = None

aftid = 0

# Displaying images
def display_im(image):
    # Generate the figure and plot object which will be linked to the root element
    global fig
    global ax
    global canvas
    global im
    global aftid
    fig, ax = plt.subplots()
    fig.set_size_inches(3,3)
    im = ax.imshow(image)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    canvas = FigureCanvasTkAgg(fig,master=tabview.tab("Display"))
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.5, rely=0.56, anchor=CENTER)

def openFile():
    global src
    global filename
    global masks
    masks = None
    filename = filedialog.askopenfilename(initialdir="", title="Select a File / Kies 'n lêer", filetypes=(("tiff","*.tiff, *.tif"),("All files","*.*")))
    src = rasterio.open(filename)
    display_channels=[5,4,2]
    display_bands = src.read(display_channels)
    normalized_display_bands = [(band - np.min(band)) / (np.max(band) - np.min(band)) for band in display_bands]
    display_image = np.dstack(normalized_display_bands)
    display_image_8bit = (display_image * 255).astype('uint8')
    display_im(display_image_8bit)

def openMask():
    global masks
    filename = filedialog.askopenfilename(initialdir="", title="Select a File / Kies 'n lêer", filetypes=(("shape","*.shp"),("All files","*.*")))
    geometries = []
    # Open the shapefile
    with fiona.open(filename) as shapefile:
        # Iterate over the records
        for record in shapefile:
            # Get the geometry from the record
            geometry = shape(record['geometry'])
            geometries.append(geometry)
    masks = geometries
    
def changeLanguage():
    if switchLang.get() == "Afrikaans":
        welcomeText.configure(text = "Laai 'n prent op met die knoppie hieronder. Die prent moet 'n .tif-uitbreiding hê.")
    elif switchLang.get() == "English":
        welcomeText.configure(text = "Upload an image using the button below. The image must have a .tif extension.")

def csv():
    global contours
    global labels
    global src
    if contours == None:
        return
    write_csv(contours, labels, src)

def shapefile():
    global contours
    global labels
    global src
    if contours == None:
        return
    write_shape(contours, labels, src)

def demo():
    global fig
    global ax
    global canvas
    global im
    global src
    global filename
    global channel_classifiers
    global dune_classifiers
    global masks
    global contours
    global labels
    display_im(src.read(1))

    contours = segment_contours(filename,5)
    lats,longs = load_coords(src)

    # print(contours)
    labels = np.zeros(len(contours))
    for i in range(len(contours)):
        # toremove = []
# for i in range(len(contours)):
#   contour = np.squeeze(contours[i])
        if masks != None:
            coords_shape = Polygon(transform_shape(np.squeeze(contours[i]), lats, longs))
            found = False
            for mask in masks:
                if coords_shape.intersects(mask):
                    found = True
                break
            if found:
                labels[i] = classify_segment(contours[i],src, channel_classifiers)
            else:
                labels[i] = classify_segment(contours[i],src, dune_classifiers)
        else:
            labels[i] = classify_segment(contours[i],src, channel_classifiers)
    print(labels)
    # Visualization or further processing
    # For example, visualizing the classified contours with different colors:
    display_channels=[5,4,2]
    display_bands = src.read(display_channels)
    normalized_display_bands = [(band - np.min(band)) / (np.max(band) - np.min(band)) for band in display_bands]
    display_image = np.dstack(normalized_display_bands)
    display_image_8bit = (display_image * 255).astype('uint8')

    # Create a canvas for drawing contours
    contour_canvas = np.zeros_like(display_image_8bit)

    # Draw contours
    for i in range(len(contours)):
        if not labels[i]:
           continue
        cv2.drawContours(display_image_8bit, [contours[i]], -1, (0,255,0), 2)

    # Overlay contours on display image
    result_image = cv2.addWeighted(display_image_8bit, 1, contour_canvas, 0.5, 0)


    display_im(result_image)

root = ctk.CTk()
root.title('!Nara Image Analysis / !Nara Beeldanalise')
ctk.set_default_color_theme("green")

# Position window in center screen
w = 600 # width for the Tk root
h = 700 # height for the Tk root

# Get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# Calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2) - 40

# Set the dimensions of the screen and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

winWidth = root.winfo_screenwidth() # window width

# Create settings frame
settings = ctk.CTkFrame(root, height=65, width=winWidth, corner_radius=0, fg_color="dimgray")
settings.place(relx=0, rely=0, anchor=NW)

# Create frame to hold language options
languageFrame = ctk.CTkFrame(root, corner_radius=0, fg_color="dimgray")
languageFrame.place(relx=0.99, rely=0.01, anchor=NE)

# Switching languages
languages = ["English","Afrikaans"]
switchLang = ctk.CTkOptionMenu(master=languageFrame, values=languages)
switchLang.grid(row=0, column=0, padx=10)
button = ctk.CTkButton(languageFrame, text = "Confirm / Bevestig", command = changeLanguage).grid(row=0, column=1, padx=10, pady=10)

# Tabs
tabview = ctk.CTkTabview(root, width=5*w/6, height=5*h/6, fg_color="transparent", border_color="dimgray", border_width=2)
tabview.place(relx=0.5, rely=0.53, anchor=CENTER)

tabview.add("Display")  # Add display tab
display = tabview.tab("Display")
tabview.add("Advanced Settings")  # Add advanced settings tab
advSettings = tabview.tab("Advanced Settings")
tabview.set("Display")  # Set default tab

channel_classifiers = [[7,1,.29,100], [4,1,.12,.22]]
channel_classifier_vars = [(ctk.StringVar(),ctk.StringVar(),ctk.StringVar(),ctk.StringVar()), (ctk.StringVar(),ctk.StringVar(),ctk.StringVar(),ctk.StringVar())]

# Add labels to advanced settings options
ndrFrame = ctk.CTkFrame(master=advSettings)
ndrFrame.place(relx=0.05, rely=0.05, anchor=NW)
ndr = ctk.CTkLabel(master=ndrFrame, text="Normalized Difference Ratios (Channel)")
ndr.grid(row=0, column=0, padx=10)
for i in range(len(channel_classifiers)):
    b1,b2,lt,ut = channel_classifiers[i]
    vb1,vb2,vlt,vut = channel_classifier_vars[i]

    channels = ["(1) Coastal", "(2) Blue", "(3) Green", "(4) Yellow", "(5) Red", "(6) Red Edge", "(7) NIR1", "(8) NIR2"]
    
    ch1 = ctk.CTkOptionMenu(master=ndrFrame, values=channels, variable=vb1)
    vb1.set(channels[b1-1])
    ch1.grid(row=2*i+1, column=0, padx=10, pady=5)
    ch2 = ctk.CTkOptionMenu(master=ndrFrame, values=channels, variable=vb2)
    vb2.set(channels[b2-1])
    ch2.grid(row=2*i+1, column=1, padx=10, pady=5)
    lower_threshold = ctk.CTkEntry(master=ndrFrame, textvariable=vlt)
    vlt.set(str(lt))
    lower_threshold.grid(row=2*i+2, column=0, padx=10, pady=5)
    upper_threshold = ctk.CTkEntry(master=ndrFrame, textvariable=vut)
    vut.set(ut)
    upper_threshold.grid(row=2*i+2, column=1, padx=10, pady=5)

def set():
    global channel_classifiers
    global channel_classifier_vars
    for i in range(len(channel_classifiers)):
        channel_classifiers[i][0] = int(channel_classifier_vars[i][0].get()[1])
        channel_classifiers[i][1] = int(channel_classifier_vars[i][1].get()[1])
        channel_classifiers[i][2] = float(channel_classifier_vars[i][2].get())
        channel_classifiers[i][3] = float(channel_classifier_vars[i][3].get())

button = ctk.CTkButton(master=ndrFrame, text="Set", command=set)
button.grid(row=2*len(channel_classifiers)+1, column=0, padx=10, pady=10)

dune_classifiers = [[7,1,.29,100], [4,1,.12,.22]]
dune_classifier_vars = [(ctk.StringVar(),ctk.StringVar(),ctk.StringVar(),ctk.StringVar()), (ctk.StringVar(),ctk.StringVar(),ctk.StringVar(),ctk.StringVar())]

# Add labels to advanced settings options
ndrFrame = ctk.CTkFrame(master=advSettings)
ndrFrame.place(relx=0.05, rely=0.5, anchor=NW)
ndr = ctk.CTkLabel(master=ndrFrame, text="Normalized Difference Ratios (Outside Channel)")
ndr.grid(row=0, column=0, padx=10)
for i in range(len(dune_classifiers)):
    b1,b2,lt,ut = dune_classifiers[i]
    vb1,vb2,vlt,vut = dune_classifier_vars[i]

    channels = ["(1) Coastal", "(2) Blue", "(3) Green", "(4) Yellow", "(5) Red", "(6) Red Edge", "(7) NIR1", "(8) NIR2"]
    
    ch1 = ctk.CTkOptionMenu(master=ndrFrame, values=channels, variable=vb1)
    vb1.set(channels[b1-1])
    ch1.grid(row=2*i+1, column=0, padx=10, pady=5)
    ch2 = ctk.CTkOptionMenu(master=ndrFrame, values=channels, variable=vb2)
    vb2.set(channels[b2-1])
    ch2.grid(row=2*i+1, column=1, padx=10, pady=5)
    lower_threshold = ctk.CTkEntry(master=ndrFrame, textvariable=vlt)
    vlt.set(str(lt))
    lower_threshold.grid(row=2*i+2, column=0, padx=10, pady=5)
    upper_threshold = ctk.CTkEntry(master=ndrFrame, textvariable=vut)
    vut.set(ut)
    upper_threshold.grid(row=2*i+2, column=1, padx=10, pady=5)

def setdune():
    global dune_classifiers
    global dune_classifier_vars
    for i in range(len(channel_classifiers)):
        dune_classifiers[i][0] = int(dune_classifier_vars[i][0].get()[1])
        dune_classifiers[i][1] = int(dune_classifier_vars[i][1].get()[1])
        dune_classifiers[i][2] = float(dune_classifier_vars[i][2].get())
        dune_classifiers[i][3] = float(dune_classifier_vars[i][3].get())

button = ctk.CTkButton(master=ndrFrame, text="Set", command=setdune)
button.grid(row=2*len(dune_classifiers)+1, column=0, padx=10, pady=10)

# Other UI elements
welcomeText = ctk.CTkLabel(master=display, text="Upload an image using the button below. The image must have a .tif extension.")
uploadButton = ctk.CTkButton(master=display, text="Upload TIF file / Laai TIF-lêer op", command=openFile)
maskButton = ctk.CTkButton(master=display, text="Upload Channel Mask Shapefile", command=openMask)
startButton = ctk.CTkButton(master=display, text="Find !Nara", command=demo)
csvButton = ctk.CTkButton(master=display, text="Download !Nara Centroid Csv", command=csv)
shapeButton = ctk.CTkButton(master=display, text="Download !Nara Shapefile", command=shapefile)

# Create UI elements

# Put UI elements on the screen
welcomeText.place(relx=0.5, rely=0.05, anchor=CENTER)
uploadButton.place(relx=0.5, rely=0.12, anchor=CENTER)
maskButton.place(relx=0.5, rely=0.18, anchor=CENTER)
startButton.place(relx=0.5, rely=0.9, anchor=CENTER)
csvButton.place(relx=0.25, rely=0.96, anchor=CENTER)
shapeButton.place(relx=0.75, rely=0.96, anchor=CENTER)

def quitter():
    tkinter.Tk.quit(root)

root.protocol('WM_DELETE_WINDOW', quitter)
root.mainloop()


