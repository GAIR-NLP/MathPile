

mkdir cache


## source inner dedup

META_DIR=../data-built-on-datasets/filtering/
TARGET_DIR=../data-built-on-datasets/dedup/

for SOURCE in math_arXiv_v0.2 wikipedia_update stackexchange   proofwiki commoncrawl 
do
    python text_dedup/minhash.py \
        --path ${META_DIR}${SOURCE} \
        --cache_dir "./cache" \
        --output ${TARGET_DIR}${SOURCE}_minhashlsh_5gram_9000perm_b45r20_dedup \
        --column "text" \
        --local \
        --ngram 5 \
        --min_length 5 \
        --seed 42 \
        --num_perm 9000 \
        --b 45 \
        --r 20 
        # --maintain_all_docs
done


for SOURCE in textbooks/textbooks_markdown textbooks/textbooks_tex textbooks/synthetic_textbooks_markdown 
do
    python text_dedup/minhash.py \
        --path ${META_DIR}${SOURCE} \
        --cache_dir "./cache" \
        --output ${TARGET_DIR}${SOURCE}_minhashlsh_5gram_9000perm_b45r20_dedup_raw \
        --column "text" \
        --local \
        --ngram 5 \
        --min_length 5 \
        --seed 42 \
        --num_perm 9000 \
        --b 45 \
        --r 20 
        # --maintain_all_docs
done

## source inter dedup 

SUFFIX="_minhashlsh_5gram_9000perm_b45r20_dedup"

python text_dedup/minhash.py \
    --path ${TARGET_DIR}arxiv_commoncrawl_stackexchange_wikipedia_all_textbooks${SUFFIX}_concat_before_inter_sources_dedup \
    --cache_dir "./cache" \
    --output ${TARGET_DIR}arxiv_commoncrawl_stackexchange_wikipedia_all_textbooks_concat_minhashlsh_5gram_9000perm_b45r20_after_inter_sources_dedup_raw \
    --column "text" \
    --local \
    --ngram 5 \
    --min_length 5 \
    --seed 42 \
    --num_perm 9000 \
    --b 45 \
    --r 20 
    # --maintain_all_docs



