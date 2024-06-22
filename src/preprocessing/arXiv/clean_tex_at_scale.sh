


# python processing_tex_at_scale.py \
#     --whole_arxiv_cleaning_mode \
#     --raw_arxiv_tex_files_dir ./case_study \
#     --cleaned_arxiv_tex_files_save_dir ./cleaned_case_study \
#     --cleaned_data_version 0.2


python processing_tex_at_scale.py \
    --whole_arxiv_cleaning_mode \
    --raw_arxiv_tex_files_dir ./merge_math_tex_data \
    --cleaned_arxiv_tex_files_save_dir ./cleaned_merge_math_tex_data \
    --cleaned_data_version 0.1 \
    --cleaning_timeout_seconds 300


# python processing_tex_at_scale.py \
#     --just_a_trial_mode \
#     --parsing_single_tex_file \
#     --parsing_single_tex_file_path ./cleaned_merge_math_tex_data/0704.0069.tex \
#     --output_path None