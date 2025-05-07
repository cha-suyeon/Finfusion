# retriever.py

import logging
from typing import List
from rank_bm25 import BM25Okapi
from langchain.docstore.document import Document
from langchain_ollama import ChatOllama

import config
from embedder import load_faiss_index

logger = logging.getLogger(__name__)


# def retrieve_relevant_chunks(query: str, ticker: str, top_k: int = 10):
#     db = load_faiss_index(ticker)

#     # FAISS 벡터 검색
#     vector_results = db.similarity_search(query, k=top_k)

#     # BM25 텍스트 기반 검색
#     docs_all = list(db.docstore._dict.values())
#     bm25 = BM25Okapi([doc.page_content for doc in docs_all])
#     bm25_top_k_contents = bm25.get_top_n(query.split(), docs_all, n=top_k)

#     # BM25 결과 재매핑 (original Document 객체 찾기)
#     bm25_docs = [doc for doc in docs_all if doc.page_content in bm25_top_k_contents]

#     # RRF 병합
#     merged = _reciprocal_rank_fusion(bm25_docs, vector_results, k=config.RRF_K)

#     # return merged[:top_k]
#     reranked = rerank_with_llm(query, merged, top_k=top_k)
#     return reranked


def retrieve_relevant_chunks(query: str, ticker: str, top_k: int = 20) -> List[Document]:
    db = load_faiss_index(ticker)

    # 전체 청크 불러오기
    docs_all = list(db.docstore._dict.values())

    # 질문 기반 Item 추론 및 필터링
    from item_semantic_filter import infer_items_by_semantic
    target_items = infer_items_by_semantic(query)
    if target_items:
        docs_all = [doc for doc in docs_all if doc.metadata.get("item") in target_items]
        logger.info("Filtered docs to items: %s", target_items)
    else:
        logger.info("No target items matched; using all chunks.")

    # FAISS 유사도 검색
    vector_results = db.similarity_search(query, k=top_k, documents=docs_all)

    # BM25 키워드 기반 검색
    bm25 = BM25Okapi([doc.page_content for doc in docs_all])
    bm25_top_k_contents = bm25.get_top_n(query.split(), docs_all, n=top_k)
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

def rerank_with_llm(query: str, docs: List[Document], top_k: int = 5) -> List[Document]:
    import re
    from langchain_ollama import ChatOllama  # 최신 방식
    llm = ChatOllama(model=config.LLM_MODEL_NAME)

    logger.info("Running LLM-based reranking on %d docs", len(docs))

    scored = []
    for doc in docs:
        # prompt = f"""On a scale of 1 to 10, how relevant is the following chunk to the question?

        #             Question: {query}

        #             Chunk:
        #             \"\"\"
        #             {doc.page_content}
        #             \"\"\"

        #             ONLY return a single number (1–10). Do not add explanation.
        #             Answer:
        #         """
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

