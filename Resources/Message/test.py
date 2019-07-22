import numpy as np

# File names
in_name = "E:\School\Computer Science\Coursework\Resources\Input\Embed\Stock\stock-image.jpg"
out_name = 'E:\School\square_out.jpg'

# Read data and convert to a list of bits
in_bytes = np.fromfile(in_name, dtype = "uint8")
in_bits = np.unpackbits(in_bytes)
data = list(in_bits)
imageBits = "".join(str(i) for i in data)
imageYO = list(map(int, data))

# Convert the list of bits back to bytes and save
data = list((map(int,list(imageBits))))
out_bits = np.array(data)
out_bytes = np.packbits(out_bits)
out_bytes.tofile(out_name)