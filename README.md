## Project background
When learning about cryptography in A Level Computer Science, I came across steganography in relation to hiding data. To make steganography more secure, I researched ways of using cryptography and steganography in combination to improve the aim of hiding media (e.g. a message) inside an image. My method of attaining this combination is to use a randomly shuffled least significant bit steganography algorithm to scatter data onto the cover image to become untraceable. With this combination, I feel there will be a greater chance that eavesdroppers will not be able to recover the media and aid encryption.

## Current solution
Current solutions to this problem are using some type of cryptography to send messages that are not easily intercepted such as TLS (Transport Layer Protocol) in emails. This works by forming a path of communication activated by a TLS-handshake when digital signatures from both parties are confirmed to be correct. RSA (Rivest, Shamir, and Adelman) encryption is useful in the event the two parties have not met and want to communicate privately. This works by using asymmetric keys to solve the interception dilemma. When you want to communicate with someone, you use their public key to encrypt the data but they then decrypt it with their private key (invisible to the interceptor).
Relevant research
Upon researching steganography’s use in the world and throughout history, I researched what makes good steganography. The design of the steganography must be robust, efficient and invisible to the human eye. After learning about this, I found the most used method of steganography, which was Least Significant Bit (LSB) steganography. LSB steganography consists of placing bits of a message into the LSBs of the cover image, as the LSB is the bit, where if changed minimal visual change would occur which means this bit can be the most dynamic. A variation of LSB steganography is LSB crypto-steganography, where we put the message bits randomly into the image’s LSBs.

## End user and target audience
My target audience will be those who want to display their media publicly but in plain sight. Specific cultures who do not have freedom of speech may want to use this to pass on messages that will not be able to be intercepted by governments. End users who have messages such as locations, times and propaganda like Hong-Kong minorities within China can protect themselves police and avoid jail time for up to ten years while expressing their views and opinions on their government. However, some limitations of steganography methods include misuse in terrorism and breaches in privacy.

## Methods and sources
A Comparative Study of Recent Steganography Techniques for Multiple Image Formats ([Ansari et al.](http://www.mecs-press.org/ijcnis/ijcnis-v11-n1/IJCNIS-V11-N1-2.pdf))
Brain Oakley’s answer to: [Best way to structure a tkinter application?](https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application)

## Objectives
Objective one – Main interface:
•	Functional message box to output strings
•	Menu bar for user to choose option
•	File browsing to select media to input
•	Display entry box for user input
•	Display radio buttons for user input
•	Implement queue for multiple files to embed

Objective two – Main program:
•	Exception handling and prompts to validate inputs
•	Add option to extract media from cover image
•	Add option to embed image into cover image
•	Watermark cover image to detect if media can be extracted.
•	Add compatibility for popular image formats {.jpg, .gif, .png, .tif, .pdf, .bmp}


## Proposed solution
When creating my program, I intend to give the user an option to cryptographically embed media (image or message) with chosen settings (colour plane, key and significant bit) into a chosen cover image so it remains undetected to the human eye which allows the cover image to be broadcast in plain sight. In the other end of things, I will create an extractor to remove the media from the cover image so that the user can give the intended recipient my program with the correct settings. I will develop the program in python as it gives me access to essential libraries crucial to my program such as; Pillow, to access the image bits, which can be modified so it can contain the user’s media and  NumPy, to access image bits and manipulate them into binary 1s and 0s and store in a long string to be placed inside the cover image. Python also allows for fast development by supporting both interpreting and compiling in its implementation and allows me to create executables with PyInstaller for better distribution between the user and the user’s recipient.

## Modelling

To test the use of different significant bits in embedding media, I used my program to create two versions of the same image with a message embedded, one using the most significant bit (bad) and one using the LSB (good). Noticeable distoration is present on figure 3. 

![Image quality investigation](https://user-images.githubusercontent.com/49583764/90334467-b8312000-dfc5-11ea-80bb-2a48ae827d93.png)

## Libraries

tkinter – Providing a user interface for user input, output strings and provide a menu to locate files and providing message boxes (.messagebox) for warnings and file dialogs (.filedialog) for retrieving the path for saving stego-images.

Pillow (PIL fork) – Generates a table of pixels for the cover image consisting of tuples for each colour plane within each pixel and extracting image information such as dimensions.

NumPy – Extract all pixels out of an image in binary and converting binary back into an image.

Random – To create seeds for pseudo-randomness and shuffle messages and pixel bits for embedding and extracting.

Datetime – Gets current date for use in cover image watermark.

OS – To retrieve the current directory path name where the program resides, getting the file size of media and extracting the extension from a directory

Time – Delay messages to user before startup message reappears.

## Key code

    shuffled_indices = self.ordering(this)
    
    for bit in range(len(this.final_bits)):
    
	    x = shuffled_indices[bit] % this.width
    
	    y = shuffled_indices[bit] // this.width
    
	    p = format(this.pixels[x, y][this.plane], 'b').zfill(8)
    
	    if p[this.sig_bit] == '0' and this.final_bits[bit] == '1':
    
		    this.pixels[x, y] = self.modify_pixel(this, this.pixels[x, y], 1)
    
	    elif this.final_bits[bit] == '0':
    
		    this.pixels[x, y] = self.modify_pixel(this, this.pixels[x, y], 0)
    
    if os.path.splitext(this.save_path)[1].find("tif"):
    
	    this.cover_image.save(this.save_path, format="tiff", compression="None")
    
    else:
    
    this.cover_image.save(this.save_path, compression="None")

This code is the algorithm which embeds the binary representation of the media in the coordinated pseudo-randomly generated indices. Firstly the indices are generated using the key containing digits of 0 to the number of pixels. The finalised media (with added length and if needed, converted to binary, and watermark added) is then looped through using the for loop. The next 3 lines finds the x and y coordinate of each pixel in shuffled indices and checks if the significant bit in the specified colour plane is equal to the selected bit in the media bits. If not then the bit is changed to match the media bit using the modify pixel method.


    shuffled_indices = self.ordering(this)
    
    extracted_bits = ""
    
    for index in shuffled_indices:
    
    	x = index % this.width
    
    	y = index // this.width
    
    	p = format(this.pixels[x, y][this.plane], 'b').zfill(8)
    
    	extracted_bits += p[this.sig_bit]
    
    this.secret_data = this.conversion(extracted_bits)
    
    this.removed_watermark = this.watermark()
    
    if not this.removed_watermark:
    
    	tk.messagebox.showinfo(
    
    	"Invalid cover image",
    
    	"Watermark not present in image, please try another image")
    
    else:
    
    	this.file_handle()

This algorithm enables the extraction of media from the cover image. This is done through firstly generating the same pseudo-randomly shuffled indices through the shared key and finding the x, y coordinates of the selected pixel in the for loop and finding the value of the significant bit in the specified colour plane. This is looped through until the all the required bits are found, validated if the watermark is present, then outputted to the user.
