# retriever.py

import os
from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings

def load_faiss_index(ticker: str, index_base_path: str = "data/index"):
    index_path = os.path.join(index_base_path, ticker)
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index for {ticker} not found in {index_path}")
    
    print("***임베딩 모델 로딩 시작")
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/e5-base-v2")
    print("***임베딩 모델 로딩 완료")  

    return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

# def retrieve_relevant_chunks(query: str, ticker: str, top_k: int = 10):
#     db = load_faiss_index(ticker)

#     # results = db.similarity_search(query, k=top_k)
#     results_with_scores = db.similarity_search_with_score(query, k=20)
#     results = [doc for doc, score in results_with_scores if score < 0.4]  # 유사도가 높은 것만 필터

#     return results

def retrieve_relevant_chunks(query: str, ticker: str, top_k: int = 10):
    db = load_faiss_index(ticker)

    # FAISS 벡터 검색
    vector_results = db.similarity_search(query, k=top_k)

    # BM25 검색 준비 (텍스트 기반 키워드 검색)
    # docs = db.docstore._dict.values()  # 모든 문서
    docs = list(db.docstore._dict.values()) # 모든 문서
    bm25 = BM25Okapi([doc.page_content for doc in docs])
    # bm25_results = [docs[i] for i in bm25.get_top_n(query.split(), docs, n=top_k)]
    bm25_results = bm25.get_top_n(query.split(), docs, n=top_k)

    # 병합 (RRF)
    merged_results = reciprocal_rank_fusion(bm25_results, vector_results)

    return merged_results[:top_k]

def reciprocal_rank_fusion(bm25_docs, vector_docs, k=60):
    from collections import defaultdict

    doc_scores = defaultdict(float)

    def doc_id(doc):
        return doc.page_content.strip()[:100]  # 청크의 앞부분으로 ID 유추

    # BM25
    for rank, doc in enumerate(bm25_docs):
        doc_scores[doc_id(doc)] += 1 / (k + rank)

    # Vector
    for rank, doc in enumerate(vector_docs):
        doc_scores[doc_id(doc)] += 1 / (k + rank)

    # 스코어 정렬
    sorted_doc_ids = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

    # 결과 문서 재구성
    seen_ids = set()
    merged_docs = []
    for doc_id_score in sorted_doc_ids:
        for doc in bm25_docs + vector_docs:
            if doc_id(doc) == doc_id_score[0] and doc_id(doc) not in seen_ids:
                merged_docs.append(doc)
                seen_ids.add(doc_id(doc))
                break
    return merged_docs