# embedder.py

import os
import logging
from uuid import uuid4
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

from typing import List, Union

import config

logger = logging.getLogger(__name__)


def create_faiss_index(
    chunks: Union[List[str], List[Document]],
    index_dir: str = "data/index",
    model_name: str = "intfloat/e5-base-v2"
) -> FAISS:
    # 1. Document 타입 확인
    if isinstance(chunks[0], str):
        docs = [Document(page_content=chunk) for chunk in chunks]
    elif isinstance(chunks[0], Document):
        docs = chunks
    else:
        raise ValueError("Input must be a list of strings or Document objects.")

    # 2. 임베딩 모델 로딩
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # 3. FAISS 벡터 인덱스 생성 및 저장
    db = FAISS.from_documents(docs, embeddings)
    os.makedirs(index_dir, exist_ok=True)
    db.save_local(index_dir)

    return db

def load_faiss_index(
    ticker: str,
    index_root: str = config.INDEX_ROOT,
    model_name: str = config.EMBEDDING_MODEL_NAME
) -> FAISS:
    """
    저장된 FAISS 인덱스를 불러옵니다.
    """
    index_path = os.path.join(index_root, ticker)
    if not os.path.isdir(index_path):
        raise FileNotFoundError(f"No FAISS index for {ticker} at {index_path}")

    logger.info("FAISS 인덱스 로딩: %s", index_path)
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    db = FAISS.load_local(
        folder_path=index_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
    logger.info("FAISS 인덱스 로딩 완료")
    return db
