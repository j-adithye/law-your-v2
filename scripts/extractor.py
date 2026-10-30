"""
Extract BNS sections from the PDF into data/processed/bns_sections.json

Layout of this PDF (from the gap printout):
  - gap 16 = next line of the same paragraph, gap 24 = new paragraph / heading
  - the bold section title sits on its OWN line, ABOVE the "1. (1) ..." line
    (and can even be on the previous page)
  - chapter heading = "CHAPTER I" line, then the chapter title in capitals
"""
import json
import os
import re

import pdfplumber

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE, "data", "raw", "BNS2023.pdf")
OUT_PATH = os.path.join(BASE, "data", "processed", "bns_sections.json")
HEADER_CUT = 60     # points cropped from the top of each page
FOOTER_CUT = 60     # points cropped from the bottom of each page
PARA_GAP = 20       # normal line gap is 16, paragraph gap is 24

SECTION_RE = re.compile(r"^(\d+[A-Z]?)\.\s+(.*)$")
CHAPTER_RE = re.compile(r"^CHAPTER\s+([IVXLC]+)\b")
# "(1)", "(a)", "(ii)" at the start of a line -> that line starts a new item
MARKER_RE = re.compile(r"^\((\d+[A-Z]?|[a-z]{1,2}|[ivx]+)\)\s")
SUBSECTION_RE = re.compile(r"^\(\d+[A-Z]?\)")
# lines to throw away completely
JUNK_RE = re.compile(r"^(Chapters and Sections HomePage|\d+)$")

BLOCK_STARTS = {
    "illustrations": re.compile(r"^illustrations?\b", re.I),
    "explanations": re.compile(r"^explanations?\b", re.I),
    "exceptions": re.compile(r"^exceptions?\b", re.I),
}
HEAD_ONLY_RE = re.compile(r"^illustrations?\.?$", re.I)
ANY_BLOCK_RE = re.compile(r"^(illustrations?|explanations?|exceptions?)\b", re.I)

def timer(func):
    def wrapper(*args,**kwargs):
        import time
        start = time.perf_counter()
        result = func(*args,**kwargs)
        end = time.perf_counter()
        tottime = end - start
        print(round(tottime,2))
        return result
    return wrapper

def is_bold(char):
    return "bold" in char["fontname"].lower()


def line_all_bold(line):
    chars = [c for c in line["chars"] if c["text"].strip()]
    return bool(chars) and all(is_bold(c) for c in chars)


def get_lines(page):
    body = page.crop((0, HEADER_CUT, page.width, page.height - FOOTER_CUT))
    return body.extract_text_lines(return_chars=True)


def clean_title(raw):
    return re.sub(r"[\s.—–-]+$", "", raw).strip()

@timer
def read_pdf():
    sections = []
    cur = None
    chapter = {"number": None, "title": ""}
    reading_chapter_title = False
    pending_title = ""      # bold heading waiting for its "N." line

    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            prev_bottom = None
            for line in get_lines(page):
                text = line["text"].strip()
                if not text or JUNK_RE.match(text):
                    continue

                gap = None if prev_bottom is None else round(line["bottom"] - prev_bottom)
                prev_bottom = line["bottom"]

                # ---- chapter heading ----
                m = CHAPTER_RE.match(text)
                if m:
                    chapter = {"number": m.group(1), "title": ""}
                    reading_chapter_title = True
                    pending_title = ""
                    continue
                if reading_chapter_title:
                    if text.isupper():
                        chapter["title"] = (chapter["title"] + " " + text).strip()
                        continue
                    reading_chapter_title = False

                # ---- new section: "N. ..." with a bold number ----
                m = SECTION_RE.match(text)
                first = next((c for c in line["chars"] if c["text"].strip()), None)
                if m and first is not None and is_bold(first):
                    if cur:
                        sections.append(cur)
                    cur = {
                        "section_number": m.group(1),
                        "chapter_number": chapter["number"],
                        "chapter_title": chapter["title"],
                        "title": clean_title(pending_title),
                        "page": page.page_number,
                        "paragraphs": [m.group(2)],
                    }
                    pending_title = ""
                    continue

                # ---- bold heading line (title of the NEXT section) ----
                if line_all_bold(line) and not ANY_BLOCK_RE.match(text):
                    if pending_title and gap is not None and gap <= PARA_GAP:
                        pending_title += " " + text       # title wrapped to 2 lines
                    else:
                        pending_title = text              # new heading replaces old one
                    continue

                # ---- normal body line ----
                if cur is None:
                    continue
                new_para = (
                    not cur["paragraphs"]
                    or (gap is not None and gap > PARA_GAP)
                    or bool(MARKER_RE.match(text))
                )
                if new_para:
                    cur["paragraphs"].append(text)
                else:
                    cur["paragraphs"][-1] += " " + text

    if cur:
        sections.append(cur)
    return sections


def split_blocks(paragraphs):
    out = {"body": [], "illustrations": [], "explanations": [], "exceptions": []}
    target = "body"
    for p in paragraphs:
        if HEAD_ONLY_RE.match(p):          # just the word "Illustration(s)."
            target = "illustrations"
            continue
        for name, rx in BLOCK_STARTS.items():
            if rx.match(p):
                target = name
                break
        else:
            # "(6) ..." after an illustration/explanation = back to the main text
            if target != "body" and SUBSECTION_RE.match(p):
                target = "body"
        out[target].append(p)
    return out

def main():
    result = []
    for s in read_pdf():
        s.update(split_blocks(s.pop("paragraphs")))
        result.append(s)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    empty = sum(1 for s in result if not s["title"])
    print(f"Saved {len(result)} sections to {OUT_PATH}")
    print(f"Sections with empty title: {empty}")


if __name__ == "__main__":
    main()