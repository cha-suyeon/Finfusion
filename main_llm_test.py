from llm_agent import answer_question_with_context

ticker = "AAPL"
query = "애플의 최근 매출 성장률은 어떻게 되나요?"

response = answer_question_with_context(query, ticker)

print("LLM 응답:")
print(response)