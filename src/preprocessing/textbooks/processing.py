import os
import shutil
import chardet
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def create_folder(folder_path):
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

def check_extension_file_in_dir(dir, extension):
    filenames = os.listdir(dir)
    for file in filenames:
        if file.endswith(extension):
            return file
    return None

# def detect_encoding(file_path):
#     with open(file_path, 'rb') as f:
#         encoding = chardet.detect(f.read()).get('encoding')
#     return encoding

# def read_file(file_path):
#     encoding = detect_encoding(file_path)
#     if encoding == None:
#         encoding = "utf-8"
#     with open(file_path, "r", encoding = encoding, errors='ignore') as f:
#         content = f.read()
#     return content

def read_source_file_write_into_target_file(scoure_file_path, target_file_path):

    if os.path.exists(target_file_path) and os.path.getsize(target_file_path) > 0:
        return
    shutil.copy(scoure_file_path, target_file_path)


def copy_md_tex_file_to_target_path(source_dir, md_target_dir, tex_target_dir):

    md_filename = check_extension_file_in_dir(source_dir, ".md")
    assert md_filename != None
    md_full_path = os.path.join(source_dir, md_filename)

    tex_dir = os.path.basename(md_filename).replace(".md", "")
    tex_filename = check_extension_file_in_dir(os.path.join(source_dir, tex_dir), ".tex")
    tex_full_path = os.path.join(source_dir, tex_dir, tex_filename)

    pdf_name = os.path.basename(source_dir)

    target_md_full_path = os.path.join(md_target_dir, pdf_name + ".md")
    target_tex_full_path = os.path.join(tex_target_dir, pdf_name + ".tex")

    read_source_file_write_into_target_file(md_full_path, target_md_full_path)
    read_source_file_write_into_target_file(tex_full_path, target_tex_full_path)


dirs = ['textbooks/high-school', 'textbooks/college', 'notes/']
# dirs = ['case_study']

TARGET_DIR = "./processed/"
create_folder(TARGET_DIR)

futures = []
with ThreadPoolExecutor(max_workers = 96) as executor:
    # for path in tqdm(all_dir_full_path):
    #     future = executor.submit(unzip_file, path)
    #     futures.append(future)
    # for future in tqdm(futures):
    #     result = future.result()
    # executor.shutdown()
    for dirname in tqdm(dirs):
        md_target_save_dir = os.path.join(TARGET_DIR, "md", dirname)
        tex_target_save_dir = os.path.join(TARGET_DIR, "tex", dirname)
        
        create_folder(md_target_save_dir)
        create_folder(tex_target_save_dir)

        pdf_dirnames = os.listdir(dirname)
        for pdf_dirname in pdf_dirnames:
            pdf_dir_full_path = os.path.join(dirname, pdf_dirname)
            if os.path.isfile(pdf_dir_full_path):
                continue
            future = executor.submit(copy_md_tex_file_to_target_path, pdf_dir_full_path, md_target_save_dir, tex_target_save_dir)
            futures.append(future)
    for future in tqdm(futures):
        result = future.result()
    executor.shutdown()








    