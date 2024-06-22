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


REST_GZ_PART_DIR = "./rest_gz_part/"


def extract(filename, full_path):
    if os.path.isfile(full_path):
        if full_path.endswith(".tex"):
            return 
        if full_path.endswith(".gz"):
            code = os.system(f"7z x {full_path} -o{REST_GZ_PART_DIR}")
            if code == 0:
                print(f"{full_path} 7z unzip success")
                os.remove(full_path)
            else:
                print(f"{full_path} 7z unzip fail")
            full_path = full_path.replace(".gz", "")
            filename = filename.replace(".gz", "")

        file_type = obtain_file_type(full_path)
        if "POSIX tar" in file_type:
            unzip_dir = os.path.join(REST_GZ_PART_DIR, "dir_" + filename)
            if os.path.exists(unzip_dir):
                if len(os.listdir(unzip_dir)):
                    return

            os.system(f"mkdir {unzip_dir}")
            os.system(f"tar -xvf {full_path} -C {unzip_dir}")
        elif "Latex" in file_type:
            if not filename.endswith(".tex"):
                os.rename(full_path, full_path + ".tex")


all_rest_gz_part_files = os.listdir(REST_GZ_PART_DIR)

futures = []
with print_time("traverse_dir..."):
    with ThreadPoolExecutor(max_workers = 200) as executor:
        for filename in tqdm(all_rest_gz_part_files):
            full_path = os.path.join(REST_GZ_PART_DIR, filename)
            future = executor.submit(extract, filename, full_path)
            futures.append(future)
        for future in tqdm(futures):
            result = future.result()
        executor.shutdown()
        
        


