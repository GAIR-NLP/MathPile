
# Textbooks


- Calculate the MD5 code for pdf dedup. `python md5_cal.py`
- Parse pdfs with MathPix:
    - `bash mathpix_parsing.sh`
    - check the download of parsed files `python check_file_download.py`
- Clean the parsed files:
    - prepare the tex files: `python unzip_files.py`
    - preparation before cleaning: `python processing.py`
    - clean tex files: `python processing_tex_file_at_scale.py`
    - clean md files: `python processing_md_file_at_scale.py`