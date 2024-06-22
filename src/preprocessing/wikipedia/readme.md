# Math Wikipedia


access math-focus part of wikipedia from `https://www.inverse.com/input/guides/how-to-download-wikipedia-offline` and `https://download.kiwix.org/zim/wikipedia/`, e.g., `wikipedia_en_mathematics_nopic_2023-08.zim`


statistics info of `wikipedia_en_mathematics_nopic_2023-08.zim`：
```
application/javascript: 31
text/css: 27
image/png: 1
text/html: 106881
image/svg+xml; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/SVG/1.0.0": 258351
image/webp: 96
undefined: 2
text/plain: 12
application/octet-stream+xapian: 2
```


## Cleaning Process

```python
python processing_zim_file.py
```

- Using libzim to traverse .zim files, we obtained over 106,000 HTML documents, totaling 12GB.
- Then, the raw text was extracted from the HTML files and saved in markdown format (without retaining links, referencing LLaMA-1).
- During the file inspection process, it was found that due to the HTML formatting, many unnecessary line breaks were included within paragraphs. These extra line breaks were removed using regular expressions. (This resulted in `wikipedia_en_mathematics_nopic_2023-08_cleaned_md_v0.1.jsonl`)
- It was found that there were many images like `![](..svg)` in the documents. These were replaced using regular expressions, although the current regex only supports one level of nested brackets inside the square brackets.
- It was found that there were many unnecessary line breaks, which were removed using regular expressions (replacing three or more consecutive line breaks, possibly interspersed with spaces, with two line breaks).
- It was found that each page contained the template/placeholder content `This article is issued from Wikipedia. The text is licensed under Creative Commons - Attribution - Sharealike. Additional terms may apply for the media files.`, which needed to be removed. (This resulted in `wikipedia_en_mathematics_nopic_2023-08_cleaned_md_v0.2.jsonl`)
- There were still many unresolved line breaks within paragraphs. These were addressed using the regular expression `((?<!\n)\n(?=[^\n\s]))`. (This resulted in `wikipedia_en_mathematics_nopic_2023-08_cleaned_md_v0.3.jsonl`)
- It was discovered that the third version misprocessed tables and headings. Based on the `v2` version, a new regular expression `(?<!\n)\n(?![\n\s#]|.*\|)` was used to create the fourth version `wikipedia_en_mathematics_nopic_2023-08_cleaned_md_v0.4.jsonl`.
