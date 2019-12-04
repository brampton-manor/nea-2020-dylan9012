from tkinter import filedialog, messagebox
from PIL import Image as cImage
from sys import path as syspath
from datetime import date
from os import path
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
        5: "Invalid file format"
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
    location = path.dirname(os.getcwd()) + "/Input/Embed"
    # - Message & image file validation
    Main.Display("Fetching text file directory...", var)
    message = filedialog.askopenfilename(initialdir=location,
                                         title="Select text file",
                                         filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
    if ExitApplication(message):
        return Inputs(var)

    Main.Display("Fetching image file directory...", var)
    image = filedialog.askopenfilename(initialdir=location,
                                       title="Select image file",
                                       filetypes=(("bmp files", "*.bmp"), ("all files", "*.*")))

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
    return message, image, key


def Initialising(image, coverImage, textHandle, var):
    dimensions = coverImage.size
    pixels = coverImage.load()
    secretMsg = textHandle.read()
    resolution = os.stat(image).st_size * 8
    secretBits = len(secretMsg) * 7
    if secretBits > resolution:
        Main.Display(
            "The message binary values exceeds the resolution binary values, therefore will not work. Please try a "
            "shorter message or larger image.\n", var)
        main(var)
    return secretMsg, dimensions, pixels


def FileHandle(coverImage, var):
    Main.Display("Fetching image file directory...", var)
    savePath = filedialog.asksaveasfilename(initialdir=path.dirname(os.getcwd()) + "/Output/Embed",
                                            defaultextension="*.jpg",
                                            title="Save image file",
                                            filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))
    if ExitApplication(savePath):
        FileHandle(coverImage, var)
    return savePath


def Ordering(dimensions, key):
    shuffledIndicies = list(range(dimensions[0] * dimensions[1]))
    random.seed(key)
    random.shuffle(shuffledIndicies)
    return shuffledIndicies


def Conversion(secretMsg):
    sbits = "".join(format(ord(char), "b").zfill(7) for char in secretMsg)
    lbits = format(len(secretMsg), "b").zfill(14)
    bits = lbits + sbits
    return bits


def ModifyPixel(pixel, modifier, sigBit, plane):
    pixel = list(pixel)
    if plane == 0:
        planeList = list("".join((format(pixel[plane], "b")).zfill(8)))
        planeList[sigBit] = str(modifier)
        pixel[plane] = int("".join(planeList), 2)

    if plane == 1:
        planeList = list("".join((format(pixel[plane], "b")).zfill(8)))
        planeList[sigBit] = str(modifier)
        pixel[plane] = int("".join(planeList), 2)

    if plane == 2:
        planeList = list("".join((format(pixel[plane], "b")).zfill(8)))
        planeList[sigBit] = str(modifier)
        pixel[plane] = int("".join(planeList), 2)
    return pixel[0], pixel[1], pixel[2]


def Opening(message, image, var):
    try:
        coverImage = cImage.open(image)
        textHandle = open(message, 'r')
        return coverImage, textHandle
    except OSError:
        ErrorMessage(5, var)
        message, image, key = Inputs(var)
        return Opening(message, image, var)


def ExitApplication(file):
    if file == "":
        MsgBox = messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application',
                                        icon='warning')
        if MsgBox == 'yes':
            raise SystemExit
        else:
            messagebox.showinfo('Return', 'You will now return to the application screen')
            return True


def WaterMark(message, savePath):
    watermark = savePath[-3:].upper() + "/dylan/" + date.today().strftime("%Y-%m-%d")
    index = random.randint(0, len(message))
    return message[:index] + watermark + message[index:]


def main(var):
    # - Optional configurations
    sigBit, plane = Config(var)
    # - User inputs
    message, image, key = Inputs(var)
    # - Opening image and text
    coverImage, textHandle = Opening(message, image, var)
    # - Opening text
    message, dimensions, pixels = Initialising(image, coverImage, textHandle, var)
    savePath = FileHandle(coverImage, var)
    # - Seeding
    shuffledIndices = Ordering(dimensions, key)
    message = WaterMark(message, savePath)
    # - Binary conversion
    bits = Conversion(message)
    # - Modify pixels
    for i in range(len(bits)):
        x = shuffledIndices[i] % dimensions[0]
        y = int(shuffledIndices[i] / dimensions[0])

        p = pixels[x, y][plane]
        p = format(p, "b").zfill(8)

        # - Change if existing bit is 0, only if secret bit is 1
        if p[sigBit] == "0":
            if bits[i] == "1":
                pixels[x, y] = ModifyPixel(pixels[x, y], 1, sigBit, plane)
        # - Change if existing bit is 1, only if secret bit is 0
        else:
            if bits[i] == "0":
                pixels[x, y] = ModifyPixel(pixels[x, y], 0, sigBit, plane)

    # - File handling
    coverImage.save(savePath, 'BMP')
    Main.Display("\n", var)
    Main.Display("ALL DONE", var)
    Main.Display("\n", var)


if __name__ == "__main__":
    main(var)
