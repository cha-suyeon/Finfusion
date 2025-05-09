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

    tables = soup.find_all("table")
    table_texts = []

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue

        # Get headers
        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        if not headers:
            headers = [td.get_text(strip=True) for td in rows[0].find_all("td")]

        # Build plain-text table
        table_lines = []
        if headers:
            table_lines.append(f"Table: {' vs '.join(headers)}")
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                values = [cell.get_text(strip=True) for cell in cells]
                if len(values) == len(headers):
                    row_line = "- " + " | ".join(f"{h}: {v}" for h, v in zip(headers, values))
                    table_lines.append(row_line)

        if table_lines:
            table_texts.append("\n".join(table_lines))
        table.decompose()

    # Return remaining text + all parsed tables
    plain_text = soup.get_text(separator="\n").strip()
    return plain_text, table_texts

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


# import os
# import re
# import glob
# from bs4 import BeautifulSoup
# from sec_edgar_downloader import Downloader

# def fetch_sec_10k(ticker: str, limit=1, save_dir="data"):
#     dl = Downloader("SoosungEng", "dronesquare@soosungeng.com", download_folder=save_dir)
#     dl.get("10-K", ticker, limit=limit)
#     print(f"[DEBUG] Fetching 10-K for {ticker}, limit={limit}")

# def get_latest_10k_texts(ticker: str, limit: int = 1, base_dir="data") -> list[tuple[str, str]]:
#     search_path = os.path.join(base_dir, "sec-edgar-filings", ticker, "10-K", "*", "full-submission.txt")
#     matches = sorted(glob.glob(search_path))[-limit:]

#     if not matches:
#         raise FileNotFoundError(f"No 10-K files found for {ticker} in {search_path}")

#     results = []
#     for path in matches:
#         cik_year_match = re.search(r"10-K/([^/]+)/", path)
#         if cik_year_match:
#             cik_part = cik_year_match.group(1)
#             year_match = re.search(r"-(\d{2})-", cik_part)
#             year = "20" + year_match.group(1) if year_match else "Unknown"
#         else:
#             year = "Unknown"

#         with open(path, encoding="utf-8", errors="ignore") as f:
#             full_text = f.read()

#         docs = full_text.split("<DOCUMENT>")
#         for doc in docs:
#             if "<TYPE>10-K" in doc and "<TEXT>" in doc:
#                 body = doc.split("<TEXT>")[1].strip()
#                 clean_text = extract_text_with_plain_table(body)
#                 print(f"[DEBUG] Extracted text length for {year}: {len(clean_text)}")
#                 results.append((year, clean_text))
#                 break

#     return results

# def extract_text_with_plain_table(html_text: str) -> str:
#     soup = BeautifulSoup(html_text, "html.parser")

#     if not soup.find():  # soup is empty or broken
#         return ""

#     for table in soup.find_all("table"):
#         rows = table.find_all("tr")
#         parsed_lines = []

#         headers = [th.get_text(strip=True) for th in rows[0].find_all("th")] if rows else []
#         if not headers and rows:
#             headers = [td.get_text(strip=True) for td in rows[0].find_all("td")]

#         if headers:
#             parsed_lines.append(f"Table: {' vs '.join(headers)}")
#             for row in rows[1:]:
#                 cells = row.find_all(["td", "th"])
#                 values = [cell.get_text(strip=True) for cell in cells]
#                 if len(values) == len(headers):
#                     line = "- " + " | ".join(f"{h}: {v}" for h, v in zip(headers, values))
#                     parsed_lines.append(line)

#         if parsed_lines:
#             table.insert_before(soup.new_tag("p"))
#             table.previous_sibling.string = "\n".join(parsed_lines)
#         table.decompose()

#     return soup.get_text(separator="\n")
