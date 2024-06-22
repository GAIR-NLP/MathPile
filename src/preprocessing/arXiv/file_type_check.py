import os
import subprocess
from tqdm import tqdm
import zipfile
import rarfile
import tarfile
import random
import chardet

def obtain_file_type(filename):
    proc = subprocess.run(['file', filename], stdout=subprocess.PIPE)
    output = proc.stdout.decode()
    filetype = output.split(":")[1].strip()
    print(f"{filename} - {filetype}")
    return filetype

# filename = "./0704.0086"
# obtain_file_type(filename)

file_signatures = {
    b'\x1f\x8b\x08': 'gz',
    b'\x42\x5a\x68': 'bz2',
    b'\x50\x4b\x03\x04': 'zip',  
    b'%PDF': 'pdf',
    b'\xEF\xBB\xBF': 'text',
    b'%!PS': 'ps',
    b'<!DOCTYPE HTML': 'html',
    b'\x75\x73\x74\x61\x72': 'tar', # tar file head
    b'\xEF\xBB\xBF\x00': 'tex'  # tex file head
}

def obtain_file_type_via_signatures(filename):
    with open(filename, 'rb') as f:
        file_start = f.read(10)
    for signature, filetype in file_signatures.items():
        if file_start.startswith(signature):
            print(f'{filename} is {filetype}')
            return 
    obtain_file_type(filename)    
    return 


def detect_encoding(file_path):

    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read()).get('encoding')
    return encoding


if __name__ == "__main__":
    # dir_to_check = "./arxiv-math-data"
    # all_long_filetypes = []
    # all_unique_filetypes = []
    # for i, filename in enumerate(tqdm(os.listdir(dir_to_check))):
    #     full_path = os.path.join(dir_to_check, filename)
    #     obtain_file_type_via_signatures(full_path)
    #     obtain_file_type(full_path)
    #     print("============")
    #     if i == 50:
    #         break
    #     cur_type = obtain_file_type(full_path)
    #     all_long_filetypes.append(cur_type)
    #     try:
    #         meta_file_type = cur_type.split('"')[1].split(".")[-1]
    #     except Exception as e:
    #         print(f"{filename} - {meta_file_type}")
    #     print(meta_file_type)
    #     all_unique_filetypes.append(meta_file_type)
    # all_unique_filetypes = list(set(all_unique_filetypes))
    # print(f"All unique file types - {len(all_unique_filetypes)}")
    # print(all_unique_filetypes)

    # path = "./0704.0004"
    # obtain_file_type_via_signatures(path)
    # obtain_file_type(path)

    # path = "./arxiv-math-data/0001003"
    # if zipfile.is_zipfile(path):
    #     print("zip")
    # elif rarfile.is_rarfile(path):
    #     print("rar")
    # elif tarfile.is_tarfile(path):
    #     print("tar")
    # elif os.path.splitext(path)[1] == '.tex':
    #     print("tex")

    META_DIR = "./tar_gz_part"
    filenames = os.listdir(META_DIR)
    sampled_filenames = random.sample(filenames, 30)
    for filename in sampled_filenames:
        path = os.path.join(META_DIR, filename)
        file_type = obtain_file_type(path)
        # print(detect_encoding(path))
        if "directory" in file_type:
            os.system(f"cp -r {path} case_study/")


    # with open("./tex_gz_part/0404458.tex", "r") as f:
    #     content = f.read()
    # print(content)

# ./tex_gz_part/0404458.tex
# ./tex_gz_part/2304.04107.tex
# ./tex_gz_part/1702.06413.tex
# ./tex_gz_part/1410.2051.tex
# ./tex_gz_part/1005.3149.tex 

#  ascii, ISO-8859-1, None, Windows-1252, Windows-1254, utf-8, SHIFT_JIS, GB2312

#  ISO-8859-1, Windows-1252, SHIFT_JIS