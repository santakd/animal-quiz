#!/usr/bin/env python3
"""
array_gen.py v1.0.1
Animal Quiz - Array Generator Utility 
-------------------------------------
Scans a target directory for image files, strips a specified suffix and extension,
and generates a formatted JavaScript array in a text file.
Writes timestamped execution logs to a local /logs directory.
"""

import os                       # For directory scanning and file handling
import sys                      # For exiting the program and handling command-line arguments
import logging                  # For robust logging of the utility's execution
import argparse                 # For parsing command-line arguments
from pathlib import Path        # For modern and cross-platform path handling
from datetime import datetime   # For timestamping log files

# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================
# Change these constants to match your exact file naming conventions
FILE_EXTENSION = ".gif"
FILE_SUFFIX = " 512"

# Default paths
DEFAULT_IMG_DIR = "img"
OUTPUT_FILE_NAME = "array_gen.txt"
LOG_DIR_NAME = "logs"

# Output formatting
ITEMS_PER_LINE = 8  # How many animal names to print per line in the JS array

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

def main():
    # Setup Logger before any processing to capture all events, including errors
    logger = setup_logging()
    logger.info("Starting Array Generator Utility.")
    
    # Setup Argument Parser with a clear description and default path
    parser = argparse.ArgumentParser(description="Scan an image directory and generate a JS array text file.")
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
                    logger.debug(f"Processed: '{filename}' -> '{base_name}'")
                    
    except PermissionError:
        logger.error(f"Permission denied while trying to read directory: {img_dir.absolute()}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred while scanning: {e}", exc_info=True)
        sys.exit(1)

    # 3. Handle Empty Results Gracefully
    if not animal_names:
        logger.warning(f"No files ending with '{FILE_EXTENSION}' were found in '{img_dir.absolute()}'.")
        logger.info("No output file generated. Exiting.")
        sys.exit(0)
        
    # Sort the array alphabetically for cleanliness
    animal_names.sort()
    logger.info(f"Successfully extracted {len(animal_names)} animal names.")

    # 4. Format and Write Output to File
    output_content = format_javascript_array(animal_names)
    output_path = Path(OUTPUT_FILE_NAME)
    
    # Write the formatted JavaScript array to the output file with UTF-8 encoding
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(output_content)
        logger.info(f"Success! JavaScript array written to: {output_path.absolute()}")
    except IOError as e:
        logger.error(f"Failed to write to output file '{output_path}': {e}", exc_info=True)
        sys.exit(1)

    logger.info("Process completed successfully.")

# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    main()