import os
import random
import time
import tkinter as tk
from tkinter import messagebox, filedialog

from stego.img_embed import ImgEmbed
from stego.img_extract import ImgExtract
from stego.msg_embed import MsgEmbed
from stego.msg_extract import MsgExtract


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.embed_menu = tk.Menu(self, tearoff=tk.NO)
        self.extract_menu = tk.Menu(self, tearoff=tk.NO)
        self.exit = tk.Menu(self, tearoff=tk.NO)
        self.exit.add_command(label="Close application", command=parent.on_exit)
        self.embed_menu.add_command(label="Message", command=lambda: parent.queue.choose_msg_embed())
        self.extract_menu.add_command(label="Message", command=lambda: parent.queue.choose_extract(
            MsgExtract(parent, parent.queue.settings(), parent.queue.open_files(''))))
        self.embed_menu.add_command(label="Image", command=lambda: parent.queue.choose_img_embed())
        self.extract_menu.add_command(label="Image", command=lambda: parent.queue.choose_extract(
            ImgExtract(parent, parent.queue.settings(), parent.queue.open_files(''))))
        self.add_cascade(label="Embed", menu=self.embed_menu)
        self.add_cascade(label="Extract", menu=self.extract_menu)
        self.add_cascade(label="Exit", menu=self.exit)

    def disable(self):
        for menu in range(2):
            self.embed_menu.entryconfigure(menu, state=tk.DISABLED)
            self.extract_menu.entryconfigure(menu, state=tk.DISABLED)

    def enable(self):
        for menu in range(2):
            self.embed_menu.entryconfigure(menu, state=tk.NORMAL)
            self.extract_menu.entryconfigure(menu, state=tk.NORMAL)


class ButtonBar(tk.Frame):
    def __init__(self, parent, text, width=15, height=2):
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.text = text
        self.height = height
        self.width = width
        tk.Button(self, text=self.text, height=self.height, width=self.width, command=self.trigger).pack()

    def trigger(self):
        self.master.button_var.set(True)


class ToolsLink:
    def __init__(self, parent):
        self.master = parent

    def embed(self, this):
        shuffled_indices = self.ordering(this)
        for bit in range(len(this.final_bits)):
            x = shuffled_indices[bit] % this.width
            y = shuffled_indices[bit] // this.width
            p = format(this.pixels[x, y][this.plane], 'b').zfill(8)

            if p[this.sig_bit] == "0":
                if this.final_bits[bit] == "1":
                    this.pixels[x, y] = self.modify_pixel(this, this.pixels[x, y], 1)

            elif this.final_bits[bit] == "0":
                this.pixels[x, y] = self.modify_pixel(this, this.pixels[x, y], 0)
        if os.path.splitext(this.save_path)[1].find('tif'):
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
        this.removed_watermark = this.watermark()
        if not this.removed_watermark:
            tk.messagebox.showinfo("Invalid cover image", "Watermark not present in image, please try another image")
        else:
            this.file_handle()

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
        self.supported_text_types = {".txt", ".rtf"}

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
            sig_bit = int(
                self.master.scale_input("Enter significant bit (0 - for low quality to 7 - for high quality)"))
            plane = int(["Red", "Blue", "Green"].index(
                self.master.radio_input("Enter Colour Plane", ["Red", "Blue", "Green"])))
        else:
            sig_bit = 7
            plane = 0
            key = 0
        return sig_bit, plane, key

    def path_validation(self, file, mode):
        if (os.path.splitext(file)[1] not in self.supported_image_types and mode == 'i') or (
                os.path.splitext(file)[1] not in self.supported_text_types and mode == 't'):
            tk.messagebox.showinfo('Illegal file', 'Please choose a supported file type and valid name')
            return True
        else:
            return False

    def file_handle(self):
        save_path = ''
        while save_path == '':
            save_path = tk.filedialog.asksaveasfilename(parent=self.master, title="Save cover image to directory",
                                                        defaultextension="*.gif")
            if self.path_validation(save_path, 'i'):
                save_path = ''
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
        cover_image_path, data_path = False, False
        while not (cover_image_path and data_path):
            cover_image_path = tk.filedialog.askopenfilename(parent=self.master, title="Select cover image file")
            if self.path_validation(cover_image_path, 'i'):
                cover_image_path = False
                continue
            if mode:
                data_path = tk.filedialog.askopenfilename(parent=self.master, title="Select media to embed")
                if self.path_validation(data_path, mode):
                    data_path = False
                    continue
            else:
                break
            return cover_image_path, data_path
        return cover_image_path

    def process_files(self, files, sig_bit, plane, key, mode):
        while files:
            paths = files.pop(-1)
            if mode == 't':
                MsgEmbed(sig_bit, plane, key, paths, ToolsLink(self.master))
            else:
                ImgEmbed(sig_bit, plane, key, paths, ToolsLink(self.master))
        self.master.clear_label()
        self.master.display("ALL DONE")
        time.sleep(3)
        self.master.menubar.enable()
        self.master.startup_msg()

    def choose_msg_embed(self):
        self.master.clear_label()
        files = []
        mode = 't'
        sig_bit, plane, key = self.settings()
        while True:
            cover_image_path, data_path = self.open_files(mode)
            message = open(data_path, 'r', encoding="ISO-8859-1").read()
            cover_size = os.stat(cover_image_path).st_size * 8
            message_bits = len(message) + 7 * 14
            if cover_size > message_bits:
                tk.messagebox.showinfo('Return', "The message size exceeds the cover image size therefore will not "
                                                 "work. Please try a shorter message or larger image.")
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
            image_size = os.stat(data_path).st_size + 100
            if cover_size < image_size:
                tk.messagebox.showinfo('Return', "The data image size exceeds the cover image size therefore will not "
                                                 "work. Please try a shorter message or larger. Please try a smaller "
                                                 "data image or larger cover image.")
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
        tk.Tk.title(self, "Steganography Program")
        tk.Tk.geometry(self, "775x450")
        self.screen_var = None
        self.button_var = None
        self.radio_var = None
        self.scale_var = None
        self.radios = None
        self.label()
        self.queue = Queue(self)
        self.menubar = MenuBar(self)
        self.config(menu=self.menubar)

    def startup_msg(self):
        self.clear_label()
        self.display("Please choose an option from the menu to continue...", "\n\n",
                     "Go to embed > message to embed a message inside an image", "\n",
                     "Go to embed > image to embed an image inside an image", "\n",
                     "Go to extract > message to extract a message from an image", "\n",
                     "Go to extract > message to extract an image from an image", "\n")

    def on_exit(self):
        if tk.messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            tk.Tk.destroy(self)

    def label(self):
        self.screen_var = tk.StringVar()
        label = tk.Label(justify=tk.LEFT, relief=tk.RIDGE, textvariable=self.screen_var, width=300, height=5,
                         anchor=tk.NW, borderwidth=3)
        label.config(state=tk.NORMAL, bg="black", fg="#42f545", font="ansifixed")
        label.pack(fill=tk.BOTH, expand=tk.YES)
        self.startup_msg()

    def display(self, *argv):
        for string in argv:
            self.screen_var.set(self.screen_var.get() + string)
        self.screen_var.set(self.screen_var.get() + "\n")
        tk.Tk.update(self)

    def clear_label(self):
        self.screen_var.set("")
        tk.Tk.update(self)

    def entry_input(self, string):
        self.display(string)
        catch = tk.StringVar()

        def callback(event):
            event.set(text_entry.get())

        text_entry = tk.Entry(self)
        text_entry.bind('<Return>', (lambda _: callback(catch)))
        text_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        text_entry.wait_variable(catch)
        text_entry.destroy()
        self.clear_label()
        return catch.get()

    def radio_input(self, string, text):
        self.display(string)
        self.button_var = tk.BooleanVar()
        radio_var = tk.IntVar()
        self.radios = [
            tk.Radiobutton(self, text=option, variable=radio_var, value=text.index(option), height=2, width=15) for
            option in text]
        for radio in self.radios:
            radio.pack(side=tk.LEFT, expand=tk.YES)
        confirm = ButtonBar(self, "Confirm")
        confirm.pack(side=tk.RIGHT)
        tk.Tk.update(self)
        confirm.wait_variable(self.button_var)
        for radio in self.radios:
            radio.destroy()
        confirm.destroy()
        return text[radio_var.get()]

    def scale_input(self, string):
        self.display(string)
        scale_var = tk.IntVar()
        scale = tk.Scale(self, from_=0, to=7, variable=scale_var, orient=tk.HORIZONTAL, length=450, cursor="hand",
                         label="Slide to significant bit")
        confirm = ButtonBar(self, "Confirm")
        scale.pack(side=tk.LEFT)
        confirm.pack(side=tk.RIGHT)
        tk.Tk.update(self)
        confirm.wait_variable(self.button_var)
        scale.destroy()
        confirm.destroy()
        return scale_var.get()


if __name__ == "__main__":
    Interface().mainloop()
