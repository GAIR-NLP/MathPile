
# line-level exact match for data leakage detection and removal

MATH_BENCH_TEST_SET_PATH=/data1/zzwang/benchmark-datasets/GSM8K_MATH_MMLU-STEM_test_set_concat_for_detect_data_leakage

MATH_BENCH_Q_A_TEST_SET_PATH=/data1/zzwang/benchmark-datasets/GSM8K_MATH_MMLU-STEM_test_set_concat_with_q_a_concat_for_detect_data_leakage


python text_dedup/ccnet_for_data_leakage.py \
    --path ${TARGET_DIR}arxiv_commoncrawl_stackexchange_wikipedia_all_textbooks_minhashlsh_5gram_9000perm_b45r20_dedup_final_dedup \
    --reference_path ${MATH_BENCH_Q_A_TEST_SET_PATH} \
    --cache_dir "./cache" \
    --output ${TARGET_DIR}arxiv_commoncrawl_stackexchange_wikipedia_all_textbooks_minhashlsh_5gram_9000perm_b45r20_dedup_final_dedup_after_ccnet_exact_match_benchmark_dedup_final \
    --column "text" \
    --local \
    --hash_func md5



OPENWEBMATH_META_DIR=/data1/zzwang/openwebpath

python text_dedup/ccnet_for_data_leakage.py \
    --path ${OPENWEBMATH_META_DIR}/openwebmath-built-on-datasets \
    --reference_path ${MATH_BENCH_Q_A_TEST_SET_PATH} \
    --cache_dir "./cache" \
    --output ${OPENWEBMATH_META_DIR}/openwebmath-built-on-datasets-after_ccnet_exact_line_remove_against_math_bench_q_a_dedup_final \
    --column "text" \
    --local \
    --hash_func md5


six_math_benchmark_path=/data1/zzwang/benchmark-datasets/agieval_math_auqa_asdiv_asdiva_swamp_numglue_mawps_mathqa_test_set_only_q_for_detect_data_leakage


python text_dedup/ccnet_for_data_leakage.py \
    --path /data1/zzwang/mathpile/data-built-on-datasets/dedup/textbooks/synthetic_textbooks_markdown_minhashlsh_5gram_9000perm_b45r20_dedup_after_ccnet_exact_match_benchmark_dedup_final \
    --reference_path ${six_math_benchmark_path} \
    --cache_dir "./cache" \
    --output /data1/zzwang/mathpile/data-built-on-datasets/dedup/textbooks/synthetic_textbooks_markdown_minhashlsh_5gram_9000perm_b45r20_dedup_after_ccnet_exact_match_benchmark_dedup_final_after_remove_more_math_benchmarks \
    --column "text" \
    --local \
    --hash_func md5