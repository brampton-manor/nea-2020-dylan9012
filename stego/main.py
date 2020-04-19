import os
import random
import time
import tkinter as tk
from tkinter import messagebox, filedialog

import img_embed
import img_extract
import msg_embed
import msg_extract


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.embed_menu = tk.Menu(self, tearoff=tk.NO)
        self.extract_menu = tk.Menu(self, tearoff=tk.NO)

        self.embed_menu.add_command(label="Message", command=lambda: parent.queue.choose_msg_embed())
        self.extract_menu.add_command(label="Message",
                                      command=lambda: parent.queue.choose_extract(
                                          msg_extract.Main(parent, parent.queue.settings(),
                                                           parent.queue.open_files(''))))
        self.embed_menu.add_command(label="Image", command=lambda: parent.queue.choose_img_embed())
        self.extract_menu.add_command(label="Image",
                                      command=lambda: parent.queue.choose_extract(
                                          img_extract.Main(parent, parent.queue.settings(),
                                                           parent.queue.open_files(''))))
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


class ButtonBar(tk.Frame):
    def __init__(self, parent, text, width=15, height=2):
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.text = text
        self.height = height
        self.width = width
        tk.Button(self, text=self.text, height=self.height, width=self.width, command=self.trigger).pack()

    def trigger(self):
        self.master.button_var.set(1)


class ToolsLink:
    def __init__(self, parent):
        self.master = parent

    def embed(self, this):
        shuffled_indices = self.ordering(this)
        for bit in range(len(this.final_bits)):
            x = shuffled_indices[bit] % this.width
            y = shuffled_indices[bit] // this.width
            p = format(this.pixels[x, y][this.plane], 'b').zfill(8)

            # - Change if existing bit is 0, only if secret bit is 1
            if p[this.sig_bit] == "0":
                if this.final_bits[bit] == "1":
                    this.pixels[x, y] = self.modify_pixel(this, this.pixels[x, y], 1)
            # - Change if existing bit is 1, only if secret bit is 0
            else:
                if this.final_bits[bit] == "0":
                    this.pixels[x, y] = self.modify_pixel(this, this.pixels[x, y], 0)

        if this.save_path.find('tif'):  # - Support for tiff
            this.cover_image.save(this.save_path, format='tiff', compression='None')
        else:
            this.cover_image.save(this.save_path, compression='None')

    def extract(self, this):
        shuffled_indices = self.ordering(this)
        extracted_bits = ""
        for index in shuffled_indices:
            x = index % this.width
            y = index // this.width
            p = format(this.pixels[x, y][this.plane], 'b').zfill(8)
            extracted_bits += p[this.sig_bit]

        this.secret_data = this.conversion(extracted_bits)

        this.removed_watermark = this.watermark(0)
        if not this.removed_watermark:
            self.error_message(3)
        else:
            # - File handling
            this.file_handle()

    def error_message(self, case):
        switch = {
            1: "Input not numerical",
            2: "Invalid file format",
            3: "Watermark not present in image, please try another image"
        }
        self.master.display("\n", "-" * 100, "\n")
        self.master.display("Error {}: {}".format(case, switch.get(case)))
        self.master.display("\n", "-" * 100, "\n")

    @staticmethod
    def modify_pixel(this, pixel, modifier):
        pixel_list = list(pixel)
        plane_list = list(''.join((format(pixel_list[this.plane], 'b')).zfill(8)))
        plane_list[this.sig_bit] = str(modifier)
        pixel_list[this.plane] = int(''.join(plane_list), 2)
        return pixel_list[0], pixel_list[1], pixel_list[2]

    @staticmethod
    def ordering(this):
        shuffled_indices = list(range(this.width * this.height))
        random.seed(this.key)
        random.shuffle(shuffled_indices)
        return shuffled_indices


class Queue:
    def __init__(self, parent):
        self.master = parent
        self.supported_image_types = {".gif", ".png", ".jpg", ".pdf", ".bmp", ".tif", ".tiff"}

    def settings(self):
        self.master.menubar.disable()
        choice = self.master.radio_input("Customised embedding?", ["Yes", "No"])
        if choice == "Yes":
            while True:
                try:
                    key = int(self.master.entry_input("Please enter numerical key"))
                    break
                except ValueError:
                    self.master.display("Error: Input not numerical", "\n")
            while True:
                try:
                    sig_bit = int(
                        self.master.entry_input("Enter significant bit (0 - for low quality to 7 - for high quality)"))
                    if sig_bit < 0 or sig_bit > 7:
                        self.master.display("Error: Input not within range", "\n")
                        continue
                    break
                except ValueError:
                    self.master.display("Error: Input not numerical", "\n")
            plane = int(["Red", "Blue", "Green"].index(
                self.master.radio_input("Enter Colour Plane", ["Red", "Blue", "Green"])))
        else:
            sig_bit = 7
            plane = 0
            key = 0
        return sig_bit, plane, key

    def path_validation(self, file, mode):
        if (os.path.splitext(file)[1] not in self.supported_image_types and mode == 'i') or (
                os.path.splitext(file)[1] != '.txt' and mode == 'm'):
            tk.messagebox.showinfo('Illegal file', 'Please choose a supported file type and valid name')
            return True
        else:
            return False

    def file_handle(self):
        save_path = tk.filedialog.asksaveasfilename(parent=self.master, title="Save cover image to directory",
                                                    defaultextension="*.gif")
        if self.path_validation(save_path, 'i'):
            self.file_handle()
        return save_path

    def add_files(self, files, data_path, image_path):
        save_path = self.file_handle()
        files.append([data_path, image_path, save_path])
        msg_box = tk.messagebox.askquestion('Processing', 'Add more files to embed?', icon='warning')
        if msg_box == 'no':
            return False
        else:
            tk.messagebox.showinfo('Return', 'Adding more files')
            return True

    def open_files(self, mode):
        cover_image_path = tk.filedialog.askopenfilename(parent=self.master, title="Select cover image file")

        if self.path_validation(cover_image_path, 'i'):
            self.open_files(mode)

        if mode:
            data_path = tk.filedialog.askopenfilename(parent=self.master, title="Select data file")
            if self.path_validation(data_path, mode):
                self.open_files(mode)
            return cover_image_path, data_path

        return cover_image_path

    def process_files(self, files, sig_bit, plane, key, mode):
        while files:
            paths = files.pop(-1)
            if mode == 'm':
                msg_embed.Main(sig_bit, plane, key, paths, ToolsLink(self.master))
            else:
                img_embed.Main(sig_bit, plane, key, paths, ToolsLink(self.master))
        self.master.clear_label()
        self.master.display("ALL DONE")
        time.sleep(3)
        self.master.menubar.enable()
        self.master.startup_msg()

    def choose_msg_embed(self):
        self.master.clear_label()
        files = []
        mode = 'm'
        sig_bit, plane, key = self.settings()
        while True:
            cover_image_path, data_path = self.open_files(mode)
            message = open(data_path, 'r', encoding="ISO-8859-1").read()
            resolution = os.stat(cover_image_path).st_size * 8
            message_bits = len(message) * 7
            if message_bits > resolution:
                tk.messagebox.showinfo('Return', "The message binary values exceeds the resolution binary values "
                                                 "therefore will not work. Please try a shorter message or larger "
                                                 "image.")
                continue
            if not self.add_files(files, data_path, cover_image_path):
                break
            self.master.clear_label()
        self.process_files(files, sig_bit, plane, key, mode)

    def choose_img_embed(self):
        self.master.clear_label()
        files = []
        mode = 'i'
        sig_bit, plane, key = self.settings()
        while True:
            cover_image_path, data_path = self.open_files(mode)
            cover_size = os.stat(cover_image_path).st_size
            image_size = os.stat(data_path).st_size
            if image_size > cover_size:
                tk.messagebox.showinfo('Return', "The insert image pixels exceed the cover image pixels "
                                                 "therefore will not work. Please try a shorter message or larger "
                                                 "image.")
                continue
            if not self.add_files(files, data_path, cover_image_path):
                break
            self.master.clear_label()
        self.process_files(files, sig_bit, plane, key, mode)

    def choose_extract(self, extractor):
        self.master.clear_label()
        ToolsLink(self.master).extract(extractor)
        time.sleep(3)
        self.master.display("ALL DONE")
        self.master.menubar.enable()
        self.master.startup_msg()


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
        self.queue = Queue(self)
        self.menubar = MenuBar(self)
        self.config(menu=self.menubar)

    def startup_msg(self):
        self.clear_label()
        self.display("Please choose an option from the menu to continue...", "\n",
                     "Go to embed > message to embed a message inside an image", "\n",
                     "Go to embed > image to embed an image inside an image", "\n",
                     "Go to extract > message to extract a message from an image", "\n",
                     "Go to extract > message to extract an image from an image", "\n")

    def on_exit(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            tk.Tk.destroy(self)

    def label(self):
        self.screen_var = tk.StringVar()
        label = tk.Label(justify=tk.LEFT, relief=tk.RIDGE, anchor=tk.NW, textvariable=self.screen_var, borderwidth=3,
                         width=300, height=5)
        label.config(state=tk.NORMAL, bg="black", fg="#42f545", font="ansifixed")
        label.pack(fill=tk.BOTH, expand=tk.YES)
        self.startup_msg()

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
        self.radios = [tk.Radiobutton(self, text=i, variable=self.radio_var, value=text.index(i), height=2, width=15)
                       for i in text]
        for i in self.radios:
            i.pack(side=tk.LEFT, expand=tk.YES)

        confirm = ButtonBar(self, "Confirm")
        confirm.pack(side=tk.RIGHT)

        tk.Tk.update(self)
        confirm.wait_variable(self.button_var)

        for i in self.radios:
            i.destroy()
        confirm.destroy()

        return text[self.radio_var.get()]


# TODO: Find out limits in message and image - put in bytes? —> will it have a minimum

if __name__ == "__main__":
    Interface().mainloop()
