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

def rename_tex_file(path):
    file_type = obtain_file_type(path)
    if convert_file_type_to_extension(file_type) == ".tex":
        if path.endswith(".tex"):
            return 
        else:
            os.rename(path, path + '.tex')
            print(f"rename {path} -> {path + '.tex'}")
    return



REST_GZ_PART_DIR = "./rest_gz_part/"

all_rest_gz_part_files = os.listdir(REST_GZ_PART_DIR)


futures = []
with print_time("rename tex files..."):
    with ThreadPoolExecutor(max_workers = 200) as executor:
        for filename in tqdm(all_rest_gz_part_files):
            full_path = os.path.join(REST_GZ_PART_DIR, filename)
            future = executor.submit(rename_tex_file, full_path)
            futures.append(future)
        for future in tqdm(futures):
            result = future.result()
        executor.shutdown()