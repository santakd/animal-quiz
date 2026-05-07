#!/usr/bin/env python3
"""
array_gen2.py v1.0.8
Animal Quiz - Array Generator Utility 
-------------------------------------
Scans a target directory for image files, strips a specified suffix and extension,
and generates two formatted JavaScript arrays: 
1. array_txt.txt (Plain text array)
2. array_enc.txt (Base64 encrypted/obfuscated array)

This utility is designed to help you easily maintain the list of animals for your quiz by simply managing your image files.
Writes timestamped execution logs to a local /logs directory.

How to use this script
    Prerequisites: Ensure you have Python 3.6+ installed.
    Save the file: Save the code above as array_gen.py in the exact same main folder where your index.html and img folder live.
    Run the program:
    python array_gen.py
    (If your folder is located somewhere else, you can pass the path directly like this: python array_gen.py /path/to/my/custom/img_folder)

What it does automatically:
    Creates a /logs folder if it doesn't exist.
    Writes a timestamped .log file (e.g., array_gen_20231024_153022.log) capturing all debug and info events.
    Scans your img folder, ignores any files that aren't .gif, and elegantly cuts off the " 512" suffix.
    Alphabetizes your animals.
    Generates array_txt.txt containing the exactly formatted, copy-paste-ready string for your HTML file.
    Generates array_enc.txt containing the Base64 encrypted, copy-paste-ready string for your HTML file to prevent cheating.
"""


import os                               # For directory scanning and file handling
import sys                              # For exiting the program and handling command-line arguments
import logging                          # For robust logging of the utility's execution
import argparse                         # For parsing command-line arguments
import base64                           # For Base64 encoding the array elements
from pathlib import Path                # For modern and cross-platform path handling
from datetime import datetime           # For timestamping log files

# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================
# Constants for the program's name and version, used in logging and reference throughout the code
PROGRAM_NAME = "Array Generator Util"   # Name of the utility for logging and reference
PROGRAM_VERSION = "1.0.8"               # Version of the utility for logging and reference

# Change these constants to match your exact file naming conventions
FILE_EXTENSION = ".gif"                 # The file extension to look for (case-insensitive)
FILE_SUFFIX = " 512"                    # The suffix to strip from the filename (case-insensitive)

# Default paths and filenames
DEFAULT_IMG_DIR = "img"                 # default directory to scan for images (relative to the script's location)
OUTPUT_TXT_FILE_NAME = "array_txt.txt"  # constant for the plain text output file
OUTPUT_ENC_FILE_NAME = "array_enc.txt"  # constant for the encrypted output file
LOG_DIR_NAME = "logs"                   # constant for the logs directory    

# Output formatting
ITEMS_PER_LINE = 8                      # How many animal names to print per line in the JS array

# ==========================================
# LOGGING SETUP
# ==========================================
def setup_logging() -> logging.Logger:
    """Configures production-grade logging with timestamped files and console output."""
    log_dir = Path(LOG_DIR_NAME)
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"array_gen_{timestamp}.log"
    
    logger = logging.getLogger("Array_Gen")
    logger.setLevel(logging.DEBUG)
    
    # Formatter for both file and console handlers
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    
    # File Handler with UTF-8 encoding
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    
    # Console Handler for INFO level and above
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

# ==========================================
# CORE PROCESSING LOGIC
# ==========================================
def format_javascript_array(animal_names: list) -> str:
    """Formats a list of strings into a neatly wrapped JavaScript array string."""
    if not animal_names:
        return "const animalNames = [];"
        
    lines = []
    # Chunk the list to make the JS file neat and readable 
    for i in range(0, len(animal_names), ITEMS_PER_LINE):
        chunk = animal_names[i:i + ITEMS_PER_LINE]
        # Wrap each name in quotes and join with commas
        formatted_chunk = ", ".join(f'"{name}"' for name in chunk)
        lines.append(f"            {formatted_chunk}")
        
    array_body = ",\n".join(lines)
    return f"const animalNames = [\n{array_body}\n];"

def format_encrypted_javascript_array(animal_names: list) -> str:
    """Formats a list of strings into a Base64 encrypted JavaScript array string."""
    if not animal_names:
        return "const encryptedAnimalNames = [];"
        
    lines = []
    # Chunk the list to make the JS file neat and readable 
    for i in range(0, len(animal_names), ITEMS_PER_LINE):
        chunk = animal_names[i:i + ITEMS_PER_LINE]
        
        # Base64 encode each name, wrap in quotes, and join with commas
        encoded_chunk = []
        for name in chunk:
            b64_bytes = base64.b64encode(name.encode('utf-8'))
            b64_string = b64_bytes.decode('utf-8')
            encoded_chunk.append(f'"{b64_string}"')
            
        formatted_chunk = ", ".join(encoded_chunk)
        lines.append(f"            {formatted_chunk}")
        
    array_body = ",\n".join(lines)
    return f"const encryptedAnimalNames = [\n{array_body}\n];"

def main():
    # Setup Logger before any processing to capture all events, including errors
    logger = setup_logging()
    logger.info(f"Starting {PROGRAM_NAME} v{PROGRAM_VERSION}")
    
    # Setup Argument Parser with a clear description and default path
    parser = argparse.ArgumentParser(description="Scan an image directory and generate JS array text files.")
    parser.add_argument(
        "path", 
        nargs="?", 
        default=DEFAULT_IMG_DIR, 
        help=f"Path to the image directory. Defaults to '{DEFAULT_IMG_DIR}' in the current directory."
    )
    
    args = parser.parse_args()
    img_dir = Path(args.path)
    
    logger.info(f"Target Image Directory: {img_dir.absolute()}")
    logger.info(f"Looking for files ending in '{FILE_EXTENSION}' and stripping suffix '{FILE_SUFFIX}'")
    
    # 1. Validate Directory Existence and Type
    if not img_dir.exists():
        logger.critical(f"Directory not found: {img_dir.absolute()}")
        logger.critical("Please ensure the directory exists or provide a valid path.")
        sys.exit(1)
        
    if not img_dir.is_dir():
        logger.critical(f"The path provided is a file, not a directory: {img_dir.absolute()}")
        sys.exit(1)

    # 2. Scan and Extract Names
    animal_names = []
    
    try:
        # Iterate through files in the directory and process those that match the criteria
        for file_path in img_dir.iterdir():
            if file_path.is_file():
                filename = file_path.name
                
                # Check for matching extension (case-insensitive for safety)
                if filename.lower().endswith(FILE_EXTENSION.lower()):
                    
                    # Strip extension to get the base name
                    base_name = filename[:-len(FILE_EXTENSION)]
                    
                    # Strip suffix if it exists (also case-insensitive)
                    if base_name.endswith(FILE_SUFFIX):
                        base_name = base_name[:-len(FILE_SUFFIX)]
                        
                    animal_names.append(base_name)
                    
                    # Generate Base64 string directly for the debug log output
                    b64_string = base64.b64encode(base_name.encode('utf-8')).decode('utf-8')
                    logger.debug(f"Processed: '{filename}' -> '{base_name}' -> Encrypted: '{b64_string}'")
                    
    except PermissionError:
        logger.error(f"Permission denied while trying to read directory: {img_dir.absolute()}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred while scanning: {e}", exc_info=True)
        sys.exit(1)

    # 3. Handle Empty Results Gracefully
    if not animal_names:
        logger.warning(f"No files ending with '{FILE_EXTENSION}' were found in '{img_dir.absolute()}'.")
        logger.info("No output files generated. Exiting.")
        sys.exit(0)
        
    # Sort the array alphabetically for cleanliness and consistency
    animal_names.sort()
    logger.info(f"Successfully extracted {len(animal_names)} animal names.")

    # 4. Format and Write Plain Text Output to File 
    output_content = format_javascript_array(animal_names)
    output_path = Path(OUTPUT_TXT_FILE_NAME)
    
    # Write the formatted JavaScript array to the output file with UTF-8 encoding and robust error handling
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(output_content)
        logger.info(f"Success! Plain text JavaScript array written to: {output_path.absolute()}")
    except IOError as e:
        logger.error(f"Failed to write to output file '{output_path}': {e}", exc_info=True)
        sys.exit(1)

    # 5. Format and Write Encrypted Output to File
    encrypted_output_content = format_encrypted_javascript_array(animal_names)
    encrypted_output_path = Path(OUTPUT_ENC_FILE_NAME)
    
    # Write the Base64 encrypted JavaScript array to the output file with UTF-8 encoding and robust error handling
    try:
        with open(encrypted_output_path, "w", encoding="utf-8") as file:
            file.write(encrypted_output_content)
        logger.info(f"Success! Encrypted JavaScript array written to: {encrypted_output_path.absolute()}")
    except IOError as e:
        logger.error(f"Failed to write to encrypted output file '{encrypted_output_path}': {e}", exc_info=True)
        sys.exit(1)

    logger.info("Process completed successfully.")

# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    main()