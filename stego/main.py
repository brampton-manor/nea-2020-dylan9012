import os
import tkinter as tk
from tkinter import messagebox, filedialog

import img_embed
import img_extract
import msg_embed
import msg_extract


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.master = parent

        self.embed_menu = tk.Menu(self, tearoff=0)
        self.extract_menu = tk.Menu(self, tearoff=0)
        self.exit = None

        self.embed_menu.add_command(label="Message", command=lambda: parent.msg_embed())
        self.extract_menu.add_command(label="Message", command=lambda: parent.msg_extract())
        self.embed_menu.add_command(label="Image", command=lambda: parent.img_embed())
        self.extract_menu.add_command(label="Image", command=lambda: parent.img_extract())
        self.add_cascade(label="Embed", menu=self.embed_menu)
        self.add_cascade(label="Extract", menu=self.extract_menu)

    def disable(self):
        for i in range(2):
            self.embed_menu.entryconfigure(i, state=tk.DISABLED)
            self.extract_menu.entryconfigure(i, state=tk.DISABLED)

    def enable(self):
        for i in range(2):
            self.embed_menu.entryconfigure(i, state=tk.NORMAL)
            self.extract_menu.entryconfigure(i, state=tk.NORMAL)


class RadioBar(tk.Frame):
    def __init__(self, parent, text, index, width=15, height=2):
        tk.Frame.__init__(self, parent)
        self.text = text
        self.index = index
        self.height = height
        self.width = width
        tk.Radiobutton(self, text=self.text, variable=parent.radio_var, value=self.index, height=self.height,
                       width=self.width).pack()


class ButtonBar(tk.Frame):
    def __init__(self, parent, text, width=15, height=2):
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.text = text
        self.height = height
        self.width = width
        tk.Button(self, text=self.text, height=self.height, width=self.width,
                  command=self.trigger).pack()

    def trigger(self):
        self.master.button_var.set(1)


class Interface(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.protocol(self, "WM_DELETE_WINDOW", self.on_exit)
        tk.Tk.title(self, "Main")
        tk.Tk.geometry(self, "775x450")

        self.screen_var = None
        self.button_var = None
        self.radio_var = None
        self.radios = None
        # Setters for widget creations

        self.label()
        self.menubar = MenuBar(self)
        self.config(menu=self.menubar)

    def on_exit(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            tk.Tk.destroy(self)

    def label(self):
        self.screen_var = tk.StringVar()
        label = tk.Label(justify=tk.LEFT, relief=tk.RIDGE, borderwidth=3, textvariable=self.screen_var, width=300,
                         height=5,
                         anchor=tk.NW)
        label.config(state=tk.NORMAL, bg="black", fg="#42f545", font="ansifixed")
        label.pack(fill=tk.BOTH, expand=1)
        self.display("Please choose an option from the Toggle menu to continue...")

    def display(self, *argv):
        for i in argv:
            self.screen_var.set(self.screen_var.get() + i)
        self.screen_var.set(self.screen_var.get() + "\n")
        tk.Tk.update(self)

    def clear_label(self):
        self.screen_var.set("")
        tk.Tk.update(self)

    def entry_input(self, string):
        self.display(string)
        text_entry = tk.Entry()
        text_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        catch = tk.StringVar()

        def callback(event):
            nonlocal catch
            catch.set(text_entry.get())

        text_entry.bind('<Return>', callback)
        text_entry.wait_variable(catch)
        text_entry.destroy()
        self.clear_label()
        return catch.get()

    def radio_input(self, string, text):
        self.display(string)

        self.button_var = tk.IntVar()
        self.radio_var = tk.IntVar()
        self.radios = [RadioBar(self, i, text.index(i)) for i in text]

        confirm = ButtonBar(self, "Confirm")
        confirm.pack(side=tk.RIGHT)

        for i in self.radios:
            i.pack(side=tk.LEFT, expand=tk.YES)

        tk.Tk.update(self)
        confirm.wait_variable(self.button_var)

        for i in self.radios:
            i.destroy()
        confirm.destroy()

        return text[self.radio_var.get()]

    def settings(self):
        choice = self.radio_input("Customised embedding?", ["Yes", "No"])
        if choice == "Yes":
            while True:
                try:
                    key = int(self.entry_input("Please enter numerical key"))
                    break
                except ValueError:
                    self.display("Error: Input not numerical", "\n")
            sig_bit = int(self.entry_input("Enter significant bit (0 - for low quality to 7 - for high quality)"))
            plane = int(["Red", "Blue", "Green"].index(
                self.radio_input("Enter Colour Plane", ["Red", "Blue", "Green"])))
        else:
            sig_bit = 7
            plane = 0
            key = 0
        return sig_bit, plane, key

    @staticmethod
    def exit_application(file):
        if file == "":
            msg_box = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application',
                                                icon='warning')
            if msg_box == 'yes':
                raise SystemExit
            else:
                tk.messagebox.showinfo('Return', 'You will now return to the application screen')
                return True

    def file_handle(self):
        save_path = tk.filedialog.asksaveasfilename(parent=self, title="Save image to directory",
                                                    filetypes=(("gif files", "*.gif"), ("png files", "*.png"),
                                                               ("tiff files", "*.tif"), ("jpeg files", "*.jpg"),
                                                               ("bitmap files", "*bmp"), ("all files", "*.*")))
        if self.exit_application(save_path):
            self.file_handle()
        return save_path

    def msg_embed(self):
        self.clear_label()
        self.menubar.disable()
        files = []
        sig_bit, plane, key = self.settings()
        while True:
            message_path = tk.filedialog.askopenfilename(parent=self, title="Select text file",
                                                         filetypes=(("text files", "*.txt"), ("all files", "*.*")))
            if self.exit_application(message_path):
                continue

            image_path = tk.filedialog.askopenfilename(parent=self, title="Select image file",
                                                       filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                                  ("tiff files", "*.tif"), ("gif files", "*.gif"),
                                                                  ("bitmap files", "*.bmp"), ("pdf files", "*.pdf"),
                                                                  ("all files", "*.*")))

            if self.exit_application(image_path):
                continue

            text_handle = open(message_path, 'r')
            message = text_handle.read()
            resolution = os.stat(image_path).st_size * 8
            secret_bits = len(message) * 7
            if secret_bits > resolution:
                tk.messagebox.showinfo('Return', "The message binary values exceeds the resolution binary values "
                                                 "therefore will not work. Please try a shorter message or larger "
                                                 "image.")
                continue
            save_path = self.file_handle()
            files.append([message_path, image_path, save_path])
            msg_box = tk.messagebox.askquestion('Processing', 'Add more files to embed?', icon='warning')
            if msg_box == 'no':
                break
            else:
                tk.messagebox.showinfo('Return', 'Adding more files')
            self.clear_label()
        while files:
            paths = files.pop(-1)
            msg_embed.Main(sig_bit, plane, key, paths[0], paths[1], paths[2])
        self.clear_label()
        self.display("ALL DONE")
        self.menubar.enable()

    def img_embed(self):
        self.clear_label()
        self.menubar.disable()
        files = []
        sig_bit, plane, key = self.settings()
        while True:
            cover_image_path = tk.filedialog.askopenfilename(parent=self, title="Select cover image file",
                                                             filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                                        ("tiff files", "*.tif"), ("gif files", "*.gif"),
                                                                        ("bitmap files", "*.bmp"),
                                                                        ("pdf files", "*.pdf"), ("all files", "*.*")))
            if self.exit_application(cover_image_path):
                continue

            image_path = tk.filedialog.askopenfilename(parent=self, title="Select image file",
                                                       filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                                  ("tiff files", "*.tif"), ("gif files", "*.gif"),
                                                                  ("bitmap files", "*.bmp"), ("pdf files", "*.pdf"),
                                                                  ("all files", "*.*")))

            if self.exit_application(image_path):
                continue

            cover_size = os.stat(cover_image_path).st_size
            image_size = os.stat(image_path).st_size
            if image_size > cover_size:
                tk.messagebox.showinfo('Return', "The message binary values exceeds the resolution binary values "
                                                 "therefore will not work. Please try a shorter message or larger "
                                                 "image.")
                continue
            save_path = self.file_handle()
            files.append([image_path, cover_image_path, save_path])
            msg_box = tk.messagebox.askquestion('Processing', 'Add more files to embed?', icon='warning')
            if msg_box == 'no':
                break
            else:
                tk.messagebox.showinfo('Return', 'Adding more files')
            self.clear_label()
        while files:
            paths = files.pop(-1)
            img_embed.Main(sig_bit, plane, key, paths[0], paths[1], paths[2])
        self.clear_label()
        self.display("ALL DONE")
        self.menubar.enable()

    def msg_extract(self):
        self.clear_label()
        self.menubar.disable()
        msg_extract.Main(self)
        self.menubar.enable()

    def img_extract(self):
        self.clear_label()
        self.menubar.disable()
        img_extract.Main(self)
        self.menubar.enable()


if __name__ == "__main__":
    Interface().mainloop()
