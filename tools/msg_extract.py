import random
from datetime import datetime
from tkinter import filedialog, messagebox

from PIL import Image


class Main:
    def __init__(self, parent):
        self.master = parent
        # - Optional configurations
        self.sig_bit, self.plane, self.key = self.inputs()
        # - User inputs, and extracting image information
        self.cover_image, self.image_path, self.file_type, self.dimensions, self.pixels = self.config()
        # - Pixel embedding order
        shuffled_indices = self.ordering()
        # - Extraction
        extracted_bits = ""
        for i in shuffled_indices:
            x = i % self.dimensions[0]
            y = i // self.dimensions[0]
            p = format(self.pixels[x, y][self.plane], 'b').zfill(8)
            extracted_bits += p[self.sig_bit]

        msg_length = int(extracted_bits[:14], 2)
        extracted_msg = extracted_bits[14:14 + msg_length * 7]

        self.secret_msg = ""
        letter = ""
        counter = 0
        for i in extracted_msg:
            counter += 1
            letter += i
            if counter == 7:
                self.secret_msg += chr(int(letter, 2))
                counter = 0
                letter = ""

        self.secret_msg = self.watermark(0)
        if not self.secret_msg:
            self.error_message(3)
        else:
            # - File handling
            self.file_handle()
            self.master.display("\n")
            self.master.display("ALL DONE")
            self.master.display("\n")

    def error_message(self, case):
        switch = {
            1: "Input not numerical",
            2: "Invalid file format",
            3: "Watermark not present in image, please try another image"
        }
        self.master.display("\n", "-" * 100, "\n")
        self.master.display("Error {}: {}".format(case, switch.get(case)))
        self.master.display("\n", "-" * 100, "\n")

    def inputs(self):
        choice = self.master.radio_input("Customised embedding?", ["Yes", "No"])
        if choice == "Yes":
            while True:
                try:
                    key = int(self.master.entry_input("Please enter numerical key"))
                    break
                except ValueError:
                    self.error_message(1)
            sig_bit = int(self.master.entry_input("Enter significant bit"))
            plane = int(["Red", "Blue", "Green"].index(
                self.master.radio_input("Enter Colour Plane", ["Red", "Blue", "Green"])))
        else:
            sig_bit = 7
            plane = 0
            key = 0
        return sig_bit, plane, key

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
        save_path = filedialog.asksaveasfilename(parent=self.master, title="Save text file to directory",
                                                 defaultextension="*.txt",
                                                 filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        if self.exit_application(save_path):
            self.file_handle()

        file = open(save_path, "w+")
        file.write(self.secret_msg)
        file.close()

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
        index = self.secret_msg.find('/dylan/', i)
        if index == -1:
            return False
        try:
            datetime.strptime(self.secret_msg[index + 7:index + 17], '%Y-%m-%d')
        except ValueError:
            return False

        if self.file_type == self.secret_msg[index - 3:index]:
            return self.secret_msg.replace(self.secret_msg[index - 3:index + 17], '')
        else:
            return self.watermark(index + 1)


if __name__ == "__main__":
    pass
