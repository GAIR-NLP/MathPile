from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os

dirs = ['textbooks/high-school', 'textbooks/college', 'notes/']
# dirs = ["case_study"]

def check_extension_file_in_dir(dir, extension):
    filenames = os.listdir(dir)
    for file in filenames:
        if file.endswith(extension):
            return file
    return None

def unzip_file(dir):
    filenames = os.listdir(dir)
    zipped_filename = check_extension_file_in_dir(dir, ".tex.zip")
    assert zipped_filename != None
    full_path = os.path.join(dir, zipped_filename)
    unzipped_dir = full_path.replace(".tex.zip", "")
    if os.path.exists(unzipped_dir) and os.path.isdir(unzipped_dir):
        return 
    os.system(f"unzip '{full_path}' -d '{dir}'")



all_dir_full_path = []

for dirname in dirs:
    for subdir in os.listdir(dirname):
        full_path = os.path.join(dirname, subdir)
        if os.path.isfile(full_path):
            continue
        all_dir_full_path.append(full_path)

futures = []
with ThreadPoolExecutor(max_workers = 8) as executor:
    for path in tqdm(all_dir_full_path):
        future = executor.submit(unzip_file, path)
        futures.append(future)
    for future in tqdm(futures):
        result = future.result()
    executor.shutdown()