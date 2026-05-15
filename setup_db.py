#!/usr/bin/env python3
"""
setup_db.py - Animal Quiz Database Utility
Initializes the SQLite database, creates application credentials,
and ingests animated GIFs into BLOB storage.
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
# Directory Structure
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "db"
LOG_DIR = BASE_DIR / "logs"
IMG_DIR = BASE_DIR / "img"

DB_FILE = DB_DIR / "animal_quiz.sqlite"

# Image Parsing
FILE_EXTENSION = ".gif"
FILE_SUFFIX = " 512"

# Application Credentials
APP_USERNAME = "admin"
APP_PASSWORD = "nimda"  # Will be securely hashed in DB

# ==========================================
# LOGGING SETUP
# ==========================================
def setup_logging():
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
    """Returns a SHA-256 hash of the provided string."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def initialize_database(logger):
    """Creates tables and inserts the default admin user."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Drop tables to ensure idempotency
        logger.info("Dropping existing tables to ensure a clean state...")
        cursor.execute("DROP TABLE IF EXISTS app_users;")
        cursor.execute("DROP TABLE IF EXISTS animals;")
        
        # Create Users Table
        logger.info("Creating 'app_users' table...")
        cursor.execute("""
            CREATE TABLE app_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)
        
        # Create Animals Table
        logger.info("Creating 'animals' table...")
        cursor.execute("""
            CREATE TABLE animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_name TEXT UNIQUE NOT NULL,
                image_blob BLOB NOT NULL
            );
        """)
        
        # Insert App User
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
    """Scans the IMG_DIR and inserts GIFs as BLOBs."""
    if not IMG_DIR.exists() or not IMG_DIR.is_dir():
        logger.error(f"Image directory not found at: {IMG_DIR}")
        return

    cursor = conn.cursor()
    ingested_count = 0
    
    for file_path in IMG_DIR.iterdir():
        if file_path.is_file() and file_path.name.lower().endswith(FILE_EXTENSION):
            filename = file_path.name
            
            # Extract clean animal name
            animal_name = filename[:-len(FILE_EXTENSION)]
            if animal_name.endswith(FILE_SUFFIX):
                animal_name = animal_name[:-len(FILE_SUFFIX)]
                
            try:
                # Read binary data
                with open(file_path, 'rb') as f:
                    blob_data = f.read()
                
                # Insert into DB
                cursor.execute(
                    "INSERT INTO animals (animal_name, image_blob) VALUES (?, ?)",
                    (animal_name, blob_data)
                )
                logger.debug(f"Ingested: {animal_name} ({len(blob_data)} bytes)")
                ingested_count += 1
                
            except sqlite3.IntegrityError:
                logger.warning(f"Animal '{animal_name}' already exists in DB. Skipping.")
            except Exception as e:
                logger.error(f"Failed to ingest {filename}: {e}")
                
    conn.commit()
    logger.info(f"Successfully ingested {ingested_count} animal images into the database.")

def main():
    logger = setup_logging()
    logger.info("Starting Database Setup Utility...")
    
    conn = initialize_database(logger)
    ingest_images(conn, logger)
    
    conn.close()
    logger.info("Database Setup Complete.")

if __name__ == "__main__":
    main()