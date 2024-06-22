import os
from lxml import etree
from bs4 import BeautifulSoup
import html
import json


def parsing_xml_file(path):
    tree = etree.parse(path)
    root = tree.getroot()
    all_posts = []
    for child in root:
        all_posts.append(child.attrib)
    return all_posts

def clean_html_content(content):
    body = html.unescape(content)
    try:
        soup = BeautifulSoup(body, features="html.parser")
    except:
        try:
            soup = BeautifulSoup(body, features="lxml")
        except:
            raise Exception        
    plain_text = soup.get_text()
    return plain_text

def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
        )

def remove_invalid_char(s):
    cleaned_string = ''.join(c for c in s if valid_xml_char_ordinal(c))
    return cleaned_string

def only_reverve_question_answer(data):
    ret_data = []
    for item in data:
        if item['PostTypeId'] not in ["1", "2"]:
            continue
        try:
            item['Body'] = remove_invalid_char(clean_html_content(item['Body']))
        except :
            print(item['Body'])
            raise Exception
        ret_data.append(item)
    return ret_data

def write_into_jsonl_file(data, target_path):
    with open(target_path, "w") as f:
        for item in data:
            f.write(json.dumps(dict(item)) + "\n")
    print(f"write into {target_path} successfully!")


if __name__ == "__main__":
    # dirnames = ['hsm.stackexchange.com', 'math.stackexchange.com', 'matheducators.stackexchange.com', 'mathematica.stackexchange.com', 'mathoverflow.net']
    dirnames = ['physics.stackexchange.com', 'proofassistants.stackexchange.com', 'tex.stackexchange.com', 'datascience.stackexchange.com', 'cstheory.stackexchange.com', 'cs.stackexchange.com']
    META_DIR = "./raw_data"
    TARGET_META_DIR = "./first_step_preprocessed_posts"

    if not os.path.exists(TARGET_META_DIR):
        os.mkdir(TARGET_META_DIR)

    for dirname in dirnames:
        full_path = os.path.join(META_DIR, dirname, "Posts.xml")

        all_posts = parsing_xml_file(full_path)

        processed_posts = only_reverve_question_answer(all_posts)

        target_path = os.path.join(TARGET_META_DIR, dirname+".jsonl")

        write_into_jsonl_file(processed_posts, target_path)
        print(f"{dirname}: {len(all_posts)}")
    print("done!")