import os
import subprocess
from tqdm import tqdm
import shutil
import zipfile
import rarfile
import tarfile

def obtain_file_type(filename):
    proc = subprocess.run(['file', filename], stdout=subprocess.PIPE)
    output = proc.stdout.decode()
    filetype = output.split(":")[1].strip()
    # print(f"{filename} - {filetype}")
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


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print(f"{path} already exists")

if __name__ == '__main__':

    arxiv_data_dir = "./arxiv-math-data"
    tex_gz_dir = "./tex_gz_part"
    tar_gz_dir = "./tar_gz_part"
    gz_dir = "./rest_gz_part"
    pdf_dir = "./pdf_part"
    tex_dir = "./tex_part"

    tex_gz_num, tar_gz_num, gz_num, pdf_num, tex_num = 0, 0, 0, 0, 0


    create_dir(tex_gz_dir)
    create_dir(tar_gz_dir)
    create_dir(gz_dir)
    create_dir(pdf_dir)
    create_dir(tex_dir)

    for i, filename in enumerate(tqdm(os.listdir(arxiv_data_dir))):
        full_path = os.path.join(arxiv_data_dir, filename)
        if not os.path.isfile(full_path):
            continue
        filetype = obtain_file_type(full_path)
        file_extension = convert_file_type_to_extension(filetype)

        if file_extension is not None:
            if file_extension == ".tar.gz":
                tar_gz_num += 1
                if os.path.exists(os.path.join(tar_gz_dir, filename + file_extension)):
                    print(f"{os.path.join(tar_gz_dir, filename + file_extension)} already exists")
                    continue
                target_full_path = os.path.join(tar_gz_dir, filename)
                shutil.copy(full_path, target_full_path)
                os.rename(target_full_path, target_full_path + file_extension)
                target_full_path = target_full_path + file_extension
                unzip_dir = os.path.join(tar_gz_dir, filename)
                os.system(f"mkdir {unzip_dir}")
                os.system(f"tar -xzvf {target_full_path} -C {unzip_dir}")
            elif file_extension == ".tex.gz":
                tex_gz_num += 1

                if os.path.exists(os.path.join(tex_gz_dir, filename + '.tex')):
                    print(f"{os.path.join(tex_gz_dir, filename + '.tex')} already exists")
                    continue
                
                target_full_path = os.path.join(tex_gz_dir, filename)
                shutil.copy(full_path, target_full_path)
                os.rename(target_full_path, target_full_path + file_extension)
                target_full_path = target_full_path + file_extension
                os.system(f"gunzip {target_full_path}")
            
            elif file_extension == ".gz":
                gz_num += 1

                if os.path.exists(os.path.join(gz_dir, filename + file_extension)):
                    print(f"{os.path.join(gz_dir, filename + file_extension)} already exists")
                    continue
                    
                target_full_path = os.path.join(gz_dir, filename)
                shutil.copy(full_path, target_full_path)
                os.rename(target_full_path, target_full_path + file_extension)
                target_full_path = target_full_path + file_extension
                os.system(f"gunzip {target_full_path}")
            
            elif file_extension == ".pdf":
                pdf_num += 1

                if os.path.exists(os.path.join(pdf_dir, filename + file_extension)):
                    print(f"{os.path.join(pdf_dir, filename + file_extension)} already exists")
                    continue

                target_full_path = os.path.join(pdf_dir, filename)
                shutil.copy(full_path, target_full_path)
                os.rename(target_full_path, target_full_path + file_extension)
            
            elif file_extension == ".tex":
                tex_num += 1
                if os.path.exists(os.path.join(tex_dir, filename + file_extension)):
                    print(f"{os.path.join(tex_dir, filename + file_extension)} already exists")
                    continue
                
                target_full_path = os.path.join(tex_dir, filename)
                shutil.copy(full_path, target_full_path)
                os.rename(target_full_path, target_full_path + file_extension)
        # if i == 50:
        #     break

    print(f"tar.gz: {tar_gz_num}, tex.gz: {tex_gz_num}, gz: {gz_num}, pdf: {pdf_num}, tex: {tex_num}")

        