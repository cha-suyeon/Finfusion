# llm_agent.py

# from langchain.chat_models import ChatOllama
from langchain_ollama import ChatOllama
from retriever import retrieve_relevant_chunks

def build_prompt(query: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(contexts)
    prompt = f"""
            당신은 SEC 보고서를 분석하는 금융 애널리스트입니다.
            아래는 Apple Inc.의 10-K 보고서에서 추출된 관련 정보입니다.

            ---------------------
            {context_text}
            ---------------------

            이제 다음 질문에 대해 단계적으로 분석하고, 가능한 경우 **정확한 숫자와 백분율을 포함하여** 응답해 주세요:

            질문: {query}

            답변 형식 예시:
            1) 관련 수치를 문서에서 찾습니다.
            2) 비교 또는 변화율을 계산합니다.
            3) 투자자 입장에서 어떤 의미인지 해석합니다.

            답변:
            """

    return prompt

def answer_question_with_context(query: str, ticker: str, top_k: int = 5) -> str:
    docs = retrieve_relevant_chunks(query, ticker, top_k=top_k)
    contexts = [doc.page_content for doc in docs]

    llm = ChatOllama(model="openhermes")
    prompt = build_prompt(query, contexts)

    print("***LLM 프롬프트 입력 준비 완료")
    response = llm.invoke(prompt)
    return response.content