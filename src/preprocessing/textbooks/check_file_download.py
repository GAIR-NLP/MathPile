import os
import requests


paths = ["textbooks/college", "textbooks/high-school", "notes/"]
all_extension = [".docx", ".html", ".lines.json", ".lines.mmd.json", ".md", ".mmd", ".tex.zip",] #  ".txt"


APP_KEY = "xxx"
APP_ID = "xxxx"


headers = {
        "app_key": APP_KEY,
        "app_id": APP_ID,
        # 'Accept-Encoding': 'gzip, deflate'
    }


def download_md_file(pdf_id, save_path):
    url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".md"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open(os.path.join(save_path, pdf_id + ".md"), "wb") as f:
        f.write(response.content)
    print(f"{pdf_id}.md download!")


for dir_path in paths:
    for sub_dir in os.listdir(dir_path):
        full_path = os.path.join(dir_path, sub_dir)
        if os.path.isfile(full_path):
            continue
        all_files = os.listdir(full_path)
        prefix = all_files[0].split(".")[0]
        for extension in all_extension:
            if extension != ".md":
                continue
            if not os.path.exists(os.path.join(full_path, prefix + extension)) or os.path.getsize(os.path.join(full_path, prefix + extension)) < 150:
                print(prefix)
                assert prefix.startswith("2023_0")
                print(f"Path: {os.path.join(full_path, prefix + extension)}  does not exist!")
                download_md_file(prefix, full_path)

