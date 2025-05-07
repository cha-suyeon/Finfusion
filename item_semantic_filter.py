# item_semantic_filter.py

from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np
import config

# 1. Item 설명 정의 (SEC 10-K 표준 전체 1~16 포함)
item_descriptions: Dict[str, str] = {
    "Item 1": "Description of the business including operations and structure.",
    "Item 1A": "Risk factors that may affect the company's business and performance.",
    "Item 1B": "Unresolved comments from SEC staff.",
    "Item 2": "Information about the company’s physical properties.",
    "Item 3": "Legal proceedings involving the company.",
    "Item 4": "Mine safety disclosures (for applicable companies).",
    "Item 5": "Market for the company’s common equity and related matters.",
    "Item 6": "Selected financial data (if provided).",
    "Item 7": "Management’s discussion and analysis (MD&A) of financial condition and results.",
    "Item 7A": "Quantitative and qualitative disclosures about market risk.",
    "Item 8": "Financial statements and supplementary financial data.",
    "Item 9": "Changes in and disagreements with accountants on accounting and financial disclosure.",
    "Item 9A": "Controls and procedures related to financial reporting.",
    "Item 9B": "Other information not reported elsewhere.",
    "Item 9C": "Disclosure regarding cybersecurity (if required).",
    "Item 10": "Information about directors, executive officers, and corporate governance.",
    "Item 11": "Executive compensation and related disclosure.",
    "Item 12": "Security ownership of certain beneficial owners and management.",
    "Item 13": "Certain relationships and related party transactions.",
    "Item 14": "Principal accounting fees and services.",
    "Item 15": "Exhibits, financial statement schedules.",
    "Item 16": "Form 10-K summary (optional)."
}

# 2. 임베딩 모델 로드 & Item 설명 벡터 생성 (최초 1회 캐시 가능)
embedding_model = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)

item_vectors: Dict[str, np.ndarray] = {
    item: np.array(embedding_model.embed_query(desc))
    for item, desc in item_descriptions.items()
}

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 3. Query 임베딩 → 유사도 기반 Top-K Item 추론
def infer_items_by_semantic(query: str, top_k: int = 3) -> List[str]:
    query_vec = np.array(embedding_model.embed_query(query))

    # scores = {
    #     item: cosine_similarity([query_vec], [vec])[0][0]  # [[score]] 형태라 [0][0] 추출
    #     for item, vec in item_vectors.items()
    # }

    scores = {
    item: cosine_similarity(query_vec, vec)
    for item, vec in item_vectors.items()
    }

    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [item for item, score in sorted_items[:top_k]]
