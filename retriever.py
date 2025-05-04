# retriever.py

import logging
from typing import List
from rank_bm25 import BM25Okapi
from langchain.docstore.document import Document

import config
from embedder import load_faiss_index

logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(query: str, ticker: str, top_k: int = 10):
    db = load_faiss_index(ticker)

    # FAISS 벡터 검색
    vector_results = db.similarity_search(query, k=top_k)

    # BM25 텍스트 기반 검색
    docs_all = list(db.docstore._dict.values())
    bm25 = BM25Okapi([doc.page_content for doc in docs_all])
    bm25_top_k_contents = bm25.get_top_n(query.split(), docs_all, n=top_k)

    # BM25 결과 재매핑 (original Document 객체 찾기)
    bm25_docs = [doc for doc in docs_all if doc.page_content in bm25_top_k_contents]

    # RRF 병합
    merged = _reciprocal_rank_fusion(bm25_docs, vector_results, k=config.RRF_K)

    return merged[:top_k]


def _reciprocal_rank_fusion(bm25_docs, vector_docs, k=60):
    from collections import defaultdict

    def get_doc_id(doc):
        meta = doc.metadata
        return f"{meta.get('item', '')}:{meta.get('chunk_id', '')}"

    score_map = defaultdict(float)

    for rank, doc in enumerate(bm25_docs):
        score_map[get_doc_id(doc)] += 1 / (k + rank)

    for rank, doc in enumerate(vector_docs):
        score_map[get_doc_id(doc)] += 1 / (k + rank)

    # 정렬
    sorted_ids = sorted(score_map.items(), key=lambda x: x[1], reverse=True)

    # 중복 제거하고 다시 문서 리스트로 구성
    seen = set()
    merged = []
    for doc_id, _ in sorted_ids:
        for doc in bm25_docs + vector_docs:
            if get_doc_id(doc) == doc_id and doc_id not in seen:
                merged.append(doc)
                seen.add(doc_id)
                break

    return merged
