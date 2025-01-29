import cv2
import numpy as np
from custom_chaos_implementation import compare_images

def embed_message(image_path, secret_message, output_path, edge_positions_file):
    try:
        capacity = calculate_capacity_return_number(image_path)

        if (capacity < len(secret_message)):
            raise Exception(f"Couldn't embed {len(secret_message)} chars in the image. Max capacity is: {capacity}.")

        # Add end of message character
        secret_message += '\0' 

        # Step 1: Read the color image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("Image not found at the specified path.")

        # Step 2: Split into RGB components
        blue, green, red = cv2.split(image)

        # Step 3: Convert secret message to binary
        message_bits = ''.join([f'{ord(c):08b}' for c in secret_message])
        message_length = len(message_bits)
        
        # Step 4: Dynamically adjust threshold to find required number of edges; start from highest value
        threshold = 1.0 
        edges = None
        edge_positions = []

        # Gradually decrease threshold until required number of edges is found
        while threshold > 0:
            current_threshold = int(threshold * 255)
            edges = cv2.Canny(red, threshold1=current_threshold, threshold2=current_threshold * 2)
            edge_positions = np.column_stack(np.where(edges != 0)) 
            
            # Check whether enough edges to hide message
            if len(edge_positions) >= message_length:
                break
            
            threshold -= 0.01

        edge_count = len(edge_positions)
        
        # Save number of edge positions to the specified file to be able to properly extract
        with open(edge_positions_file, 'w') as f:
            f.write(str(edge_count))

        # Step 5: Embed the bits of the secret message in the LSB of the green component at edge positions
        for i, bit in enumerate(message_bits):
            row, col = edge_positions[i]
            green[row, col] = (green[row, col] & 0xFE) | int(bit)

        # Step 6: Merge the components (Blue, Green, Red) into the stego image
        stego_image = cv2.merge((blue, green, red))
        
        cv2.imwrite(output_path, stego_image)
        compare_images(image_path, output_path)

    except Exception as e:
        raise Exception(f"Error during embeding: {e}")

def extract_message(stego_image_path, edge_positions_file):
    try:
        # Step 1: Read the edge positions count from the file
        with open(edge_positions_file, 'r') as f:
            edge_positions_count = int(f.read().strip())
        
        # Step 2: Read the stego image and split into RGB components
        stego_image = cv2.imread(stego_image_path)
        if stego_image is None:
            raise FileNotFoundError("Stego image not found at the specified path.")

        blue, green, red = cv2.split(stego_image)

        # Step 3: Start from the highest threshold and decrease until proper number of edges achieved
        threshold = 1.0
        extracted_bits = []

        while threshold > 0:
            current_threshold = int(threshold * 255)
            edges = cv2.Canny(red, threshold1=current_threshold, threshold2=current_threshold * 2)
            edge_positions = np.column_stack(np.where(edges != 0))
            
            # Check if proper number of edges achieved
            if len(edge_positions) == edge_positions_count:
                break
            
            threshold -= 0.01
            if threshold <= 0:
                raise ValueError("Cannot match edge positions with the required count.")

        # Step 4: Extract bits from the LSB of the green component at edge positions
        for i in range(edge_positions_count):
            row, col = edge_positions[i]
            bit = green[row, col] & 0x01
            extracted_bits.append(str(bit))
            
            # Check for end of message
            if len(extracted_bits) >= 8:
                last_byte = ''.join(extracted_bits[-8:])
                if last_byte == '00000000':
                    break

        # Step 5: Combine bits into the secret message
        message_chars = [chr(int(''.join(extracted_bits[i:i + 8]), 2)) for i in range(0, len(extracted_bits), 8)]
        secret_message = ''.join(message_chars).rstrip('\0')  # Remove newline character
        return secret_message
    
    except Exception as e:
        raise Exception(f"Error during extracting: {e}")

def calculate_capacity_return_number(image_path):
    try:   
        # Step 1: Read the color image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("Image not found at the specified path.")

        # Step 2: Split into RGB components (using only the green channel as used for hiding)
        blue, green, red = cv2.split(image)

        # Step 3: Use min threshold as it matches to the max capacity
        min_threshold = 0.01
        scaled_threshold = int(min_threshold * 255)

        edges = cv2.Canny(green, threshold1=scaled_threshold, threshold2=2 * scaled_threshold)
            
        # Step 4: Calculate the number of edge positions
        edge_positions = np.column_stack(np.where(edges != 0))
        capacity = len(edge_positions)//8 - 1 # Each edge pixel can hold 1 bit; -1 byte because of end message indicator

        return capacity
    
    except Exception as e:
        raise Exception(f"Error during calculating capacity: {e}")


def calculate_capacity(image_path):
    capacity = calculate_capacity_return_number(image_path)

    return f"Maximum capacity for embedding: {capacity} chars (it's for min threshold=0.01)"