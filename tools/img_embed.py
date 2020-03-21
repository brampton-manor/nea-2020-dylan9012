from tkinter import filedialog, messagebox
from PIL import Image as cImage
from datetime import date
from os import path
import numpy as np
import random
import os


class Main:
    def __init__(self, parent):
        self.master = parent
        # - Optional configurations
        self.sig_bit, self.plane = self.config()
        # - User inputs
        self.image, self.cover_image, self.image_path, self.cover_image_path, self.key = self.inputs()
        # - Opening images
        self.save_path = self.file_handle()
        # - Opening text
        self.dimensions, self.pixels = self.initialising()
        # - Seeding
        self.shuffled_indices = self.ordering()
        self.image_bits = self.watermark()
        # - Conversion
        bits = self.add_length()
        # - Modify pixels
        for i in range(len(bits)):
            x = self.shuffled_indices[i] % self.dimensions[0]
            y = int(self.shuffled_indices[i] / self.dimensions[0])
            p = format(self.pixels[x, y][self.plane], 'b').zfill(8)

            # - Change if existing bit is 0, only if secret bit is 1
            if p[self.sig_bit] == "0":
                if bits[i] == "1":
                    self.pixels[x, y] = self.modify_pixel(self.pixels[x, y], 1)
            # - Change if existing bit is 1, only if secret bit is 0
            else:
                if bits[i] == "0":
                    self.pixels[x, y] = self.modify_pixel(self.pixels[x, y], 0)

        # - File handling
        self.cover_image.save(self.save_path, 'BMP')
        self.master.display("\n")
        self.master.display("ALL DONE")
        self.master.display("\n")

    def error_message(self, case):
        switch = {
            1: "Invalid choice",
            2: "Invalid inputs",
            3: "Please choose file",
            4: "Input not numerical",
            5: "Invalid file format"
        }
        self.master.display("Error {number}: {case}".format(number=case, case=switch.get(case)))
        self.master.display("\n")
        self.master.display("-" * 100)
        self.master.display("\n")

    def config(self):
        choice = self.master.radio_input("Customised embedding?", ["Yes", "No"])
        if choice == 'y' or choice == 'Y' or choice == "yes" or choice == "Yes":
            sig_bit = int(self.master.entry_input("Enter significant bit"))
            plane = int(["Red", "Blue", "Green"].index(
                self.master.radio_input("Enter Colour Plane", ["Red", "Blue", "Green"])))
        else:
            sig_bit = 7
            plane = 0
        return sig_bit, plane

    def inputs(self):
        location = path.dirname(os.getcwd())
        # - Message & image file validation
        self.master.display("Fetching cover image file directory...")
        cover_image_path = filedialog.askopenfilename(initialdir=location,
                                                      title="Select cover image file",
                                                      filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))
        if self.exit_application(cover_image_path):
            return self.inputs()

        self.master.display("Fetching image file directory...")
        image_path = filedialog.askopenfilename(initialdir=location,
                                                title="Select image file",
                                                filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))

        if self.exit_application(image_path):
            return self.inputs()

        try:
            cover_image = cImage.open(cover_image_path)
            bits = np.unpackbits(np.fromfile(self.image_path, dtype="uint8"))
            image = ''.join(str(i) for i in list(bits))
        except OSError:
            self.error_message(5)
            return self.inputs()

        # - Integer validation on key
        try:
            self.master.display("\n")
            key = int(self.master.entry_input("Please enter numerical key"))
        except ValueError:
            self.error_message(4)
            return self.inputs()
        return image, cover_image, image_path, cover_image_path, key

    def initialising(self):
        dimensions = self.cover_image.size
        pixels = self.cover_image.load()
        cover_size = os.stat(self.cover_image_path).st_size
        image_size = os.stat(self.image_path).st_size
        if image_size > cover_size:
            self.master.display(
                "The message binary values exceeds the resolution binary values, therefore will not work. Please try a "
                "shorter message or larger image.\n")
        else:
            return dimensions, pixels

    def file_handle(self):
        self.master.display("Fetching image file directory...", )
        save_path = filedialog.asksaveasfilename(initialdir=path.dirname(os.getcwd()) + "/Output/Embed",
                                                 defaultextension="*.jpg",
                                                 title="Save image file",
                                                 filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))
        if self.exit_application(save_path):
            self.file_handle()
        return save_path

    def ordering(self):
        shuffled_indices = list(range(self.dimensions[0] * self.dimensions[1]))
        random.seed(self.key)
        random.shuffle(shuffled_indices)
        return shuffled_indices

    def add_length(self):
        length = format(len(self.image_bits), 'b').zfill(100)
        return length + self.image_bits

    def modify_pixel(self, pixel, modifier):
        pixel = list(pixel)
        if self.plane == 0:
            plane_list = list(''.join((format(pixel[self.plane], 'b')).zfill(8)))
            plane_list[self.sig_bit] = str(modifier)
            pixel[self.plane] = int(''.join(plane_list), 2)

        if self.plane == 1:
            plane_list = list(''.join((format(pixel[self.plane], 'b')).zfill(8)))
            plane_list[self.sig_bit] = str(modifier)
            pixel[self.plane] = int(''.join(plane_list), 2)

        if self.plane == 2:
            plane_list = list(''.join((format(pixel[self.plane], 'b')).zfill(8)))
            plane_list[self.sig_bit] = str(modifier)
            pixel[self.plane] = int(''.join(plane_list), 2)
        return pixel[0], pixel[1], pixel[2]

    @staticmethod
    def exit_application(file):
        if file == "":
            msg_box = messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application',
                                             icon='warning')
            if msg_box == 'yes':
                raise SystemExit
            else:
                messagebox.showinfo('Return', 'You will now return to the application screen')
                return True

    def watermark(self):
        watermark = self.save_path[-3:].upper() + "/dylan/" + date.today().strftime("%Y-%m-%d")
        watermark = ''.join(format(ord(i), 'b').zfill(8) for i in watermark)
        index = random.randint(0, len(self.image))
        return self.image[:index] + watermark + self.image[index:]


if __name__ == "__main__":
    pass
