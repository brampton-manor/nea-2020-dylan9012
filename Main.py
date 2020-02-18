from sys import path as syspath
from tkinter import *
import os

syspath.insert(0, os.getcwd() + "/Resources/Message")
import MsgEmbed
import MsgExtract

syspath.insert(0, os.getcwd() + "/Resources/Image")
import ImgEmbed
import ImgExtract


class MenuBar(Menu):
    def __init__(self, parent):
        Menu.__init__(self, parent)

        menuBar = Menu(self, tearoff=0)
        fileMenu = Menu(self, tearoff=0)
        subMenu = Menu(self, tearoff=0)
        embedSubMenu = Menu(self, tearoff=0)
        extractSubMenu = Menu(self, tearoff=0)

        embedSubMenu.add_command(label="Message", command=lambda: parent.ChooseMsgEmbed())
        embedSubMenu.add_command(label="Image", command=lambda: parent.ChooseImgEmbed())
        extractSubMenu.add_command(label="Message", command=lambda: parent.ChooseMsgExtract())
        extractSubMenu.add_command(label="Image", command=lambda: parent.ChooseImgExtract())
        self.add_cascade(label="Embed", menu=embedSubMenu)
        self.add_cascade(label="Extract", menu=extractSubMenu)


class RadioBar(Frame):
    def __init__(self, parent, text, index, width=15, height=2):
        Frame.__init__(self, parent)
        self.master = parent
        self.text = text
        self.index = index
        self.height = height
        self.width = width
        Radiobutton(self, text=self.text, variable=parent.radiovar, value=self.index, height=self.height,
                    width=self.width).pack()


class ButtonBar(Frame):
    def __init__(self, parent, text, width=15, height=2):
        Frame.__init__(self, parent)
        self.master = parent
        self.text = text
        self.height = height
        self.width = width
        Button(self, text=self.text, height=self.height, width=self.width,
               command=self.update).pack()

    def update(self):
        self.master.buttonvar.set(1)


class Interface(Tk):
    def __init__(self):
        Tk.__init__(self)
        Tk.title(self, "Main")
        Tk.geometry(self, "1000x500")

        menubar = MenuBar(self)
        self.config(menu=menubar)
        self.label()

    def label(self):
        self.var = StringVar()
        label = Label(justify=LEFT, relief=RIDGE, borderwidth=3, textvariable=self.var, width=300, height=5, anchor=NW)
        label.config(state=NORMAL, bg="black", fg="#42f545", font="ansifixed")
        label.pack(fill=BOTH, expand=1)
        self.Display("Please choose an option from the Toggle menu to continue...")

    def Display(self, event):
        self.var.set(self.var.get() + event + "\n")

    def ClearLabel(self):
        self.var.set("")

    def EntryInput(self, event):
        self.Display(event)
        textEntry = Entry()
        textEntry.pack(side=TOP, fill=X, padx=5, pady=5)
        catch = StringVar()

        def Callback(event):
            nonlocal catch
            catch.set(textEntry.get())

        textEntry.bind('<Return>', Callback)
        textEntry.wait_variable(catch)
        textEntry.destroy()
        self.ClearLabel()
        return catch.get()

    def RadioInput(self, event, text):
        self.Display(event)

        self.buttonvar = IntVar()
        self.radiovar = IntVar()
        self.radios = [RadioBar(self, i, text.index(i)) for i in text]

        confirm = ButtonBar(self, "Confirm")
        confirm.pack(side=RIGHT)

        for i in self.radios: i.pack(side=LEFT, expand=YES)

        Tk.update(self)
        confirm.wait_variable(self.buttonvar)

        for i in self.radios: i.destroy()
        confirm.destroy()

        return text[self.radiovar.get()]

    def ChooseMsgEmbed(self):
        MsgEmbed.main(self)

    def ChooseMsgExtract(self):
        MsgExtract.main(self)

    def ChooseImgEmbed(self):
        ImgEmbed.main(self)

    def ChooseImgExtract(self):
        ImgExtract.main(self)


if __name__ == "__main__": Interface().mainloop()
