# fusion_pipeline.py
import os
from loader import fetch_sec_10k, get_latest_10k_texts
from chunker import chunk_text_by_item
from embedder import create_faiss_index, load_faiss_index
from retriever import retrieve_relevant_chunks
from llm_agent import answer_with_agent

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

            chunks = chunk_text_by_item(docs)
            print(f"[DONE] {ticker} 청킹 완료 (총 {len(chunks)}개 청크)")

            create_faiss_index(chunks, index_dir=idx_dir)
            print(f"[DONE] {ticker} 인덱스 생성 및 저장 완료 → {idx_dir}")
        else:
            print(f"[INFO] {ticker} 인덱스가 이미 존재합니다.")

    def retrieve(self, ticker: str, query: str, top_k=15):
        return retrieve_relevant_chunks(query, ticker, top_k=top_k)

    def answer(self, ticker: str, query: str, limit: int = 1, answer_template: list[str] | None = None):
        # self.ensure_index(ticker, limit=limit)
        return answer_with_agent(query, ticker, answer_template=answer_template)

