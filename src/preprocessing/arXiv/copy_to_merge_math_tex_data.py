import os
from concurrent.futures import ThreadPoolExecutor
from utils import print_time
import threading
import os
import subprocess
from tqdm import tqdm
import zipfile
import rarfile
import tarfile
import random

def obtain_file_type(filename):
    proc = subprocess.run(['file', filename], stdout=subprocess.PIPE)
    output = proc.stdout.decode()
    filetype = output.split(":")[1].strip()
    print(f"{filename} - {filetype}")
    return filetype

def convert_file_type_to_extension(file_type):
    if "gzip compressed data" in file_type:
        if ".tex" in file_type and ".tar" not in file_type:
            return ".tex.gz"
        elif ".tar" in file_type:
            return ".tar.gz"
        else:
            return ".gz"
    elif "PDF document" in file_type:
        return ".pdf"
    elif "latex" in file_type.lower():
        return ".tex"
    else:
        print(file_type)
        return None

TARGET_DIR_PATH = "./merge_math_tex_data"


def copy_files(file_path):
    if os.path.isfile(file_path):
        entension = convert_file_type_to_extension(obtain_file_type(file_path))
        if file_path.endswith(".tex") or entension == ".tex":
            basename = os.path.basename(file_path)
            if os.path.exists(os.path.join(TARGET_DIR_PATH, basename)):
                return 
            os.system(f"cp {file_path} {TARGET_DIR_PATH}")
    elif os.path.isdir(file_path):
        basename = os.path.basename(file_path)
        if os.path.exists(os.path.join(TARGET_DIR_PATH, basename)):
            return
        os.system(f"cp -r {file_path} {TARGET_DIR_PATH}")
    return


folders = ["tex_part", "tex_gz_part", "tar_gz_part", "rest_gz_part"]

futures = []
with print_time(f"copy files to {TARGET_DIR_PATH}"):
    with ThreadPoolExecutor(max_workers = 200) as executor:
        for folder in tqdm(folders):
            filenames_in_folder = os.listdir(folder)
            for filename in tqdm(filenames_in_folder):
                full_path = os.path.join(folder, filename)
                future = executor.submit(copy_files, full_path)
                futures.append(future)
            for future in tqdm(futures):
                result = future.result()
        executor.shutdown()