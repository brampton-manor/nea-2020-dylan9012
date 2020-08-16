# img_embed.py

import os
import random
from datetime import date

import numpy as np
from PIL import Image


class ImgEmbed:
    def __init__(self, sig_bit, plane, key, paths, shared_methods):
        self.sig_bit = sig_bit
        self.plane = plane
        self.key = key
        self.data_image_path, self.cover_image_path, self.save_path = paths
        self.cover_image = Image.open(self.cover_image_path)
        self.width, self.height = self.cover_image.size
        self.pixels = self.cover_image.load()
        unpacked_bits = np.unpackbits(
            np.fromfile(self.data_image_path, dtype="uint8"))
        self.data_image_bits = ''.join(str(bit) for bit in list(unpacked_bits))
        self.watermarked_bits = self.watermark()
        self.final_bits = self.add_length()
        shared_methods.embed(self)

    def add_length(self):
        length = format(len(self.watermarked_bits), 'b').zfill(100)
        return length + self.watermarked_bits

    def watermark(self):
        secret_watermark = os.path.splitext(
            self.save_path)[1][1:] + "/dylan/" + date.today().strftime("%Y-%m-%d")
        secret_watermark_bits = ''.join(
            format(ord(character), 'b').zfill(8) for character in secret_watermark)
        random_index = random.randint(0, len(self.data_image_bits))
        return self.data_image_bits[:random_index] + secret_watermark_bits + self.data_image_bits[random_index:]


if __name__ == "__main__":
    pass
