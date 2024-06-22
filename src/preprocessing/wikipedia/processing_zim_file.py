from libzim.reader import Archive
from collections import defaultdict
import re
import html2text
from bs4 import BeautifulSoup, NavigableString
import random
import json
import os
from resiliparse.extract.html2text import extract_plain_text

def decode_content(doc):
    return bytes(doc).decode("UTF-8")

def write_list_to_jsonl(data, json_file_name):
    with open(json_file_name, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")
    print("Done")

def load_data_from_jsonl(jsonl_file_name):

  with open(jsonl_file_name, "r") as f:
    data = [json.loads(line) for line in f.readlines()]

  return data

def detach_data(zim):
    all_types = []
    type_to_data = defaultdict(list)
    for i in range(0, zim.all_entry_count):
        item = zim._get_entry_by_id(i)
        item_type = item.get_item().mimetype
        type_to_data[item_type].append(item.get_item())
        all_types.append(item_type)
    all_types = list(set(all_types))
    print(all_types)
    # print(len(all_types))
    for key in type_to_data:
        print(f"{key}: {len(type_to_data[key])}")
    return type_to_data

def gather_all_html_pages(type_to_data, jsonl_filename = "wikipedia_en_mathematics_nopic_2023-08_all_html.jsonl"):
    all_html_data = []
    for i in range(len(type_to_data['text/html'])):
        item = {}
        item['mimetype'] = type_to_data['text/html'][i].mimetype
        item['filesize'] = type_to_data['text/html'][i].size
        item['page_title'] = type_to_data['text/html'][i].title
        item['page_path'] = type_to_data['text/html'][i].path
        item['page_index'] = type_to_data['text/html'][i]._index
        item['content'] = decode_content(type_to_data['text/html'][i].content)
        all_html_data.append(item)
    write_list_to_jsonl(all_html_data, jsonl_filename)

# new added function: 2023/12/31
def processing_latex_conent(html_doc):
    from resiliparse.parse.html import HTMLTree
    tree = HTMLTree.parse(html_doc)
    for item in tree.body.get_elements_by_tag_name("math"):
        latex = "$" + item['alttext'].replace(r"{\displaystyle ", "").replace(r"{\textstyle","")[:-1] + "$"
        print(f"{item['alttext']} -> {latex}")
        item.text = latex
    for item in tree.body.get_elements_by_tag_name("img"):
        item.text = ""
    return tree

def convert_html_to_markdown(html_doc, remove_links = True, use_resiliparse = True):
    tree = processing_latex_conent(html_doc)
    if use_resiliparse:
        md_text = extract_plain_text(tree, alt_texts=False, links=False, preserve_formatting=True)      
    else:
        html_doc = tree.document.html
        html2md_converter = html2text.HTML2Text()
        html2md_converter.ignore_links = True
        md_text = html2md_converter.handle(html_doc)
    return md_text

def remove_in_paragraph_newline(md_text):

    pattern = re.compile(r'(?<=[\w.,;!?])\n(?=\w)', re.MULTILINE)

    segments = md_text.split('\n\n')  
    for i, segment in enumerate(segments):
        # if i in [1, 2, 4]:  
        segments[i] = re.sub(pattern, ' ', segment)  

    result_text = '\n\n'.join(segments)

    # # new add, v0.3 data
    # result_text = re.sub(r'(?<!\n)\n(?=[^\n\s])', ' ', result_text)
    # fix bugs: v0.4 data
    result_text = re.sub(r'(?<!\n)\n(?![\n\s#]|.*\|)', ' ', result_text)

    # print(result_text)
    return result_text

def clean_md_picture_and_save_placeholder_text(string):
    # pattern = r"!\[([^]]*)\]\([^)]*\)"
    pattern = r"!\[((?:[^\[\]]|\[[^\]]*\])*)\]\([^)]*\)"

    # result_string = re.sub(pattern, r"\1", string)
    # 20231231 update
    result_string = re.sub(pattern, "", string)
    return result_string

def convert_html_to_cleaned_md(raw_undecoded_content, remove_links = True, use_resiliparse = True):
    html_doc = decode_content(raw_undecoded_content)
    md_text = convert_html_to_markdown(html_doc, remove_links = remove_links, use_resiliparse = use_resiliparse)
    cleaned_md_text = clean_md_picture_and_save_placeholder_text(md_text)
    cleaned_md_text = replace_excessive_newlines(cleaned_md_text)
    cleaned_md_text = remove_wiki_template_term(cleaned_md_text)
    return cleaned_md_text

def replace_excessive_newlines(content):
    print(f"replacing excessive newlines...")
    # excessive_newlines_pattern = r"\n{3,}"
    excessive_newlines_pattern = re.compile(r'((\s*\n){3,})')
    cleaned_content = re.sub(excessive_newlines_pattern, "\n\n", content)
    return cleaned_content

def remove_wiki_template_term(md_doc):
    template = "This article is issued from Wikipedia. The text is licensed under Creative Commons - Attribution - Sharealike. Additional terms may apply for the media files."
    if template in md_doc:
        md_doc = md_doc.replace(template, "")
    return md_doc

def gather_all_cleaned_md_format_pages(type_to_data, jsonl_filename = "wikipedia_en_mathematics_nopic_2023-08_cleaned_md.jsonl"):
    all_cleaned_md_docs = []
    for i in range(len(type_to_data['text/html'])):
        item = {}
        item['mimetype'] = type_to_data['text/html'][i].mimetype
        item['filesize'] = type_to_data['text/html'][i].size
        item['page_title'] = type_to_data['text/html'][i].title
        item['page_path'] = type_to_data['text/html'][i].path
        item['page_index'] = type_to_data['text/html'][i]._index
        item['content'] = convert_html_to_cleaned_md(type_to_data['text/html'][i].content)
        all_cleaned_md_docs.append(item)
    write_list_to_jsonl(all_cleaned_md_docs, jsonl_filename)
    



if __name__ == "__main__":
    path = "wikipedia_en_mathematics_nopic_2023-08.zim"
    zim = Archive(path)
    type_to_data = detach_data(zim)
    # # gather_all_html_pages(type_to_data)
    gather_all_cleaned_md_format_pages(type_to_data, "wikipedia_en_mathematics_nopic_2023-08_cleaned_md_20231231_updated_w_resiliparse.jsonl")