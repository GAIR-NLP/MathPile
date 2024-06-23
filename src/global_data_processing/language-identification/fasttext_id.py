import fasttext
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
    "wikipedia_update": ['wikipedia/wikipedia_en_mathematics_nopic_2023-08_math_latex_fix_20231231.jsonl']
}

def split_large_file(file_path, chunk_size):
    data = load_data_from_jsonl(file_path)
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i: i+chunk_size])
    return chunks

def obtain_language_detection_probs(model, text, return_only_english=True, model_path = None):
    lang_labels, lang_probs = model.predict(text.replace("\n", " "), k=10)
    results = {}
    for i in range(len(lang_labels)):
        results[lang_labels[i].replace("__label__","")] = lang_probs[i]
    
    if return_only_english:
        if "eng_Latn" in results:
            return results['eng_Latn']
        if model_path == "lid.176.bin" and "en" in results:
            return results['en']
        else:
            return 0
    return results

def detect_language(args):
    chunk, model_path, return_dict = args
    model = fasttext.load_model(model_path)
    local_eng_docs = 0
    local_total_docs = 0
    local_ave_score = 0

    processed_chunk = []

    if chunk[0]['subset'] == "StackExchange":
        for item in chunk:
            new_item = copy.deepcopy(item)
            new_item['answers'] = []
            new_item['question'] = {}

            all_q_a_items = []
            e = item['question']
            e['type'] = 'q'
            all_q_a_items.append(e)
            for e in item['answers']:
                e['type'] = 'a'
                all_q_a_items.append(e)

            for e in all_q_a_items:
                eng_score = obtain_language_detection_probs(model = model, text = e['Body'], return_only_english=True, model_path = model_path)
                local_ave_score += eng_score
                local_total_docs += 1
                if eng_score > ENGLISH_FILTER_SCORE:
                    local_eng_docs += 1
                    e['language_detection_score'] = eng_score
                    if e['type'] == 'q':
                        del e['type']
                        new_item['question'] = e
                    elif e['type'] == 'a':
                        del e['type']
                        new_item['answers'].append(e)
                else:
                    print("=="*30 + str(eng_score) + "=="*30)
                    print(e['Body'])
            if new_item['question'] != {} and new_item['answers'] != []:
                processed_chunk.append(new_item)

    else:
        for item in chunk:
            eng_score = obtain_language_detection_probs(model = model, text = item['text'], return_only_english=True, model_path = model_path)
            local_ave_score += eng_score
            local_total_docs += 1
            if eng_score > ENGLISH_FILTER_SCORE:
                local_eng_docs += 1
                if 'meta' not in item:
                    item['meta'] = {}
                item['meta']['language_detection_score'] = eng_score
                processed_chunk.append(item)
            else:
                print("=="*30 + str(eng_score) + "=="*30)
                print(item['text'])
    
    with return_dict_lock:
        return_dict['eng_docs'] += local_eng_docs
        return_dict['total_docs'] += local_total_docs
        return_dict['ave_score'] += local_ave_score
    
    return processed_chunk




if __name__ == "__main__":
    model_path = "lid.176.bin"


    ENGLISH_FILTER_SCORE = 0.3
    CHUNK_SIZE = 5000
    manager = Manager()
    return_dict = manager.dict({'eng_docs': 0, 'total_docs': 0, 'ave_score': 0})
    return_dict_lock = manager.Lock()

    num_processes = 96  # Set the number of processes you want to use
    meta_dir = "../data/raw/"
    target_dir = "../data/LangID"
    ensure_directory_exists(target_dir)

    target_source = "arXiv"

    for path in paths[target_source]:
        start_time = time.time()

        ensure_directory_exists(os.path.join(target_dir, target_source))
        file_chunks = split_large_file(os.path.join(meta_dir, path), CHUNK_SIZE)
        pool_args = []
        for chunk in file_chunks:
            pool_args.append((chunk, model_path, return_dict))
        
        all_chunks_after_filter = []

        with Pool(processes=num_processes) as pool:
            results = pool.map(detect_language, pool_args)
            for result in results:
                all_chunks_after_filter.extend(result)
        write_into_jsonl_file(all_chunks_after_filter, os.path.join(target_dir, path))
        end_time = time.time()
        total_time = end_time - start_time
        print(f"******************{path}*******************")
        print(return_dict['eng_docs'])
        print(return_dict['total_docs'])
        print(return_dict['ave_score'] / return_dict['total_docs'] if return_dict['total_docs'] > 0 else 0)
        print(f"Cost time: {total_time/60:.2f} minutes")