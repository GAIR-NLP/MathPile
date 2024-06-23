import os
import json
from multiprocessing import Pool, Manager
import time
import copy

def load_data_from_jsonl(jsonl_file_name):

  with open(jsonl_file_name, "r") as f:
    data = [json.loads(line) for line in f.readlines()]

  return data

def write_into_jsonl_file(data, path):
    with open(path, 'w') as file:
        for d in data:
            json.dump(d, file)
            file.write('\n')
    print(f"{path} Done!")


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory created: {directory_path}")
    else:
        print(f"Directory already exists: {directory_path}")
    
paths = {
    "arXiv": ['arXiv/math_arXiv_v0.2.jsonl'],
    "commoncrawl": ['commoncrawl/C4_math_docs_chunk_0.jsonl', 'commoncrawl/CC_math_docs_chunk_0.jsonl'],
    "proofwiki": ['proofwiki/ProofWiki_definitions.jsonl', 'proofwiki/ProofWiki_theorem_proofs.jsonl'],
    "stackexchange": [
        'stackexchange/cs.stackexchange.com.jsonl', 
        "stackexchange/matheducators.stackexchange.com.jsonl",
        "stackexchange/physics.stackexchange.com.jsonl",
        "stackexchange/cstheory.stackexchange.com.jsonl",
        "stackexchange/mathematica.stackexchange.com.jsonl",
        "stackexchange/proofassistants.stackexchange.com.jsonl",
        "stackexchange/datascience.stackexchange.com.jsonl",
        "stackexchange/mathoverflow.net.jsonl",
        "stackexchange/tex.stackexchange.com.jsonl",
        "stackexchange/math.stackexchange.com.jsonl",
        "stackexchange/hsm.stackexchange.com.jsonl",
    ],
    "textbooks": ['textbooks/synthetic_textbooks_markdown.jsonl', "textbooks/textbooks_markdown.jsonl", "textbooks/textbooks_tex.jsonl"],
    "wikipedia": ['wikipedia/wikipedia_en_mathematics_nopic_2023-08.jsonl'],
    "wikipedia_update": ['wikipedia_update/wikipedia_en_mathematics_nopic_2023-08_math_latex_fix_20231231.jsonl']
}


def split_large_file(file_path, chunk_size):
    data = load_data_from_jsonl(file_path)
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i: i+chunk_size])
    return chunks