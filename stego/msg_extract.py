# msg_extract.py

import os
from datetime import datetime
from tkinter import filedialog

from PIL import Image


class MsgExtract:
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
        msg_length = int(extracted_bits[:14], 2)
        extracted_msg_bits = extracted_bits[14:14 + msg_length * 7]
        secret_message = ""
        letter = ""
        position = 0
        for bit in extracted_msg_bits:
            position += 1
            letter += bit
            if position == 7:
                secret_message += chr(int(letter, 2))
                position = 0
                letter = ""
        return secret_message

    def file_handle(self):
        save_path = False
        while not save_path:
            save_path = filedialog.asksaveasfilename(parent=self.master, title="Save text file to directory",
                                                     defaultextension="*.txt")
            if self.master.queue.path_validation(save_path, 't'):
                save_path = False
        file = open(save_path, "w+")
        file.write(self.removed_watermark)
        file.close()

    def watermark(self):
        index = 0
        while index != -1:
            index = self.secret_data.find('/dylan/', index)
            if index == -1:
                continue
            date = self.secret_data[index + 7:index + 17]
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                index += 1
                continue
            file_type = self.secret_data[index - 3:index]
            if self.file_type == file_type:
                watermark_string = self.secret_data[index - 3:index + 17]
                return self.secret_data.replace(watermark_string, '')
            else:
                index += 1
        return False


if __name__ == "__main__":
    pass
