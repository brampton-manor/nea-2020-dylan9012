from tkinter import filedialog, messagebox
from sys import path as syspath
from PIL import Image as cImage
from datetime import datetime
from os import path
import random
import string
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
                                       filetypes=(("bmp files", "*bmp"), ("all files", "*.*")))
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


def FileHandle(secretMsg, var):
    Main.Display("Fetching text file directory...", var)
    message = filedialog.asksaveasfilename(initialdir=path.dirname(os.getcwd()) + "/Output/Extract",
                                           title="Save text file to directory",
                                           defaultextension="*.txt",
                                           filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
    if ExitApplication(message):
        FileHandle(message, var)

    file = open(message, "w+")
    file.write(secretMsg)
    file.close()


def TextTransformation(secretMsg, key):
    ASCII = string.printable
    random.seed(key)
    shuffledASCII = ''.join(random.sample(ASCII, len(ASCII)))
    table = str.maketrans(shuffledASCII, ASCII)
    return secretMsg.translate(table)


def Ordering(dimensions, key):
    shuffledIndices = list(range(0, dimensions[0] * dimensions[1]))
    random.seed(key)
    random.shuffle(shuffledIndices)
    return shuffledIndices


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


def WaterMark(secretMsg, i, fileType, var):
    index = secretMsg.find('/dylan/', i)
    if index == -1:
        ErrorMessage(5, var)
        return "Error"
    try:
        datetime.strptime(secretMsg[index + 7:index + 17], '%Y-%m-%d')
    except ValueError:
        return "Error"

    if secretMsg[index - 3:index] == fileType:
        return secretMsg.replace(secretMsg[index - 3:index + 17], '')
    else:
        return WaterMark(secretMsg, index, fileType, var)


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
    shuffledIndicies = Ordering(dimensions, key)
    # - Extraction
    extractedBits = []
    for i in shuffledIndicies:
        x = i % dimensions[0]
        y = int(i / dimensions[0])
        p = format(pixels[x, y][plane], 'b').zfill(8)
        extractedBits.append(p[sigBit])

    MsgLength = int(''.join(extractedBits[:14]), 2)
    extractedMsg = extractedBits[14:14 + MsgLength * 7]

    secretMsg = ""
    word = []
    counter = 0
    for i in extractedMsg:
        counter += 1
        word.append(i)
        if counter == 7:
            secretMsg += chr(int(''.join(word), 2))
            counter = 0
            word.clear()

    secretMsg = WaterMark(secretMsg, 0, fileType, var)

    if secretMsg == "Error":
        ErrorMessage(5, var)
    else:
        # - File handling
        FileHandle(secretMsg, var)
        Main.Display("\n", var)
        Main.Display("ALL DONE", var)
        Main.Display("\n", var)


if __name__ == "__main__":
    main(var)
