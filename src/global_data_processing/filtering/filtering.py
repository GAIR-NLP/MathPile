import string
import re
import os
import json
from multiprocessing import Pool, Manager
import time
import copy

from utils import *

def contains_lorem_ipsum(content):
    # from C4, detect it.
    normalized_content = content.lower()

    return 'lorem ipsum' in normalized_content

def filter_lorem_ipsum(content):
    if not contains_lorem_ipsum(content):
        return content

    final_lines = []
    for line in content.split("\n"):
        if contains_lorem_ipsum(line):
            if len(line.lower().replace("lorem ipsum", "")) < 5:
                print(line)
                continue
            else:
                final_lines.append(line)
        else:
            final_lines.append(line)
    final_content = "\n".join(final_lines)
    if final_content != content:
        print(f"{len(content)} -> {len(final_content)}")
    return final_content


def count_sentences(content):
    # refer to C4, if less than 3 sentences, will be removed.
    # TODO
    sentences = re.findall(r'\b[^.!?]+[.!?]*', content)

    return len(sentences)

def detect_javescript_line(line):
    # some examples:
    # MathOverflow works best with JavaScript enabled
    # Cross Validated works best with JavaScript enabled
    # You need JavaScript enabled to view it.

    count = line.lower().count('javascript')
    detect_words = ['enable', 'disable', 'browser']
    if count:
        for word in detect_words:
            if word in line and len(line) < 200:
                return True
    return False


def filter_javascript_lines(content):
    # refer to C4, improved by us 
    lines = content.split('\n')

    javascript_counts = [line.lower().count('javascript') for line in lines]
    if sum(javascript_counts):
        print("*******"*10)
    
    final_lines = []
    for line in lines:
        if detect_javescript_line(line):
            print("*"*10)
            print(line)
        else:
            final_lines.append(line)
    final_content = "\n".join(final_lines)
    if final_content != content:
        print(f"{len(content)} -> {len(final_content)}")
    return final_content


def calculate_uppercase_fraction(content):
    # from Pretrainer's Guide
    words = content.split()

    uppercase_count = sum(word.isupper() for word in words)

    total_count = len(words)
    if total_count == 0:
        return 0

    return uppercase_count / total_count

def filter_doc_via_uppercase_fraction(content):
    ratio = calculate_uppercase_fraction(content)
    if ratio > 0.4:
        return None
    else:
        return (content, ratio)

def calculate_ellipsis_fraction(content):
    # from Gopher, more than 30%, will be removed.
    lines = content.split('\n')

    ellipsis_count = sum(line.endswith('...') or line.endswith('…') for line in lines)

    total_lines = len(lines)
    if total_lines == 0:
        return 0

    return ellipsis_count / total_lines

def filter_doc_via_ellipsis_fraction(content):

    ratio = calculate_ellipsis_fraction(content)
    
    if ratio > 0.3:
        return None
    else:
        return (content, ratio)


def calculate_non_alphabetical_fraction(content):
    # from Gopher, if more than 20%, will be remove
    words = content.split()

    non_alphabetical_count = sum(not any(char.isalpha() for char in word) for word in words)

    total_count = len(words)
    if total_count == 0:
        return 0

    return non_alphabetical_count / total_count

def filter_doc_via_non_alphabetical_fraction(content):

    ratio = calculate_non_alphabetical_fraction(content)

    if ratio > 0.8:
        return None
    else:
        return (content, ratio)


def calculate_mean_length_of_alpha_words(content):
    # from Gopher, if outside the range of 3 to 10 characters, will be removed.
    words = content.split()

    alpha_words = [word for word in words if word.isalpha()]

    total_length = sum(len(word) for word in alpha_words)

    total_alpha_words = len(alpha_words)
    if total_alpha_words == 0:
        return 0

    return total_length / total_alpha_words

def filter_doc_via_mean_length_of_alpha_words(content):

    ratio = calculate_mean_length_of_alpha_words(content)

    if ratio > 10 or ratio < 3:
        return None
    else:
        return (content, ratio)


def contain_stop_words(content, min_count=2):
    # from Gopher
    
    stop_words = {"the", "be", "to", "of", "and", "that", "have", "with"}

    words = content.lower().split()
    count = sum(word in stop_words for word in words)
    if count >= min_count:
        return True

    return False

def filter_doc_via_containing_stop_words(content):
    if not contain_stop_words(content):
        return None 
    else:
        return content


def calculate_symbols_to_words_ratio(content):
    # from Gopher, if more than 0.1, will be removed.

    # symbols = {"#", "...", "…"}
    symbols = {"...", "…"} # do not consider "#", due to the characteristics of the math domain

    words = content.split()

    symbol_count = sum(content.count(symbol) for symbol in symbols)

    total_words = len(words)
    if total_words == 0:
        return 0

    return symbol_count / total_words

def filter_doc_via_symbols_to_words_ratio(content):
    ratio = calculate_symbols_to_words_ratio(content)
    if ratio > 0.5:
        return None
    else:
        return (content, ratio)

def calculate_lines_start_with_bullet_point_fraction(content):
    # refer to Gopher, if more than 90% lines in a doc starting with a bullet point, will be removed.
    bullet_points = {'\u2022', '\u2023', '\u25B6', '\u25C0', '\u25E6',
                     '\u25A0', '\u25A1', '\u25AA', '\u25AB', '\u2013'}

    lines = content.split('\n')

    starts_with_bullet = [line.startswith(tuple(bullet_points)) for line in lines]


    return sum(starts_with_bullet) / len(starts_with_bullet)

def filter_doc_via_lines_start_with_bullet_point_fraction(content):
    ratio = calculate_lines_start_with_bullet_point_fraction(content)
    if ratio > 0.9:
        return None
    else:
        return (content, ratio)


def calculate_uppercase_ratio_per_line(content):
    # refer to RefinedWeb, If it is mainly composed of uppercase characters, will be discarded.
    # TODO
    lines = content.split('\n')

    uppercase_ratios = []
    for line in lines:
        uppercase_count = sum(char.isupper() for char in line)
        total_characters = len(line)

        if total_characters == 0:
            ratio = 0
        else:
            ratio = uppercase_count / total_characters
        
        if ratio > 0.5:
            print("*"*50)
            print(line)

        uppercase_ratios.append(ratio)

    return uppercase_ratios


def detect_short_line(line):
    # refer to RefinedWeb, 
    # If it is short (≤ 10 words) and matches a pattern (edit):
    #     – At the beginning of the line (e.g. sign-in);
    #     – At the end of the line (e.g. Read more...);
    #     – Anywhere in the line (e.g. items in cart).
    pattern = r"Login|sign-in|read more\.{3}|items in cart"
    words = line.split()
    if len(words) <= 10 and re.search(pattern, line):
        return True
    return False


def remove_short_lines(content):
    
    lines = content.split('\n')
    final_lines = []
    for line in lines:
        if detect_short_line(line):
            print("*"*50)
            print(line)
            continue
        else:
            final_lines.append(line)
    final_content = "\n".join(lines)

    if final_content != content:
        print(f"{len(content)} -> {len(final_content)}")

    return final_content

def count_characters_without_spaces_punctuation(content):
    # refer to Slimpajama, if less than 200 characters, will be removed.
    content = content.replace(" ", "").replace("\n", "").replace("\t", "")

    content = content.translate(str.maketrans('', '', string.punctuation))

    return len(content)

def filter_doc_via_char_nums(content):
    num = count_characters_without_spaces_punctuation(content)

    if num < 200:
        return None
    else:
        return (content, num)

def filtering_content_pipeline(content):

    filtered_content = filter_lorem_ipsum(content)

    filtered_content = filter_javascript_lines(filtered_content)

    
    update_meta = {}
    filtered_content = remove_short_lines(filtered_content)


    filtered_content = filter_doc_via_uppercase_fraction(filtered_content)
    if filtered_content == None:
        return None
    else:
        filtered_content, uppercase_word_ratio = filtered_content
        update_meta['uppercase_word_ratio'] = uppercase_word_ratio


    
    filtered_content = filter_doc_via_ellipsis_fraction(filtered_content)
    if filtered_content == None:
        return None
    else:
        filtered_content, ellipsis_line_ratio = filtered_content
        update_meta['ellipsis_line_ratio'] = ellipsis_line_ratio

    filtered_content = filter_doc_via_non_alphabetical_fraction(filtered_content)
    if filtered_content == None:
        return None
    else:
        filtered_content, non_alphabetical_char_ratio = filtered_content
        update_meta['non_alphabetical_char_ratio'] = non_alphabetical_char_ratio
    
    filtered_content = filter_doc_via_mean_length_of_alpha_words(filtered_content)
    if filtered_content == None:
        return None
    else:
        filtered_content, mean_length_of_alpha_words = filtered_content
        update_meta['mean_length_of_alpha_words'] = mean_length_of_alpha_words

    
    filtered_content = filter_doc_via_containing_stop_words(filtered_content)
    if filtered_content == None:
        return None
    else:
        update_meta['contain_at_least_two_stop_words'] = True

    filtered_content = filter_doc_via_symbols_to_words_ratio(filtered_content)
    if filtered_content == None:
        return None
    else:
        filtered_content, symbols_to_words_ratio = filtered_content
        update_meta['symbols_to_words_ratio'] = symbols_to_words_ratio

    
    filtered_content = filter_doc_via_lines_start_with_bullet_point_fraction(filtered_content)
    if filtered_content == None:
        return None
    else:
        filtered_content, lines_start_with_bullet_point_ratio = filtered_content
        update_meta['lines_start_with_bullet_point_ratio'] = lines_start_with_bullet_point_ratio

    filtered_content = filter_doc_via_char_nums(filtered_content)
    if filtered_content == None:
        return None
    else:
        filtered_content, char_num_after_normalized = filtered_content
        update_meta['char_num_after_normalized'] = char_num_after_normalized
    
    if filtered_content == None:
        return None
    return (filtered_content, update_meta)


def filtering_full_pipeline(args):
    chunk, return_dict = args
    local_total_docs = 0
    local_docs_after_filtering = 0

    processed_chunk = []

    if chunk[0]['subset'] == "StackExchange":
        for item in chunk:
            new_item = copy.deepcopy(item)
            new_item['answers'] = []
            new_item['question'] = {}

            all_q_a_items = []
            e = item['question']
            e['type'] = 'q'
            all_q_a_items.append(e)
            for e in item['answers']:
                e['type'] = 'a'
                all_q_a_items.append(e)

            for e in all_q_a_items:
                local_total_docs += 1
                content = e['Body']
                ret = filtering_content_pipeline(content)
                if ret == None:
                    continue
                content, update_meta = ret
                local_docs_after_filtering += 1
                e['Body'] = content
                e.update(update_meta)
                if e['type'] == 'q':
                    del e['type']
                    new_item['question'] = e
                elif e['type'] == 'a':
                    del e['type']
                    new_item['answers'].append(e)
            if new_item['question'] != {} and new_item['answers'] != []:
                processed_chunk.append(new_item)

    else:
        for item in chunk:
            local_total_docs += 1
            content = item['text']
            ret = filtering_content_pipeline(content)
            if ret == None:
                continue
            content, update_meta = ret
            item['text'] = content
            item['meta'].update(update_meta)
            processed_chunk.append(item)
            local_docs_after_filtering += 1

    
    with return_dict_lock:
        return_dict['doc_num_after_filtering'] += local_docs_after_filtering
        return_dict['total_doc_num'] += local_total_docs
    
    return processed_chunk


if __name__ == "__main__":

    target_source = "wikipedia_update"
    CHUNK_SIZE = 5000
    num_processes = 96  # Set the number of processes you want to use
    meta_dir = "../data/LangID/"
    target_dir = "../data/filtering"
    ensure_directory_exists(target_dir)

    manager = Manager()
    return_dict = manager.dict({'total_doc_num': 0, 'doc_num_after_filtering': 0})
    return_dict_lock = manager.Lock()

    for path in paths[target_source]:
        start_time = time.time()

        ensure_directory_exists(os.path.join(target_dir, target_source))
        file_chunks = split_large_file(os.path.join(meta_dir, path), CHUNK_SIZE)
        pool_args = []
        for chunk in file_chunks:
            pool_args.append((chunk, return_dict))
        all_chunks_after_filter = []
        with Pool(processes=num_processes) as pool:
            results = pool.map(filtering_full_pipeline, pool_args)
            for result in results:
                print(type(result))
                print(len(result))
                all_chunks_after_filter.extend(result)

            # all_chunks_after_filter = pool.map(filtering_full_pipeline, pool_args)
            print(len(all_chunks_after_filter))
            # print(type(all_chunks_after_filter[0]))
            # print(len(all_chunks_after_filter[0]))

        write_into_jsonl_file(all_chunks_after_filter, os.path.join(target_dir, path))
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"******************{path}*******************")
        print(return_dict['doc_num_after_filtering'])
        print(return_dict['total_doc_num'])
        print(f"Cost time: {total_time/60:.2f} minutes")