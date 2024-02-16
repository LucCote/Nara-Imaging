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

fig = None
ax = None

def openFile():
    root.filename = filedialog.askopenfilename(initialdir="", title="Select a File / Kies 'n lêer", filetypes=(("tiff","*.tiff"),("All files","*.*")))
    demo(root.filename)

def changeLanguage():
    if switchLang.get() == "Afrikaans":
        welcomeText.configure(text = "Laai 'n prent op met die knoppie hieronder. Die prent moet 'n .tif-uitbreiding hê.")
    elif switchLang.get() == "English":
        welcomeText.configure(text = "Upload an image using the button below. The image must have a .tif extension.")

def demo(filename):
    def display_image(src, contours, labels, display_channels=[5,4,2]):
        # Read and normalize display bands
        display_bands = src.read(display_channels)
        normalized_display_bands = [(band - np.min(band)) / (np.max(band) - np.min(band)) for band in display_bands]
        display_image = np.dstack(normalized_display_bands)
        display_image_8bit = (display_image * 255).astype('uint8')

        # Create a canvas for drawing contours
        contour_canvas = np.zeros_like(display_image_8bit)

        # Draw contours
        colors = {0: (0,255,0), 1: (255,0,0), 2:(255,0,255), 3:(0,0,255)}  # Define colors for each class
        for i in range(len(contours)):
            cv2.drawContours(display_image_8bit, [contours[i]], -1, colors[labels[i]], 2)

        # Overlay contours on display image
        result_image = cv2.addWeighted(display_image_8bit, 1, contour_canvas, 0.5, 0)

        # Display result
        ax.imshow(result_image)
        ax.title("Result with Contours")
        ax.axis('off')
        ax.show()

    src = rasterio.open(filename)
    contours = segment_contours(filename,8)

    print(contours)
    labels = np.zeros(len(contours))
    for i in range(len(contours)):
        labels[i] = classify_segment(contours[i],src)
    print(labels)
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

    true_pos, false_pos, true_neg, false_neg, metric_labels = get_metrics(src,contours,labels,"test_sheet.csv")
    display_image(src,contours,metric_labels)
    print(true_pos, false_pos, true_neg, false_neg)

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

# Add labels to advanced settings options
ndrFrame = ctk.CTkFrame(master=advSettings)
ndrFrame.place(relx=0.05, rely=0.05, anchor=NW)
ndr = ctk.CTkLabel(master=ndrFrame, text="Normalized Difference Ratio")
ndr.grid(row=0, column=0, padx=10)

channels = ["(1) Coastal", "(2) Blue", "(3) Green", "(4) Yellow", "(5) Red", "(6) Red Edge", "(7) NIR1", "(8) NIR2"]
ch1 = ctk.CTkOptionMenu(master=ndrFrame, values=channels)
ch1.grid(row=1, column=0, padx=10, pady=10)
ch2 = ctk.CTkOptionMenu(master=ndrFrame, values=channels)
ch2.grid(row=1, column=1, padx=10, pady=10)

# Other UI elements
welcomeText = ctk.CTkLabel(master=display, text="Upload an image using the button below. The image must have a .tif extension.")
uploadButton = ctk.CTkButton(master=display, text="Upload TIF file / Laai TIF-lêer op", command=openFile)

# Displaying images
def updateDisplay():
    # Generate the figure and plot object which will be linked to the root element
    global fig
    global ax
    fig, ax = plt.subplots()
    fig.set_size_inches(2,2)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    canvas = FigureCanvasTkAgg(fig,master=tabview.tab("Display"))
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.5, rely=0.56, anchor=CENTER)

# Create UI elements

# Put UI elements on the screen
welcomeText.place(relx=0.5, rely=0.05, anchor=CENTER)
uploadButton.place(relx=0.5, rely=0.12, anchor=CENTER)
updateDisplay()

root.mainloop()


