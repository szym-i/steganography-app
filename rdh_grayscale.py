import matplotlib.pyplot as plt
import numpy as np
import logging
import random
import json
import cv2

def calculate_capacity(image_path):
    try:
        possible_message_sizes = []
        for i in range(1000,20,-25):
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            max_message_size = calculate_max_message_length(image, i)//8
            possible_message_sizes.append((i, max_message_size))
            logging.debug(f"For i={i}, max message size is {max_message_size} chars")
        i_max, message_size = max(possible_message_sizes, key=lambda x: x[0] and x[1] > 0)
        return f"Message size is={message_size} chars, achieved for block size={i_max}"
    
    except Exception as e:
        raise Exception(f"Error during calculating capacity: {e}")

def store_extract_data(peak_zero_positions, secret_length, seed, block_size, filename):
    data = {
        "peak_zero_positions": peak_zero_positions,
        "secret_length": secret_length,
        "seed": seed,
        "block_size": block_size
    }
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

    logging.debug(f"Metadata successfully saved to {filename}.")


def read_extract_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    
    peak_zero_positions = data.get("peak_zero_positions", [])
    secret_length = data.get("secret_length", 0)
    seed = data.get("seed", 0)
    block_size = data.get("block_size", 0)

    logging.debug(f"Metadata successfully loaded from {filename}.")
    return peak_zero_positions, secret_length, seed, block_size


def calculate_max_message_length(image, block_size):
    height, width = image.shape
    max_bits = 0

    for row in range(0, height, block_size):
        for col in range(0, width, block_size):
            block = image[row:row + block_size, col:col + block_size]
            hist, _ = np.histogram(block, bins=range(257))

            peak = np.argmax(hist)
            zero = np.where(hist == 0)[0][0] if np.any(hist == 0) else None # Find zero position, if possible

            if zero is not None and peak < zero: # Check if it is possible to hide data in block
                peak_count = hist[peak]
                max_bits += peak_count

    return max_bits


def plot_histogram(block, title):
    hist, bins = np.histogram(block, bins=range(257))
    plt.figure()
    plt.bar(bins[:-1], hist, width=1, edgecolor='black')
    plt.title(title)
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.xlim([0, 255])
    plt.show()


def embed_message(image_path, secret_message, output_path, metadata_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    try:
        possible_message_sizes = []
        for i in range(1000,20,-25):
            max_message_size = calculate_max_message_length(image, i)//8
            possible_message_sizes.append((i, max_message_size))
            logging.debug(f"For i={i}, max message size is {max_message_size} chars")
        block_size, message_size = max(possible_message_sizes, key=lambda x: x[0] and x[1] > 0)
        logging.info(f"Message size is={message_size} chars, achieved for block size={block_size}")
    except Exception as e:
        raise Exception(f"Error during calculating possible: {e}")

    if message_size >= len(secret_message):
        try:
            height, width = image.shape
            # Generate random seed and set it 
            seed = random.randint(0, 10000000)
            random.seed(seed)

            # Generate random bits sequence
            random_sequence = ''.join(format(random.getrandbits(1), 'b') for _ in range(len(secret_message)*8))

            # Convert secret message to bits
            text_bits = ''.join(format(ord(char), '08b') for char in secret_message)
            
            # XOR original text with random bits sequence
            secret_bits = ''.join(str(int(random_sequence[i]) ^ int(text_bits[i])) for i in range(len(text_bits)))
            logging.debug(f"Secret bits:\n{secret_bits}")
            
            max_length_bits = calculate_max_message_length(image, block_size)
            
            if len(secret_bits) > max_length_bits:
                raise ValueError(f"Message is too long to be hidden in the image. Maximum size is {max_length_bits}")

            peak_zero_positions = []
            bit_index = 0  # bit index for message to hide

            for row in range(0, height, block_size):
                for col in range(0, width, block_size):
                    block = image[row:row + block_size, col:col + block_size]
                    hist, _ = np.histogram(block, bins=range(257))
                    # Find peak and zero positions
                    peak = np.argmax(hist)
                    zero = np.where(hist == 0)[0][0] if np.any(hist == 0) else None

                    if zero is not None and peak < zero: # Check if it is possible to hide data in block
                        plot_histogram(block, "Histogram before shift")
                        for i in range(block.shape[0]):
                            for j in range(block.shape[1]):
                                if block[i, j] > peak and block[i, j] < zero:
                                    block[i, j] += 1  # Przesunięcie wartości pikseli w górę, aby zrobić miejsce

                        # Hiding data
                        for i in range(block.shape[0]):
                            for j in range(block.shape[1]):
                                if bit_index >= len(secret_bits):
                                    break
                                if block[i, j] == peak:  # '0' carrier
                                    if secret_bits[bit_index] == '1':
                                        block[i, j] += 1  # Change value to peak+1 for bit '1'
                                    bit_index += 1

                        plot_histogram(block, "Histogram after shift")
                        peak_zero_positions.append((int(peak), int(zero)))
                    else:
                        peak_zero_positions.append(None)

                    image[row:row + block_size, col:col + block_size] = block

                    if bit_index >= len(secret_bits): # Stop when whole message is hidden
                        break

            store_extract_data(peak_zero_positions, len(secret_bits), seed, block_size, metadata_path)
            cv2.imwrite(output_path, image)
            logging.debug(f"Stego image saved to {output_path}")
           
        except Exception as e:
            raise Exception(f"Error during extracting: {e}")
    else:
        raise Exception(f"Message size={message_size} [chars], achieved for block size={block_size} was not sufficient to hide secret data. Secret data size = {len(secret_message)}")

def extract_message(image_path, metadata_file):
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        peak_zero_positions, secret_length, seed, block_size = read_extract_data(metadata_file)

        height, width = image.shape
        extracted_bits = []
        bit_index = 0
        peak_zero_used_index = 0

        # Extract data and restore the original
        for row in range(0, height, block_size):
            for col in range(0, width, block_size):
                if peak_zero_used_index >= len(peak_zero_positions):
                    break  # No more peak/zero data

                peak_zero = peak_zero_positions[peak_zero_used_index]

                if peak_zero is None: # Block was not used for data hiding
                    peak_zero_used_index += 1
                    continue

                peak, zero = peak_zero
                block = image[row:row + block_size, col:col + block_size]

                # Display the histogram before reversing
                plot_histogram(block, "Histogram before reversing shift")

                # Extract hidden data from this block
                for i in range(block.shape[0]):
                    for j in range(block.shape[1]):
                        if bit_index >= secret_length:
                            break
                        if block[i, j] == peak:  # Carrier of '0'
                            extracted_bits.append('0')
                            bit_index += 1
                        elif block[i, j] == peak + 1:  # Carrier of '1'
                            extracted_bits.append('1')
                            bit_index += 1

                # Reverse the histogram shifting for this block
                for i in range(block.shape[0]):
                    for j in range(block.shape[1]):
                        if peak < block[i, j] <= zero: 
                            block[i, j] -= 1
                
                # Display the histogram after reversing
                plot_histogram(block, "Histogram after reversing shift")

                image[row:row + block_size, col:col + block_size] = block
                peak_zero_used_index += 1

                if bit_index >= secret_length:
                    break

        ciphered_sequence = ''.join(extracted_bits)

        # Use seed to generate the random sequence
        random.seed(seed)
        random_sequence = ''.join(format(random.getrandbits(1), 'b') for _ in range(secret_length))

        # XOR the extracted ciphered sequence with the random sequence
        original_bits = ''.join(str(int(ciphered_sequence[i]) ^ int(random_sequence[i])) for i in range(secret_length))

        # Convert the original bits into the original message
        original_message = ''.join(chr(int(original_bits[i:i+8], 2)) for i in range(0, len(original_bits), 8))

        cv2.imwrite("rdh_recovered.png", image)
        logging.debug("Extracted message:", original_message)
        logging.debug("Recovered image saved as 'rdh_recovered.png'")

        return f"{original_message}\n\nReversed image saved to: rdh_recovered.png"

    except Exception as e:
        raise Exception(f"Error during extracting: {e}")
