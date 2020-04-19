import os
from datetime import datetime
from tkinter import filedialog

import numpy as np
from PIL import Image


class Main:
    def __init__(self, parent, settings, cover_image_path):
        self.master = parent
        # - Optional configurations
        self.sig_bit, self.plane, self.key = settings
        # - User inputs, and extracting image information
        self.file_type = os.path.splitext(cover_image_path)[1][1:]
        self.cover_image = Image.open(cover_image_path)
        self.width, self.height = self.cover_image.size
        self.pixels = self.cover_image.load()

    @staticmethod
    def conversion(extracted_bits):
        data_img_bits_length = int(extracted_bits[:100], 2)
        return extracted_bits[100:100 + data_img_bits_length]

    def file_handle(self):
        save_path = filedialog.asksaveasfilename(parent=self.master, title="Save image to directory",
                                                 defaultextension="*.gif")
        if self.master.queue.path_validation(save_path, 'i'):
            self.file_handle()

        image_bits = list((map(int, list(self.removed_watermark))))
        bits = np.array(list(image_bits))
        byte = np.packbits(bits)
        byte.tofile(save_path)

    def watermark(self, i):
        name_bits = ''.join(format(ord(i), 'b').zfill(8) for i in "/dylan/")
        index = str(self.secret_data).find(name_bits, i)
        if index == -1:
            return False

        # date validation
        date = self.secret_data[index + 7 * 8:index + 17 * 8]
        try:
            datetime.strptime(''.join(chr(int(date[i:i + 8], 2)) for i in range(0, len(date), 8)), '%Y-%m-%d')
        except ValueError:
            return False

        # file-type validation
        file_type_bits = self.secret_data[index - 3 * 8:index]
        file_type = ''
        for i in range(0, len(file_type_bits), 8):
            file_type += ''.join(
                chr(int(file_type_bits[i:i + 8], 2)))  # - Converts every 8 bits to ascii code to letter

        if self.file_type == file_type:
            return self.secret_data.replace(self.secret_data[index - 3 * 8:index + 17 * 8], '')
        else:
            return self.watermark(i + 1)


if __name__ == "__main__":
    pass
