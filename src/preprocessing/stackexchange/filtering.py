import json
import os
from collections import defaultdict


def check_item(item, delete_keys = True):
    item_question = item['Question']
    item_accepted_answer = item['AcceptedAnswer']
    other_answers = item['OtherAnswers']
    if item_accepted_answer != None:
        try:
            assert item_question["Id"] == item_accepted_answer["ParentId"]
            assert item_question["AcceptedAnswerId"] == item_accepted_answer["Id"]
        except:
            # print(item)
            print("one assert error")
            return item
    for e in other_answers:
        assert item_question["Id"] == e["ParentId"]
    
    del item["Question"]['PostTypeId']
    if "AcceptedAnswerId" in item["Question"]:
        del item["Question"]["AcceptedAnswerId"]
    del item["Question"]["ViewCount"]
    del item["Question"]["AnswerCount"]
    del item["Question"]["CommentCount"]
    del item["Question"]["ContentLicense"]
    if "CommunityOwnedDate" in item["Question"]:
        del item["Question"]["CommunityOwnedDate"]

    keys = ["OwnerDisplayName", "LastEditorDisplayName"]

    if item_accepted_answer != None:
        del item["AcceptedAnswer"]["PostTypeId"]
        del item["AcceptedAnswer"]["ParentId"]
        del item["AcceptedAnswer"]["CommentCount"]
        del item["AcceptedAnswer"]["ContentLicense"]
        if "CommunityOwnedDate" in item["AcceptedAnswer"]:
            del item["AcceptedAnswer"]["CommunityOwnedDate"]
        for key in keys:
            if key in item["AcceptedAnswer"]:
                del item["AcceptedAnswer"][key]
    
    for idx in range(len(item['OtherAnswers'])):
        del item['OtherAnswers'][idx]["PostTypeId"]
        del item['OtherAnswers'][idx]["ParentId"]
        del item['OtherAnswers'][idx]["CommentCount"]
        del item['OtherAnswers'][idx]["ContentLicense"]
        if "CommunityOwnedDate" in item['OtherAnswers'][idx]:
            del item['OtherAnswers'][idx]["CommunityOwnedDate"]
        for key in keys:
            if key in item['OtherAnswers'][idx]:
                del item['OtherAnswers'][idx][key]
    return item

def read_jsonl_file(path, check_item_flag = True):
    data = []
    with open(path, "r") as f:
        for line in f:
            item = json.loads(line)
            if check_item_flag:
                item = check_item(item, delete_keys = True)
                if item == None:
                    continue
            data.append(item)
    return data

def filter_data(data):
    ret_data = []
    original_q_num = len(data)
    original_ans_num = 0
    final_ans_num = 0
    for item in data:
        if float(item['Question']["Score"]) < QUESTION_SCORE_FILTER_VALUE:
            continue
        cur_acc_ans_score = None
        min_ans_score = ANSWER_SCORE_FILTER_VALUE
        if item["AcceptedAnswer"] != None:
            cur_acc_ans_score = float(item["AcceptedAnswer"]["Score"])
            min_ans_score = min(cur_acc_ans_score, ANSWER_SCORE_FILTER_VALUE)
            final_ans_num += 1
            original_ans_num += 1
        
        remove_ans_idxs = []

        original_ans_num += len(item['OtherAnswers'])
        
        for idx in range(len(item['OtherAnswers'])):
            if float(item['OtherAnswers'][idx]["Score"]) < min_ans_score:
                remove_ans_idxs.append(idx)
        
        if len(item['OtherAnswers']) == len(remove_ans_idxs) and item["AcceptedAnswer"] == None:
            continue
        final_ans_num += len(item['OtherAnswers']) - len(remove_ans_idxs)
        
        for idx in sorted(remove_ans_idxs, reverse = True):
            del item['OtherAnswers'][idx]
        
        ret_data.append(item)
    
    print(f"Question: {original_q_num} -> {len(ret_data)}")
    print(f"Answer: {original_ans_num} -> {final_ans_num}")

    return ret_data

def write_into_jsonl_file(data, target_path):
    with open(target_path, "w") as f:
        for item in data:
            f.write(json.dumps(dict(item)) + "\n")
    print(f"write into {target_path} successfully!")

if __name__ == "__main__":
    # dirnames = ['math.stackexchange.com', 'mathoverflow.net', 'mathematica.stackexchange.com', 'matheducators.stackexchange.com', 'hsm.stackexchange.com']
    dirnames = ['physics.stackexchange.com', 'proofassistants.stackexchange.com', 'tex.stackexchange.com', 'datascience.stackexchange.com', 'cstheory.stackexchange.com', 'cs.stackexchange.com']
    
    META_DIR = "./second_step_preprocessed_posts"
    TARGET_META_DIR = "./final_filtered_posts"

    QUESTION_SCORE_FILTER_VALUE = 5
    ANSWER_SCORE_FILTER_VALUE = 5

    TARGET_META_DIR += f"/Q{QUESTION_SCORE_FILTER_VALUE}A{ANSWER_SCORE_FILTER_VALUE}"
    
    if not os.path.exists(TARGET_META_DIR):
        os.mkdir(TARGET_META_DIR)
    
    for dirname in dirnames:
        full_path = os.path.join(META_DIR, dirname + ".jsonl")
        all_posts = read_jsonl_file(full_path, check_item_flag = True)

        filtered_posts = filter_data(all_posts)
        print(f"{dirname}:{len(filtered_posts)}")

        target_path = os.path.join(TARGET_META_DIR, dirname + ".jsonl")
        write_into_jsonl_file(filtered_posts, target_path)
    print("All Done!")