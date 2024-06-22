
# StackExchange


1. Mathematics: Q&A for people studying math at any level and professionals in related fields  https://math.stackexchange.com/

2. MathOverflow: Q&A for professional mathematicians  https://mathoverflow.net/

3. Mathematica: Q&A for users of Wolfram Mathematica https://mathematica.stackexchange.com/

4. Mathematics Educators: Q&A for those involved in the field of teaching mathematics https://matheducators.stackexchange.com/

5. History of Science and Mathematics: Q&A for people interested in the history and origins of science and mathematics https://hsm.stackexchange.com/


6. Physics: Q&A for active researchers, academics and students of physics (227k questions)

7. Proof Assistants: Q&A for mathematicians and computer scientists who develop and use proof assistants (763 question)

8. TeX - LaTeX: Q&A for users of TeX, LaTeX, ConTeXt, and related typesetting systems (253k questions)

9. Data Science: Q&A for Data science professionals, Machine Learning specialists, and those interested in learning more about the field (36k questions)

10. Theoretical Computer Science: Q&A for theoretical computer scientists and researchers in related fields (13k question)

11. Computer Science: Q&A for students, researchers and practitioners of computer science (47k question)


Data info: https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede


## Processing

- convert xml to raw text and write into jsonl file: `python preprocessing.py`
- pair question and answer, filter questions without answers, and write into jsonl file: `python pair_question_answer.py`
- filter data by score: `python filtering.py`
- collect some high-quality questions (despite no answers): `python pair_question_and_answer.py`