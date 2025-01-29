from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def calculate_capacity(image_path):
    image = Image.open(image_path)
    points = henon_map(image.size, a=1.4, b=0.3, x0=0.1, y0=0.3)
    return f"Maximum message size is {(len(points)//8)-1} chars. (remember about time-limitation)"

def henon_map(image_size, a=1.4, b=0.3, x0=0.1, y0=0.3):
    x, y = x0, y0
    points = set()
    normalized_points = []

    attempts = 0
    width, height = image_size
    while attempts < width * height:
        # Generate Henon's points
        x_new = 1 - a * x**2 + y
        y_new = b * x
        x, y = x_new, y_new

        # Normalize points to image resolution
        x_norm = int((x + 1.5) * (width // 3)) % width
        y_norm = int((y + 1.5) * (height // 3)) % height

        # Add only unique points to list
        if (x_norm, y_norm) not in points:
            points.add((x_norm, y_norm))
            normalized_points.append((x_norm, y_norm))

        attempts += 1

    return normalized_points


def plot_henon(points):
    if not points:
        print("No points to plot.")
        return
    x_vals, y_vals = zip(*points)
    plt.figure(figsize=(8, 6))
    plt.plot(x_vals, y_vals, 'o', markersize=1)
    plt.title('Henon\'s Trajectory')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid()
    plt.show()

def embed_message(cover_image_path, secret_message, output_path, a=1.4, b=0.3, x0=0.1, y0=0.3):
    image = Image.open(cover_image_path)
    pixels = np.array(image)

    secret_bits = ''.join(format(ord(char), '08b') for char in secret_message + '\0')

    points = henon_map(image.size, a, b, x0, y0)
    
    if len(points) < len(secret_bits):
        raise Exception(f"Could not embed secret message ({len(secret_message)} chars). Max capacity is {len(points)//8} chars.")
    
    plot_henon(points)

    for i in range(len(secret_bits)):
        x, y = points[i]

        r, g, b = pixels[y, x]
        b = (b & 0b11111110) | int(secret_bits[i])  # modify LSB for Blue
        pixels[y, x] = (r, g, b)

    stego_image = Image.fromarray(pixels)
    stego_image.save(output_path)
    
    compare_images(cover_image_path, output_path)

def extract_message(stego_image_path, a=1.4, b=0.3, x0=0.1, y0=0.3):
    image = Image.open(stego_image_path)
    pixels = np.array(image)

    points = henon_map(image.size, a, b, x0, y0)

    bits = []
    for i in range(len(points)):
        x, y = points[i]

        _, _, b = pixels[y, x]
        bits.append(str(b & 1))

        if len(bits) >= 8 and ''.join(bits[-8:]) == '00000000':
            break

    secret_bits = ''.join(bits)
    message = ''.join(chr(int(secret_bits[i:i+8], 2)) for i in range(0, len(secret_bits) - 8, 8))

    return message

def compare_images(image_path1, image_path2):
    image1 = Image.open(image_path1)
    image2 = Image.open(image_path2)

    if image1.size != image2.size:
        raise ValueError("Images need to be same size.")
    
    # Convert images to  NumPy arrays
    pixels1 = np.array(image1)
    pixels2 = np.array(image2)

    differences = np.bitwise_xor(pixels1, pixels2)
    bit_differences = np.unpackbits(differences, axis=-1).sum()
    
    plt.figure(figsize=(8, 8))
    plt.imshow(differences.any(axis=-1), cmap='gray')
    plt.title("Pixels difference between images")
    
    plt.text(10, 10, f"Different bits: {bit_differences} (some might have matched before embedding data).", 
             color='red', fontsize=12, bbox=dict(facecolor='white', alpha=0.7))
    
    plt.show()
