# Deduplication 

text_dedup is built on deduplicate-text-datasets. 

Thanks for amazing codebase [text_dedup](https://github.com/ChenghaoMou/text-dedup) and [deduplicate-text-datasets](https://github.com/google-research/deduplicate-text-datasets)


We conducted de-duplication with Minhash Algorithm (LSH version). Specificially, we conducted deduplication within each source and then across sources.

```
bash text-dedup.sh
```


# Leakage Detection and Removal

We leverage line-level exact match to detect any leakage and remove them.

```
bash leakage_detection_remove.sh
```

Note that before runing these scripts, we need convert data into huggingface `datasets` format.