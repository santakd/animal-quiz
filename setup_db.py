#!/usr/bin/env python3
"""
setup_db.py - Animal Quiz Database Utility
Initializes the SQLite database, creates application credentials,
and ingests animated GIFs into BLOB storage, complete with robust logging 
and error handling for maintainability and security.
"""

import os
import sys
import sqlite3
import logging
import hashlib
from pathlib import Path
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================
# Resolve directories dynamically relative to this script's location
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "db"
LOG_DIR = BASE_DIR / "logs"
IMG_DIR = BASE_DIR / "img"

# SQLite database file path
DB_FILE = DB_DIR / "animal_quiz.sqlite"

# Image ingestion configurations
FILE_EXTENSION = ".gif"
FILE_SUFFIX = " 512"  # Suffix to strip from filenames (e.g., "cat 512.gif" -> "cat")

# Application credentials for the initial administrative account
APP_USERNAME = "admin"
APP_PASSWORD = "nimda"  # Will be securely hashed in DB

# ==========================================
# LOGGING SETUP
# ==========================================
def setup_logging():
    """
    Configures logging to output to both a timestamped file and the console.
    Creates the logging directory if it does not already exist.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"setup_db_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("SetupDB")

# ==========================================
# DATABASE UTILITY
# ==========================================
def hash_password(password: str) -> str:
    """
    Returns a SHA-256 hash of the provided string.
    
    Note: While SHA-256 is sufficient for this initialization utility, 
    production environments should ideally use stronger, salted, and 
    computationally expensive hashing algorithms such as bcrypt, argon2, 
    or PBKDF2 to resist brute-force attacks.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def initialize_database(logger):
    """
    Creates tables and inserts the default admin user.
    Drops existing tables to ensure a clean state upon execution.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Drop tables to ensure execution is idempotent (can run repeatedly without error)
        logger.info("Dropping existing tables to ensure a clean state...")
        cursor.execute("DROP TABLE IF EXISTS app_users;")
        cursor.execute("DROP TABLE IF EXISTS animals;")
        
        # Create Users Table
        # Store usernames uniquely to avoid duplicates and password hashes instead of plaintext
        logger.info("Creating 'app_users' table...")
        cursor.execute("""
            CREATE TABLE app_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)
        
        # Create Animals Table
        # Store unique animal names and represent their images as binary BLOBs
        logger.info("Creating 'animals' table...")
        cursor.execute("""
            CREATE TABLE animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_name TEXT UNIQUE NOT NULL,
                image_blob BLOB NOT NULL
            );
        """)
        
        # Insert App User
        # Parameterized queries are used to prevent SQL injection hazards
        hashed_pw = hash_password(APP_PASSWORD)
        cursor.execute(
            "INSERT INTO app_users (username, password_hash) VALUES (?, ?)", 
            (APP_USERNAME, hashed_pw)
        )
        logger.info(f"Default user '{APP_USERNAME}' created securely.")
        
        conn.commit()
        return conn
        
    except sqlite3.Error as e:
        logger.critical(f"Database initialization failed: {e}", exc_info=True)
        sys.exit(1)

def ingest_images(conn, logger):
    """
    Scans the specified IMG_DIR and inserts GIF files as BLOBs into the database.
    
    Extracts the animal name from the filename by removing the target extension
    and stripping specific trailing suffixes (e.g. " 512").
    """
    if not IMG_DIR.exists() or not IMG_DIR.is_dir():
        logger.error(f"Image directory not found at: {IMG_DIR}")
        return

    cursor = conn.cursor()
    ingested_count = 0
    
    # Iterate over items in the image directory
    for file_path in IMG_DIR.iterdir():
        # Ensure we only process files with the matching target extension
        if file_path.is_file() and file_path.name.lower().endswith(FILE_EXTENSION):
            filename = file_path.name
            
            # Extract clean animal name (e.g., "lion 512.gif" -> "lion")
            animal_name = filename[:-len(FILE_EXTENSION)]
            if animal_name.endswith(FILE_SUFFIX):
                animal_name = animal_name[:-len(FILE_SUFFIX)]
                
            try:
                # Read raw binary data from file
                with open(file_path, 'rb') as f:
                    blob_data = f.read()
                
                # Insert animal record; parameterized query prevents issues with names containing special characters
                cursor.execute(
                    "INSERT INTO animals (animal_name, image_blob) VALUES (?, ?)",
                    (animal_name, blob_data)
                )
                logger.debug(f"Ingested: {animal_name} ({len(blob_data)} bytes)")
                ingested_count += 1
                
            except sqlite3.IntegrityError:
                # Triggered if an entry with the same unique 'animal_name' already exists
                logger.warning(f"Animal '{animal_name}' already exists in DB. Skipping.")
            except Exception as e:
                # Catch general IO or database execution exceptions for individual files
                logger.error(f"Failed to ingest {filename}: {e}")
                
    # Commit transaction to persist all successfully ingested records
    conn.commit()
    logger.info(f"Successfully ingested {ingested_count} animal images into the database.")

def main():
    """Main execution block to set up logs, initialize the DB, and ingest assets."""
    logger = setup_logging()
    logger.info("Starting Database Setup Utility...")
    
    conn = initialize_database(logger)
    ingest_images(conn, logger)
    
    conn.close()
    logger.info("Database Setup Complete.")

if __name__ == "__main__":
    main()