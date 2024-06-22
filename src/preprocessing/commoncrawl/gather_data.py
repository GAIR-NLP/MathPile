import json
import os
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


chunk_idx = 0
CHUNK_SIZE = 1000000
for split in ['train']: # 'test', 'validation', 
    filter_dir = f"SlimPajama-627B/{split}"
    for saved_set in ['RedPajamaCommonCrawl', "RedPajamaC4"]:
        all_filenames = gci(filter_dir)
        target_data = []
        for path in all_filenames:
            if not path.endswith(".jsonl"):
                continue
            cur_chunk_data = load_data_from_jsonl(path)
            for item in cur_chunk_data:
                if item['meta']["redpajama_set_name"] != saved_set:
                    continue
                else:
                    target_data.append(item)
                    if len(target_data) == CHUNK_SIZE:
                        write_list_to_jsonl(target_data, f"{filter_dir.replace('/', '_')}_{saved_set}_chunk{chunk_idx}.jsonl")
                        chunk_idx += 1
                        print(f"Chunk: {chunk_idx}")
                        target_data = []
        if len(target_data):
            write_list_to_jsonl(target_data, f"{filter_dir.replace('/', '_')}_{saved_set}_chunk{chunk_idx}.jsonl")