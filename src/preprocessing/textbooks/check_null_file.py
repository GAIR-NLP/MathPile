import os

TARGET_PATH = "./cleaned_data_v0.1/md"

for root, dirs, files in os.walk(TARGET_PATH):
    for filename in files:
        if filename.endswith(".md"):
            full_path = os.path.join(root, filename)
            with open(full_path, "r") as f:
                content = f.read()
                if content.strip() == "":
                    print(full_path)