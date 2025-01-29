from custom_chaos_implementation import compare_images
from PIL import Image

def calculate_capacity_return_number(image_path):
    try:
        image = Image.open(image_path)
        width, height = image.size
        capacity = (((width*height*3)//8)-1)
        return capacity
    except Exception as e:
        raise Exception(f"Error during calculating capacity: {e}")

def calculate_capacity(image_path):
    capacity = calculate_capacity_return_number(image_path)
    return f"Maximum message size is {capacity} chars."

# Set LSB bit
def set_lsb(value, bit):
    return (value & ~1) | bit

def embed_message(image_path, message, output_path):
    try:
        capacity = calculate_capacity_return_number(image_path)

        if (capacity < len(message)):
            raise Exception(f"Couldn't embed {len(message)} chars in the image. Max capacity is: {capacity}.")

        # Step 1: Convert message to bits
        message_bits = ''.join(format(ord(char), '08b') for char in message + '\0')

        # Step 2: Load image
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size

        bit_index = 0

        # Step 3: LSB
        for y in range(height):
            for x in range(width):
                if bit_index >= len(message_bits):
                    break

                r, g, b = pixels[x, y]

                # Change LSB in R channel
                r = set_lsb(r, int(message_bits[bit_index]))
                bit_index += 1

                # Change LSB in G channel
                if bit_index < len(message_bits):
                    g = set_lsb(g, int(message_bits[bit_index]))
                    bit_index += 1

                # Change LSB in B channel
                if bit_index < len(message_bits):
                    b = set_lsb(b, int(message_bits[bit_index]))
                    bit_index += 1

                pixels[x, y] = (r, g, b)

        image.save(output_path)
        compare_images(image_path, output_path)

    except Exception as e:
        raise Exception(f"Error during embeding: {e}")

def extract_message(stego_image_path):
    try:
        # Step 1: Load image
        image = Image.open(stego_image_path)
        pixels = image.load()
        width, height = image.size

        binary_message = []

        # Step 2: LSB
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                # Read LSB from R, G, B
                binary_message.append(str(r & 1))
                binary_message.append(str(g & 1))
                binary_message.append(str(b & 1))

        # Step 3: Convert bits to ASCII 
        message = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            if len(byte) == 8:
                char = chr(int(''.join(byte), 2))
                # Check for end of message
                if char == '\0':
                    break
                message += char

        return message

    except Exception as e:
        raise Exception(f"Error during extracting: {e}")