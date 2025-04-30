# main_chunk_and_embed.py

from loader import fetch_sec_10k, get_latest_10k_text
from chunker import chunk_text
from embedder import create_faiss_index

ticker = "AAPL"

fetch_sec_10k(ticker)                       # 수집
text = get_latest_10k_text(ticker)          # 텍스트 추출
chunks = chunk_text(text)                   # 청킹

print(f"\n총 청크 수: {len(chunks)}")
for i, chunk in enumerate(chunks[:5], 1):
    print(f"\n--- Chunk {i} ---\n{chunk[:1000]}")

db = create_faiss_index(chunks, index_dir=f"data/index/{ticker}")       # 벡터 저장
