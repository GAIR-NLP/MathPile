import time
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
import os
import subprocess
from tqdm import tqdm
import zipfile
import rarfile
import tarfile
import random
import chardet
from functools import wraps


class print_time:
    def __init__(self, desc):
        self.desc = desc
    def __enter__(self):
        self.t = time.time()
    def __exit__(self, type, value, traceback):
        print(f'{self.desc} took {time.time() - self.t:.02f}s')



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
    
def detect_encoding(file_path):
    
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read()).get('encoding')
    return encoding

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print(f"{path} already exists")

# def time_it(timeout):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             start_time = time.time()
#             result = func(*args, **kwargs)
#             end_time = time.time()
#             if end_time - start_time > timeout:
#                 print("The function `{}` took too long to run.".format(func.__name__))
#                 return None
#             return result
#         return wrapper
#     return decorator
def time_it_break(timeout):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    result = future.result(timeout=timeout)
                    return result
                except TimeoutError:
                    print("The function `{}` took too long to run.".format(func.__name__))
                    future.cancel()  # Cancel the task
                    return None
        return wrapper
    return decorator


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'Function {func.__name__} elapsed time: {end - start:.4f}s')
        return result
    return wrapper