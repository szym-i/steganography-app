from custom_chaos_implementation import compare_images
from PIL import Image

def calculate_capacity_return_number(image_path):
    try:
        image = Image.open(image_path)
        width, height = image.size
        capacity = (((width*height*8)//8)-1)
        return capacity
    except Exception as e:
        raise Exception(f"Error during calculating capacity: {e}")

def calculate_capacity(image_path):
    capacity = calculate_capacity_return_number(image_path)
    return f"Maximum message size is {capacity} chars."

def embed_message(image_path, secret_message, output_path):
    try:
        capacity = calculate_capacity_return_number(image_path)

        if (capacity < len(secret_message)):
            raise Exception(f"Couldn't embed {len(secret_message)} chars in the image. Max capacity is: {capacity}.")

        # Step 1: Convert message to bits
        message_bits = ''.join(format(ord(char), '08b') for char in secret_message + '\0')

        # Step 2: Load image
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size

        bit_index = 0

        # Step 3: LSB 2-2-4
        for y in range(height):
            for x in range(width):
                if bit_index >= len(message_bits):
                    break
                
                r, g, b = pixels[x, y]

                # Change 2 LSB for R
                if bit_index + 2 <= len(message_bits):
                    r = (r & ~3) | int(message_bits[bit_index:bit_index + 2], 2)
                    bit_index += 2

                # Change 2 LSB for G
                if bit_index + 2 <= len(message_bits):
                    g = (g & ~3) | int(message_bits[bit_index:bit_index + 2], 2)
                    bit_index += 2

                # Change 4 LSB for B
                if bit_index + 4 <= len(message_bits):
                    b = (b & ~15) | int(message_bits[bit_index:bit_index + 4], 2)
                    bit_index += 4

                pixels[x, y] = (r, g, b)

        image.save(output_path)

        compare_images(image_path, output_path)

    except Exception as e:
        raise Exception(f"Error during embeding: {e}")

def extract_message(image_path):
    try:
        # Step 1: Load image
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size

        binary_message = ''

        # Step 2: Iterate through pixels LSB 2-2-4
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                # Take 2 LSB from R
                binary_message += format(r & 3, '02b')
                # Take 2 LSB from G
                binary_message += format(g & 3, '02b')
                # Take 4 LSB from B
                binary_message += format(b & 15, '04b')

        # Step 3: Convert Bits to ASCII
        decoded_message = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]  
            if len(byte) == 8:
                decoded_message += chr(int(byte, 2))

                # Check for end of message
                if decoded_message[-1:] == '\0': 
                    return decoded_message[:-1]

        return decoded_message
    
    except Exception as e:
        raise Exception(f"Error during extracting: {e}")