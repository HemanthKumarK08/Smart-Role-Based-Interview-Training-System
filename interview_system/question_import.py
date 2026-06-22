# """Parse CSV/JSON question banks for bulk admin upload."""

# import csv
# import json
# import os

# REQUIRED_MCQ = (
#     "question",
#     "option_a",
#     "option_b",
#     "option_c",
#     "option_d",
#     "correct_answer",
# )
# VALID_TYPES = ("mcq", "technical", "hr")
# VALID_DIFF = ("Easy", "Medium", "Hard")


# def _norm_type(raw):
#     t = (raw or "").strip().lower()
#     if t in VALID_TYPES:
#         return t
#     raise ValueError(f"Invalid type '{raw}'. Use: mcq, technical, hr")


# def _norm_diff(raw, required=False):
#     d = (raw or "").strip()
#     if not d:
#         if required:
#             raise ValueError("difficulty is required for mcq/technical")
#         return None
#     cap = d.capitalize()
#     if cap not in VALID_DIFF:
#         raise ValueError(f"Invalid difficulty '{raw}'. Use: Easy, Medium, Hard")
#     return cap


# def parse_csv_file(filepath):
#     """Return list of normalized question dicts from CSV."""
#     questions = []
#     with open(filepath, newline="", encoding="utf-8-sig") as f:
#         reader = csv.DictReader(f)
#         if not reader.fieldnames:
#             raise ValueError("CSV file is empty or missing header row.")

#         fields = {c.strip().lower(): c for c in reader.fieldnames}

#         def col(name):
#             key = fields.get(name)
#             if not key:
#                 return ""
#             return name

#         for row_num, row in enumerate(reader, start=2):
#             get = lambda n: (row.get(fields.get(n, ""), "") or "").strip()

#             qtype = _norm_type(get("type"))
#             difficulty = _norm_diff(
#                 get("difficulty"),
#                 required=qtype in ("mcq", "technical"),
#             )
#             question = get("question")
#             if not question:
#                 raise ValueError(f"Row {row_num}: question is required.")

#             item = {
#                 "type": qtype,
#                 "difficulty": difficulty,
#                 "question": question,
#                 "option_a": get("option_a"),
#                 "option_b": get("option_b"),
#                 "option_c": get("option_c"),
#                 "option_d": get("option_d"),
#                 "correct_answer": get("correct_answer").upper(),
#                 "keywords": get("keywords"),
#                 "ideal_answer": get("ideal_answer"),
#             }

#             if qtype == "mcq":
#                 for f in REQUIRED_MCQ:
#                     if not item.get(f):
#                         raise ValueError(
#                             f"Row {row_num}: MCQ missing '{f}'."
#                         )
#                 if item["correct_answer"] not in ("A", "B", "C", "D"):
#                     raise ValueError(
#                         f"Row {row_num}: correct_answer must be A, B, C, or D."
#                     )
#             elif qtype == "technical":
#                 kws = [k.strip() for k in item["keywords"].split(",") if k.strip()]
#                 if len(kws) < 3:
#                     raise ValueError(
#                         f"Row {row_num}: technical needs 3+ comma-separated keywords."
#                     )
#             elif qtype == "hr":
#                 if not item["keywords"]:
#                     raise ValueError(
#                         f"Row {row_num}: HR needs keywords."
#                     )

#             questions.append(item)

#     if not questions:
#         raise ValueError("No questions found in file.")
#     return questions


# def parse_json_file(filepath):
#     """Return list of normalized question dicts from JSON."""
#     with open(filepath, encoding="utf-8") as f:
#         data = json.load(f)

#     items = []
#     if isinstance(data, list):
#         items = [dict(x) for x in data]
#     elif isinstance(data, dict):
#         for qtype in VALID_TYPES:
#             for entry in data.get(qtype, []):
#                 row = dict(entry)
#                 row["type"] = qtype
#                 items.append(row)
#     else:
#         raise ValueError("JSON must be a list or object with mcq/technical/hr keys.")

#     if not items:
#         raise ValueError("No questions found in JSON file.")

#     questions = []
#     for i, entry in enumerate(items, start=1):
#         qtype = _norm_type(entry.get("type"))
#         difficulty = _norm_diff(
#             entry.get("difficulty"),
#             required=qtype in ("mcq", "technical"),
#         )
#         question = (entry.get("question") or "").strip()
#         if not question:
#             raise ValueError(f"Item {i}: question is required.")

#         item = {
#             "type": qtype,
#             "difficulty": difficulty,
#             "question": question,
#             "option_a": (entry.get("option_a") or "").strip(),
#             "option_b": (entry.get("option_b") or "").strip(),
#             "option_c": (entry.get("option_c") or "").strip(),
#             "option_d": (entry.get("option_d") or "").strip(),
#             "correct_answer": (entry.get("correct_answer") or "").strip().upper(),
#             "keywords": (entry.get("keywords") or "").strip(),
#             "ideal_answer": (entry.get("ideal_answer") or "").strip(),
#         }

#         if qtype == "mcq":
#             for f in REQUIRED_MCQ:
#                 if not item.get(f):
#                     raise ValueError(f"Item {i}: MCQ missing '{f}'.")
#         elif qtype == "technical":
#             kws = [k.strip() for k in item["keywords"].split(",") if k.strip()]
#             if len(kws) < 3:
#                 raise ValueError(f"Item {i}: technical needs 3+ keywords.")
#         elif not item["keywords"]:
#             raise ValueError(f"Item {i}: HR needs keywords.")

#         questions.append(item)

#     return questions


# def load_questions_file(filepath):
#     ext = os.path.splitext(filepath)[1].lower()
#     if ext == ".csv":
#         return parse_csv_file(filepath)
#     if ext == ".json":
#         return parse_json_file(filepath)
#     raise ValueError("Supported formats: .csv and .json")


"""Parse CSV/JSON/DOCX question banks for bulk admin upload."""

import csv
import json
import os
from docx import Document

REQUIRED_MCQ = (
    "question",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_answer",
)

VALID_TYPES = ("mcq", "technical", "coding", "hr")
VALID_DIFF = ("Easy", "Medium", "Hard")


# ==========================================
# NORMALIZERS
# ==========================================
def _norm_type(raw):
    t = (raw or "").strip().lower()
    if t in VALID_TYPES:
        return t
    # Return raw for validator in admin.py to handle gracefully with row number
    return t


def _norm_diff(raw, required=False):
    d = (raw or "").strip()

    if not d:
        if required:
            return None
        return None

    cap = d.capitalize()
    if cap not in VALID_DIFF:
        # Return cap so it can be verified in validator
        return cap

    return cap


# ==========================================
# CSV PARSER
# ==========================================
def parse_csv_file(filepath):
    questions = []

    # Map new CSV header names to standardized database fields
    header_mapping = {
        "questiontype": "type",
        "codesnippet": "code_snippet",
        "optiona": "option_a",
        "optionb": "option_b",
        "optionc": "option_c",
        "optiond": "option_d",
        "correctanswer": "correct_answer"
    }

    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError(
                "CSV file is empty or missing header row."
            )

        fields = {
            c.strip().lower(): c
            for c in reader.fieldnames
        }

        for row_num, row in enumerate(
            reader,
            start=2
        ):
            def get_field(name):
                # Check standard field directly
                key = fields.get(name)
                if key:
                    return (row.get(key, "") or "").strip()
                # Check mapped fields
                for mapped_from, standard_name in header_mapping.items():
                    if standard_name == name:
                        key = fields.get(mapped_from)
                        if key:
                            return (row.get(key, "") or "").strip()
                return ""

            qtype = _norm_type(get_field("type"))
            difficulty = _norm_diff(get_field("difficulty"))

            item = {
                "type": qtype,
                "difficulty": difficulty,
                "question": get_field("question"),
                "code_snippet": get_field("code_snippet"),
                "option_a": get_field("option_a"),
                "option_b": get_field("option_b"),
                "option_c": get_field("option_c"),
                "option_d": get_field("option_d"),
                "correct_answer": get_field("correct_answer"),
                "keywords": get_field("keywords"),
                "ideal_answer": get_field("ideal_answer"),
                "row_num": row_num,
            }

            questions.append(item)

    if not questions:
        raise ValueError(
            "No questions found in file."
        )

    return questions


# ==========================================
# JSON PARSER
# ==========================================
def parse_json_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    items = []

    if isinstance(data, list):
        items = [dict(x) for x in data]

    elif isinstance(data, dict):
        for qtype in VALID_TYPES:
            for entry in data.get(
                qtype,
                []
            ):
                row = dict(entry)
                row["type"] = qtype
                items.append(row)

    else:
        raise ValueError(
            "JSON must be list or object."
        )

    if not items:
        raise ValueError(
            "No questions found in JSON file."
        )

    questions = []

    for i, entry in enumerate(
        items,
        start=1
    ):
        qtype = _norm_type(
            entry.get("type") or entry.get("QuestionType")
        )

        difficulty = _norm_diff(
            entry.get("difficulty") or entry.get("Difficulty")
        )

        question = (
            entry.get("question")
            or entry.get("Question")
            or ""
        ).strip()

        option_a = (entry.get("option_a") or entry.get("OptionA") or "").strip()
        option_b = (entry.get("option_b") or entry.get("OptionB") or "").strip()
        option_c = (entry.get("option_c") or entry.get("OptionC") or "").strip()
        option_d = (entry.get("option_d") or entry.get("OptionD") or "").strip()
        correct_answer = (entry.get("correct_answer") or entry.get("CorrectAnswer") or "").strip().upper()
        code_snippet = (entry.get("code_snippet") or entry.get("CodeSnippet") or entry.get("code") or "").strip()
        keywords = (entry.get("keywords") or entry.get("Keywords") or "").strip()
        ideal_answer = (entry.get("ideal_answer") or entry.get("IdealAnswer") or "").strip()

        item = {
            "type": qtype,
            "difficulty": difficulty,
            "question": question,
            "code_snippet": code_snippet,
            "option_a": option_a,
            "option_b": option_b,
            "option_c": option_c,
            "option_d": option_d,
            "correct_answer": correct_answer,
            "keywords": keywords,
            "ideal_answer": ideal_answer,
            "row_num": i,
        }

        questions.append(item)

    return questions


# ==========================================
# DOCX PARSER
# ==========================================
def parse_docx_file(filepath):
    doc = Document(filepath)

    text = "\n".join(
        para.text.strip()
        for para in doc.paragraphs
        if para.text.strip()
    )

    blocks = text.split("----")
    questions = []

    for idx, block in enumerate(blocks, start=1):
        if not block.strip():
            continue

        row = {
            "type": "",
            "difficulty": "",
            "question": "",
            "code_snippet": "",
            "option_a": "",
            "option_b": "",
            "option_c": "",
            "option_d": "",
            "correct_answer": "",
            "keywords": "",
            "ideal_answer": "",
            "row_num": idx,
        }

        current_key = None
        prefixes = {
            "TYPE:": "type",
            "DIFFICULTY:": "difficulty",
            "QUESTION:": "question",
            "CODE:": "code_snippet",
            "CODE_SNIPPET:": "code_snippet",
            "A:": "option_a",
            "B:": "option_b",
            "C:": "option_c",
            "D:": "option_d",
            "ANSWER:": "correct_answer",
            "KEYWORDS:": "keywords",
            "IDEAL_ANSWER:": "ideal_answer"
        }

        for line in block.splitlines():
            stripped_line = line.strip()
            
            matched_prefix = None
            for pref, key in prefixes.items():
                if stripped_line.startswith(pref):
                    matched_prefix = pref
                    current_key = key
                    break
            
            if matched_prefix:
                val = stripped_line[len(matched_prefix):].strip()
                row[current_key] = val
            elif current_key:
                val_to_add = line if current_key == "code_snippet" else stripped_line
                if not val_to_add and current_key != "code_snippet":
                    continue
                if row[current_key]:
                    row[current_key] += "\n" + val_to_add
                else:
                    row[current_key] = val_to_add

        if row["question"] or row["type"]:
            if row["type"]:
                row["type"] = _norm_type(row["type"])
            if row["difficulty"]:
                row["difficulty"] = _norm_diff(row["difficulty"])
            questions.append(row)

    if not questions:
        raise ValueError(
            "No questions found in DOCX file."
        )

    return questions


# ==========================================
# MAIN LOADER
# ==========================================
def load_questions_file(filepath):
    ext = os.path.splitext(
        filepath
    )[1].lower()

    if ext == ".csv":
        return parse_csv_file(filepath)

    if ext == ".json":
        return parse_json_file(filepath)

    if ext == ".docx":
        return parse_docx_file(filepath)

    raise ValueError(
        "Supported formats: .csv, .json, .docx"
    )