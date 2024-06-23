


TARGET_DIR=../data-built-on-datasets/dedup/


python text_dedup/counting_common_ngram.py \
    --path ${TARGET_DIR}arxiv_commoncrawl_stackexchange_wikipedia_all_textbooks_minhashlsh_5gram_9000perm_b45r20_dedup_final_dedup \
    --cache_dir "./cache" \
    --output "./cache" \
    --column "text" \
    --local \
    --hash_func md5 \
    --ngram_size 10 \
    --common_words_num 20 