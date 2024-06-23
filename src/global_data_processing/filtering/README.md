# Cleaning and Filtering


```
paths = {
    "arXiv": ['arXiv/math_arXiv_v0.2.jsonl'],
    "commoncrawl": ['commoncrawl/C4_math_docs_chunk_0.jsonl', 'commoncrawl/CC_math_docs_chunk_0.jsonl'],
    "proofwiki": ['proofwiki/ProofWiki_definitions.jsonl', 'proofwiki/ProofWiki_theorem_proofs.jsonl'],
    "stackexchange": [
        'stackexchange/cs.stackexchange.com.jsonl', 
        "stackexchange/matheducators.stackexchange.com.jsonl",
        "stackexchange/physics.stackexchange.com.jsonl",
        "stackexchange/cstheory.stackexchange.com.jsonl",
        "stackexchange/mathematica.stackexchange.com.jsonl",
        "stackexchange/proofassistants.stackexchange.com.jsonl",
        "stackexchange/datascience.stackexchange.com.jsonl",
        "stackexchange/mathoverflow.net.jsonl",
        "stackexchange/tex.stackexchange.com.jsonl",
        "stackexchange/math.stackexchange.com.jsonl",
        "stackexchange/hsm.stackexchange.com.jsonl",
    ],
    "textbooks": ['textbooks/synthetic_textbooks_markdown.jsonl', "textbooks/textbooks_markdown.jsonl", "textbooks/textbooks_tex.jsonl"],
    "wikipedia": ['wikipedia/wikipedia_en_mathematics_nopic_2023-08.jsonl'],
    "wikipedia_update": ['wikipedia_update/wikipedia_en_mathematics_nopic_2023-08_math_latex_fix_20231231.jsonl']
}
```

1. modify the ` target_source` varible (options can be chosen from  the above `paths`'s keys) in the `filtering.py` file;
2. run: `python filtering.py`