import os
from datetime import datetime
from tkinter import filedialog

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
        save_path = filedialog.asksaveasfilename(parent=self.master, title="Save text file to directory",
                                                 defaultextension="*.txt")
        if self.master.queue.path_validation(save_path, 'i'):
            self.file_handle()

        file = open(save_path, "w+")
        file.write(self.removed_watermark)
        file.close()

    def watermark(self, i):
        index = self.secret_data.find('/dylan/', i)
        if index == -1:
            return False
        try:
            datetime.strptime(self.secret_data[index + 7:index + 17], '%Y-%m-%d')
        except ValueError:
            return False
        if self.file_type == self.secret_data[index - 3:index]:
            return self.secret_data.replace(self.secret_data[index - 3:index + 17], '')
        else:
            return self.watermark(index + 1)


if __name__ == "__main__":
    pass
