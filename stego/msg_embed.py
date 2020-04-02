import random
from datetime import date

from PIL import Image


class Main:
    def __init__(self, sig_bit, plane, key, message_path, image_path, save_path):
        self.sig_bit = sig_bit
        self.plane = plane
        self.key = key

        self.message_path = message_path
        self.image_path = image_path
        self.save_path = save_path

        self.cover_image = Image.open(self.image_path)
        self.message = open(self.message_path, 'r').read()

        self.dimensions = self.cover_image.size
        self.pixels = self.cover_image.load()
        # - Seeding
        self.shuffled_indices = self.ordering()
        # - Binary conversion
        self.message = self.watermark()
        bits = self.add_length()
        # - Modify pixels
        for i in range(len(bits)):
            x = self.shuffled_indices[i] % self.dimensions[0]
            y = self.shuffled_indices[i] // self.dimensions[0]
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
        if self.save_path.find('tif'):  # - Support for tiff
            self.cover_image.save(self.save_path, format='tiff', compression='None')
        else:
            self.cover_image.save(self.save_path, compression='None')

    def ordering(self):
        shuffled_indices = list(range(self.dimensions[0] * self.dimensions[1]))
        random.seed(self.key)
        random.shuffle(shuffled_indices)
        return shuffled_indices

    def add_length(self):
        s_bits = ''.join(format(ord(char), 'b').zfill(7) for char in self.message)
        l_bits = format(len(self.message), 'b').zfill(14)
        return l_bits + s_bits

    def modify_pixel(self, pixel, modifier):
        pixel = list(pixel)
        plane_list = list(''.join((format(pixel[self.plane], 'b')).zfill(8)))
        plane_list[self.sig_bit] = str(modifier)
        pixel[self.plane] = int(''.join(plane_list), 2)
        return pixel[0], pixel[1], pixel[2]

    def watermark(self):
        string = self.save_path[-3:].upper() + "/dylan/" + date.today().strftime("%Y-%m-%d")
        index = random.randint(0, len(self.message))
        return self.message[:index] + string + self.message[index:]


if __name__ == "__main__":
    pass
