import os
import random
from datetime import date

from PIL import Image


class Main:
    def __init__(self, sig_bit, plane, key, paths, shared_methods):
        self.sig_bit = sig_bit
        self.plane = plane
        self.key = key

        self.message_path, self.cover_image_path, self.save_path = paths

        self.cover_image = Image.open(self.cover_image_path)
        self.secret_message = open(self.message_path, 'r').read()

        self.width, self.height = self.cover_image.size
        self.pixels = self.cover_image.load()
        self.watermarked_bits = self.watermark()
        self.final_bits = self.add_length()

        shared_methods.embed(self)

    def add_length(self):
        message_bits = ''.join(format(ord(character), 'b').zfill(7) for character in self.watermarked_bits)
        length_bits = format(len(self.watermarked_bits), 'b').zfill(14)
        return length_bits + message_bits

    def watermark(self):
        secret_watermark = os.path.splitext(self.save_path)[1][1:] + "/dylan/" + date.today().strftime(
            "%Y-%m-%d")
        random_index = random.randint(0, len(self.secret_message))
        return self.secret_message[:random_index] + secret_watermark + self.secret_message[random_index:]


if __name__ == "__main__":
    pass
