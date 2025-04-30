# embedder.py

import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document

def create_faiss_index(chunks: list[str], index_dir: str = "data/index", model_name="intfloat/e5-base-v2"):
    docs = [Document(page_content=chunk) for chunk in chunks]
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    db = FAISS.from_documents(docs, embeddings)
    os.makedirs(index_dir, exist_ok=True)
    db.save_local(index_dir)
    return db
