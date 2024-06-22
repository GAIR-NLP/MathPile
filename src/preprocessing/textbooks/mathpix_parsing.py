import os
import argparse
from utils import create_directory, calculate_md5, print_time
import time
import json
import copy
import requests
import random
from fake_useragent import UserAgent


APP_KEY = "xxxx"
APP_ID = "xxx"


headers = {
        "app_key": APP_KEY,
        "app_id": APP_ID
    }
ua = UserAgent()



def check_processing_status_with_infinite_loop(pdf_id):
    # check process status
    url = f"https://api.mathpix.com/v3/converter/{pdf_id}"
    status = "processing"
    with print_time("Processing..."):
        while status == "processing":
            response = requests.get(url, headers=headers)
            _content = eval(response._content.decode("utf8"))
            print(_content)
            if "status" not in _content:
                time.sleep(1)
                continue
            status = _content['status']
            print(status)
            if status == "completed":
                break

def check_processing_completed_status(pdf_id):
    # check process status
    url = f"https://api.mathpix.com/v3/converter/{pdf_id}"
    status = "processing"
    response = requests.get(url, headers=headers)
    _content = eval(response._content.decode("utf8"))
    if "status" not in _content:
        return False
    status = _content['status']
    if status == "completed":
        return True
    else:
        return False

def get_parsed_results(filename, pdf_id, save_path = "./", page_ranges = None):

    headers.update(
        {
            "User-Agent": ua.random,
            "Proxy-Tunnel": str(random.randint(1,10000))
        }
    )
    
    if page_ranges is not None:
        save_path = os.path.join(save_path, f"PDF-{filename.replace('.pdf','')}_{page_ranges}/")
    else:
        save_path = os.path.join(save_path, f"PDF-{filename.replace('.pdf','')}/")
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        print("Directory", save_path, "created")
    else:
        print("Directory", save_path, "already exists")
    
    with open(save_path + pdf_id + ".txt", "w") as f:
        f.write(pdf_id)
    
    def _get_request_and_save_content(url, save_path):
        try:
            with requests.get(url, headers=headers, stream = True) as response:
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
        except Exception as e:
            print(f"requesting {url} with {e}")
            print(f"sleep 60s due to the connection error")
            time.sleep(1 * 60)
            return _get_request_and_save_content(url, save_path)


    # get md file
    with print_time(f"Download {pdf_id}.md file"):
        md_url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".md"
        md_save_path = save_path + pdf_id + ".md"
        _get_request_and_save_content(md_url, md_save_path)
        
    time.sleep(1)
    
    # get mmd response
    with print_time(f"Download {pdf_id}.mmd file"):
        mmd_url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".mmd"
        mmd_save_path = save_path + pdf_id + ".mmd"
        _get_request_and_save_content(mmd_url, mmd_save_path)
        
    time.sleep(1)

    # get docx response
    with print_time(f"Download {pdf_id}.docx file"):
        docx_url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".docx"
        docx_save_path = save_path + pdf_id + ".docx"
        _get_request_and_save_content(docx_url, docx_save_path)

        
    time.sleep(1)

    # get LaTeX zip file
    with print_time(f"Download {pdf_id}.tex file"):
        tex_url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".tex"
        tex_save_path = save_path + pdf_id + ".tex.zip"
        _get_request_and_save_content(tex_url, tex_save_path)
        
    time.sleep(1)

    # get HTML file
    with print_time(f"Download {pdf_id}.html file"):
        html_url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".html"
        html_save_path = save_path + pdf_id + ".html"
        _get_request_and_save_content(html_url, html_save_path)
        
    time.sleep(1)

    # get lines data
    with print_time(f"Download {pdf_id}.lines.json file"):
        lines_json_url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".lines.json"
        lines_json_save_path = save_path + pdf_id + ".lines.json"
        _get_request_and_save_content(lines_json_url, lines_json_save_path)
        
    time.sleep(1)

    # get lines mmd json
    with print_time(f"Download {pdf_id}.lines.mmd.json file"):
        lines_mmd_json_url = "https://api.mathpix.com/v3/pdf/" + pdf_id + ".lines.mmd.json"
        lines_mmd_json_save_path = save_path + pdf_id + ".lines.mmd.json"
        _get_request_and_save_content(lines_mmd_json_url, lines_mmd_json_save_path)
        

def check_have_downloaded(parsed_results_saved_dir, filename):

    dir_name = f"PDF-{filename.replace('.pdf','')}/"

    file_path = os.path.join(parsed_results_saved_dir, dir_name)

    if os.path.exists(file_path):
        filenames_in_dir = os.listdir(file_path)
        if len(filenames_in_dir) >= 7:
            print(f"{file_path} already exists!")
            return True
        download_suffix = ['.md', '.mmd', '.json', '.html', '.docx', '.zip']
        if len(filenames_in_dir) > 0:
            for item in filenames_in_dir:
                for suffix in download_suffix:
                    if item.endswith(suffix):
                        print(f'Found file {filename} with suffix {suffix}')
                        return True
        else:
            return False
    else:
        return False

def parsing_local_pdf(filename = "css299-notes.pdf", page_ranges = None):
    options = {
        "conversion_formats": {"docx": True, "tex.zip": True},
        "math_inline_delimiters": ["$", "$"],
        "math_display_delimiters": ["$$", "$$"],
        "rm_spaces": True,
        "auto_number_sections": False,  
        "enable_tables_fallback": True,  # Enables advanced table processing algorithm that supports very large and complex tables.
    }
    if page_ranges is not None:
        options["page_ranges"] = page_ranges
    r = requests.post("https://api.mathpix.com/v3/pdf",
        headers={
            "app_id": APP_ID,
            "app_key": APP_KEY
        },
        data={
            "options_json": json.dumps(options)
        },
        files={
            "file": open(filename,"rb")
        }
    )
    pdf_id = r.text.encode("utf8")
    status = pdf_id.decode("utf8")
    print(filename)
    print(status)
    return eval(status)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf_dir', type = str, required=True, default="./")
    parser.add_argument('--parsed_results_saved_dir',type=str, required=True, default="./")
    parser.add_argument('--page_ranges', type=str, required=False, default=None)
    parser.add_argument('--max_pdf_file_size', type=float, required=False, default=40, help= "40MB")
    parser.add_argument('--wait_minutes', type=float, required=False, default=1, help= "waiting 10 minutes...")
    args = parser.parse_args()

    filenames = os.listdir(args.pdf_dir)

    pdf_filenames = []
    for item in filenames:
        if item.endswith(".pdf"):
            if os.path.getsize(os.path.join(args.pdf_dir, item)) > args.max_pdf_file_size * 1024 * 1024:
                print(f"{item} exceeds {args.max_pdf_file_size} MB")
            else:
                if check_have_downloaded(args.parsed_results_saved_dir, item):
                    continue
                else:
                    pdf_filenames.append(item)

    assert len(filenames) >= len(pdf_filenames)
    print(f"Parsing {len(pdf_filenames)} files...")

    create_directory(args.parsed_results_saved_dir)

    print(pdf_filenames)


    
    md5_jsonl_path = os.path.join(args.pdf_dir, "md5-pdf_id-filename.jsonl")

    for filename in pdf_filenames:
        print(f"processing {filename}...")
        cur_pdf_file_path = args.pdf_dir + filename
        status = parsing_local_pdf(cur_pdf_file_path, args.page_ranges)
        pdf_id = status["pdf_id"]

        while not check_processing_completed_status(pdf_id):
            time.sleep(10)
            print("sleeping 10s...")

        get_parsed_results(filename, pdf_id, save_path = args.parsed_results_saved_dir, page_ranges = args.page_ranges)
        
        # cur_md5 = calculate_md5(cur_pdf_file_path)
        # time.sleep(10)
        # with open(md5_jsonl_path, 'a') as f:
        #     f.write(json.dumps({"md5": cur_md5, "pdf_id": pdf_id, "filename": filename}) + '\n')

        print(f"{filename} with id: {pdf_id} done!")
        time.sleep(args.wait_minutes * 60)
    print(f"All of {len(pdf_filenames)} PDFs downloaded!")
    