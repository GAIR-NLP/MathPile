import tiktoken
import os
from tqdm import tqdm
import json
from transformers import AutoTokenizer
from concurrent.futures import ThreadPoolExecutor
import time
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")


def cal_tokens_number_via_tiktoken(doc):
    # print("**"*50)
    encoding = tiktoken.get_encoding("cl100k_base")
    cl100k_num_tokens = len(encoding.encode(doc))
    # print(f"The number of tokens (cl100k_base) is {cl100k_num_tokens} tokens")

    encoding = tiktoken.get_encoding("p50k_base")
    p50k_num_tokens = len(encoding.encode(doc))
    # print(f"The number of tokens (p50k_base) is {p50k_num_tokens} tokens")

    encoding = tiktoken.get_encoding("r50k_base")
    r50k_num_tokens = len(encoding.encode(doc))
    # print(f"The number of tokens (r50k_base) is {r50k_num_tokens} tokens")

    return cl100k_num_tokens, p50k_num_tokens, r50k_num_tokens

def cal_tokens_number_via_GPT_NEOX_20B(doc):
    return len(tokenizer.tokenize(doc))


def cal_tokens_of_a_jsonl_file(path):
    all_cl100k_tokens_num, all_p50k_tokens_num, all_r50k_tokens_num = 0, 0, 0
    GPTNeoX_tokens_num = 0
    with open(path, "r") as f:
        for line in f:
            texts = []
            item = json.loads(line)
            texts.append(item['Question']['Body'])
            texts.append(item['Question']['Title'])
            if item['AcceptedAnswer'] != None:
                texts.append(item['AcceptedAnswer']['Body'])
            for e in item['OtherAnswers']:
                texts.append(e['Body'])
            content = " ".join(texts)

            cl100k, p50k, r50k = cal_tokens_number_via_tiktoken(content)
            all_cl100k_tokens_num += cl100k
            all_p50k_tokens_num += p50k
            all_r50k_tokens_num += r50k
            GPTNeoX_tokens_num += cal_tokens_number_via_GPT_NEOX_20B(content)
    return all_cl100k_tokens_num, all_p50k_tokens_num, all_r50k_tokens_num, GPTNeoX_tokens_num


if __name__ == "__main__":

    TARGET_PATH = "final_filtered_posts/Q5A5"

    filtered_dirnames = ['math.stackexchange.com', 'mathoverflow.net', 'mathematica.stackexchange.com', 'matheducators.stackexchange.com', 'hsm.stackexchange.com']

    dirnames = os.listdir(TARGET_PATH)
    start_time = time.time()
    all_cl100k_tokens_num, all_p50k_tokens_num, all_r50k_tokens_num, GPTNeoX_tokens_num = 0,0,0,0
    for dirname in dirnames:
        full_path = os.path.join(TARGET_PATH, dirname)
        if not os.path.isfile(full_path) or not full_path.endswith(".jsonl"):
            continue
        filter_flag = False
        for filtername in filtered_dirnames:
            if filtername in full_path:
                filter_flag = True
                break
        if filter_flag:
            continue
        print(full_path)
        cl100k, p50k, r50k, gptneox = cal_tokens_of_a_jsonl_file(full_path)
    
        all_cl100k_tokens_num += cl100k
        all_p50k_tokens_num += p50k
        all_r50k_tokens_num += r50k
        GPTNeoX_tokens_num += gptneox

        print("="*50 + TARGET_PATH + "="*50)
        print(f"The number of tokens (cl100k_base) is {cl100k} tokens")
        print(f"The number of tokens (p50k_base) is {p50k} tokens")
        print(f"The number of tokens (r50k_base) is {r50k} tokens")
        print(f"The number of tokens (GPTNeoX-20B_base) is {gptneox} tokens")

    print("="*50 + "All" + "="*50)
    print(f"The number of tokens (cl100k_base) is {all_cl100k_tokens_num} tokens")
    print(f"The number of tokens (p50k_base) is {all_p50k_tokens_num} tokens")
    print(f"The number of tokens (r50k_base) is {all_r50k_tokens_num} tokens")
    print(f"The number of tokens (GPTNeoX-20B_base) is {GPTNeoX_tokens_num} tokens")
    
    print(f"Time cost: {(time.time()-start_time)/(60*60)}h")