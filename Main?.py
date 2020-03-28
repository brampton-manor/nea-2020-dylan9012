import os
import tkinter as tk
from tkinter import messagebox, filedialog

from PIL import Image as cImage

from tools import msg_embed, msg_extract, img_embed, img_extract


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        embed_submenu = tk.Menu(self, tearoff=0)
        extract_submenu = tk.Menu(self, tearoff=0)

        embed_submenu.add_command(label="Message", command=lambda: parent.msg_embed())
        embed_submenu.add_command(label="Image", command=lambda: parent.img_embed())
        extract_submenu.add_command(label="Message", command=lambda: parent.msg_extract())
        extract_submenu.add_command(label="Image", command=lambda: parent.img_extract())
        self.add_cascade(label="Embed", menu=embed_submenu)
        self.add_cascade(label="Extract", menu=extract_submenu)


class RadioBar(tk.Frame):
    def __init__(self, parent, text, index, width=15, height=2):
        tk.Frame.__init__(self, parent)
        self.text = text
        self.index = index
        self.height = height
        self.width = width
        tk.Radiobutton(self, text=self.text, variable=parent.radio_var, value=self.index, height=self.height,
                       width=self.width).pack()


class ButtonBar(tk.Frame):
    def __init__(self, parent, text, width=15, height=2):
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.text = text
        self.height = height
        self.width = width
        tk.Button(self, text=self.text, height=self.height, width=self.width,
                  command=self.update).pack()

    def update(self):
        self.master.button_var.set(1)


class Interface(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.protocol(self, "WM_DELETE_WINDOW", self.on_exit)
        tk.Tk.title(self, "Main")
        tk.Tk.geometry(self, "1000x500")

        self.screen_var = None
        self.button_var = None
        self.radio_var = None
        self.radios = None
        # Setters for widget creations

        self.label()
        menubar = MenuBar(self)
        self.config(menu=menubar)

    def on_exit(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            tk.Tk.destroy(self)

    def label(self):
        self.screen_var = tk.StringVar()
        label = tk.Label(justify=tk.LEFT, relief=tk.RIDGE, borderwidth=3, textvariable=self.screen_var, width=300,
                         height=5,
                         anchor=tk.NW)
        label.config(state=tk.NORMAL, bg="black", fg="#42f545", font="ansifixed")
        label.pack(fill=tk.BOTH, expand=1)
        self.display("Please choose an option from the Toggle menu to continue...")

    def display(self, event):
        self.screen_var.set(self.screen_var.get() + event + "\n")
        tk.Tk.update(self)

    def clear_label(self):
        self.screen_var.set("")
        tk.Tk.update(self)

    def entry_input(self, event):
        self.display(event)
        text_entry = tk.Entry()
        text_entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        catch = tk.StringVar()

        def callback(event):
            nonlocal catch
            catch.set(text_entry.get())

        text_entry.bind('<Return>', callback)
        text_entry.wait_variable(catch)
        text_entry.destroy()
        self.clear_label()
        return catch.get()

    def radio_input(self, event, text):
        self.display(event)

        self.button_var = tk.IntVar()
        self.radio_var = tk.IntVar()
        self.radios = [RadioBar(self, i, text.index(i)) for i in text]

        confirm = ButtonBar(self, "Confirm")
        confirm.pack(side=tk.RIGHT)

        for i in self.radios:
            i.pack(side=tk.LEFT, expand=tk.YES)

        tk.Tk.update(self)
        confirm.wait_variable(self.button_var)

        for i in self.radios:
            i.destroy()
        confirm.destroy()

        return text[self.radio_var.get()]

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

    def msg_embed(self):
        files = []

        while True:
            message_path = filedialog.askopenfilename(title="Select text file",
                                                      filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
            if self.exit_application(message_path):
                self.on_exit()
            image_path = filedialog.askopenfilename(title="Select image file",
                                                    filetypes=(("bmp files", "*.bmp"), ("all files", "*.*")))
            if self.exit_application(image_path):
                self.on_exit()

            try:
                cImage.open(image_path)
                text_handle = open(message_path, 'r')
                message = text_handle.read()
                resolution = os.stat(image_path).st_size * 8
                secret_bits = len(message) * 7
                if secret_bits > resolution:
                    messagebox.showinfo('Return',
                                        "The message binary values exceeds the resolution binary values, therefore "
                                        "will not work. "
                                        "Please try a shorter message or larger image.\n")
                    continue
            except OSError:
                messagebox.showinfo('Return', "Invalid plaintext or image paths...")
                continue

            files.append([message_path, image_path])
            msg_box = messagebox.askquestion('Processing', 'Add more files to embed?',
                                             icon='warning')
            if msg_box == 'no':
                break
            else:
                messagebox.showinfo('Return', 'Select')
        for i in files:
            msg_embed.Main(self, i[0], i[1])

    def msg_extract(self):
        msg_extract.Main(self)

    def img_embed(self):
        img_embed.Main(self)

    def img_extract(self):
        img_extract.Main(self)

if __name__ == "__main__":
    Interface().mainloop()

