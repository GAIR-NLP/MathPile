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

def read_tex_file(file_path):
    encoding = detect_encoding(file_path)
    if encoding == None:
        encoding = "utf-8"
    try:
        with open(file_path, "r", encoding = encoding, errors='ignore') as f:
            content = f.read()
    except:
        return None
    return content

@time_it
def remove_comments(content):
    def _remove_comments_inline(text):
        import regex
        # ref: https://github.com/google-research/arxiv-latex-cleaner/blob/main/arxiv_latex_cleaner/arxiv_latex_cleaner.py#L179
        if text.lstrip(" ").lstrip("\t").startswith("%"):
            print("cleaning comments")
            return ""
        match = regex.search(r"(?<!\\)%", text)
        if match:
            print("cleaning comments")
            return text[:match.end()-1] #+ "\n"
        else:
            return text

    content_wo_comment = ""
    for line in content.splitlines():
        content_wo_comment += _remove_comments_inline(line) + "\n"

    return content_wo_comment

@time_it
def extract_title(content):
    print("extract title...")
    title_pattern = r'\\title\{(.*?)\}'
    title = re.search(title_pattern, content, re.S)
    if title:
        return title.group(1)
    else:
        return None

@time_it
def check_title_in_main_body(content):
    pattern = r"\\title\{(.*?)\}"
    match = re.search(pattern, content, re.S)
    if match:
        print(f"title '{match.group(1)}' in main body")
        return True
    else:
        print("no title in main body")
        return False
@time_it
def replace_title(title, main_body):
    print("replacing title...")

    if check_title_in_main_body(main_body):
        return main_body
    if "\\maketitle" in main_body:
        try:
            main_body = re.sub(r"\\maketitle", r"\\title{%s}"%title, main_body)
        except:
            main_body = main_body.replace("\\maketitle", "\\title{%s}"%title)
        print("\\maketitle -> \\title{%s}"%title)
    else:
        print("no \\maketitle")
    return main_body

@time_it
def remove_preface(content):
    pattern = r"\\(section|subsection)\*?{Preface}(.*?)(?=^\\(section|subsection))"
    # cleaned_content = re.sub(pattern, "\n", content, re.S | re.I)
    match = re.search(pattern, content, re.S|re.I|re.M)
    print(match)
    if match:
        cleaned_content = content.replace(match.group(), "\n")
    else:
        return content
    return cleaned_content

@time_it
def remove_table_of_contents(content):
    pattern = r"\\(section|subsection)\*?{(Contents|Table of Contents|Brief Contents|Contents at a glance)}(.*?)(?=^\\(section|subsection))"
    # cleaned_content = re.sub(pattern, "\n", content, re.S | re.I)
    match = re.search(pattern, content, re.S|re.I|re.M)
    print(match)
    if match:
        cleaned_content = content.replace(match.group(), "\n")
    else:
        return content
    return cleaned_content

@time_it
def clean_figure_environment(content):
    pattern = r"\\begin{center}\s+\\includegraphics\[max width=\\textwidth\]{(.*?)}\s+\\end{center}"
    cleaned_content = re.sub(pattern, "\n", content)

    pattern = r"\\includegraphics\[max width=\\textwidth, center\]{(.*?)}"
    cleaned_content = re.sub(pattern, "\n", cleaned_content)
    return cleaned_content

@time_it
def replace_excessive_newlines(content):
    print(f"replacing excessive newlines...")
    excessive_newlines_pattern = r"\n{3,}"
    cleaned_content = re.sub(excessive_newlines_pattern, "\n\n", content)
    return cleaned_content

@time_it
def remove_acknowledgements(content):
    print("removing acknowledgements...")

    # pattern = r"section\*{acknowledgements}(.*?)(?=\\begin{|\\section|\\subsection|\\subsubsection|\\end{document})}})"
    pattern = r"\\(section|subsection|subsubsection|chapter|begin)\*?({acknowledgements}|{acknowledgement}|{ack}|acknowledgments|acknowledgement)"
    match = re.search(pattern, content, re.I)
    print(match)

    if match:
        ack_content = content[match.end():]
        end_pattern = r"\\(begin{|section|subsection|subsubsection|bibliography|end{document}|end{ack})"
        end_match = re.search(end_pattern, ack_content, re.I)
        # print(end_match)
        if end_match:
            return content[:match.start()] + "\n" + content[match.end() + end_match.start():]
        else:
            return content[:match.start()] + "\n" + "\\end{document}"
    else:
        print("No acknowledgement section")
        return content

@time_it
def remove_index_section(content):
    pattern = r"\\(section|subsection)\*?{(Index|Index of Keywords and Terms|Subject Index)}(.*?)(?=^\\(end{document}))"
    match = re.search(pattern, content, re.S|re.I|re.M)
    print(match)
    if match:
        cleaned_content = content.replace(match.group(), "\n")
        # cleaned_content = content[:match.start()] + "\end{document}"
    else:
        return content
    return cleaned_content


@time_it
def extract_tex_main_body(content):
    print("extracting tex main body...")

    pattern = r"\\begin{document}([\s\S]*)\\end{document}"
    # pattern = r"\begin{document}(.*?)\end{document}"
    match = re.search(pattern, content, re.S)
    if match:
        document_text = "\\begin{document}\n" + match.group(1) + "\n\\end{document}"
    else:
        document_text = ""
        print("extracting main body fails")
    return document_text

@time_it
def mathpix_parsed_tex_content_clean_pipeline(content):
    assert content != None
    print(len(content))

    content = remove_comments(content)

    title = extract_title(content)
    
    content = clean_figure_environment(content)
    print(len(content))
    
    content = remove_preface(content)
    print(len(content))

    content = remove_table_of_contents(content)
    print(len(content))

    content = remove_acknowledgements(content)
    print(len(content))
    
    # content = remove_index_section(content)
    # print(len(content))

    assert content.strip() != ""

    main_body = extract_tex_main_body(content)
    print(len(main_body))

    assert main_body.strip() != ""


    if title is not None:
        print(f"extracted title is: {title}")
        main_body = replace_title(title, main_body).strip()

    main_body = replace_excessive_newlines(main_body)
    print(len(main_body))
    

    return main_body


@time_it
def mathpix_parsed_tex_file_clean_pipeline(source_file_path, target_save_dir):

    basename = os.path.basename(source_file_path)
    
    target_full_path = os.path.join(target_save_dir, basename)

    if os.path.exists(target_full_path) and os.path.getsize(target_full_path):
        return
    
    encoding = detect_encoding(source_file_path)
    if encoding == None:
        encoding = "utf-8"
    with open(source_file_path, "r", encoding = encoding, errors='ignore') as f:
        content = f.read()
    
    assert content != None
    
    cleaned_content = mathpix_parsed_tex_content_clean_pipeline(content)

    assert cleaned_content.strip() != ""

    with open(target_full_path, "w", encoding = "utf-8") as f:
        f.write(cleaned_content)
    
    return



if __name__ == "__main__":

    # path = "./merged-mathpix-parsed-results/tex/textbooks/college/PDF-Worldwide Integral Calculus with infinite series.tex"
    # content = read_tex_file(path)

    # content = remove_preface(content)

    # content = remove_table_of_contents(content)

    # content = clean_figure_environment(content)

    # content = remove_acknowledgements(content)

    # content = remove_index_section(content)

    # content = extract_tex_main_body(content)

    # content = mathpix_parsed_tex_file_clean_pipeline(content)
    # print("*"*50)
    # print(content[-5000:])

    # version = 0.1
    # TARGET_SAVE_DIR = f"cleaned_data_v{version}"

    # dirs = ["./merged-mathpix-parsed-results/tex/notes", "./merged-mathpix-parsed-results/tex/textbooks/college", "./merged-mathpix-parsed-results/tex/textbooks/high-school"]

    # with print_time(f"cleaning tex file"):
    #     futures = []
    #     with ThreadPoolExecutor(max_workers = 200) as executor:
    #         for dirpath in dirs:
    #             filenames = os.listdir(dirpath)
    #             for filename in tqdm(filenames):
    #                 if not filename.endswith(".tex"):
    #                     continue
    #                 full_path = os.path.join(dirpath, filename)

    #                 target_save_dir = dirpath.replace("merged-mathpix-parsed-results", TARGET_SAVE_DIR)
    #                 create_recursive_dir(target_save_dir)

    #                 future = executor.submit(mathpix_parsed_tex_file_clean_pipeline, full_path, target_save_dir)
    #                 futures.append(future)

    #         for future in tqdm(futures):
    #             result = future.result()
    #         executor.shutdown()
    source_path = "merged-mathpix-parsed-results/tex/textbooks/college/PDF-Fundamentals Of Mathematics.tex"
    if os.path.exists(source_path.replace("merged-mathpix-parsed-results", "cleaned_data_v0.1")):
        os.remove(source_path.replace("merged-mathpix-parsed-results", "cleaned_data_v0.1"))
    target_save_dir = "cleaned_data_v0.1/tex/textbooks/college"
    mathpix_parsed_tex_file_clean_pipeline(source_path, target_save_dir)
