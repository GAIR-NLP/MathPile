
# Common Crawl

1. gather 'RedPajamaCommonCrawl', "RedPajamaC4" set from the SlimPajama-627B.
    - `python gather_data.py`
2. filtering out math documents with hard pattern matching.
    - `python hard_pattern_filter.py`