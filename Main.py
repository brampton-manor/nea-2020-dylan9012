from sys import path as syspath
from tkinter import *
import os

syspath.insert(0, os.getcwd() + "/Resources/Message")
import MsgEmbed
import MsgExtract

syspath.insert(0, os.getcwd() + "/Resources/Image")
import ImgEmbed
import ImgExtract

var = None
labelContents = ""


def UI(master):
    global var

    var = StringVar()

    master.title("Crypto-Stegonography Program")

    Image = PhotoImage(file=os.getcwd() + "/Resources/Background.gif")
    backgroundLabel = Label(master, image=Image)
    backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)
    backgroundLabel.image = Image

    label = Label(justify=LEFT, relief=RIDGE, borderwidth=3, textvariable=var, width=300, height=5, anchor=NW)
    label.config(state=NORMAL, bg="black", fg="#42f545", font="ansifixed")
    label.pack(fill=BOTH, expand=1)
    Display("Please choose an option from the Toggle menu to continue...\n", var)

    closeButton = Button(text="Close", height=1, width=10, command=master.destroy)
    closeButton.pack(side=RIGHT, padx=5, pady=5)

    menuBar = Menu(master)
    master.config(menu=menuBar)
    fileMenu = Menu(menuBar)
    subMenu = Menu(fileMenu)
    embedSubMenu = Menu(subMenu)
    extractSubMenu = Menu(subMenu)

    embedSubMenu.add_command(label="Message", command=ChooseMsgEmbed)
    embedSubMenu.add_command(label="Image", command=ChooseImgEmbed)
    extractSubMenu.add_command(label="Message", command=ChooseMsgExtract)
    extractSubMenu.add_command(label="Image", command=ChooseImgExtract)
    subMenu.add_cascade(label="Embed", menu=embedSubMenu)
    subMenu.add_cascade(label="Extract", menu=extractSubMenu)
    fileMenu.add_cascade(label="Tools", menu=subMenu, underline=0)
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit", underline=0, command=master.destroy)
    menuBar.add_cascade(label="Toggle", underline=0, menu=fileMenu)


def Display(event, var):
    global labelContents
    labelContents += event
    labelContents += "\n"
    var.set(labelContents)


def ClearLabel(var):
    global labelContents
    labelContents = ""
    var.set(labelContents)


def TkinterInput(event, var):
    Display(event, var)
    textEntry = Entry()
    textEntry.pack(side=TOP, fill=X, padx=5, pady=5)
    catch = StringVar()

    def Callback(event):
        nonlocal catch
        catch.set(textEntry.get())

    textEntry.bind('<Return>', Callback)
    textEntry.wait_variable(catch)
    textEntry.destroy()
    ClearLabel(var)
    return catch.get()


def ChooseMsgEmbed():
    global var
    global labelContents
    ClearLabel(var)
    MsgEmbed.main(var)


def ChooseMsgExtract():
    global var
    global labelContents
    ClearLabel(var)
    MsgExtract.main(var)


def ChooseImgEmbed():
    global var
    global labelContents
    ClearLabel(var)
    ImgEmbed.main(var)


def ChooseImgExtract():
    global var
    global labelContents
    ClearLabel(var)
    ImgExtract.main(var)



if __name__ == "__main__":
    root = Tk()
    root.geometry("700x400")
    root.resizable(0, 0)
    UI(root)
    root.mainloop()
