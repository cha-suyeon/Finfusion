import os
import re
import glob
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader


def fetch_sec_10k(ticker: str, limit=1, save_dir="data"):
    """
    지정한 티커의 10-K 보고서를 다운로드.
    실제 저장 경로는 save_dir/sec-edgar-filings/<TICKER>/10-K/... 가 된다.
    """
    dl = Downloader("SoosungEng", "dronesquare@soosungeng.com", download_folder=save_dir)
    dl.get("10-K", ticker, limit=limit)


def extract_clean_10k_text(raw_text: str) -> str:
    """
    Item 1 ~ Item 8 사이의 구간을 추출하여 잡음 제거
    """
    start_match = re.search(r"Item\s+1[\.\s\-]+Business", raw_text, re.IGNORECASE)
    start = start_match.start() if start_match else 0

    end_match = re.search(r"Item\s+8[\.\s\-]+Financial Statements", raw_text, re.IGNORECASE)
    end = end_match.start() if end_match else len(raw_text)

    section = raw_text[start:end]
    clean = ''.join([c if 32 <= ord(c) <= 126 or c in '\n\r\t' else ' ' for c in section])
    return clean


def get_latest_10k_text(ticker: str, base_dir="data") -> str:
    """
    가장 최근의 10-K full-submission.txt 파일을 불러와서 텍스트를 추출
    """
    search_path = os.path.join(base_dir, "sec-edgar-filings", ticker, "10-K", "*", "full-submission.txt")
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

    # 우선순위 1: 10-K 문서
    for dtype, body in candidates:
        if dtype == "10-K":
            soup = BeautifulSoup(body, "html.parser")
            return soup.get_text(separator="\n")

    # 우선순위 2: EX-13 또는 EX-99 (대체 문서)
    for dtype, body in candidates:
        if dtype.startswith("EX-13") or dtype.startswith("EX-99"):
            soup = BeautifulSoup(body, "html.parser")
            return soup.get_text(separator="\n")

    raise ValueError("No readable 10-K or EX-13 document found.")
