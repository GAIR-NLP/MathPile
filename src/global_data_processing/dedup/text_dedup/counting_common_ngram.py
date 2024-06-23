#!/usr/bin/env python
# @Date         : 2023-05-06 19:34:35
# @Author       : Chenghao Mou (mouchenghao@gmail.com)
# @Description  : Line-level deduplication based on Exact Hashing
# @Reference    : https://github.com/facebookresearch/cc_net/blob/main/cc_net/dedup.py

import argparse
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

import numpy as np
from datasets import Dataset
from datasets import load_dataset, load_from_disk, concatenate_datasets
from tqdm import tqdm
import heapq
import os, sys, re
current_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder)
sys.path.append(parent_folder)

from text_dedup import logger
from text_dedup.utils import add_exact_hash_args
from text_dedup.utils import add_io_args
from text_dedup.utils import add_meta_args, add_counting_ngrams_args
from text_dedup.utils import ngrams as ngrams_func
from text_dedup.utils.hashfunc import md5_digest
from text_dedup.utils.hashfunc import sha256_digest
from text_dedup.utils.hashfunc import xxh3_64_digest
from text_dedup.utils.hashfunc import xxh3_128_digest
from text_dedup.utils.preprocess import normalize as normalize_for_dedup
from text_dedup.utils.timer import Timer
from collections import defaultdict

HASH_SIZE = np.uint64(0).nbytes  # 8 bytes
NON_ALPHA = re.compile(r"\W", re.UNICODE)

def compute_hashes(batch: Dict[str, Any], idx: List[int], column: str, hash_func: Callable, ngram_size: int) -> Dict[str, Any]:
    """
    Compute a hash for each line in the document.

    Parameters
    ----------
    batch : Dict[str, Any]
        A batch of one example.
    idx : List[int]
        The index of the example in the dataset.
    column : str
        The column name of the text.
    hash_func : Callable
        The hash function to use.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the hashes, the index of the example, and the index of the lines.
    """
    # lines = batch[column][0].split("\n")
    # n = len(lines)
    # ngrams = [" ".join(t).lower() for t in ngrams_func(NON_ALPHA.split(batch[column][0]), ngram_size, ngram_size)]
    ngrams = [" ".join(t).lower() for t in ngrams_func(batch[column][0].split(), ngram_size, ngram_size) if len(" ".join(t).strip())]
    n = len(ngrams)
    # hashes = [hash_func(bytes(normalize_for_dedup(line), encoding="utf-8")) for line in lines]
    # hashes = [hash_func(bytes(line, encoding="utf-8")) for line in lines]
    hashes = [hash_func(bytes(gram, encoding="utf-8")) for gram in ngrams]

    return {
        "__hash__": hashes,
        "__id__": [idx[0] for _ in range(n)],
        "__ngrams__": ngrams,
        "__subset__": [batch['subset'][0]] * len(ngrams),
        "__file_path__": [batch['file_path'][0]] * len(ngrams),
    }




if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog="text_dedup.ccnet",
        description="Counting most & least common ngrams using exact hashing",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = add_io_args(parser)
    parser = add_meta_args(parser)
    parser = add_exact_hash_args(parser)
    parser = add_counting_ngrams_args(parser)
    args = parser.parse_args()

    timer = Timer()

    with timer("Total"):
        with timer("Loading"):
            if not args.local:
                raise Exception            
            ds = load_from_disk(args.path)
            print(ds)


        def md5_digest_sized(data: bytes) -> bytes:
            return md5_digest(data)[:HASH_SIZE]

        def sha256_digest_sized(data: bytes) -> bytes:
            return sha256_digest(data)[:HASH_SIZE]

        def xxh3_digest_sized(data: bytes) -> bytes:
            return xxh3_128_digest(data)[:HASH_SIZE]

        hash_func = {
            "md5": md5_digest,
            "sha256": sha256_digest,
            # xxh3 is much faster when used raw
            "xxh3": xxh3_64_digest if HASH_SIZE == 8 else xxh3_digest_sized,
        }[args.hash_func]

        LEN_DATASET = len(ds)

        with timer("Processing"):
            hashed = ds.map(
                compute_hashes,
                batched=True,
                batch_size=1,
                with_indices=True,
                num_proc=args.num_proc,
                fn_kwargs={"column": args.column, "hash_func": hash_func, "ngram_size": args.ngram_size},
                remove_columns=ds.column_names,
                desc="Computing hashes...",
            )
            

            common_ngrams_per_subset_count = defaultdict(dict)

            NUM_SHARDS = int(np.ceil(len(hashed) / args.batch_size))
            for batch_idx in tqdm(range(0, NUM_SHARDS), desc="Processing..."):
                ds_shard = hashed.shard(NUM_SHARDS, batch_idx, contiguous=True)
                for h, id_, ngram, subset in tqdm(
                    zip(ds_shard["__hash__"], ds_shard["__id__"], ds_shard["__ngrams__"], ds_shard["__subset__"]),
                    leave=False,
                ):
                    if (h, ngram) not in common_ngrams_per_subset_count[subset]:
                        common_ngrams_per_subset_count[subset][(h, ngram)] = 0
                    common_ngrams_per_subset_count[subset][(h, ngram)] += 1


        with timer("Gathering Data"):
            for subset in common_ngrams_per_subset_count:
                print("=="*10)
                freq_dict = common_ngrams_per_subset_count[subset]

                top_k_words = heapq.nlargest(args.common_words_num, freq_dict.items(), key=lambda x: x[1])

                bottom_k_words = heapq.nsmallest(args.common_words_num, freq_dict.items(), key=lambda x: x[1])

                print(f"Top {args.common_words_num} Words and Their Frequencies in {subset}:")
                for word, frequency in top_k_words:
                    print(f"{word}: {frequency}")

                # 打印频率最低的10个单词及其频率
                print(f"\nBottom {args.common_words_num} Words and Their Frequencies in {subset}:")
                for word, frequency in bottom_k_words:
                    print(f"{word}: {frequency}")