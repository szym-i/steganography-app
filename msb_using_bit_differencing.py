from custom_chaos_implementation import compare_images
from PIL import Image

def calculate_capacity(image_path):
    try:
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size
        return f"Maximum message size is {((width*height)//8)-1} chars."
    
    except Exception as e:
        raise Exception(f"Error during calculating capacity: {e}")

def embed_message(image_path, message, output_path):
    try:
        # Convert message to bits
        message_bits = ''.join(format(ord(char), '08b') for char in message +'\0' )
        
        # Load image
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size
        
        bit_index = 0  # Message bit index
        
        for y in range(height):
            for x in range(width):
                if bit_index >= len(message_bits):
                    break
                
                r, g, b = pixels[x, y]
                
                # Read 5th and 6th bit
                bit_5 = (r >> 4) & 1
                bit_6 = (r >> 5) & 1
                
                if abs(bit_6 - bit_5) != int(message_bits[bit_index]):
                    if bit_5 == 0:
                        r = r | (1<<4) # Set 5th bit
                    else:
                        r = r & ~ (1<<4) # Clear 5th bit
                
                pixels[x, y] = (r, g, b)

                r, g, b = pixels[x, y]
                bit_index += 1
        
        image.save(output_path)
        compare_images(image_path, output_path)

    except Exception as e:
        raise Exception(f"Error during embeding: {e}")
 
def extract_message(stego_image_path):
    try:
        image = Image.open(stego_image_path)
        pixels = image.load()
        width, height = image.size

        message_bits = []  # List for message bits

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                bit_5 = (r >> 4) & 1
                bit_6 = (r >> 5) & 1
                # Extract message bit
                if bit_6 == bit_5:
                    message_bits.append(0)
                else:
                    message_bits.append(1)

        # Bits to ASCII conversion
        message = ''
        for i in range(0, len(message_bits), 8):
            byte = message_bits[i:i+8]  # Get next 8 bits
            if len(byte) == 8:
                # Convert bits to one ASCII char
                char = chr(int(''.join(map(str, byte)), 2))
                if char == '\0':
                    break
                message += char

        return message
    
    except Exception as e:
        raise Exception(f"Error during extracting: {e}")
