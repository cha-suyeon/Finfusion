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

    # Step 1: extract all <tr> rows as table-like lines
    rows = soup.find_all("tr")
    table_lines = []
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
        line = " | ".join(cell.get_text(strip=True) for cell in cells)
        if line.strip():
            table_lines.append(line)

    # Step 2: remove those <tr> so they don't affect plain text
    for tr in rows:
        tr.decompose()

    # Step 3: extract remaining plain text
    plain_text = soup.get_text(separator="\n").strip()

    # Step 4: join text and table lines
    if table_lines:
        table_text = "\n".join(table_lines)
        combined_text = f"{plain_text}\n\n[Structured Table Data]\n{table_text}"
    else:
        combined_text = plain_text

    return combined_text, []  # tables merged into text, so return [] for table list

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