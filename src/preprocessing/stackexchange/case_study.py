import os
import random
from pprint import pprint
import json


TARGET_PATH = "final_filtered_posts/Q5A5"

N = 1

filenames = ['math.stackexchange.com', 'mathoverflow.net', 'mathematica.stackexchange.com', 'matheducators.stackexchange.com', 'hsm.stackexchange.com']

full_path = os.path.join(TARGET_PATH, filenames[0] + ".jsonl")

with open(full_path, "r") as f:
    lines = f.readlines()
    data = [json.loads(line) for line in lines]
    for i in range(N):
        idx = random.randint(0, len(data) - 1)
        print("="*50 + str(idx) + "="*50)
        # print(data[idx])
        pprint(data[idx], width=150, indent=2)

