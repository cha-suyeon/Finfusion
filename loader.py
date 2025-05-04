# loader.py

import os
import glob
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
import re

def fetch_sec_10k(ticker: str, limit=1):
    """
    지정한 티커의 10-K 보고서를 다운로드
    기본 저장 경로는 sec-edgar-filings/
    """
    dl = Downloader("SoosungEng", "dronesquare@soosungeng.com")
    dl.get("10-K", ticker, limit=limit)


def extract_clean_10k_text(raw_text: str) -> str:
    """
    Item 1~Item 8 사이의 구간만 추출하여 잡음 제거
    """
    # 구간 시작 (예: "Item 1. Business")
    start_match = re.search(r"Item\s+1[\.\s\-]+Business", raw_text, re.IGNORECASE)
    start = start_match.start() if start_match else 0

    # 구간 끝 (예: "Item 8. Financial Statements")
    end_match = re.search(r"Item\s+8[\.\s\-]+Financial Statements", raw_text, re.IGNORECASE)
    end = end_match.start() if end_match else len(raw_text)

    # 본문 텍스트 자르기
    section = raw_text[start:end]

    # 비정상 ASCII 제거 (바이너리 인코딩 제거)
    clean = ''.join([c if 32 <= ord(c) <= 126 or c in '\n\r\t' else ' ' for c in section])
    return clean


def get_latest_10k_text(ticker: str, base_dir="sec-edgar-filings") -> str:
    import glob, os
    from bs4 import BeautifulSoup

    search_path = os.path.join(base_dir, ticker, "10-K", "*", "full-submission.txt")
    matches = glob.glob(search_path)
    if not matches:
        raise FileNotFoundError(f"No 10-K files found for {ticker} in {search_path}")

    latest_file = sorted(matches)[-1]
    with open(latest_file, encoding="utf-8", errors="ignore") as f:
        full_text = f.read()

    docs = full_text.split("<DOCUMENT>")
    candidates = []
    for doc in docs:
        doc_type = ""
        if "<TYPE>" in doc:
            doc_type = doc.split("<TYPE>")[1].split("\n")[0].strip()
        if "<TEXT>" in doc:
            body = doc.split("<TEXT>")[1].strip()
            candidates.append((doc_type, body))

    # 1순위: 10-K 텍스트
    for dtype, body in candidates:
        if dtype == "10-K":
            soup = BeautifulSoup(body, "html.parser")
            return soup.get_text(separator="\n")

    # 2순위: EX-13 (텍스트형 리포트)
    for dtype, body in candidates:
        if dtype.startswith("EX-13") or dtype.startswith("EX-99"):
            soup = BeautifulSoup(body, "html.parser")
            return soup.get_text(separator="\n")

    raise ValueError("No readable 10-K or EX-13 document found.")
