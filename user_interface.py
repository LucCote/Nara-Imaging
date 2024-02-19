# ES90 !Nara Project
# User Interface

import tkinter
import tkinter as tk
from tkinter import *
from PIL import ImageTk,Image
from tkinter import ttk
from tkinter import filedialog

root = Tk()
root.title('Welcome')

def openFile():
    root.filename = filedialog.askopenfilename(initialdir="", title="Select a File", filetypes=(("tiff","*.tiff"),("All files","*.*")))
    file = Label(root, text=root.filename).grid(row=2, column=0)

def changeLanguage(): 
    label.config(text = clicked.get())

# Create UI elements
buttonText="Upload TIF File"
uploadButton = Button(root, text=buttonText, command=openFile)
welcomeText = Label(root, text="Upload an image using the button below. The image must be a multispectral image with a .tif extension.")



# Create combobox to choose language
clicked = StringVar()
languages = ["English","Afrikaans"]
drop = OptionMenu(root, clicked, *languages)
drop.grid(row=0, column=2, padx=30)
clicked.set("Select Language")
drop.config(width=12)
button = Button(root, text = "Confirm Choice", command = changeLanguage).grid(row=0, column=3) 
label = Label(root, text = " ")
label.grid(row=0,column=4) 

# Put UI elements on the screen
uploadButton.grid(row=1, column=0, padx=30, pady=30)
welcomeText.grid(row=0, column=0)

root.mainloop()
