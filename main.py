import os
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
import signal


# Signal handling for graceful shutdown
def handle_exit(signum, frame):
    logging.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# Constants for optimization
BATCH_SIZE = 64

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Define directories
HOME = Path.home()

logging.info("Script starting up....")
logging.info(f"Working directory: {os.getcwd()}")
logging.info(f"Home directory: {str(HOME)}")

# Directories to monitor
SOURCE_DIRS = [
    HOME,  # Home directory
    HOME / "Downloads"  # Downloads directory
]

# Destination directories
MUSIC_DIR = HOME / "Music"
PICTURES_DIR = HOME / "Pictures"
VIDEOS_DIR = HOME / "Videos"
STUDY_DIR = HOME / "study_materials"

# Create destination directories if they don't exist
MUSIC_DIR.mkdir(exist_ok=True)
PICTURES_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)
STUDY_DIR.mkdir(exist_ok=True, parents=True)

# File type mappings
FILE_MAPPINGS = {
    # Music files
    '.mp3': MUSIC_DIR,
    '.wav': MUSIC_DIR,
    '.flac': MUSIC_DIR,
    '.aac': MUSIC_DIR,
    '.ogg': MUSIC_DIR,
    '.m4a': MUSIC_DIR,

    # Picture files
    '.jpg': PICTURES_DIR,
    '.jpeg': PICTURES_DIR,
    '.png': PICTURES_DIR,
    '.gif': PICTURES_DIR,
    '.bmp': PICTURES_DIR,
    '.tiff': PICTURES_DIR,
    '.webp': PICTURES_DIR,

    # Study materials (PDFs and documents)
    '.pdf': STUDY_DIR,
    '.djvu': STUDY_DIR,
    '.epub': STUDY_DIR,
    '.doc': STUDY_DIR,
    '.docx': STUDY_DIR,
    '.ppt': STUDY_DIR,
    '.pptx': STUDY_DIR,
    '.xls': STUDY_DIR,
    '.xlsx': STUDY_DIR,
    '.txt': STUDY_DIR,

    # Video files
    '.mp4': VIDEOS_DIR,
    '.mkv': VIDEOS_DIR,
    '.avi': VIDEOS_DIR,
    '.mov': VIDEOS_DIR,
    '.webm': VIDEOS_DIR,
    '.flv': VIDEOS_DIR,
    '.wmv': VIDEOS_DIR
}


def move_file_parallel(file_info):
    """Move a single file for parallel processing"""
    file_path, destination = file_info
    try:
        # Use direct rename if on same filesystem
        if os.stat(file_path).st_dev == os.stat(destination.parent).st_dev:
            os.rename(str(file_path), str(destination))
        else:
            shutil.move(str(file_path), str(destination))
        return f"Moved: {file_path.name} → {destination}"
    except Exception as e:
        return f"Error moving {file_path.name}: {e}"


def process_batch_moves(move_operations):
    """Process a batch of file moves in parallel for better performance"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(move_file_parallel, move_operations))

    # Print results
    for result in results:
        print(result)


class FileHandler(FileSystemEventHandler):
    """Handle file system events for automatic organization"""

    def process(self, event):
        """Process file events"""
        path = Path(event.src_path)

        # Skip directories, hidden files, and files already in destination folders
        if (path.is_dir() or
                path.name.startswith('.') or
                any(str(path).startswith(str(dest_dir)) for dest_dir in
                    [MUSIC_DIR, PICTURES_DIR, VIDEOS_DIR, STUDY_DIR])):
            return

        # Get file extension (lowercase)
        extension = path.suffix.lower()

        # If we have a mapping for this file type
        if extension in FILE_MAPPINGS:
            destination_dir = FILE_MAPPINGS[extension]
            destination = destination_dir / path.name

            # Handle duplicate filenames
            if destination.exists():
                base_name = path.stem
                count = 1
                while destination.exists():
                    new_name = f"{base_name}_{count}{extension}"
                    destination = destination_dir / new_name
                    count += 1

            # Move the file (delay slightly to ensure it's not in use)
            try:
                # Small delay to ensure file is fully written
                time.sleep(0.5)

                # Use direct rename if on same filesystem (faster)
                if os.stat(str(path)).st_dev == os.stat(str(destination_dir)).st_dev:
                    os.rename(str(path), str(destination))
                else:
                    shutil.move(str(path), str(destination))
                print(f"Moved: {path.name} → {destination}")
            except Exception as e:
                print(f"Error moving {path.name}: {e}")

    def on_created(self, event):
        """File created event handler"""
        self.process(event)

    def on_modified(self, event):
        """File modified event handler - also catches some download completions"""
        self.process(event)


def organize_existing_files(directory):
    """Organize files that already exist in the specified directory"""
    print(f"Scanning existing files in {directory}...")

    # Skip destination directories to prevent moving files that are already organized
    if any(str(directory).startswith(str(dest_dir)) for dest_dir in [MUSIC_DIR, PICTURES_DIR, VIDEOS_DIR, STUDY_DIR]):
        return

    # Get list of files using os.scandir (faster than glob)
    files = []
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and not entry.name.startswith('.'):
                    files.append(Path(entry.path))
    except Exception as e:
        print(f"Error scanning directory {directory}: {e}")
        return

    if not files:
        print(f"No existing files to organize in {directory}.")
        return

    # Process files in batches for better performance
    pending_moves = []
    for file_path in files:
        extension = file_path.suffix.lower()

        if extension in FILE_MAPPINGS:
            destination_dir = FILE_MAPPINGS[extension]
            destination = destination_dir / file_path.name

            # Handle duplicate filenames
            if destination.exists():
                base_name = file_path.stem
                count = 1
                while destination.exists():
                    new_name = f"{base_name}_{count}{extension}"
                    destination = destination_dir / new_name
                    count += 1

            # Add to pending moves instead of moving immediately
            pending_moves.append((file_path, destination))

            # Process batch when it reaches the threshold
            if len(pending_moves) >= BATCH_SIZE:
                process_batch_moves(pending_moves)
                pending_moves = []

    # Process any remaining files
    if pending_moves:
        process_batch_moves(pending_moves)


def monitor_directory(directory):
    """Set up monitoring for a specific directory"""
    event_handler = FileHandler()
    observer = Observer()

    # Use more specific event patterns for efficiency
    observer.schedule(
        event_handler,
        str(directory),
        recursive=False,  # Don't monitor subdirectories
    )

    logging.info(f"Monitoring directory: {directory}")
    return observer


def start_monitoring():
    """Start monitoring multiple directories"""
    observers = []

    # Set up an observer for each source directory
    for directory in SOURCE_DIRS:
        observer = monitor_directory(directory)
        observers.append(observer)

    # Start all observers
    for observer in observers:
        observer.start()

    print(f"Now monitoring directories: {', '.join(str(d) for d in SOURCE_DIRS)}")
    print("Press Ctrl+C to stop monitoring.")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop all observers on keyboard interrupt
        for observer in observers:
            observer.stop()
        print("\nFile monitoring stopped.")

    # Wait for all observer threads to join
    for observer in observers:
        observer.join()


if __name__ == "__main__":
    print("File Organizer - Starting up...")

    # First organize existing files in all source directories
    for directory in SOURCE_DIRS:
        organize_existing_files(directory)

    # Then start monitoring for new files
    start_monitoring()
