# retriever.py
import logging
from typing import List
from rank_bm25 import BM25Okapi
from collections import defaultdict
from langchain_ollama import ChatOllama
from langchain.docstore.document import Document

import config
from embedder import load_faiss_index
from item_semantic_filter import infer_items_by_semantic

logger = logging.getLogger(__name__)

def retrieve_relevant_chunks(query: str, ticker: str, top_k: int = 20) -> List[Document]:
    db = load_faiss_index(ticker)
    all_docs = list(db.docstore._dict.values())

    # Item 필터
    target_items = infer_items_by_semantic(query)
    if target_items:
        all_docs = [doc for doc in all_docs if doc.metadata.get("item") in target_items]

    # 연도별 정렬
    from collections import defaultdict
    docs_by_year = defaultdict(list)
    for doc in all_docs:
        year = doc.metadata.get("year", "unknown")
        docs_by_year[year].append(doc)

    final_docs = []
    for year, docs in docs_by_year.items():
        # BM25
        bm25 = BM25Okapi([doc.page_content for doc in docs])
        bm25_top_k = bm25.get_top_n(query.split(), docs, n=top_k)

        # FAISS
        vector_results = db.similarity_search(query, k=top_k, documents=docs)

        # RRF
        merged = _reciprocal_rank_fusion(bm25_top_k, vector_results, k=config.RRF_K)

        # contains_table 우선 정렬
        merged.sort(key=lambda d: d.metadata.get("contains_table", False), reverse=True)

        final_docs.extend(merged[:top_k])

    # LLM re-ranking
    reranked = rerank_with_llm(query, final_docs, top_k=top_k)
    return reranked

# def retrieve_relevant_chunks(query: str, ticker: str, top_k: int = 20) -> List[Document]:
#     db = load_faiss_index(ticker)
#     all_docs = list(db.docstore._dict.values())

#     # 1. 의미 기반 Item 필터링
#     target_items = infer_items_by_semantic(query)
#     if target_items:
#         all_docs = [doc for doc in all_docs if doc.metadata.get("item") in target_items]
#         logger.info("Filtered docs to items: %s", target_items)
#     else:
#         logger.info("No target items matched; using all chunks.")

#     # 2. 연도별로 그룹핑
#     docs_by_year = defaultdict(list)
#     for doc in all_docs:
#         year = doc.metadata.get("year", "unknown")
#         docs_by_year[year].append(doc)

#     final_docs = []
#     for year, docs in docs_by_year.items():
#         logger.info(f"Retrieving from year: {year} with {len(docs)} docs")

#         # BM25
#         bm25 = BM25Okapi([doc.page_content for doc in docs])
#         bm25_top_k_contents = bm25.get_top_n(query.split(), docs, n=top_k)
#         bm25_docs = [doc for doc in docs if doc.page_content in bm25_top_k_contents]

#         # FAISS
#         vector_results = db.similarity_search(query, k=top_k, documents=docs)

#         # RRF 병합
#         merged = _reciprocal_rank_fusion(bm25_docs, vector_results, k=config.RRF_K)

#         # 상위 top_k 개수만 선택 (연도별로)
#         final_docs.extend(merged[:top_k])

#     # 전체 문서 중 top_k개만 LLM에 넣기 위해 relevance rerank 진행
#     reranked = rerank_with_llm(query, final_docs, top_k=top_k)

#     return reranked

def _reciprocal_rank_fusion(bm25_docs, vector_docs, k=60):
    from collections import defaultdict
    def get_doc_id(doc):
        meta = doc.metadata
        return f"{meta.get('year','')}:{meta.get('item','')}:{meta.get('chunk_id','')}"

    score_map = defaultdict(float)
    for rank, doc in enumerate(bm25_docs):
        score_map[get_doc_id(doc)] += 1 / (k + rank)
    for rank, doc in enumerate(vector_docs):
        score_map[get_doc_id(doc)] += 1 / (k + rank)

    sorted_ids = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    seen = set()
    merged = []
    for doc_id, _ in sorted_ids:
        for doc in bm25_docs + vector_docs:
            if get_doc_id(doc) == doc_id and doc_id not in seen:
                merged.append(doc)
                seen.add(doc_id)
                break
    return merged

def rerank_with_llm(query: str, docs: List[Document], top_k: int = 5) -> List[Document]:
    import re
    llm = ChatOllama(model=config.LLM_MODEL_NAME)

    logger.info("Running LLM-based reranking on %d docs", len(docs))

    scored = []
    for doc in docs:
        prompt = f"""
                Rate the relevance of the following document chunk to the question below
                on a scale from 1 (least relevant) to 10 (highly relevant), considering the following:

                - Whether it contains exact numeric figures (e.g., revenue, percentage growth)
                - Whether it helps directly answer the question, not just related background
                - Avoid guessing — prefer chunks that contain clearly stated data

                Question: {query}

                Chunk:
                \"\"\"
                {doc.page_content}
                \"\"\"

                ONLY return a number between 1 and 10. Do not explain.
                Answer:
                """
        try:
            response = llm.invoke(prompt).content.strip()
            match = re.search(r"\b(\d+(\.\d+)?)\b", response)
            if match:
                score = float(match.group(1))
                scored.append((score, doc))
            else:
                raise ValueError(f"No valid score found in response: {response}")
        except Exception as e:
            logger.warning("Failed to score a chunk: %s", e)

    reranked = [doc for _, doc in sorted(scored, key=lambda x: -x[0])]
    return reranked[:top_k]