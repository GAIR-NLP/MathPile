import os
import json


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

def write_into_jsonl_file(data, target_path):
    with open(target_path, "w") as f:
        for item in data:
            f.write(json.dumps(dict(item)) + "\n")
    print(f"write into {target_path} successfully!")


def collect_unanswered_questions(data, filter_score = None):
    unanswered_questions = []
    keys = ["PostTypeId", "AnswerCount", "CommentCount", "ContentLicense", "ViewCount"]
    for item in data:
        if item["PostTypeId"] not in ["1"]:
            continue
        if "AnswerCount" in item and item["AnswerCount"] != "0":
            continue
        for key in keys:
            if key in item:
                del item[key]
        if filter_score is not None and float(item["Score"]) < filter_score:
            continue
        unanswered_questions.append(item)
    return unanswered_questions


if __name__ == '__main__':

    dirnames = ['hsm.stackexchange.com', 'math.stackexchange.com', 'matheducators.stackexchange.com', 'mathematica.stackexchange.com', 'mathoverflow.net']
    # dirnames = ['physics.stackexchange.com', 'proofassistants.stackexchange.com', 'tex.stackexchange.com', 'datascience.stackexchange.com', 'cstheory.stackexchange.com', 'cs.stackexchange.com']
    
    META_DIR = "./first_step_preprocessed_posts"
    TARGET_META_DIR = "./good_questions"
    
    if not os.path.exists(TARGET_META_DIR):
        os.mkdir(TARGET_META_DIR)

    TARGET_DIR = f"{TARGET_META_DIR}/unanswered"
    if not os.path.exists(TARGET_DIR):
        os.mkdir(TARGET_DIR)

    FILTER_SCORE = None
    
    
    for dirname in dirnames:
        full_path = os.path.join(META_DIR, dirname + ".jsonl")
        all_posts = read_jsonl_file(full_path, delete_keys = True)
        final_data = collect_unanswered_questions(all_posts, FILTER_SCORE)
        print(dirname)
        print(len(final_data))
        target_path = os.path.join(TARGET_DIR, dirname + ".jsonl")
        write_into_jsonl_file(final_data, target_path)