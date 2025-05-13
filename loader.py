# loader.py

import os
import re
import glob
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader

def fetch_sec_10k(ticker: str, limit=1, save_dir="data"):
    dl = Downloader("SoosungEng", "dronesquare@soosungeng.com", download_folder=save_dir)
    dl.get("10-K", ticker, limit=limit)
    print(f"[DEBUG] Fetching 10-K for {ticker}, limit={limit}")

def extract_text_and_tables_from_html(html_text: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html_text, "html.parser")

    if not soup.find():
        return "", []

    plain_text = soup.get_text(separator="\n").strip()
    return plain_text, []

# def extract_text_and_tables_from_html(html_text: str) -> tuple[str, list[str]]:
#     soup = BeautifulSoup(html_text, "html.parser")

#     if not soup.find():
#         return "", []

#     tables = soup.find_all("table")
#     table_texts = []

#     for table in tables:
#         rows = table.find_all("tr")
#         if not rows or len(rows) < 2:
#             continue

#         # 가장 긴 행을 헤더 후보로 사용
#         max_row = max(rows, key=lambda r: len(r.find_all(["th", "td"])))
#         headers = [cell.get_text(strip=True) for cell in max_row.find_all(["th", "td"])]

#         if not headers or all(h == "" for h in headers):
#             continue  # 아무 값도 없으면 건너뜀

#         table_lines = [f"Table: {' | '.join(headers)}"]

#         for row in rows:
#             cells = row.find_all(["td", "th"])
#             values = [cell.get_text(strip=True) for cell in cells]
#             if len(values) != len(headers):
#                 continue
#             row_line = "- " + " | ".join(f"{h}: {v}" for h, v in zip(headers, values))
#             table_lines.append(row_line)

#         # 실질 내용 있는지 다시 확인
#         if len(table_lines) > 1:
#             table_texts.append("\n".join(table_lines))

#         table.decompose()  # 원문 제거

#     plain_text = soup.get_text(separator="\n").strip()
#     return plain_text, table_texts


def get_latest_10k_texts(ticker: str, limit: int = 1, base_dir="data") -> list[tuple[str, str, list[str]]]:
    search_path = os.path.join(base_dir, "sec-edgar-filings", ticker, "10-K", "*", "full-submission.txt")
    matches = sorted(glob.glob(search_path))[-limit:]

    if not matches:
        raise FileNotFoundError(f"No 10-K files found for {ticker} in {search_path}")

    results = []
    for path in matches:
        cik_year_match = re.search(r"10-K/([^/]+)/", path)
        if cik_year_match:
            cik_part = cik_year_match.group(1)
            year_match = re.search(r"-(\d{2})-", cik_part)
            year = "20" + year_match.group(1) if year_match else "Unknown"
        else:
            year = "Unknown"

        with open(path, encoding="utf-8", errors="ignore") as f:
            full_text = f.read()

        docs = full_text.split("<DOCUMENT>")
        for doc in docs:
            if "<TYPE>10-K" in doc and "<TEXT>" in doc:
                body = doc.split("<TEXT>")[1].strip()
                text, tables = extract_text_and_tables_from_html(body)
                print(f"[DEBUG] Extracted text length for {year}: {len(text)}, tables: {len(tables)}")
                results.append((year, text, tables))
                break

    return results