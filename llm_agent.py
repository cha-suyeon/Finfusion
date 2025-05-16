# llm_agent.py
import logging
from typing import List
from langchain_ollama import ChatOllama
import config
from retriever import retrieve_relevant_chunks
from langchain.docstore.document import Document
from llm_template_generator import generate_answer_template_from_llm

logger = logging.getLogger(__name__)

class LlmAgent:
    def __init__(self, model_name=config.LLM_MODEL_NAME, temperature=config.LLM_TEMPERATURE, max_tokens=config.LLM_MAX_TOKENS):
        self.llm = ChatOllama(model=model_name, temperature=temperature, max_tokens=max_tokens)

    def build_prompt(self, query: str, docs: list[Document], ticker: str, answer_template: list[str] | None = None) -> str:
        if answer_template is None:
            answer_template = generate_answer_template_from_llm(query)

        sources = []
        for doc in docs:
            meta = doc.metadata
            header = f"[Year: {meta.get('year')}] [Item: {meta.get('item')} - {meta.get('item_title')}]"

            # 테이블 추가 코드
            content = doc.page_content.strip()
            if "[Structured Table Data]" in content:
                content = "The following chunk contains tabular financial data. Use it when answering numeric questions.\n\n" + content

            sources.append(f"{header}\n{doc.page_content.strip()}")

        context_text = "\n\n".join(sources)
        instructions = "\n".join([
                                "You must strictly follow the rules below when generating your answer:",
                                "- Use only explicitly stated numbers from the filings. Do not infer or guess.",
                                "- If a number or statement is not explicitly available, say so clearly.",
                                "- Avoid speculative language. Focus on facts.",
                                "- Mention the year each number comes from (e.g., \"In 2023, revenue was...\").",
                                "- Do not average or estimate across years unless directly stated.",
                                "- Compare across years when relevant.",
                                "- Prioritize chunks that include structured tables ([Structured Table Data]) when answering numeric questions."
                            ])

        if answer_template:
            instructions += "\n\nPlease follow these steps:\n"
            instructions += "\n".join(f"{i+1}. {step}" for i, step in enumerate(answer_template))

        return f"""You are a financial analyst specializing in SEC filings.

                Some chunks may contain structured tables marked by [Structured Table Data].
                Prioritize those chunks for numeric accuracy when relevant.

                Below is context from {ticker}'s 10-K report across multiple years:

                {context_text}

                Question: {query}

                Instructions:
                {instructions}

                Answer:
                """

    def answer(self, query: str, ticker: str, top_k: int = config.TOP_K_FINAL, answer_template: list[str] | None = None) -> dict:
        docs: List[Document] = retrieve_relevant_chunks(query, ticker, top_k=top_k)
        prompt = self.build_prompt(query, docs, ticker, answer_template=answer_template)
        response = self.llm.invoke(prompt)

        table_chunks = [
            doc.page_content for doc in docs
            if doc.metadata.get("contains_table", False)
        ]

        answer_text = response.content.strip()
        if table_chunks:
            answer_text += "\n\n---\nRelevant Table(s):\n" + "\n\n".join(table_chunks[:3])  # 최대 3개

        return {
            "prompt": prompt.strip(),
            "answer": answer_text,
            "relevant_tables": table_chunks[:3]
        }

# 기존 단일 질문용
def answer_question_with_context(query: str, ticker: str, top_k: int = config.TOP_K_FINAL, answer_template: list[str] | None = None) -> dict:
    agent = LlmAgent()
    return agent.answer(query, ticker, top_k=top_k, answer_template=answer_template)

answer_with_agent = answer_question_with_context

# 기존 follow-up 방식 (no retrieval)
def answer_with_followup(followup_question: str, ticker: str, chat_history: list[dict]) -> str:
    llm = ChatOllama(model=config.LLM_MODEL_NAME, temperature=config.LLM_TEMPERATURE, max_tokens=config.LLM_MAX_TOKENS)

    try:
        previous_q = chat_history[-1]["question"]
        previous_a = chat_history[-1]["answer"]
    except (IndexError, KeyError):
        return "Cannot generate follow-up answer: missing prior question and answer."

    prompt = f"""You are a financial assistant trained on SEC 10-K filings.

            Prior question: {previous_q}

            Prior answer: {previous_a}

            Follow-up question: {followup_question}

            Please respond based on the prior context and the new question, and do not hallucinate numbers.

            Answer:
            """

    response = llm.invoke(prompt)
    return response.content.strip()

# 새 기능: follow-up 질문을 standalone으로 보정
def refine_followup_with_context(followup_question: str, prior_question: str, prior_answer: str) -> str:
    prompt = f"""You are a helpful assistant refining follow-up questions for document retrieval.

                Given the previous Q&A:
                Question: {prior_question}
                Answer: {prior_answer}

                And the follow-up question: {followup_question}

                Rewrite the follow-up so that it is standalone and complete for retrieval.

                Rewritten question:"""

    llm = ChatOllama(model=config.LLM_MODEL_NAME)
    response = llm.invoke(prompt)
    return response.content.strip()

# 새 기능: 보정된 query로 retrieval + 응답 생성
def answer_followup_with_retrieval(followup_question: str, ticker: str, chat_history: list[dict]) -> str:
    if not chat_history:
        return "Cannot proceed: No prior chat history."

    prior_q = chat_history[-1]["question"]
    prior_a = chat_history[-1]["answer"]

    # 1. Query 재구성
    refined_query = refine_followup_with_context(followup_question, prior_q, prior_a)
    print(f"[DEBUG] Refined Query: {refined_query}")

    # 2. Chunk retrieval
    docs = retrieve_relevant_chunks(refined_query, ticker, top_k=config.TOP_K_FINAL)
    print(f"[DEBUG] Retrieved {len(docs)} chunks")

    # 3. Prompt 구성 및 응답 생성
    agent = LlmAgent()
    prompt = agent.build_prompt(refined_query, docs, ticker)
    response = agent.llm.invoke(prompt)

    return response.content.strip()
