from tkinter import filedialog, messagebox
from PIL import Image as cImage
from datetime import datetime
from os import path
import random
import os


class Main:
    def __init__(self, parent):
        self.master = parent
        # - Optional configurations
        self.sig_bit, self.plane = self.config()
        # - User inputs, and extracting image information
        self.cover_image, self.image_path, self.key, self.file_type, self.dimensions, self.pixels = self.inputs()
        # - Pixel embedding order
        shuffled_indices = self.ordering()
        # - Extraction
        extracted_bits = []
        for i in shuffled_indices:
            x = i % self.dimensions[0]
            y = int(i / self.dimensions[0])
            p = format(self.pixels[x, y][self.plane], 'b').zfill(8)
            extracted_bits.append(p[self.sig_bit])

        msg_length = int(''.join(extracted_bits[:14]), 2)
        extracted_msg = extracted_bits[14:14 + msg_length * 7]

        self.secret_msg = ""
        word = []
        counter = 0
        for i in extracted_msg:
            counter += 1
            word.append(i)
            if counter == 7:
                self.secret_msg += chr(int(''.join(word), 2))
                counter = 0
                word.clear()

        self.secret_msg = self.watermark(0)
        if self.secret_msg == "Error":
            self.error_message(5)
        else:
            # - File handling
            self.file_handle()
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
        # - Image file validation
        self.master.display("Fetching image file directory...")
        image_path = filedialog.askopenfilename(initialdir=location,
                                                title="Select image file",
                                                filetypes=(("bmp files", "*bmp"), ("all files", "*.*")))
        if self.exit_application(image_path):
            return self.inputs()

        try:
            cover_image = cImage.open(image_path)
        except OSError:
            self.error_message(5)
            return self.inputs()

        dimensions = cover_image.size
        pixels = cover_image.load()

        # - Integer validation on key
        try:
            self.master.display("\n")
            key = int(self.master.entry_input("Please enter numerical key"))
        except ValueError:
            self.error_message(4)
            return self.inputs()
        return cover_image, image_path, key, image_path[-3:].upper(), dimensions, pixels

    def file_handle(self):
        self.master.display("Fetching text file directory...")
        save_path = filedialog.asksaveasfilename(initialdir=path.dirname(os.getcwd()),
                                                 title="Save text file to directory",
                                                 defaultextension="*.txt",
                                                 filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
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
            print("Check")
            self.error_message(5)
            return "Error"
        try:
            datetime.strptime(self.secret_msg[index + 7:index + 17], '%Y-%m-%d')
        except ValueError:
            return "Error"

        if self.secret_msg[index - 3:index] == self.file_type:
            return self.secret_msg.replace(self.secret_msg[index - 3:index + 17], '')
        else:
            return self.watermark(index + 1)


if __name__ == "__main__":
    pass
