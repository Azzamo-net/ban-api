from database import SessionLocal  # Add this line

# Utility functions for file synchronization and temporary ban management 

import os

RATE_LIMIT = int(os.getenv("RATE_LIMIT", 100))

def ensure_lists_directory_and_files():
    # Define the directory and file paths
    directory = "lists"
    files = [
        "blocked_pubkeys.txt",
        "blocked_words.txt",
        "blocked_ips.txt",
        "temp_bans.txt"
    ]

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create each file if it doesn't exist
    for file in files:
        file_path = os.path.join(directory, file)
        if not os.path.exists(file_path):
            open(file_path, 'a').close()

def export_all():
    # Implement export logic to text files
    pass

def import_all():
    # Implement import logic from text files
    pass

def save_moderator_keys_to_file(db: SessionLocal):
    moderators = db.query(Moderator).all()
    with open("lists/moderator_keys.txt", "w") as file:
        for moderator in moderators:
            file.write(f"{moderator.name},{moderator.private_key}\n")
