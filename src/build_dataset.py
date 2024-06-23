import datasets
from datasets import load_dataset, Dataset, load_from_disk
from utils import load_data_from_jsonl
import sys, os
current_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder)
sys.path.append(parent_folder)
from utils import *


META_DIR = "./data/filtering/"
TARGET_DIR = "./data-built-on-datasets/filtering"

for source in paths:
    
    if source not in ["arXiv"]:
        continue
    for path in paths[source]:
        
        full_path = os.path.join(META_DIR, path)
        data = load_data_from_jsonl(full_path)
        for item in data:
            item['file_path'] = path
            if "synthetic_textbooks" in path:
                keys = ['outline', 'concepts', 'queries', 'context']
                for key in keys:
                    if key in item['meta']:
                        del item['meta'][key]

        ds = Dataset.from_list(data)
        ds.save_to_disk(os.path.join(TARGET_DIR, os.path.basename(path).replace(".jsonl", "")))
    print(f"{source} done!")


