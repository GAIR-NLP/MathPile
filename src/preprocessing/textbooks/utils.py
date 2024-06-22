import chardet
from functools import wraps
import time
import os
import hashlib


def detect_encoding(file_path):
    
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read()).get('encoding')
    return encoding

    
def create_recursive_dir(folder_path):
    if not os.path.exists(folder_path):
        print(f'create dir {folder_path}')
        path_list = folder_path.split('/')
        
        for i in range(1, len(path_list)):
            parent_path = '/'.join(path_list[:i])
            if not os.path.exists(parent_path):
                os.mkdir(parent_path)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
    else:
        print(f'{folder_path} already exists')

def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'Function {func.__name__} elapsed time: {end - start:.4f}s')
        return result
    return wrapper

class print_time:
    def __init__(self, desc):
        self.desc = desc
    def __enter__(self):
        self.t = time.time()
    def __exit__(self, type, value, traceback):
        print(f'{self.desc} took {time.time() - self.t:.02f}s')



def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"dir {path} created successfully")
    else:
        print(f"dir {path} already exists")


def calculate_md5(file_path):
    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5()
        chunk = file.read(8192)
        while chunk:
            md5_hash.update(chunk)
            chunk = file.read(8192)
    return md5_hash.hexdigest()