from tkinter import filedialog, messagebox
from sys import path as syspath
from PIL import Image as cImage
from datetime import datetime
from os import path
import numpy as np
import random
import os

syspath.insert(0, path.dirname(path.dirname(os.getcwd())))

import Main


def ErrorMessage(errorCase, var):
    switch = {
        1: "Invalid choice",
        2: "Invalid inputs",
        3: "Please choose file",
        4: "Input not numerical",
        5: "Cover image not compatible with extractor. Please try a different image"
    }
    Main.Display("Error {case}: {number}".format(case=errorCase, number=switch.get(errorCase)), var)
    Main.Display("\n", var)
    Main.Display("----------------------------------------------------------------------------------------------------",
                 var)
    Main.Display("\n", var)


def Config(var):
    choice = Main.TkinterInput("Customised embedding?: ", var)
    try:
        if choice == 'y' or choice == 'Y' or choice == "yes" or choice == "Yes":
            sigBit = int(Main.TkinterInput("Enter significant bit: ", var))
            plane = int(Main.TkinterInput("Enter Colour Plane (R:0,G:1,B:2): ", var))
        else:
            sigBit = 7
            plane = 0
    except:
        ErrorMessage(4, var)
        return Config(var)
    return sigBit, plane


def Inputs(var):
    location = path.dirname(os.getcwd()) + "/Input/Extract"
    # - Image file validation
    Main.Display("Fetching image file directory...", var)
    image = filedialog.askopenfilename(initialdir=location,
                                       title="Select image file",
                                       filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))
    if ExitApplication(image):
        return Inputs(var)

    # - Integer validation on key
    try:
        Main.Display("\n", var)
        key = Main.TkinterInput("Please enter numerical key (or 'stock'): ", var)
        key = 21 if key == "stock" else key
        key = int(key)
    except ValueError:
        ErrorMessage(4, var)
        return Inputs(var)
    return image, key, image[-3:].upper()


def Initialising(coverImage):
    dimensions = coverImage.size
    pixels = coverImage.load()
    return dimensions, pixels


def FileHandle(imageBits, var):
    Main.Display("Fetching image file directory...", var)
    image = filedialog.asksaveasfilename(initialdir=path.dirname(os.getcwd()) + "/Output/Extract",
                                         title="Save image to directory",
                                         defaultextension="*.jpg",
                                         filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))
    if ExitApplication(image):
        FileHandle(image, var)

    imageBits = list((map(int, list(imageBits))))
    bits = np.array(list(imageBits))
    bytes = np.packbits(bits)
    bytes.tofile(image)


def Ordering(dimensions, key):
    shuffledIndicies = list(range(0, dimensions[0] * dimensions[1]))
    random.seed(key)
    random.shuffle(shuffledIndicies)
    return shuffledIndicies


def Opening(image, var):
    try:
        coverImage = cImage.open(image)
        return coverImage
    except OSError:
        ErrorMessage(5, var)
        image, key = Inputs(var)
        return Opening(image, var)


def ExitApplication(file):
    if file == "":
        MsgBox = messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application',
                                        icon='warning')
        if MsgBox == 'yes':
            raise SystemExit
        else:
            messagebox.showinfo('Return', 'You will now return to the application screen')
            return True


def WaterMark(imageBits, i, fileType, var):
    string = "/dylan/"
    string = ''.join(format(ord(i), 'b').zfill(8) for i in string)

    index = str(imageBits).find(string, i)
    if index == -1:
        ErrorMessage(5, var)
        return "Error"

    # date validation
    date = imageBits[index + 7 * 8:index + 17 * 8]
    try:
        datetime.strptime(''.join(chr(int(date[i:i + 8], 2)) for i in range(0, len(date), 8)), '%Y-%m-%d')  # converts 8
        # bit binary to text
    except ValueError:
        return "Error"

    # file-type validation
    type = imageBits[index - 3 * 8:index]
    if ''.join(chr(int(type[i:i + 8], 2)) for i in range(0, len(type), 8)) == fileType:
        return imageBits.replace(imageBits[index - 3 * 8:index + 17 * 8], '')
    else:
        return WaterMark(imageBits, index, fileType, var)


def main(var):
    # - Optional configurations
    sigBit, plane = Config(var)
    # - User inputs
    image, key, fileType = Inputs(var)
    # - Opening image
    coverImage = Opening(image, var)
    # - Extracting image information
    dimensions, pixels = Initialising(coverImage)
    # - Pixel embedding order
    shuffledIndices = Ordering(dimensions, key)
    # - Extraction
    extractedBits = []
    for i in shuffledIndices:
        x = i % dimensions[0]
        y = int(i / dimensions[0])
        p = format(pixels[x, y][plane], "b").zfill(8)
        extractedBits.append(p[sigBit])
    ImgLength = int(''.join(extractedBits[:100]), 2)
    extractedBits = ''.join(extractedBits[100:100 + ImgLength])

    imageBits = WaterMark(extractedBits, 0, fileType, var)

    # - Check for watermark
    if imageBits == "Error":
        ErrorMessage(5, var)
    else:
        # - File handling
        FileHandle(imageBits, var)
        Main.Display("\n", var)
        Main.Display("ALL DONE", var)
        Main.Display("\n", var)


if __name__ == "__main__":
    main(var)
