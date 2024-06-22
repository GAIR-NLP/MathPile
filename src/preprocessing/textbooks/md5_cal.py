import hashlib
import os

def calculate_md5(file_path):
    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5()
        chunk = file.read(8192)
        while chunk:
            md5_hash.update(chunk)
            chunk = file.read(8192)
    return md5_hash.hexdigest()


if __name__ == "__main__":
    md5_dict = {}
    count = 0
    duplicates = []
    for path in ["./college", "./high-school", "./college/notes"]:
        for filename in os.listdir(path):
            if os.path.isdir(filename):
                for subfilename in os.listdir(filename):
                    if subfilename.endswith('.pdf'):
                        file_path = f"{path}/{filename}/{subfilename}"
                        md5 = calculate_md5(file_path)
                        if md5 not in md5_dict:
                            md5_dict[md5] = file_path
                        else:
                            count += 1
                            print(f"{file_path} is identical to {md5_dict[md5]}")
                            duplicates.append(file_path)
            elif filename.endswith('.pdf'):
                file_path = f"{path}/{filename}"
                md5 = calculate_md5(file_path)
                if md5 not in md5_dict:
                    md5_dict[md5] = file_path
                else:
                    count += 1
                    print(f"{file_path} is identical to {md5_dict[md5]}")
                    duplicates.append(file_path)
    print(f"\nTotal {count} files identified as identical")

    # for duplicate_file in duplicates:
    #     print('Removing duplicate file:', duplicate_file)
    #     os.remove(duplicate_file)
    print('Done')
