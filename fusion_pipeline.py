# fusion_pipeline.py

import os
from loader import fetch_sec_10k, get_latest_10k_text
from chunker import chunk_text_by_item
from embedder import create_faiss_index, load_faiss_index
from retriever import retrieve_relevant_chunks
from llm_agent import answer_with_agent

class FusionPipeline:
    def __init__(self, base_dir="sec-edgar-filings", index_root="data/index"):
        self.base_dir = base_dir
        self.index_root = index_root

    def ensure_index(self, ticker: str):
        idx_dir = os.path.join(self.index_root, ticker)
        if not os.path.isdir(idx_dir):
            print(f"[INFO] {ticker} 인덱스가 없으므로 생성합니다.")
            # 1) SEC 10-K 다운로드 (없으면)
            fetch_sec_10k(ticker)
            # 2) 텍스트 추출 → 청킹 → 인덱스 생성
            raw = get_latest_10k_text(ticker, base_dir=self.base_dir)
            chunks = chunk_text_by_item(raw)
            # 3) 인덱스 생성 (ticker, index_root로 전달)
            create_faiss_index(chunks,
                               ticker,
                               index_root=self.index_root)
        else:
            print(f"[INFO] {ticker} 인덱스가 이미 존재합니다.")

    def retrieve(self, ticker: str, query: str, top_k=15):
        return retrieve_relevant_chunks(query, ticker, top_k=top_k)

    def answer(self, ticker: str, query: str):
        # 1) 인덱스 확인/생성
        self.ensure_index(ticker)
        # 2) agent에게 ticker 전달
        return answer_with_agent(query, ticker)
