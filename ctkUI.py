import tkinter
from tkinter import NW, NE, CENTER
import customtkinter as ctk
import rasterio
import numpy as np
from segment import segment_contours
from analyze import classify_segment
import matplotlib.pyplot as plt
import cv2
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import fiona
from shapely.geometry import shape, Polygon
from metrics import load_coords, transform_shape
from output import write_csv, write_shape

fig = None
ax = None
im = None
canvas = None
src = None
filename = None
masks = None
contours = None
dunes = False

# load an image into the display canvas
def display_im(image):
    # Generate the figure and plot object which will be linked to the display element
    global fig
    global ax
    global canvas
    global im
    global dunes
    fig, ax = plt.subplots()
    fig.set_size_inches(3,3)
    im = ax.imshow(image)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    canvas = FigureCanvasTkAgg(fig,master=tabview.tab("Display"))
    canvas.draw()
    canvas.get_tk_widget().place(relx=0.5, rely=0.56, anchor=CENTER)

# asks user to open image and then and displays it
def openImageFile():
    global src
    global filename
    global masks
    masks = None # reset channel masks as we now have a new image
    filename = ctk.filedialog.askopenfilename(initialdir="", title="Select a File / Kies 'n lêer", filetypes=(("tiff","*.tiff, *.tif"),("All files","*.*")))
    if filename is None or len(filename) == 0:
        return
    src = rasterio.open(filename)
    display_channels=[5,4,2]
    display_bands = src.read(display_channels)
    normalized_display_bands = [(band - np.min(band)) / (np.max(band) - np.min(band)) for band in display_bands]
    display_image = np.dstack(normalized_display_bands)
    display_image_8bit = (display_image * 255).astype('uint8')
    display_im(display_image_8bit)

# asks user to open channel mask shapefile and stores it
def openMask():
    global masks
    filename = ctk.filedialog.askopenfilename(initialdir="", title="Select a File / Kies 'n lêer", filetypes=(("shape","*.shp"),("All files","*.*")))
    if filename is None or len(filename) == 0:
        return
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
        for labelut in label_uts:
            labelut.configure(text = "Boonste Drempel")
        for labellt in label_lts:
            labellt.configure(text = "Laer Drempel")
        for labelch1 in label_ch1:
            labelch1.configure(text = "Primêre Kanaal")
        for labelch2 in label_ch2:
            labelch2.configure(text = "Verskil Kanaal")
        ndr.configure(text = "Genormaliseerde Verskilverhoudings (Kanaal)")
        ndrout.configure(text = "Genormaliseerde Verskilverhoudings (Buite Kanaal)")
        upload_text.set("Laai TIF-lêer Op")
        mask_text.set("Laai Kanaalmaskervormlêer Op")
        start_text.set("Vind !Nara")
        csv_text.set("Laai !Nara Sentroïed CSV Af")
        shape_text.set("Aflaai !Nara Vormlêer")
        dunes_text.set("Buitekanaalanalise (beta)")
        set_text.set("Bevestig")
        set2_text.set("Bevestig")
        tabview._segmented_button._buttons_dict["Display"].configure(state=ctk.NORMAL, text="Vertoon")
        tabview._segmented_button._buttons_dict["Advanced Settings"].configure(state=ctk.NORMAL, text="Gevorderde Instellings")

    elif switchLang.get() == "English":
        welcomeText.configure(text = "Upload an image using the button below. The image must have a .tif extension.")
        for labelut in label_uts:
            labelut.configure(text = "Upper Threshold")
        for labellt in label_lts:
            labellt.configure(text = "Lower Threshold")
        for labelch1 in label_ch1:
            labelch1.configure(text = "Primary Channel")
        for labelch2 in label_ch2:
            labelch2.configure(text = "Difference Channel")
        ndr.configure(text = "Normalized Difference Ratios (Channel)")
        ndrout.configure(text = "Normalized Difference Ratios (Outside Channel)")
        upload_text.set("Upload TIF File")
        mask_text.set("Upload Channel Mask Shapefile")
        start_text.set("Find !Nara")
        csv_text.set("Download !Nara Centroid CSV")
        shape_text.set("Download !Nara Shapefile")
        dunes_text.set("Outside Channel Analysis (beta)")
        set_text.set("Set")
        set2_text.set("Bevestig")
        tabview._segmented_button._buttons_dict["Vertoon"].configure(state=ctk.NORMAL, text="Display")
        tabview._segmented_button._buttons_dict["Gevorderde Instellings"].configure(state=ctk.NORMAL, text="Advanced Settings")

def csv():
    global contours
    global labels
    global src
    if contours == None:
        return
    f = ctk.filedialog.asksaveasfilename(initialdir="", filetypes=(("csv","*.csv"),("All files","*.*")))
    if f is None or len(f) == 0: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    write_csv(f,contours, labels, src)

def shapefile():
    global contours
    global labels
    global src
    if contours == None:
        return
    f = ctk.filedialog.asksaveasfilename(initialdir="", filetypes=(("shape","*.shp"),("All files","*.*")))
    if f is None or len(f) == 0: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    write_shape(f,contours, labels, src)

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
    progressbar = ctk.CTkProgressBar(master=root)
    progressbar.set(0)
    progressbar.place(relx=0.5, rely=0.5, anchor=CENTER)
    root.update_idletasks()
    contours = segment_contours(filename,5)
    progressbar.set(0.1)
    root.update_idletasks()
    lats,longs = load_coords(src)

    labels = np.zeros(len(contours))
    for i in range(len(contours)):
        progressbar.set(0.1+0.9*(float(i)/len(contours)))
        root.update_idletasks()
        if masks != None:
            coords_shape = Polygon(transform_shape(np.squeeze(contours[i]), lats, longs))
            found = False
            for mask in masks:
                if coords_shape.intersects(mask):
                    found = True
                break
            if found:
                labels[i] = classify_segment(contours[i],src, channel_classifiers)
            elif dunes:
                labels[i] = classify_segment(contours[i],src, dune_classifiers)
        else:
            labels[i] = classify_segment(contours[i],src, channel_classifiers)

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
    progressbar.destroy()

    display_im(result_image)

root = ctk.CTk()
root.title("!Nara Image Analysis / !Nara Beeldanalise")
ctk.set_default_color_theme("dark-blue")

# Position window in center screen
w = 1000 # width for the Tk root
h = 800 # height for the Tk root

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

label_uts = []
label_lts = []
label_ch1 = []
label_ch2 = []

# Add labels to advanced settings options
ndrFrame = ctk.CTkFrame(master=advSettings)
ndrFrame.place(relx=0.5, rely=0.25, anchor=CENTER)
ndr = ctk.CTkLabel(master=ndrFrame, text="Normalized Difference Ratios (Channel)")
ndr.grid(row=0, column=0, padx=10)
for i in range(len(channel_classifiers)):
    frameclassifier = ctk.CTkFrame(master=ndrFrame)
    frameclassifier.grid(row=i+1, column=0, padx=0, pady=5)

    b1,b2,lt,ut = channel_classifiers[i]
    vb1,vb2,vlt,vut = channel_classifier_vars[i]

    framech1 = ctk.CTkFrame(master=frameclassifier)
    framech1.grid(row=0, column=0, padx=10, pady=3)
    channels = ["(1) Coastal", "(2) Blue", "(3) Green", "(4) Yellow", "(5) Red", "(6) Red Edge", "(7) NIR1", "(8) NIR2"]
    labelch1 = ctk.CTkLabel(master=framech1, text="Primary Channel")
    ch1 = ctk.CTkOptionMenu(master=framech1, values=channels, variable=vb1)
    label_ch1.append(labelch1)
    vb1.set(channels[b1-1])
    labelch1.grid(row=0, column=0, padx=10, pady=3)
    ch1.grid(row=0, column=1, padx=10, pady=5)

    framech2 = ctk.CTkFrame(master=frameclassifier)
    framech2.grid(row=0, column=1, padx=10, pady=3)
    labelch2 = ctk.CTkLabel(master=framech2, text="Difference Channel")
    labelch2.grid(row=0, column=0, padx=10, pady=3)
    label_ch2.append(labelch2)
    ch2 = ctk.CTkOptionMenu(master=framech2, values=channels, variable=vb2)
    vb2.set(channels[b2-1])
    ch2.grid(row=0, column=1, padx=10, pady=5)

    framellt = ctk.CTkFrame(master=frameclassifier)
    framellt.grid(row=1, column=0, padx=10, pady=3)
    labellt = ctk.CTkLabel(master=framellt, text="Lower Threshold")
    labellt.grid(row=0, column=0, padx=10, pady=3)
    label_lts.append(labellt)
    lower_threshold = ctk.CTkEntry(master=framellt, textvariable=vlt)
    vlt.set(str(lt))
    lower_threshold.grid(row=0, column=1, padx=10, pady=3)
    
    frameut = ctk.CTkFrame(master=frameclassifier)
    frameut.grid(row=1, column=1, padx=10, pady=3)
    labelut = ctk.CTkLabel(master=frameut, text="Upper Threshold")
    labelut.grid(row=0, column=0, padx=10, pady=3)
    label_uts.append(labelut)
    upper_threshold = ctk.CTkEntry(master=frameut, textvariable=vut)
    vut.set(ut)
    upper_threshold.grid(row=0, column=1, padx=10, pady=3)

def set():
    global channel_classifiers
    global channel_classifier_vars
    for i in range(len(channel_classifiers)):
        channel_classifiers[i][0] = int(channel_classifier_vars[i][0].get()[1])
        channel_classifiers[i][1] = int(channel_classifier_vars[i][1].get()[1])
        channel_classifiers[i][2] = float(channel_classifier_vars[i][2].get())
        channel_classifiers[i][3] = float(channel_classifier_vars[i][3].get())

set_text = ctk.StringVar()
button = ctk.CTkButton(master=ndrFrame, textvariable=set_text, command=set)
set_text.set("Set")
button.grid(row=2*len(channel_classifiers)+1, column=0, padx=10, pady=10)

dune_classifiers = [[7,1,.29,100], [4,1,.12,.22]]
dune_classifier_vars = [(ctk.StringVar(),ctk.StringVar(),ctk.StringVar(),ctk.StringVar()), (ctk.StringVar(),ctk.StringVar(),ctk.StringVar(),ctk.StringVar())]

# Add labels to advanced settings options
ndrFrame = ctk.CTkFrame(master=advSettings)
ndrFrame.place(relx=0.5, rely=0.75, anchor=CENTER)
ndrout = ctk.CTkLabel(master=ndrFrame, text="Normalized Difference Ratios (Outside Channel)")
ndrout.grid(row=0, column=0, padx=10)
for i in range(len(dune_classifiers)):
    frameclassifier = ctk.CTkFrame(master=ndrFrame)
    frameclassifier.grid(row=i+1, column=0, padx=0, pady=5)

    b1,b2,lt,ut = dune_classifiers[i]
    vb1,vb2,vlt,vut = dune_classifier_vars[i]

    framech1 = ctk.CTkFrame(master=frameclassifier)
    framech1.grid(row=0, column=0, padx=10, pady=3)
    channels = ["(1) Coastal", "(2) Blue", "(3) Green", "(4) Yellow", "(5) Red", "(6) Red Edge", "(7) NIR1", "(8) NIR2"]
    labelch1 = ctk.CTkLabel(master=framech1, text="Primary Channel")
    ch1 = ctk.CTkOptionMenu(master=framech1, values=channels, variable=vb1)
    label_ch1.append(labelch1)
    vb1.set(channels[b1-1])
    labelch1.grid(row=0, column=0, padx=10, pady=3)
    ch1.grid(row=0, column=1, padx=10, pady=3)

    framech2 = ctk.CTkFrame(master=frameclassifier)
    framech2.grid(row=0, column=1, padx=10, pady=3)
    labelch2 = ctk.CTkLabel(master=framech2, text="Difference Channel")
    labelch2.grid(row=0, column=0, padx=10, pady=3)
    ch2 = ctk.CTkOptionMenu(master=framech2, values=channels, variable=vb2)
    label_ch2.append(labelch2)
    vb2.set(channels[b2-1])
    ch2.grid(row=0, column=1, padx=10, pady=3)

    framellt = ctk.CTkFrame(master=frameclassifier)
    framellt.grid(row=1, column=0, padx=10, pady=3)
    labellt = ctk.CTkLabel(master=framellt, text="Lower Threshold")
    label_lts.append(labellt)
    labellt.grid(row=0, column=0, padx=10, pady=3)
    lower_threshold = ctk.CTkEntry(master=framellt, textvariable=vlt)
    vlt.set(str(lt))
    lower_threshold.grid(row=0, column=1, padx=10, pady=3)

    frameut = ctk.CTkFrame(master=frameclassifier)
    frameut.grid(row=1, column=1, padx=10, pady=3)
    labelut = ctk.CTkLabel(master=frameut, text="Upper Threshold")
    labelut.grid(row=0, column=0, padx=10, pady=3)
    label_uts.append(labelut)
    upper_threshold = ctk.CTkEntry(master=frameut, textvariable=vut)
    vut.set(ut)
    upper_threshold.grid(row=0, column=1, padx=10, pady=3)

def setdune():
    global dune_classifiers
    global dune_classifier_vars
    for i in range(len(channel_classifiers)):
        dune_classifiers[i][0] = int(dune_classifier_vars[i][0].get()[1])
        dune_classifiers[i][1] = int(dune_classifier_vars[i][1].get()[1])
        dune_classifiers[i][2] = float(dune_classifier_vars[i][2].get())
        dune_classifiers[i][3] = float(dune_classifier_vars[i][3].get())

def toggle_dune():
    global dunes
    dunes = not dunes

set2_text = ctk.StringVar()
button = ctk.CTkButton(master=ndrFrame, textvariable=set2_text, command=setdune)
set2_text.set("Set")
button.grid(row=2*len(dune_classifiers)+1, column=0, padx=10, pady=10)

# Other UI elements
welcomeText = ctk.CTkLabel(master=display, text="Upload an image using the button below. The image must have a .tif extension.")

upload_text = ctk.StringVar()
uploadButton = ctk.CTkButton(master=display, textvariable=upload_text, command=openImageFile)
upload_text.set("Upload TIF File")

mask_text = ctk.StringVar()
maskButton = ctk.CTkButton(master=display, textvariable=mask_text, command=openMask)
mask_text.set("Upload Channel Mask Shapefile")

start_text = ctk.StringVar()
startButton = ctk.CTkButton(master=display, textvariable=start_text, command=demo)
start_text.set("Find !Nara")

csv_text = ctk.StringVar()
csvButton = ctk.CTkButton(master=display, textvariable=csv_text, command=csv)
csv_text.set("Download !Nara Centroid CSV")

shape_text = ctk.StringVar()
shapeButton = ctk.CTkButton(master=display, textvariable=shape_text, command=shapefile)
shape_text.set("Download !Nara Shapefile")

dunes_text = ctk.StringVar()
dunesButton = ctk.CTkCheckBox(master=display, textvariable=dunes_text, command=toggle_dune, onvalue="on", offvalue="off")
dunes_text.set("Outside Channel Analysis (beta)")

# Put UI elements on the screen
welcomeText.place(relx=0.5, rely=0.05, anchor=CENTER)
uploadButton.place(relx=0.5, rely=0.12, anchor=CENTER)
maskButton.place(relx=0.5, rely=0.18, anchor=CENTER)
startButton.place(relx=0.35, rely=0.9, anchor=CENTER)
dunesButton.place(relx=0.65, rely=0.9, anchor=CENTER)
csvButton.place(relx=0.35, rely=0.96, anchor=CENTER)
shapeButton.place(relx=0.65, rely=0.96, anchor=CENTER)

def quitter():
    tkinter.Tk.quit(root)

root.protocol('WM_DELETE_WINDOW', quitter)
root.mainloop()
