# fusion_pipeline.py

import os
from loader import fetch_sec_10k, get_latest_10k_text
from chunker import chunk_text_by_item
from embedder import create_faiss_index, load_faiss_index
from retriever import retrieve_relevant_chunks
from llm_agent import answer_with_agent

class FusionPipeline:
    def __init__(self, base_dir="data", index_root="data/index"):
        self.base_dir = base_dir
        self.index_root = index_root

    def ensure_index(self, ticker: str):
        idx_dir = os.path.join(self.index_root, ticker)
        if not os.path.isdir(idx_dir):
            print(f"[INFO] {ticker} 인덱스가 없으므로 생성합니다.")
            # 1) SEC 10-K 다운로드 (없으면)
            fetch_sec_10k(ticker, limit=1, save_dir=self.base_dir)
            print(f"[DONE] {ticker} 10-K 보고서 다운로드 완료")

            # 2) 텍스트 추출
            raw = get_latest_10k_text(ticker, base_dir=self.base_dir)
            print(f"[DONE] {ticker} 텍스트 추출 완료")

            # 3) 청킹
            chunks = chunk_text_by_item(raw)
            print(f"[DONE] {ticker} 청킹 완료 (총 {len(chunks)}개 청크)")

            # 4) FAISS 인덱스 생성 (ticker, index_root로 전달)
            create_faiss_index(
                                chunks,
                                index_dir=os.path.join(self.index_root, ticker)
                                )
            
            print(f"[DONE] {ticker} 인덱스 생성 및 저장 완료 → {idx_dir}")
        else:
            print(f"[INFO] {ticker} 인덱스가 이미 존재합니다.")

    def retrieve(self, ticker: str, query: str, top_k=15):
        return retrieve_relevant_chunks(query, ticker, top_k=top_k)

    def answer(self, ticker: str, query: str):
        # 1) 인덱스 확인/생성
        self.ensure_index(ticker)
        # 2) agent에게 ticker 전달
        return answer_with_agent(query, ticker)
