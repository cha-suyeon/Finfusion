import logging
from typing import List
from langchain_ollama import ChatOllama

import config
from retriever import retrieve_relevant_chunks
from langchain.docstore.document import Document

logger = logging.getLogger(__name__)

class LlmAgent:
    """
    금융 도메인 특화 ReAct + ToT 스타일 LLM 에이전트
    """
    def __init__(
        self,
        model_name: str = config.LLM_MODEL_NAME,
        temperature: float = config.LLM_TEMPERATURE,
        max_tokens: int = config.LLM_MAX_TOKENS
    ):
        logger.info("Initializing LLM: model=%s, temp=%.2f, max_tokens=%d", model_name, temperature, max_tokens)
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def build_prompt(self, query: str, docs: list[Document], ticker: str) -> str:
        # 출처가 포함된 context 생성
        sources = []
        for doc in docs:
            meta = doc.metadata
            header = f"[Source: {meta.get('item', 'Unknown')} - {meta.get('item_title', '')}]"
            content = f"{header}\n{doc.page_content.strip()}"
            sources.append(content)

        context_text = "\n\n".join(sources)

        prompt = f"""You are a financial analyst specializing in SEC filings.

                Below is context from {ticker}'s 10-K report:

                {context_text}

                Please analyze the following question step by step, and include exact figures and percentages whenever possible:

                Question: {query}

                Example answer format:
                1) Identify the relevant figures in the document.
                2) Calculate any comparisons or rates of change.
                3) Interpret what these findings mean from an investor’s perspective.

                If the base value is not clearly stated, you may estimate it **only if there is strong supporting context**.
                Otherwise, state that it is missing.

                Answer:
                """
        
        return prompt

    def answer(
        self,
        query: str,
        ticker: str,
        top_k: int = config.TOP_K_FINAL
    ) -> str:
        """
        1) retrieve_relevant_chunks 로 청크 검색
        2) build_prompt 로 프롬프트 작성
        3) LLM 호출 후 응답 반환
        """
        logger.info("Retrieving top %d chunks for ticker=%s, query=%s", top_k, ticker, query)
        docs: List[Document] = retrieve_relevant_chunks(query, ticker, top_k=top_k)
        # contexts = [doc.page_content for doc in docs]

        prompt = self.build_prompt(query, docs, ticker)
        logger.info("Prompt built, invoking LLM...")
        response = self.llm.invoke(prompt)
        logger.info("LLM response received")
        return response.content

# 편의 함수

def answer_question_with_context(
    query: str,
    ticker: str,
    top_k: int = config.TOP_K_FINAL
) -> str:
    agent = LlmAgent()
    return agent.answer(query, ticker, top_k)

answer_with_agent = answer_question_with_context