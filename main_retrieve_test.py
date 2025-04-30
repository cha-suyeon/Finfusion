# main_retrieve_test.py

from retriever import retrieve_relevant_chunks

query = "애플의 최근 매출 성장률은 어떻게 되나요?"
ticker = "AAPL"

results = retrieve_relevant_chunks(query, ticker)

print("검색된 청크 결과:")
for i, doc in enumerate(results, 1):
    print(f"\n--- Chunk {i} ---\n{doc.page_content[:500]}")