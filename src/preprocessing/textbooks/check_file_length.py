import os


def read_file(path):
    with open(path, "r") as f:
        content = f.read()
        return content



SOURCE_DIR = "./merged-mathpix-parsed-results"
CLEANED_DIR = "./cleaned_data_v0.1"
FILE_TYPE = "md"

# dirs = ["textbooks/high-school"]
# dirs = ["textbooks/college"]
# dirs = ["textbooks/high-school", "textbooks/college"]
# dirs = ["notes"]
dirs = ["textbooks/high-school", "textbooks/college", "notes"]



total_source_len = 0
total_cleaned_len = 0

for dirname in dirs:
    source_full_dir = os.path.join(SOURCE_DIR, FILE_TYPE, dirname)
    cleaned_full_dir = os.path.join(CLEANED_DIR, FILE_TYPE, dirname)

    for filename in os.listdir(source_full_dir):
        source_full_path = os.path.join(source_full_dir, filename)
        cleaned_full_path = os.path.join(cleaned_full_dir, filename)
        source_content = read_file(source_full_path)
        cleaned_content = read_file(cleaned_full_path)
        
        source_content_len = len(source_content)
        cleaned_content_len = len(cleaned_content)

        total_source_len += source_content_len
        total_cleaned_len += cleaned_content_len


        
        clean_rate = (source_content_len - cleaned_content_len) / source_content_len
        if clean_rate >= 0.5:
            print("Clean Error")
            print(cleaned_full_path)
            print(f"Source: {source_content_len}, Cleaned: {cleaned_content_len} Clean Rate: {round(clean_rate*100, 2)}")

        if source_content_len < cleaned_content_len:
            print("Length Error")
            print(cleaned_full_path)
            print(f"Source: {source_content_len}, Cleaned: {cleaned_content_len} Clean Rate: {round(clean_rate*100, 2)}")


print(f"Total Clean Rate: {round(100 - total_cleaned_len / total_source_len * 100, 2)}")
