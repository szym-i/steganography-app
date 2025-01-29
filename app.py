import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import custom_chaos_implementation as chaos
import edges as edges
import emphasize_blue_lsb as blue_lsb
import improved_lsb as impr_lsb
import msb_using_bit_differencing as msb
import rdh_grayscale as rdh
import standard_lsb as stand_lsb

def display_message_window(message):
    message_window = tk.Toplevel()
    message_window.title("Message view")
    message_window.geometry("1920x1080")

    # Add a Scrollbar
    scrollbar = tk.Scrollbar(message_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(message_window, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text_widget.pack(expand=True, fill=tk.BOTH)

    text_widget.insert(tk.END, message)
    text_widget.config(state=tk.DISABLED)

    # Connect the scrollbar to the text widget
    scrollbar.config(command=text_widget.yview)

def show_help():
    help_text = (
        "1. RDH (grayscale)\n"
        "   - **Hide:** Enter the message to be hidden. Requires an input file (image). Saves metadata JSON file and stego image to provided directory.\n"
        "   - **Extract:** Requires an input file (image) and a metadata JSON file to read the message.\n"
        "   - **Description:** Histogram shift-based Reversible Data Hiding (RDH) leverages the statistical characteristics of the image itself. The pixel with the highest frequency in the histogram is selected as the information carrier.\n\n"
        "2. Standard LSB\n"
        "   - **Hide:** Enter the message to be hidden. Requires an input file (image). Saves stego image to provided directory.\n"
        "   - **Extract:** Requires an input file (image) to read the message.\n"
        "   - **Description:** Least Significant Bit (LSB) is a steganographic technique used to embed data into digital media by modifying the least significant bits of pixel values, which minimally alters the image and is imperceptible to the human eye.\n\n"
        "3. Improved LSB\n"
        "   - **Hide:** Enter the message to be hidden. Requires an input file (image). Saves key file and stego image to provided directory.\n"
        "   - **Extract:** Requires an input file (image) and a key file to read the message.\n"
        "   - **Description:** Characteristic is similar to the standard LSB technique, but the embedding process involves encoding the message using AES encryption. This adds an extra layer of security, ensuring the hidden information is protected even if the cover image is analyzed.\n\n"
        "4. Emphasize Blue LSB\n"
        "   - **Hide:** Enter the message to be hidden. Requires an input file (image). Saves stego image to provided directory.\n"
        "   - **Extract:** Requires an input file (image) to read the message.\n"
        "   - **Description:** Characteristic is similar to the standard LSB technique, but more data is hidden in the Blue channel, as it is proven that the human eye is less sensitive to changes in this spectrum. In summary, data is embedded into 2 LSBs for the Red and Green channels, and 4 LSBs for the Blue channel.\n\n"
        "5. MSB using bit differencing\n"
        "   - **Hide:** Enter the message to be hidden. Requires an input file (image). Saves stego image to provided directory.\n"
        "   - **Extract:** Requires an input file (image) to read the message.\n"
        "   - **Description:** MSB method operates by calculating the difference between the 6th and 5th bits of each pixel. Depending on the result of this calculation compared to the bit of the message to be hidden, the 5th bit is either left unchanged or modified to match the message bit.\n\n"
        "6. Edges\n"
        "   - **Hide:** Enter the message to be hidden. Requires an input file (image). Saves edge positions file and stego image to provided directory.\n"
        "   - **Extract:** Requires an input file (image) and an edge positions file to read the message.\n"
        "   - **Description:** Edge-based hiding involves embedding data in areas where the gradient falls within a specified threshold. If more data needs to be hidden, the threshold is reduced to allow for embedding additional bits.\n\n"
        "7. Custom Chaos implementation using Henon's algorithm\n"
        "   - **Hide:** Enter the message to be hidden. Requires a cover image.\n"
        "   - **Extract:** Requires a stego image to read the message.\n"
        "   - **Description:** Custom chaos implementation involves generating a point map using the Henon algorithm, normalizing it to fit the dimensions of the image, and embedding the message in the corresponding pixels using the LSB technique."
    )
    display_message_window(help_text)

def load_message_from_file():
    """Loads a message from a .txt file and inserts it into the entry field."""
    filepath = filedialog.askopenfilename(
        title="Choose text file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                message = file.read()
            entry.delete(0, tk.END)
            entry.insert(0, message)
            display_message_window(message)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load message from file: {e}")

def embed_message(method, message=None):
    filepath = image_label.cget("text")
    if "No file chosen." in filepath:
        messagebox.showwarning("No file chosen.", "Please choose a file before running the script.")
        return

    output_filepath = filedialog.asksaveasfilename(
        title="Save stego file",
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
    )
    if not output_filepath:
        return  # If user cancels the save dialog, do nothing

    try:
        if method == "rdh":
            extra_argument_filepath = filedialog.asksaveasfilename(
                title="Save metadata file",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            rdh.embed_message(filepath, message, output_filepath, extra_argument_filepath)
        elif method == "standard_lsb":
            stand_lsb.embed_message(filepath, message, output_filepath)
        elif method == "improved_lsb":
            extra_argument_filepath = filedialog.asksaveasfilename(
                title="Save key file",
                defaultextension=".key",
                filetypes=[("Key files", "*.key"), ("All files", "*.*")]
            )
            impr_lsb.embed_message(filepath, message, output_filepath, extra_argument_filepath)
        elif method == "emphasize_blue_lsb":
            blue_lsb.embed_message(filepath, message, output_filepath)
        elif method == "msb":
            msb.embed_message(filepath, message, output_filepath)
        elif method == "edges":
            extra_argument_filepath = filedialog.asksaveasfilename(
                title="Save edge positions file",
                defaultextension=".txt",
                filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
            )
            edges.embed_message(filepath, message, output_filepath, extra_argument_filepath)
        elif method == "chaos":
            chaos.embed_message(filepath, message, output_filepath)

        entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Message successfully hidden.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while hiding the message: {e}")

def extract_message(method):
    filepath = image_label.cget("text")
    if "No file chosen." in filepath:
        messagebox.showwarning("No file chosen.", "Please choose a file before running the script.")
        return
    try:
        if method == "rdh":
            extra_argument_filepath = filedialog.askopenfilename(
                title="Choose metadata file",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            message = rdh.extract_message(filepath, extra_argument_filepath)
        elif method == "standard_lsb":
            message = stand_lsb.extract_message(filepath)
        elif method == "improved_lsb":
            extra_argument_filepath = filedialog.askopenfilename(
                title="Choose key file",
                filetypes=[("Key files", "*.key"), ("All files", "*.*")]
            )
            message = impr_lsb.extract_message(filepath, extra_argument_filepath)
        elif method == "emphasize_blue_lsb":
            message = blue_lsb.extract_message(filepath)
        elif method == "msb":
            message = msb.extract_message(filepath)
        elif method == "edges":
            extra_argument_filepath = filedialog.askopenfilename(
                title="Choose edge positions file",
                defaultextension=".txt",
                filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
            )
            message = edges.extract_message(filepath, extra_argument_filepath)
        elif method == "chaos":
            message = chaos.extract_message(filepath)

        display_message_window(message)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while extracting the message: {e}")

def calculate_capacity(method):
    filepath = image_label.cget("text")
    if "No file chosen." in filepath:
        messagebox.showwarning("No file chosen.", "Please choose a file before running the script.")
        return
    try:
        if method == "rdh":
            capacity = rdh.calculate_capacity(filepath)
            rdh_label_result.config(text=capacity)
        elif method == "standard_lsb":
            capacity = stand_lsb.calculate_capacity(filepath)
            standard_lsb_label_result.config(text=capacity)
        elif method == "improved_lsb":
            capacity = impr_lsb.calculate_capacity(filepath)
            improved_lsb_label_result.config(text=capacity)
        elif method == "emphasize_blue_lsb":
            capacity = blue_lsb.calculate_capacity(filepath)
            emphasize_blue_lsb_label_result.config(text=capacity)
        elif method == "msb":
            capacity = msb.calculate_capacity(filepath)
            msb_label_result.config(text=capacity)
        elif method == "edges":
            capacity = edges.calculate_capacity(filepath)
            edges_label_result.config(text=capacity)
        elif method == "chaos":
            capacity = chaos.calculate_capacity(filepath)
            custom_chaos_label_result.config(text=capacity)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while calculating capacity: {e}")

def choose_file():
    filepath = filedialog.askopenfilename(
        title="Choose cover image", 
        filetypes=[("Image files", ".png .jpg .jpeg .bmp .gif"), ("All files", "*.*")]
    )
    if filepath:
        image_label.config(text=f"{filepath}")

        # Clear capacity calculation results, when pick another image
        clear_results()

        try:
            image = Image.open(filepath)

            max_width = 200
            max_height = 200

            original_width, original_height = image.size
            ratio = min(max_width / original_width, max_height / original_height)

            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)

            tk_image = ImageTk.PhotoImage(resized_image)

            image_label.config(image=tk_image)
            image_label.image = tk_image

        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

def clear_results():
    rdh_label_result.config(text="")
    standard_lsb_label_result.config(text="")
    improved_lsb_label_result.config(text="")
    emphasize_blue_lsb_label_result.config(text="")
    msb_label_result.config(text="")
    edges_label_result.config(text="")
    custom_chaos_label_result.config(text="")

if __name__ == '__main__':
    # Main window
    root = tk.Tk()
    root.title("Stegano app")
    root.geometry("1920x1080")

    # Label
    label = tk.Label(root, text="Enter message to be hidden")
    label.pack(pady=10)

    # Entry for the message
    entry = tk.Entry(root)
    entry.pack(pady=5)

    # Choose file button
    choose_file_button = tk.Button(root, text="Choose file", command=choose_file)
    choose_file_button.pack(pady=10)

    # Button to load message from a text file
    load_text_button = tk.Button(root, text="Load message from file", command=lambda: load_message_from_file())
    load_text_button.pack(pady=5)

    # Filename label
    image_label = tk.Label(root, text="No file chosen.")
    image_label.pack(pady=10)

    # Help button
    help_button = tk.Button(root, text="Help", command=show_help)
    help_button.pack(pady=10)

    # Frame for methods 1, 2, 3, 4
    first_frame = tk.Frame(root)
    first_frame.pack(pady=10)

    # Frame for 1. RDH (grayscale) method
    frame_rdh = tk.Frame(first_frame, borderwidth=2, relief="groove")
    frame_rdh.pack(side='left', pady=10, padx=10, fill="both")

    label_rdh = tk.Label(frame_rdh, text="1. RDH (grayscale)")
    label_rdh.grid(row=0, column=0, columnspan=2, pady=5)
    
    button_rdh_hide = tk.Button(frame_rdh, text="Hide", command=lambda: embed_message("rdh", entry.get()))
    button_rdh_hide.grid(row=1, column=0, padx=10, pady=5)

    button_rdh_extract = tk.Button(frame_rdh, text="Extract", command=lambda: extract_message("rdh"))
    button_rdh_extract.grid(row=1, column=1, padx=10, pady=5)

    button_rdh_calculate_capacity = tk.Button(frame_rdh, text="Calculate image capacity", command=lambda: calculate_capacity("rdh"))
    button_rdh_calculate_capacity.grid(row=2, column=0, columnspan=2, pady=5)
    rdh_label_result = tk.Label(frame_rdh, text="")
    rdh_label_result.grid(row=3, column=0, columnspan=2, pady=5)

    frame_rdh.grid_columnconfigure(0, weight=1)
    frame_rdh.grid_columnconfigure(1, weight=1)

    # Frame for 2. Standard LSB method
    frame_standard_lsb = tk.Frame(first_frame, borderwidth=2, relief="groove")
    frame_standard_lsb.pack(side='left', pady=10, padx=10, fill="both")

    label_standard_lsb = tk.Label(frame_standard_lsb, text="2. Standard LSB")
    label_standard_lsb.grid(row=0, column=0, columnspan=2, pady=5)

    button_standard_lsb_hide = tk.Button(frame_standard_lsb, text="Hide", command=lambda: embed_message("standard_lsb", entry.get()))
    button_standard_lsb_hide.grid(row=1, column=0, padx=10, pady=5)

    button_standard_lsb_extract = tk.Button(frame_standard_lsb, text="Extract", command=lambda: extract_message("standard_lsb"))
    button_standard_lsb_extract.grid(row=1, column=1, padx=10, pady=5)

    button_standard_lsb_calculate_capacity = tk.Button(frame_standard_lsb, text="Calculate image capacity", command=lambda: calculate_capacity("standard_lsb"))
    button_standard_lsb_calculate_capacity.grid(row=2, column=0, columnspan=2, pady=5)
    standard_lsb_label_result = tk.Label(frame_standard_lsb, text="")
    standard_lsb_label_result.grid(row=3, column=0, columnspan=2, pady=5)

    frame_standard_lsb.grid_columnconfigure(0, weight=1)
    frame_standard_lsb.grid_columnconfigure(1, weight=1)

    # Frame for 3. Improved LSB method
    frame_improved_lsb = tk.Frame(first_frame, borderwidth=2, relief="groove")
    frame_improved_lsb.pack(side='left', pady=10, padx=10, fill="both")

    label_improved_lsb = tk.Label(frame_improved_lsb, text="3. Improved LSB")
    label_improved_lsb.grid(row=0, column=0, columnspan=2, pady=5)

    button_improved_lsb_hide = tk.Button(frame_improved_lsb, text="Hide", command=lambda: embed_message("improved_lsb", entry.get()))
    button_improved_lsb_hide.grid(row=1, column=0, padx=10, pady=5)

    button_improved_lsb_extract = tk.Button(frame_improved_lsb, text="Extract", command=lambda: extract_message("improved_lsb"))
    button_improved_lsb_extract.grid(row=1, column=1, padx=10, pady=5)

    button_improved_lsb_calculate_capacity = tk.Button(frame_improved_lsb, text="Calculate image capacity", command=lambda: calculate_capacity("improved_lsb"))
    button_improved_lsb_calculate_capacity.grid(row=2, column=0, columnspan=2, pady=5)
    improved_lsb_label_result = tk.Label(frame_improved_lsb, text="")
    improved_lsb_label_result.grid(row=3, column=0, columnspan=2, pady=5)

    frame_improved_lsb.grid_columnconfigure(0, weight=1)
    frame_improved_lsb.grid_columnconfigure(1, weight=1)

    # Frame for 4. Emphasize blue LSB method
    frame_emphasize_blue_lsb = tk.Frame(first_frame, borderwidth=2, relief="groove")
    frame_emphasize_blue_lsb.pack(side='left', pady=10, padx=10, fill="both")

    label_emphasize_blue_lsb = tk.Label(frame_emphasize_blue_lsb, text="4. Emphasize Blue LSB")
    label_emphasize_blue_lsb.grid(row=0, column=0, columnspan=2, pady=5)

    button_emphasize_blue_lsb_hide = tk.Button(frame_emphasize_blue_lsb, text="Hide", command=lambda: embed_message("emphasize_blue_lsb", entry.get()))
    button_emphasize_blue_lsb_hide.grid(row=1, column=0, padx=10, pady=5)

    button_emphasize_blue_lsb_extract = tk.Button(frame_emphasize_blue_lsb, text="Extract", command=lambda: extract_message("emphasize_blue_lsb"))
    button_emphasize_blue_lsb_extract.grid(row=1, column=1, padx=10, pady=5)

    button_emphasize_blue_lsb_calculate_capacity = tk.Button(frame_emphasize_blue_lsb, text="Calculate image capacity", command=lambda: calculate_capacity("emphasize_blue_lsb"))
    button_emphasize_blue_lsb_calculate_capacity.grid(row=2, column=0, columnspan=2, pady=5)
    emphasize_blue_lsb_label_result = tk.Label(frame_emphasize_blue_lsb, text="")
    emphasize_blue_lsb_label_result.grid(row=3, column=0, columnspan=2, pady=5)

    frame_emphasize_blue_lsb.grid_columnconfigure(0, weight=1)
    frame_emphasize_blue_lsb.grid_columnconfigure(1, weight=1)

    # Frame for methods 5, 6, 7
    second_frame = tk.Frame(root)
    second_frame.pack(pady=10)

    # Frame for 5. MSB using bit differencing method
    frame_msb_bit_differencing = tk.Frame(second_frame, borderwidth=2, relief="groove")
    frame_msb_bit_differencing.pack(side='left', pady=10, padx=10, fill="both")

    label_msb_bit_differencing = tk.Label(frame_msb_bit_differencing, text="5. MSB using bit differencing")
    label_msb_bit_differencing.grid(row=0, column=0, columnspan=2, pady=5)

    button_msb_bit_differencing_hide = tk.Button(frame_msb_bit_differencing, text="Hide", command=lambda: embed_message("msb", entry.get()))
    button_msb_bit_differencing_hide.grid(row=1, column=0, padx=10, pady=5)

    button_msb_bit_differencing_extract = tk.Button(frame_msb_bit_differencing, text="Extract", command=lambda: extract_message("msb"))
    button_msb_bit_differencing_extract.grid(row=1, column=1, padx=10, pady=5)

    button_msb_calculate_capacity = tk.Button(frame_msb_bit_differencing, text="Calculate image capacity", command=lambda: calculate_capacity("msb"))
    button_msb_calculate_capacity.grid(row=2, column=0, columnspan=2, pady=5)
    msb_label_result = tk.Label(frame_msb_bit_differencing, text="")
    msb_label_result.grid(row=3, column=0, columnspan=2, pady=5)

    frame_msb_bit_differencing.grid_columnconfigure(0, weight=1)
    frame_msb_bit_differencing.grid_columnconfigure(1, weight=1)

    # Frame for 6. Edges
    frame_edges = tk.Frame(second_frame, borderwidth=2, relief="groove")
    frame_edges.pack(side='left', pady=10, padx=10, fill="both")

    label_edges = tk.Label(frame_edges, text="6. Edges")
    label_edges.grid(row=0, column=0, columnspan=2, pady=5)

    button_edges_hide = tk.Button(frame_edges, text="Hide", command=lambda: embed_message("edges", entry.get()))
    button_edges_hide.grid(row=1, column=0, padx=10, pady=5)

    button_edges_extract = tk.Button(frame_edges, text="Extract", command=lambda: extract_message("edges"))
    button_edges_extract.grid(row=1, column=1, padx=10, pady=5)

    button_edges_capacity = tk.Button(frame_edges, text="Calculate image capacity", command=lambda: calculate_capacity("edges"))
    button_edges_capacity.grid(row=2, column=0, columnspan=2, pady=5)
    edges_label_result = tk.Label(frame_edges, text="")
    edges_label_result.grid(row=3, column=0, columnspan=2, pady=5)

    frame_edges.grid_columnconfigure(0, weight=1)
    frame_edges.grid_columnconfigure(1, weight=1)

    # Frame for 7. Custom chaos implementation using Henon Algorithm
    frame_custom_chaos = tk.Frame(second_frame , borderwidth=2, relief="groove")
    frame_custom_chaos.pack(side='left', pady=10, padx=10, fill="both")

    label_custom_chaos = tk.Label(frame_custom_chaos, text="7. Custom chaos implementation using Henon algorithm")
    label_custom_chaos.grid(row=0, column=0, columnspan=2, pady=5)

    button_custom_chaos_hide = tk.Button(frame_custom_chaos, text="Hide", command=lambda: embed_message("chaos", entry.get()))
    button_custom_chaos_hide.grid(row=1, column=0, padx=10, pady=5)

    button_custom_chaos_extract = tk.Button(frame_custom_chaos, text="Extract", command=lambda: extract_message("chaos"))
    button_custom_chaos_extract.grid(row=1, column=1, padx=10, pady=5)

    button_custom_chaos_calculate_capacity = tk.Button(frame_custom_chaos, text="Calculate image capacity", command=lambda: calculate_capacity("chaos"))
    button_custom_chaos_calculate_capacity.grid(row=2, column=0, columnspan=2, pady=5)
    custom_chaos_label_result = tk.Label(frame_custom_chaos, text="")
    custom_chaos_label_result.grid(row=3, column=0, columnspan=2, pady=5)

    frame_custom_chaos.grid_columnconfigure(0, weight=1)
    frame_custom_chaos.grid_columnconfigure(1, weight=1)

    # Main app loop
    root.mainloop()
