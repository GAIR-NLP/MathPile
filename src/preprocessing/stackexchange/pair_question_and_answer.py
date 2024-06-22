import os
from lxml import etree
from bs4 import BeautifulSoup
import html
import json
from collections import defaultdict


def delete_keys_in_a_dict(item):
    keys = ['CreationDate', 'OwnerUserId', 'LastEditorUserId', 'LastEditDate', 'LastActivityDate']
    for key in keys:
        if key in item:
            del item[key]
    return item


def read_jsonl_file(path, delete_keys = True):
    data = []
    with open(path, "r") as f:
        for line in f:
            item = json.loads(line)
            if delete_keys:
                item = delete_keys_in_a_dict(item)
            data.append(item)
    return data

def pair_question_and_answer(data):
    question_id_to_item_dict = {}
    answer_id_to_item_dict = {}

    for item in data:
        if item["PostTypeId"] not in ["1", "2"]:
            continue
        if "AnswerCount" in item and item["AnswerCount"] == "0":
            continue
        if item["PostTypeId"] == "1":
            assert item["Id"] not in question_id_to_item_dict
            question_id_to_item_dict[item["Id"]] = item
        elif item["PostTypeId"] == "2":
            assert item["Id"] not in answer_id_to_item_dict
            answer_id_to_item_dict[item["Id"]] = item

    final_question_to_multiple_answer_dict = {}
    for id_key in answer_id_to_item_dict:
        answer_item = answer_id_to_item_dict[id_key]
        assert answer_item["PostTypeId"] == "2"

        corresponding_question_id = answer_item['ParentId']
        question_item = question_id_to_item_dict[corresponding_question_id]

        if "AcceptedAnswerId" in question_item:
            accepted_answer_id = question_item["AcceptedAnswerId"]
            accepted_answer_item = answer_id_to_item_dict[accepted_answer_id]
            # try:
            #     assert accepted_answer_item["ParentId"] == corresponding_question_id # new add
            # except:
            #     print(question_item)
        else:
            accepted_answer_id, accepted_answer_item = None, None

        if corresponding_question_id not in final_question_to_multiple_answer_dict:
            final_question_to_multiple_answer_dict[corresponding_question_id] = {}
        
        if "Question" not in final_question_to_multiple_answer_dict[corresponding_question_id]:
            final_question_to_multiple_answer_dict[corresponding_question_id]["Question"] = question_item
        
        if "AcceptedAnswer" not in final_question_to_multiple_answer_dict[corresponding_question_id]:
            final_question_to_multiple_answer_dict[corresponding_question_id]["AcceptedAnswer"] = accepted_answer_item
        
        if "OtherAnswers" not in final_question_to_multiple_answer_dict[corresponding_question_id]:
            final_question_to_multiple_answer_dict[corresponding_question_id]["OtherAnswers"] = []

        if id_key == accepted_answer_id:
            continue
        else:
            if answer_item not in final_question_to_multiple_answer_dict[corresponding_question_id]["OtherAnswers"]:
                final_question_to_multiple_answer_dict[corresponding_question_id]["OtherAnswers"].append(answer_item)
    
    return final_question_to_multiple_answer_dict

def convert_dict_to_list(final_dict):
    data = []
    for key in final_dict:
        data.append(final_dict[key])
    return data

def write_into_jsonl_file(data, target_path):
    with open(target_path, "w") as f:
        for item in data:
            f.write(json.dumps(dict(item)) + "\n")
    print(f"write into {target_path} successfully!")


if __name__ == "__main__":
    # dirnames = ['hsm.stackexchange.com', 'math.stackexchange.com', 'matheducators.stackexchange.com', 'mathematica.stackexchange.com', 'mathoverflow.net']
    dirnames = ['physics.stackexchange.com', 'proofassistants.stackexchange.com', 'tex.stackexchange.com', 'datascience.stackexchange.com', 'cstheory.stackexchange.com', 'cs.stackexchange.com']
    
    META_DIR = "./first_step_preprocessed_posts"
    TARGET_META_DIR = "./second_step_preprocessed_posts"
    
    if not os.path.exists(TARGET_META_DIR):
        os.mkdir(TARGET_META_DIR)
    
    for dirname in dirnames:
        full_path = os.path.join(META_DIR, dirname + ".jsonl")
        all_posts = read_jsonl_file(full_path, delete_keys = True)
        final_question_answer_dict = pair_question_and_answer(all_posts)
        final_data = convert_dict_to_list(final_question_answer_dict)
        print(len(final_data))
        target_path = os.path.join(TARGET_META_DIR, dirname + ".jsonl")
        write_into_jsonl_file(final_data, target_path)
    print("All Done!")

