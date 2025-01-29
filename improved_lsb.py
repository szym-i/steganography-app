from custom_chaos_implementation import compare_images
from PIL import Image
import os
from cryptography.fernet import Fernet
import json

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
    return f"Maximum message size is less than {capacity} chars\n(doesn't take encoding into consideration, actual capacity is lower)."

# Set LSB bit
def set_lsb(value, bit):
    return (value & ~1) | bit

# Generate key
def generate_key():
    return Fernet.generate_key()

# Encrypt message
def encrypt_message(message, secret_key):
    fernet = Fernet(secret_key)
    encrypted_message = fernet.encrypt(message.encode())
    return encrypted_message

# Decrypt message
def decrypt_message(encrypted_message, secret_key):
    fernet = Fernet(secret_key)
    decrypted_message = fernet.decrypt(encrypted_message).decode()
    return decrypted_message

# Convert text to bits
def text_to_bits(text):
    bits = ''.join(format(ord(char), '08b') for char in text)
    return bits

# Convert bits to text
def bits_to_text(bits):
    chars = [chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)

# Expand key to fit the message's length
def extend_secret_key(secret_key, target_length):
    secret_key_bits = text_to_bits(secret_key)
    extended_key = (secret_key_bits * ((target_length // len(secret_key_bits)) + 1))[:target_length]
    return extended_key

# Save key to a file
def save_key(secret_key, key_file_path):
    metadata = {
        'secret_key': secret_key.decode(),
    }
    with open(key_file_path, 'w') as key_file:
        json.dump(metadata, key_file)

# Load key from a file
def load_key(key_file_path):
    if not os.path.exists(key_file_path):
        raise FileNotFoundError(f"Key file {key_file_path} not found.")
    
    with open(key_file_path, 'r') as key_file:
        metadata = json.load(key_file)
        secret_key = metadata['secret_key'].encode()
        return secret_key

def embed_message(image_path, message, output_path, key_file_path):
    try:
        capacity = calculate_capacity_return_number(image_path)

        if (capacity < len(message)):
            raise Exception(f"Couldn't embed {len(message)} chars in the image. Max capacity is: {capacity}.")
        
        # Step 1: Generate key
        secret_key = generate_key()
        
        # Step 2: Load image
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size

        # Step 3: Encrypt message
        encrypted_message = encrypt_message(message, secret_key)

        message_bits = text_to_bits(encrypted_message.decode() + '\0')

        secret_key_bits = extend_secret_key(secret_key.decode(), len(message_bits))

        message_index = 0
        message_length = len(message_bits)

        # Step 4: LSB
        for y in range(height):
            for x in range(width):
                if message_index >= message_length:
                    break

                r, g, b = pixels[x, y]

                # XOR key bit with Red
                xor_value = int(secret_key_bits[message_index]) ^ (r & 1)

                # If XOR value 1, then LSB with B
                if xor_value == 1:
                    b = set_lsb(b, int(message_bits[message_index]))
                # If XOR value 0, then LSB with G
                else:
                    g = set_lsb(g, int(message_bits[message_index]))

                pixels[x, y] = (r, g, b)

                message_index += 1

        image.save(output_path)

        # Step 4: Save key to a file
        save_key(secret_key, key_file_path)

        compare_images(image_path, output_path)

    except Exception as e:
        raise Exception(f"Error during embeding: {e}")

def extract_message(stego_image_path, key_file_path):
    try:
        # Step 1: Load image
        image = Image.open(stego_image_path)
        pixels = image.load()
        width, height = image.size

        # Step 2: Load key
        secret_key = load_key(key_file_path)

        binary_message = []

        # Step 3: LSB
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                xor_value = int(extend_secret_key(secret_key.decode(), len(binary_message) + 1)[len(binary_message)]) ^ (r & 1)

                # If XOR value 1, then take LSB from B
                if xor_value == 1:
                    binary_message.append(str(b & 1))
                # If XOR value 0, then take LSB from G
                else:
                    binary_message.append(str(g & 1))

                # Check for end of message
                if len(binary_message) % 8 == 0:
                    extracted_text = bits_to_text(''.join(binary_message))
                    if '\0' in extracted_text:
                        extracted_text = extracted_text.split('\0')[0]
                        decrypted_message = decrypt_message(extracted_text.encode(), secret_key)
                        return decrypted_message

    except Exception as e:
        raise Exception(f"Error during extracting: {e}")