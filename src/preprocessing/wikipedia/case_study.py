import json
import os
import random

def load_data_from_jsonl(jsonl_file_name):
    with open(jsonl_file_name, "r") as f:
        data = [json.loads(line) for line in f.readlines()]
    return data

def print_example(item):
    for key in item:
        print(f"{'*'*30}{key}{'*'*30}")
        print(item[key])

path = "wikipedia_en_mathematics_nopic_2023-08_cleaned_md_20231231_updated_w_resiliparse.jsonl"

data = load_data_from_jsonl(path)

print(len(data))
random_idx = random.randint(0, len(data))



print_example(data[random_idx])

