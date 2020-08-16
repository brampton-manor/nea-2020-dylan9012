# img_extract.py

import os
from datetime import datetime
from tkinter import filedialog

import numpy as np
from PIL import Image


class ImgExtract:
    def __init__(self, parent, settings, cover_image_path):
        self.master = parent
        self.sig_bit, self.plane, self.key = settings
        self.file_type = os.path.splitext(cover_image_path)[1][1:]
        self.cover_image = Image.open(cover_image_path)
        self.width, self.height = self.cover_image.size
        self.pixels = self.cover_image.load()
        self.removed_watermark = None
        self.secret_data = None

    @staticmethod
    def conversion(extracted_bits):
        data_img_bits_length = int(extracted_bits[:100], 2)
        return extracted_bits[100:100 + data_img_bits_length]

    def file_handle(self):
        save_path = False
        while not save_path:
            save_path = filedialog.asksaveasfilename(
                parent=self.master,
                title="Save image to directory",
                defaultextension="*.gif")
            if self.master.queue.path_validation(save_path, 'i'):
                save_path = False

        image_bits = list((map(int, list(self.removed_watermark))))
        bits = np.array(list(image_bits))
        byte = np.packbits(bits)
        byte.tofile(save_path)

    def watermark(self):
        name_bits = ''.join(
            format(ord(character), 'b').zfill(8) for character in "/dylan/")
        index = 0
        while index != -1:
            index = str(self.secret_data).find(name_bits, index)
            if index == -1:
                continue
            date_bits = self.secret_data[index + 7 * 8:index + 17 * 8]
            date = ''
            for position in range(0, len(date_bits), 8):
                date += ''.join(chr(int(date[position:position + 8], 2)))
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                index += 1
                continue
            file_type_bits = self.secret_data[index - 3 * 8:index]
            file_type = ''
            for position in range(0, len(file_type_bits), 8):
                file_type += ''.join(chr(int(file_type_bits[position:position + 8], 2)))
            if self.file_type == file_type:
                return self.secret_data.replace(
                    self.secret_data[index - 3 * 8:index + 17 * 8], '')
            else:
                index += 1
        return False


if __name__ == "__main__":
    pass
