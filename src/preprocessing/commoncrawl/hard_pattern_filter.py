import os
import json
from concurrent.futures import ThreadPoolExecutor
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import concurrent
from multiprocessing import Pool, cpu_count

def load_data_from_jsonl(jsonl_file_name):
  with open(jsonl_file_name, "r") as f:
    data = [json.loads(line) for line in f.readlines()]
  return data

def gci(filepath):
  result = []
  for fpathe, dirs, fs in os.walk(filepath):
    for f in fs:
      result.append(os.path.join(fpathe, f))
  return result

def write_list_to_jsonl(data, json_file_name):
    with open(json_file_name, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")
    print(f"{json_file_name} Done")

def read_txt_file(path):
    data = []
    with open(path, "r") as f:
        lines = f.readlines()
        for line in lines:
            data.append(line.strip())
    return data

def read_doc(path):
    with open(path, "r") as f:
        return f.read()


def check_math_content(text):
    if "\math" in text:
        if "$$" in text or "$" in text:
            return True
    patterns = [
        "\\begin{",
        "\\ldots",
        "\\vdots",
        "\\times",
        "\\infty", # REMOVE
        "\\frac{",
        "$x_{1}, \\ldots, x_{n}$",
        "$x_",
        "$\\alpha_{1}, \\ldots, \\alpha_{n}$",
        "$\\alpha",
    ]
    for item in patterns:
        if item in text:
            if "$$" in text or "$" in text:
                return True
    return False 

def process_path(path):
    results = []
    if not path.endswith(".jsonl"):
        return results
    data = load_data_from_jsonl(path)
    for idx, item in enumerate(data):
        # if "\math" in item['text']:
        if check_math_content(item['text']):
            results.append({"idx": idx, "path": path, 'text':item['text']})
    return results


def process_chunk(file_chunk):
    results = []
    for path in file_chunk:
        results.extend(process_path(path))
    return results
    

if __name__ == '__main__':
    
    all_c4_file_paths = gci("CC-data/C4_train")
    chunk_size = 32

    chunks = [all_c4_file_paths[i:i + chunk_size] for i in range(0, len(all_c4_file_paths), chunk_size)]

    num_processes = cpu_count() - 16 
    with Pool(processes=num_processes) as pool:
        all_results = pool.map(process_chunk, chunks)
        

    c4_results = [item for sublist in all_results for item in sublist]

    res_chunk_size = 1000000

    for i in range(0, len(c4_results), res_chunk_size):
        write_list_to_jsonl(c4_results[i: i + res_chunk_size], f"C4_train_hard_multiple_match_final_math_chunk_{i//res_chunk_size}.jsonl")

    # write_list_to_jsonl(c4_results, "CC_train_sim_cos_score.jsonl")