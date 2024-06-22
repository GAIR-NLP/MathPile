import os
import re
import argparse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import multiprocessing
from tqdm import tqdm
from utils import (
    convert_file_type_to_extension, 
    obtain_file_type,
    detect_encoding,
    create_dir,
    print_time,
    time_it_break,
    time_it
    )

# import regex as re

NO_TEX_DIR_NUM = 0
NO_MAIN_TEX_DIR_NUM = 0


# # # # # # # # # # # # # Processing single tex file # # # # # # # # # # # # # 

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

# def extract_author(content):
#     author_pattern = r'\\author\{([\s\S]*?)\}'
#     author = re.search(author_pattern, content).group(1)
#     return author

def count_char(string, char):
    count = 0
    for c in string:
        if c == char:
            count += 1
    return count

def incomplete_original_command_check(command):
    if not command:
        return True
    begining_brace_count = count_char(command, '{')
    end_brace_count = count_char(command, '}')
    return begining_brace_count != end_brace_count

@time_it
def new_command_find(content):
    print("function new_command_find")
    new_origin_command_mapping = dict()
    new_command_pattern = re.compile(r'\\newcommand{\\(.*?)}')
    new_commands = new_command_pattern.findall(content)

    for command in new_commands:

        find_patterns = [
            r"\\newcommand{\\%s}{(.*?)}"% command,
            r"\\newcommand{\\%s}{([^{}]*\{(?:[^{}]*\{[^{}]*\}[^{}]*)*\}[^{}]*)}"% command,
        ]
        find_patterns = [re.compile(item) for item in find_patterns]

        for pattern in find_patterns:
            try:
                origin = pattern.search(content, re.S)
                if origin:
                    if incomplete_original_command_check(origin.group(1)):
                        continue
                    new_origin_command_mapping[command] = origin.group(1)
                    # content = content.replace("\\%s"%command, origin.group(1))
            except:
                continue
    return new_origin_command_mapping

@time_it
def renew_command_find(content):
    print("function renew_command_find")

    renew_origin_command_mapping = dict()
    renew_command_pattern = re.compile(r'\\renewcommand{\\(.*?)}')
    renew_commands = renew_command_pattern.findall(content)
    
    for command in renew_commands:

        find_patterns = [
            r"\\renewcommand{\\%s}{(.*?)}"% command,
            r"\\renewcommand{\\%s}{([^{}]*\{(?:[^{}]*\{[^{}]*\}[^{}]*)*\}[^{}]*)}"% command,
        ]
    
        find_patterns = [re.compile(item) for item in find_patterns]
        
        for pattern in find_patterns:
            try:
                origin = pattern.search(content, re.S)
                if origin:
                    if incomplete_original_command_check(origin.group(1)):
                        continue
                    renew_origin_command_mapping[command] = origin.group(1)
                    # content = content.replace("\\%s"%command, origin.group(1))
            except:
                continue
    return renew_origin_command_mapping

@time_it
def def_command_find(content):
    def_command_mapping = dict()
    def_command_pattern = r"\\def\\(.*?){"
    new_def_commands = re.findall(def_command_pattern, content)

    for command in new_def_commands:
        # case: \def\intlarge{\mathop{\int}\limits}  TODO

        find_patterns = [
            r"\\def\\%s{(.*?)}" % command,
            r"\\def\\%s{([^{}]*\{(?:[^{}]*\{[^{}]*\}[^{}]*)*\}[^{}]*)}" % command,
        ]

        for pattern in find_patterns:
            try:
                original_command = re.search(pattern, content)
                if original_command:
                    if incomplete_original_command_check(original_command.group(1)):
                        continue
                    def_command_mapping[command] = original_command.group(1)
            except:
                continue

    return def_command_mapping

@time_it
def optimized_new_command_find(content):
    
    command_def_pattern = re.compile(r'\\newcommand{\\(.*)}{(.*)}')

    results = re.findall(command_def_pattern, content)
    
    command_defs = {}
    for name, def_text in results:
        if incomplete_original_command_check(def_text):
            continue
        if re.match(r".*?(?=#[0-9]+)", name):
            if re.match(r".*?(?=#[0-9]+)", def_text):
                continue
        command_defs[name] = def_text
    return command_defs

@time_it
def optimized_renew_command_find(content):
    
    command_def_pattern = re.compile(r'\\renewcommand{\\(.*)}{(.*)}')

    results = re.findall(command_def_pattern, content)
    
    command_defs = {}
    for name, def_text in results:
        if incomplete_original_command_check(def_text):
            continue
        if re.match(r".*?(?=#[0-9]+)", name):
            if re.match(r".*?(?=#[0-9]+)", def_text):
                continue
        command_defs[name] = def_text
    return command_defs

@time_it
def optimized_def_command_find(content):
    command_def_pattern = re.compile(r'\\def\\(.*?){(.*)}')

    results = re.findall(command_def_pattern, content)
    
    command_defs = {}
    for name, def_text in results:
        if incomplete_original_command_check(def_text):
            continue
        if re.match(r".*?(?=#[0-9]+)", name):
            if re.match(r".*?(?=#[0-9]+)", def_text):
                continue
        command_defs[name] = def_text
    return command_defs

@time_it
def new_command_replace(content, to_be_replaced_main_body):
    print("replacing new command...")

    new_origin_command_mapping = dict()
    length = len(content)

    new_commands_mapping = optimized_new_command_find(content)
    renew_commands_mapping = optimized_renew_command_find(content)
    def_command_mapping = optimized_def_command_find(content)

    new_origin_command_mapping.update(new_commands_mapping)
    new_origin_command_mapping.update(renew_commands_mapping)
    new_origin_command_mapping.update(def_command_mapping)

    print(new_origin_command_mapping)

    for command in new_origin_command_mapping:
        to_be_replaced_main_body = to_be_replaced_main_body.replace("\\%s"%command, new_origin_command_mapping[command])
    return to_be_replaced_main_body

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
def extract_abstract(content):
    print("extracting abstract...")

    patterns = [
        r"\\begin{abstract}([\s\S]*)\\end{abstract}",
        r"\\abstract([\s\S]*)\\endabstract"
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.S)
        if match:
            break
    if match:
        abstract = match.group(1)
    else:
        abstract = ""
        print("extracting abstract fails")
    return abstract.strip()

@time_it
def extract_introduction(content):
    print("extracting introduction...")
    intro_start_pattern = r"\\section\*?{introduction}"
    intro_start_match = re.search(intro_start_pattern, content, re.I)
    if intro_start_match:
        intro_content = content[intro_start_match.end():]

        next_section_pattern = r"\\section\*?{.*?}"
        next_section_start_match = re.search(next_section_pattern, intro_content)

        if next_section_start_match:
            return intro_content[:next_section_start_match.start()].strip()
        return intro_content.strip()
    else:
        return ""

@time_it
def replace_formatting_commands(content):
    print("replacing formatting commands...")

    replaced_command_patterns = [
        r"\\clearpage",
        r"\\newpage",
        r"\\smallskip",
        r"\\medskip",
        r"\\bigskip",
        r"\\hfill",
        r"\\vfill",
        r"\\vspace{.*?}"
    ]
    replaced_content = content
    for pattern in replaced_command_patterns:
        replaced_content = re.sub(pattern, "\n", replaced_content)

    return replaced_content

@time_it
def replace_excessive_newlines(content):
    print(f"replacing excessive newlines...")
    excessive_newlines_pattern = r"\n{3,}"
    cleaned_content = re.sub(excessive_newlines_pattern, "\n\n", content)
    return cleaned_content

@time_it
def clean_figure_environment(content):
    print("cleaning figure environment...")

    figure_pattern = re.compile(r"\\begin{figure(\*{0,1})}(.*?)\\end{figure(\*{0,1})", re.DOTALL)

    matches = re.findall(figure_pattern, content)

    for match in matches:
        figure_match = match[1]
        captions = re.findall(r"\\caption{(.*?)}", figure_match, re.DOTALL)
        labels = re.findall(r"\\label{(.*?)}", figure_match, re.DOTALL)
        replacement = ""
        if len(captions) == len(labels) and ("minipage" in figure_match or "subfigure" in figure_match):
            for i in range(len(captions)):
                if captions[i] == "":
                    continue
                replacement += "\n\\caption{" + captions[i] + "}\n"
                replacement += "\\label{" + labels[i] + "}\n"
            content = content.replace(figure_match, replacement)
        else:
            if len(captions):
                for i in range(len(captions)):
                    if captions[i] == "":
                        continue
                    replacement += "\n\\caption{" + captions[i] + "}\n"
            if len(labels):
                for i in range(len(labels)):
                    replacement += "\\label{" + labels[i] + "}\n"
            if replacement != "":
                content = content.replace(figure_match, replacement)
            else:
                content = content.replace("\\begin{figure}" + figure_match + "\\end{figure}", "")
                content = content.replace("\\begin{figure*}" + figure_match + "\\end{figure*}", "")
    return content

@time_it
def remove_acknowledgements(content):
    print("removing acknowledgements...")

    pattern = r"\\(section|subsection|subsubsection|chapter|begin)\*?({acknowledgements}|{acknowledgement}|{ack}|acknowledgments|acknowledgement)"
    match = re.search(pattern, content, re.I)
    print(match)

    if match:
        ack_content = content[match.end():]
        end_pattern = r"\\(begin{|section|subsection|subsubsection|bibliography|end{document}|end{ack})"
        end_match = re.search(end_pattern, ack_content, re.I)
        if end_match:
            return content[:match.start()] + "\n" + content[match.end() + end_match.start():]
        else:
            return content[:match.start()] + "\n" + "\\end{document}"
    else:
        print("No acknowledgement section")
        return content

@time_it
def remove_bibliography_lines(content):
    print("removing bibliography lines...")
    
    pattern = r"\\begin{thebibliography}([\s\S]*)\\end{thebibliography}"

    heuristic_start = int(len(content)/3)*2
    match = re.search(pattern, content[heuristic_start:])
    final_content = ""
    if match:
        print(match.start())
        print(match.end())
        final_content = content.replace("\\begin{thebibliography}" + match.group(1) + "\\end{thebibliography}", "\n")
    else:
        print("no bibliography")
        final_content = content


    final_content = final_content.replace("\\section{References}", "\n")

    bib_pattern = r'\\bibliographystyle{.*?}|\\bibliography{.*?}'
    final_content = re.sub(bib_pattern, "\n", final_content)
    return final_content



def cal_tokens_number_via_tiktoken(doc):
    print("**"*50)
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(doc))
    print(f"The number of tokens (cl100k_base) is {num_tokens} tokens")

    encoding = tiktoken.get_encoding("p50k_base")
    num_tokens = len(encoding.encode(doc))
    print(f"The number of tokens (p50k_base) is {num_tokens} tokens")

    encoding = tiktoken.get_encoding("r50k_base")
    num_tokens = len(encoding.encode(doc))
    print(f"The number of tokens (r50k_base) is {num_tokens} tokens")


@time_it_break(timeout=5 * 60)
def tex_file_clean_pipeline(content):
    if content == "" or content is None:
        return None

    content = remove_comments(content)

    # cal_tokens_number_via_tiktoken(content)
    title = extract_title(content)
    
    main_body = extract_tex_main_body(content)
    
    main_body = new_command_replace(content, main_body)

    if title is not None:
        print(f"extracted title is: {title}")
        main_body = replace_title(title, main_body).strip()


    main_body = clean_figure_environment(main_body)

    main_body = remove_acknowledgements(main_body)

    main_body = remove_bibliography_lines(main_body)

    main_body = replace_formatting_commands(main_body)
    main_body = replace_excessive_newlines(main_body)

    return main_body

# # # # # # # # # # # # # Processing a arxiv folder # # # # # # # # # # # # #

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

def traverse_directory(directory):
    all_files = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            all_files.append(os.path.join(root, filename))
    return all_files

def check_main_tex_document(path):
    content = read_tex_file(path)
    if content == None:
        return False
    pattern = r"\\begin{document}"
    match = re.search(pattern, content)
    if match:
        return True
    else:
        return False


def merge_a_tex_dir(directory):
    global NO_TEX_DIR_NUM
    global NO_MAIN_TEX_DIR_NUM
    

    all_files = traverse_directory(directory)
    all_tex_files = []

    for filepath in all_files:
        if filepath.lower().endswith(".tex"):
            all_tex_files.append(filepath)
    print(all_tex_files)
    print(len(all_tex_files))

    if len(all_tex_files) == 0:
        NO_TEX_DIR_NUM += 1
        return None
    if len(all_tex_files) == 1:
        print("Only single tex file...")
        return read_tex_file(all_tex_files[0])
    assert len(all_tex_files) > 1

    main_tex_file_path = None        
    for tex_path in all_tex_files:
        if check_main_tex_document(tex_path):
            main_tex_file_path = tex_path
            break
    # assert main_tex_file_path != None
    if main_tex_file_path == None:
        NO_MAIN_TEX_DIR_NUM += 1
        return None


    main_tex_content = read_tex_file(main_tex_file_path)


    #  \input{} command
    input_pattern = r"\\(input|include){(.*?)}"

    input_matches = re.findall(input_pattern, main_tex_content)
    print(input_matches)
    for match in input_matches:
        input_tex_path = match[1]
        if ".tex" not in input_tex_path.lower():
            input_tex_path += ".tex"
        input_tex_full_path = os.path.join(directory, input_tex_path)
        if not os.path.exists(input_tex_full_path) or not os.path.isfile(input_tex_full_path):
            continue
        input_tex_content = read_tex_file(input_tex_full_path)
        main_tex_content = main_tex_content.replace("\\%s{%s}" % (match[0], match[1]), input_tex_content)
        print(f"{input_tex_full_path} replace success!")
    
    # processing \import{}{} command

    import_dir_pattern = r"import\*?{(.*?)}"
    import_dir_matches = re.findall(import_dir_pattern, main_tex_content, re.S)

    for match in import_dir_matches:
        import_dir = match
        cur_import_file_pattern = r"import\*?{%s}{(.*?)}"%import_dir

        import_file_matches = re.findall(cur_import_file_pattern, main_tex_content, re.S)

        for import_file in import_file_matches:
            original_import_file = import_file
            if ".tex" not in import_file.lower():
                import_file += ".tex"
            import_file_full_path = os.path.join(directory, import_dir, import_file)

            if not os.path.exists(import_file_full_path) or not os.path.isfile(import_file_full_path):
                continue
            import_file_content = read_tex_file(import_file_full_path)
                
            main_tex_content = main_tex_content.replace("\\import{%s}{%s}"%(import_dir, original_import_file), import_file_content)
            main_tex_content = main_tex_content.replace("\\import*{%s}{%s}"%(import_dir, original_import_file), import_file_content)
            main_tex_content = main_tex_content.replace("\\subimport{%s}{%s}"%(import_dir, original_import_file), import_file_content)
            main_tex_content = main_tex_content.replace("\\subimport*{%s}{%s}"%(import_dir, original_import_file), import_file_content)

            print(f"{import_file_full_path} replace success!")

    return main_tex_content


def write_tex_to_file(tex_content, target_file_path):
    with open(target_file_path, "w", encoding = "utf-8") as f:
        f.write(tex_content)

def init_args():
    parser = argparse.ArgumentParser("Tex files cleaning args")
    parser.add_argument("--just_a_trial_mode", action = "store_true")
    parser.add_argument("--parsing_dir", action = "store_true")
    parser.add_argument("--tex_files_dir", type = str, default = None)
    parser.add_argument("--parsing_single_tex_file", action = "store_true")
    parser.add_argument("--parsing_single_tex_file_path", type = str)
    parser.add_argument("--output_path", type = str, default = "cleaned_output.tex")

    parser.add_argument("--whole_arxiv_cleaning_mode", action = "store_true")
    parser.add_argument("--raw_arxiv_tex_files_dir", type = str, required = False, default = "./merge_math_tex_data")
    parser.add_argument("--cleaned_arxiv_tex_files_save_dir", type = str, required = False, default = "./cleaned_math_tex_data")
    parser.add_argument("--cleaned_data_version", type = float, required = False, default = 0.1)
    parser.add_argument("--cleaning_timeout_seconds", type = int, required = False, default = 5 * 60)

    args = parser.parse_args()

    return args

def run_with_timeout(func, timeout):
    start_time = time.time()
    result = func()
    end_time = time.time()

    if end_time - start_time > timeout:
        print(f"{func} took too long to execute. Skipping.")
        return None

    return result

    

if __name__ == "__main__":

    args = init_args()
    print(args)

    if args.just_a_trial_mode:
        if args.parsing_dir:
            content = merge_a_tex_dir(args.parsing_dir)
            cleaned_content = tex_file_clean_pipeline(content)
        elif args.parsing_single_tex_file:
            content = read_tex_file(args.parsing_single_tex_file_path)
            cleaned_content = tex_file_clean_pipeline(content)
        if cleaned_content:
            if args.output_path != "None":
                write_tex_to_file(cleaned_content, args.output_path)
                print(f"write tex to file successfully!")
            else:
                # pass
                print(cleaned_content)
    elif args.whole_arxiv_cleaning_mode:
        final_save_dir = args.cleaned_arxiv_tex_files_save_dir + f"_v{str(args.cleaned_data_version)}"
        create_dir(final_save_dir)

        def _arxiv_clean_pipeline(full_path, save_dir):
            basename = ""
            if os.path.isdir(full_path):
                basename = os.path.basename(full_path)
                assert basename != ""
                if basename.startswith("dir_"):
                    basename = basename.replace("dir_", "")
                basename += ".tex"
                save_path = os.path.join(save_dir, basename)
                if os.path.exists(save_path) and os.path.getsize(save_path):
                    print(f"{save_path} already exists")
                    return 
                print(f"Processing {full_path}...")
                content = merge_a_tex_dir(full_path)
                cleaned_content = tex_file_clean_pipeline(content)

                if cleaned_content:
                    write_tex_to_file(cleaned_content, save_path)
                    print(f"{save_path} is successfully written and saved...")
            elif os.path.isfile(full_path):
                basename = os.path.basename(full_path)
                assert basename != ""
                if ".tex" not in basename:
                    basename += ".tex"
                save_path = os.path.join(save_dir, basename)
                if os.path.exists(save_path) and os.path.getsize(save_path):
                    print(f"{save_path} already exists")
                    return 
                print(f"Processing {full_path}...")
                content = read_tex_file(full_path)
                cleaned_content = tex_file_clean_pipeline(content)
                # cleaned_content = run_with_timeout(lambda: tex_file_clean_pipeline(content), args.timeout_seconds)
                if cleaned_content:
                    write_tex_to_file(cleaned_content, save_path)
                    print(f"{save_path} is successfully written and saved...")
            return 
        
        filenames = os.listdir(args.raw_arxiv_tex_files_dir)
        futures = []
        with print_time(f"cleaning {args.raw_arxiv_tex_files_dir} dir"):
            with ThreadPoolExecutor(max_workers = 200) as executor:
                for filename in tqdm(filenames):
                    full_path = os.path.join(args.raw_arxiv_tex_files_dir, filename)
                    future = executor.submit(_arxiv_clean_pipeline, full_path, final_save_dir)
                    futures.append(future)
                for future in tqdm(futures):
                    result = future.result()
                executor.shutdown()


    # META_DIR = "./case_study"
    # for dir_name in os.listdir(META_DIR):
    #     path = os.path.join(META_DIR, dir_name)
    #     content = merge_a_tex_dir(path)
    #     if content:
    #         cleaned_content = tex_file_clean_pipeline(content)
    
    print(f"# of dir without .tex files :{NO_TEX_DIR_NUM}")
    print(f"# of dir without main tex file :{NO_MAIN_TEX_DIR_NUM}")
