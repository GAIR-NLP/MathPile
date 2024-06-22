import os
import re
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from utils import (
    detect_encoding,
    time_it,
    create_dir,
    create_recursive_dir,
    print_time
)


@time_it
def clean_perface(content):

    pattern = r'^#{1,6}\s*(Preface).*?(?=^#)'
    match = re.search(pattern, content, re.M | re.I | re.S)

    if match:
        print("Replacing perface....")
        # print(match.group())
        cleaned_content = content.replace(match.group(), "\n")
    else:
        return content

    return cleaned_content

@time_it
def clean_table_of_content(content):
    # pattern = r'^#{2,}\s*(Contents|Table of contents).*(\n|.)*?^#.*'

    # match = re.search(pattern, content, re.M | re.I)

    # print(match.group(2))

    pattern = r'^#{1,6}\s*(Contents|Table of contents).*?(?=^#)'
    match = re.search(pattern, content, re.M | re.I | re.S)
    # print(match.group())
    # print("==="*100)
    # cleaned_content = re.sub(pattern, "\n", content, re.M | re.I | re.S)

    if match:
        print("Replacing....")
        cleaned_content = content.replace(match.group(), "\n")
    else:
        return content

    return cleaned_content

@time_it
def replace_excessive_newlines(content):
    print(f"replacing excessive newlines...")
    excessive_newlines_pattern = r"\n{3,}"
    cleaned_content = re.sub(excessive_newlines_pattern, "\n\n", content)
    return cleaned_content

# def is_end_of_sentence(word):
#     punctuations = ['.', '!', '?', '...', '"', ')', ']', '}', '-', '—', ';', "'"]
#     if word in punctuations:
#         return True
#     else:
#         return False
    

# def locate_incomplete_lines_before_and_after_mathpix_parsed_picture(content):

#     pattern = r'!\[(.*?)\]\(https:\/\/cdn.mathpix.com\/.+?\)'

#     match = re.search(pattern, content)

#     if not match:
#         return content

#     content = content.replace("\n\n", "\n")

#     matches = re.finditer(pattern, content)

#     removed_span = []

#     for match in matches:
#         start, end = match.span()
#         print(start, end)
#         print(content[start:end])

#         prev_para_end = content.rfind("\n", 0, start)

#         prev_prev_para_end = content.rfind("\n", 0, prev_para_end)
        
#         print(prev_prev_para_end, prev_para_end)
        

#         i = prev_para_end
#         span_end_idx, span_start_idx = -1, -1
#         while i >= prev_prev_para_end -2:

#             if content[i].isalpha():
#                 i -= 1
#                 continue

#             elif is_end_of_sentence(content[i]) and span_end_idx == -1 and span_start_idx == -1:
#                 print("quit")
#                 break

#             elif (content[i].isalpha() or content[i] in [',', ':']) and content[i+1].isspace():
#                 if span_end_idx == -1:
#                     print("Start Success!")
#                     span_end_idx = i
#                 i -= 1
#                 continue
            

#             elif is_end_of_sentence(content[i]) and span_end_idx != -1:
#                 print("Success!!!")
#                 span_start_idx = i + 2
#                 break

#             i -= 1

#         if span_end_idx != -1 and span_start_idx != -1:
#             removed_span.append((span_start_idx, span_end_idx))
        
#         # next_para_start = content.find("\n", start=end)

#         # next_next_para_start = content.find("\n", start=next_para_start)
    
#     for item in removed_span:

#         start_idx, end_idx = item
#         content = content[:start_idx] + content[end_idx+1:]
    
#     return content

@time_it
def remove_image_mathpix_url(content):
    pattern = r'!\[(.*?)\]\(https:\/\/cdn.mathpix.com\/.+?\)'

    cleaned = re.sub(pattern, '', content) 
    
    # pattern = r'<img class="imgSvg"(.*?)=="\/>'
    pattern = r'<img class(.*?)\/>'
    cleaned = re.sub(pattern, ' ', cleaned, re.S) 

    return cleaned

@time_it
def clean_acknowledgements_section(content):

    length = len(content)
    
    pattern = r'^#{1,6}\s*(Acknowledgements).*?(?=^#)'
    match = re.search(pattern, content, re.M | re.I | re.S)

    if match:
        print("Replacing Acknowledgements....")
        cleaned_content = content.replace(match.group(), "\n")
    else:
        pattern = r'^#{1,6}\s*(Acknowledgements)'
        match = re.search(pattern, content, re.M | re.I | re.S)
        if match:
            if match.end() - match.start() < 5000:
                cleaned_content = content[:match.start()]
        else:
            return content

        return content

    return cleaned_content

@time_it
def clean_index_section(content):
    length = len(content)
    # pattern = r'^#{1,6}\s*(Index|Index of Keywords and Terms|Subject Index).*?(?=^#)'
    # match = re.search(pattern, content, re.M | re.I | re.S)

    # if match:
    #     print("Replacing Index....")
    #     cleaned_content = content.replace(match.group(), "\n")
    # else:
    #     pattern = r'^#{1,6}\s*(Index|Index of Keywords and Terms|Subject Index)'
    #     match = re.search(pattern, content[length//5*4:], re.M | re.I | re.S)
    #     if match:
    #         cleaned_content = content[:match.start()]
    #     else:
    #         return content

    pattern = r'^#{1,6}\s*(Index|Index of Keywords and Terms|Subject Index)'
    match = re.search(pattern, content, re.I | re.M)
    if match:
        print(match)
        # print(len(content))
        # print(match.start())
        # print(content[match.end():match.end()+50])
        cleaned_content = content[:match.start()]
    else:
        return content

    return cleaned_content

@time_it
def markdown_content_clean_pipeline(content):
    print(len(content))
    cleaned_content = remove_image_mathpix_url(content)
    print(len(cleaned_content))
    
    cleaned_content = clean_perface(cleaned_content)
    print(len(cleaned_content))
    
    cleaned_content = clean_table_of_content(cleaned_content)
    print(len(cleaned_content))
    
    # cleaned_content = locate_incomplete_lines_before_and_after_mathpix_parsed_picture(cleaned_content)

    cleaned_content = clean_acknowledgements_section(cleaned_content)
    print(len(cleaned_content))

    # cleaned_content = clean_index_section(cleaned_content)
    # print(len(cleaned_content))

    cleaned_content = replace_excessive_newlines(cleaned_content)
    print(len(cleaned_content))

    return cleaned_content

@time_it
def markdown_file_clean_pipeline(source_file_path, target_save_dir):

    basename = os.path.basename(source_file_path)
    
    target_full_path = os.path.join(target_save_dir, basename)

    if os.path.exists(target_full_path) and os.path.getsize(target_full_path):
        return
    
    encoding = detect_encoding(source_file_path)
    if encoding == None:
        encoding = "utf-8"
    with open(source_file_path, "r", encoding = encoding, errors='ignore') as f:
        content = f.read()
    
    cleaned_content = markdown_content_clean_pipeline(content)

    with open(target_full_path, "w", encoding = "utf-8") as f:
        f.write(cleaned_content)
    
    return


if __name__ == "__main__":
    # version = 0.1
    # TARGET_SAVE_DIR = f"cleaned_data_v{version}"

    # dirs = ["./merged-mathpix-parsed-results/md/notes", "./merged-mathpix-parsed-results/md/textbooks/college", "./merged-mathpix-parsed-results/md/textbooks/high-school"]

    # with print_time(f"cleaning markdown file"):
    #     futures = []
    #     with ThreadPoolExecutor(max_workers = 200) as executor:
    #         for dirpath in dirs:
    #             filenames = os.listdir(dirpath)
    #             for filename in tqdm(filenames):
    #                 if not filename.endswith(".md"):
    #                     continue
    #                 full_path = os.path.join(dirpath, filename)

    #                 target_save_dir = dirpath.replace("merged-mathpix-parsed-results", TARGET_SAVE_DIR)
    #                 create_recursive_dir(target_save_dir)

    #                 future = executor.submit(markdown_file_clean_pipeline, full_path, target_save_dir)
    #                 futures.append(future)

    #         for future in tqdm(futures):
    #             result = future.result()
    #         executor.shutdown()


    source_path = "merged-mathpix-parsed-results/md/notes/PDF-Geometry and Group Theory.md"
    if os.path.exists(source_path.replace("merged-mathpix-parsed-results", "cleaned_data_v0.1")):
        os.remove(source_path.replace("merged-mathpix-parsed-results", "cleaned_data_v0.1"))
    target_save_dir = "cleaned_data_v0.1/md/notes/"
    markdown_file_clean_pipeline(source_path, target_save_dir)

    # with open("test.md", "r") as f:
    #     content = f.read()
    #     content= markdown_content_clean_pipeline(content)
    #     print(content)
    

