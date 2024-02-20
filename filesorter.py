import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_files_and_folders(downloads_path):
    downloads_path = Path(downloads_path)
    files = [f for f in downloads_path.iterdir() if f.is_file()]
    folders = [d for d in downloads_path.iterdir() if d.is_dir()]
    return files, folders

def create_folders(downloads_path, folder_names, filename_sorting_rules):
    # First, create folders based on the file extension categories
    for folder in folder_names:
        folder_path = downloads_path / folder
        folder_path.mkdir(exist_ok=True)
    
    # Next, create folders based on the filename sorting rules
    for folder in filename_sorting_rules.keys():
        folder_path = downloads_path / folder
        folder_path.mkdir(exist_ok=True)


def map_extensions_to_folder(folder_names):
    extension_map = {}
    for folder, extensions in folder_names.items():
        for extension in extensions:
            extension_map[extension] = folder
    return extension_map

def determine_target_folder(file_name, filename_sorting_rules, extension_map, default_folder='Others'):
    file_stem = file_name.stem
    file_extension = file_name.suffix[1:].lower()  # Remove the dot and convert to lowercase
    
    for folder, patterns in filename_sorting_rules.items():
        if any(file_stem.startswith(pattern) for pattern in patterns):
            return folder
    # Use file_extension for the fallback
    return extension_map.get(file_extension, default_folder)

def move_files(files, downloads_path, extension_map, filename_sorting_rules):
    for file in files:
        target_folder = determine_target_folder(file, filename_sorting_rules, extension_map)
        target_path = downloads_path / target_folder / file.name
        
        if not target_path.exists():
            try:
                file.rename(target_path)
                logging.info(f"Moved {file.name} to {target_folder}")
            except Exception as e:
                logging.error(f"Could not move {file.name} to {target_folder}: {e}")
        else:
            logging.warning(f"File {file} already exists in {target_path}. Skipping.")

def move_folders(folders, downloads_path, folder_names):
    others_path = downloads_path / 'Others'
    for folder in folders:
        if folder.name not in folder_names and folder != others_path:
            target_path = others_path / folder.name
            if not target_path.exists():
                folder.rename(target_path)
            else:
                logging.warning(f"Folder {folder} already exists in Others. Skipping.")

#Sort folders by majority of files

def combine_categories(folder_names, filename_sorting_rules):
    all_categories = set(folder_names.keys()) | set(filename_sorting_rules.keys())
    return all_categories

def classify_folder_by_content(folder_path, extension_map, all_categories):
    file_counts = {category: 0 for category in all_categories}
    total_files = 0
    
    for item in folder_path.iterdir():
        if item.is_file():
            total_files += 1
            ext_category = extension_map.get(item.suffix[1:].lower(), None)
            if ext_category:
                file_counts[ext_category] = file_counts.get(ext_category, 0) + 1
            else:
                # If no extension match, consider as Others but don't increment total_files
                file_counts["Others"] += 1

    if total_files == 0:
        return "Others"  # Empty or no files, classify as Others

    predominant_category, predominant_count = max(file_counts.items(), key=lambda x: x[1])
    if (predominant_count / total_files) > 0.5:
        return predominant_category
    else:
        return "Others"

def move_folders_based_on_content(folders, downloads_path, folder_names, filename_sorting_rules, extension_map):
    all_categories = combine_categories(folder_names, filename_sorting_rules)
    
    for folder in folders:
        # Skip if the folder is a top-level category itself
        if folder.name in all_categories:
            logging.info(f"Skipping top-level category folder: {folder.name}")
            continue

        classification = classify_folder_by_content(folder, extension_map, all_categories)
        # Further checks to ensure we don't move a folder into a category it already belongs to
        if folder.parent.name != classification:
            target_path = downloads_path / classification
            
            # Ensure target folder exists
            target_path.mkdir(exist_ok=True)
            
            # Construct new folder path
            new_folder_path = target_path / folder.name
            
            if not new_folder_path.exists():
                folder.rename(new_folder_path)
                logging.info(f"Moved {folder} to {new_folder_path}")
            else:
                logging.warning(f"Folder {folder} already exists in {new_folder_path}. Skipping.")
        else:
            logging.info(f"Folder {folder} is already in its correct category: {classification}")






if __name__ == "__main__":
    downloads_path = Path("H:\\Downloads")
    folder_names = {
        "Audio": {'aif','cda','mid','midi','mp3','mpa','ogg','wav','wma','m4a'},
        "Compressed":{'7z','deb','pkg','rar','rpm', 'tar.gz','z','zip','gz'},
        'Code':{'htm','js','jsp','html','ipynb','py','java','css','php','json'},
        'Documents':{'ods','odt','rtf','ppt','pptx','pdf','xls', 'xlsx','doc','docx','txt', 'tex', 'epub'},
        'Images':{'bmp','gif','ico','jpeg','jpg','png','jfif','svg','tif','tiff','webp','heic'},
        'Softwares':{'apk','bat','bin', 'exe','jar','msi','iso'},
        'Videos':{'3gp','avi','flv','h264','mkv','mov','mp4','mpg','mpeg','wmv','m4v'},
        'Torrents':{'torrent'},
        'WPbackup':{'wpress','sql'},
        'Data':{'csv','xml'},
        'Maps':{'gpx'},
        'Graphics':{'psd', 'stl','dwg'},
        'Others': {'NONE'}
    }
    filename_sorting_rules = {
    "Photos": ["IMG_"],  # List of prefixes or patterns for the "Photos" folder
    # Add more rules as needed
}

    try:
        files, folders = get_files_and_folders(downloads_path)
        create_folders(downloads_path, folder_names, filename_sorting_rules)
        extension_map = map_extensions_to_folder(folder_names)
        move_files(files, downloads_path, extension_map, filename_sorting_rules)
        #move_folders(folders, downloads_path, folder_names)
        move_folders_based_on_content(folders, downloads_path, folder_names, filename_sorting_rules, extension_map)
        logging.info("Files and folders have been organized.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

