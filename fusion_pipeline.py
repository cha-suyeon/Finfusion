# # fusion_pipeline.py
# import os
# from loader import fetch_sec_10k, get_latest_10k_texts
# from chunker import chunk_text_by_item
# from embedder import create_faiss_index, load_faiss_index
# from retriever import retrieve_relevant_chunks
# from llm_agent import answer_with_agent

# class FusionPipeline:
#     def __init__(self, base_dir="data", index_root="data/index"):
#         self.base_dir = base_dir
#         self.index_root = index_root

#     def ensure_index(self, ticker: str, limit: int = 1):
#         idx_dir = os.path.join(self.index_root, ticker)
#         if not os.path.isdir(idx_dir):
#             print(f"[INFO] {ticker} 인덱스가 없으므로 생성합니다.")
#             fetch_sec_10k(ticker, limit=limit, save_dir=self.base_dir)
#             print(f"[DONE] {ticker} 10-K 보고서 다운로드 완료")

#             docs = get_latest_10k_texts(ticker, limit=limit, base_dir=self.base_dir)
#             print(f"[DONE] {ticker} 텍스트 추출 및 병합 완료")

#             # 📁 디렉토리 확인 및 생성
#             os.makedirs(self.base_dir, exist_ok=True)

#             # 📝 디버깅 텍스트 저장
#             debug_path = os.path.join(self.base_dir, f"{ticker}_10k_raw_debug.txt")
#             try:
#                 with open(debug_path, "w", encoding="utf-8") as f:
#                     for year, text, tables in docs:
#                         f.write(f"==== {ticker} ({year}) ====\n\n")
#                         # f.write(text[-3000:])  # 최대 3000자만 저장
#                         # 가운데 3000자
#                         mid = len(text) // 2
#                         start = max(0, mid - 1500)
#                         end = min(len(text), mid + 1500)
#                         f.write(text[start:end])
#                         f.write("\n\n---\n\n")
#                 print(f"[DEBUG] Raw 텍스트 저장 완료: {debug_path}")
#             except Exception as e:
#                 print(f"[ERROR] 텍스트 저장 실패: {e}")


#             chunks = chunk_text_by_item(docs)
#             print(f"[DONE] {ticker} 청킹 완료 (총 {len(chunks)}개 청크)")

#             create_faiss_index(chunks, index_dir=idx_dir)
#             print(f"[DONE] {ticker} 인덱스 생성 및 저장 완료 → {idx_dir}")
#         else:
#             print(f"[INFO] {ticker} 인덱스가 이미 존재합니다.")

#     def retrieve(self, ticker: str, query: str, top_k=15):
#         return retrieve_relevant_chunks(query, ticker, top_k=top_k)

#     def answer(self, ticker: str, query: str, limit: int = 1, answer_template: list[str] | None = None):
#         # self.ensure_index(ticker, limit=limit)
#         return answer_with_agent(query, ticker, answer_template=answer_template)

import os
from loader import fetch_sec_10k, get_latest_10k_texts
from chunker import chunk_text_by_item
from embedder import create_faiss_index, load_faiss_index
from retriever import retrieve_relevant_chunks
from llm_agent import answer_with_agent

# 유틸 함수 추가 (정규식 기반)
import re

def parse_conformed_period(text: str) -> str:
    """텍스트에서 CONFORMED PERIOD OF REPORT 추출 (예: 20231231 → 2023-12-31)"""
    match = re.search(r"CONFORMED PERIOD OF REPORT:\s*(\d{4})(\d{2})(\d{2})", text, re.IGNORECASE)
    if match:
        y, m, d = match.groups()
        return f"{y}-{m}-{d}"
    return "unknown"

def parse_filing_year_from_filename(filename: str) -> int:
    """EDGAR 스타일 파일명에서 제출 연도 추출"""
    match = re.search(r"-([0-9]{2})-", filename)
    if match:
        return 2000 + int(match.group(1))
    return -1

class FusionPipeline:
    def __init__(self, base_dir="data", index_root="data/index"):
        self.base_dir = base_dir
        self.index_root = index_root

    def ensure_index(self, ticker: str, limit: int = 1):
        idx_dir = os.path.join(self.index_root, ticker)
        if not os.path.isdir(idx_dir):
            print(f"[INFO] {ticker} 인덱스가 없으므로 생성합니다.")
            fetch_sec_10k(ticker, limit=limit, save_dir=self.base_dir)
            print(f"[DONE] {ticker} 10-K 보고서 다운로드 완료")

            docs = get_latest_10k_texts(ticker, limit=limit, base_dir=self.base_dir)
            print(f"[DONE] {ticker} 텍스트 추출 및 병합 완료")

            os.makedirs(self.base_dir, exist_ok=True)

            debug_path = os.path.join(self.base_dir, f"{ticker}_10k_raw_debug.txt")
            try:
                with open(debug_path, "w", encoding="utf-8") as f:
                    for year, text, tables in docs:
                        f.write(f"==== {ticker} ({year}) ====\n\n")
                        mid = len(text) // 2
                        start = max(0, mid - 1500)
                        end = min(len(text), mid + 1500)
                        f.write(text[start:end])
                        f.write("\n\n---\n\n")
                print(f"[DEBUG] Raw 텍스트 저장 완료: {debug_path}")
            except Exception as e:
                print(f"[ERROR] 텍스트 저장 실패: {e}")

            all_chunks = []
            for year, text, tables in docs:
                conformed_period = parse_conformed_period(text)  # ex: 2023-05-31
                filing_year = int(year) + 1  # 일반적으로 다음 해 제출됨
                chunks = chunk_text_by_item(
                    docs=[(year, text, tables)],
                    ticker=ticker,
                    company_name="Nike, Inc.",  # TODO: 실제로 추출하거나 ticker → 이름 맵핑
                    conformed_period=conformed_period,
                    filing_year=filing_year
                )
                all_chunks.extend(chunks)

            print(f"[DONE] {ticker} 청킹 완료 (총 {len(all_chunks)}개 청크)")
            create_faiss_index(all_chunks, index_dir=idx_dir)
            print(f"[DONE] {ticker} 인덱스 생성 및 저장 완료 → {idx_dir}")
        else:
            print(f"[INFO] {ticker} 인덱스가 이미 존재합니다.")

    def retrieve(self, ticker: str, query: str, top_k=15):
        return retrieve_relevant_chunks(query, ticker, top_k=top_k)

    def answer(self, ticker: str, query: str, limit: int = 1, answer_template: list[str] | None = None):
        return answer_with_agent(query, ticker, answer_template=answer_template)
