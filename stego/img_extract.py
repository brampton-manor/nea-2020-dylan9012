import random
from datetime import datetime
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image


class Main:
    def __init__(self, parent, settings):
        self.master = parent
        self.master.menubar.disable()
        # - Optional configurations
        self.sig_bit, self.plane, self.key = settings
        # - User inputs, and extracting image information
        self.cover_image, self.image_path, self.file_type, self.dimensions, self.pixels = self.config()
        # - Pixel embedding order
        self.shuffled_indices = self.ordering()
        self.extracted_img = None
        self.image_bits = None

    def extract(self):
        extracted_bits = ""
        for i in self.shuffled_indices:
            x = i % self.dimensions[0]
            y = i // self.dimensions[0]
            p = format(self.pixels[x, y][self.plane], 'b').zfill(8)
            extracted_bits += p[self.sig_bit]
        img_length = int(extracted_bits[:100], 2)
        self.extracted_img = extracted_bits[100:100 + img_length]

        self.image_bits = self.watermark(0)
        # - Check for watermark
        if not self.image_bits:
            self.error_message(3)
        else:
            # - File handling
            self.file_handle()
            self.master.display("ALL DONE")
            self.master.menubar.enable()

    def error_message(self, case):
        switch = {
            1: "Input not numerical",
            2: "Invalid file format",
            3: "Watermark not present in image, please try another image"
        }
        self.master.display("\n", "-" * 100, "\n")
        self.master.display("Error {number}: {case}".format(number=case, case=switch.get(case)))
        self.master.display("\n", "-" * 100, "\n")

    def config(self):
        # - Image file validation
        image_path = filedialog.askopenfilename(parent=self.master, title="Select image file",
                                                filetypes=(("jpeg files", "*.jpg"), ("png files", "*.png"),
                                                           ("tiff files", "*.tif"), ("gif files", "*.gif"),
                                                           ("bitmap files", "*.bmp"), ("pdf files", "*.pdf"),
                                                           ("all files", "*.*")))
        if self.exit_application(image_path):
            return self.config()

        try:
            cover_image = Image.open(image_path)
        except OSError:
            self.error_message(2)
            return self.config()

        dimensions = cover_image.size
        pixels = cover_image.load()
        return cover_image, image_path, image_path[-3:].upper(), dimensions, pixels

    def file_handle(self):
        save_path = filedialog.asksaveasfilename(parent=self.master, title="Save image to directory",
                                                 filetypes=(("gif files", "*.gif"), ("png files", "*.png"),
                                                            ("tiff files", "*.tif"), ("jpeg files", "*.jpg"),
                                                            ("bitmap files", "*.bmp"), ("pdf files", "*.pdf"),
                                                            ("all files", "*.*")))
        if self.exit_application(save_path):
            self.file_handle()

        image_bits = list((map(int, list(self.image_bits))))
        bits = np.array(list(image_bits))
        byte = np.packbits(bits)
        byte.tofile(save_path)

    def ordering(self):
        shuffled_indices = list(range(self.dimensions[0] * self.dimensions[1]))
        random.seed(self.key)
        random.shuffle(shuffled_indices)
        return shuffled_indices

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

    def watermark(self, i):
        string = "/dylan/"
        string = ''.join(format(ord(i), 'b').zfill(8) for i in string)

        index = str(self.extracted_img).find(string, i)
        if index == -1:
            return False

        # date validation
        date = self.extracted_img[index + 7 * 8:index + 17 * 8]
        try:
            datetime.strptime(''.join(chr(int(date[i:i + 8], 2)) for i in range(0, len(date), 8)),
                              '%Y-%m-%d')
        except ValueError:
            return False

        # file-type validation
        file_type = self.extracted_img[index - 3 * 8:index]
        if ''.join(chr(int(file_type[i:i + 8], 2)) for i in range(0, len(file_type), 8)) == self.file_type:
            return self.extracted_img.replace(self.extracted_img[index - 3 * 8:index + 17 * 8], '')
        else:
            return self.watermark(i + 1)


if __name__ == "__main__":
    pass
