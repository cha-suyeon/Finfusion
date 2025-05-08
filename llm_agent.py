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
            sources.append(f"{header}\n{doc.page_content.strip()}")

        context_text = "\n\n".join(sources)
        instructions = "\n".join([
            "- Compare across years when relevant.",
            "- Mention which year a number is from (e.g., \"in 2023, revenue was...\").",
            "- Do NOT fabricate numbers or guess.",
            "- If a value is missing, state it clearly.",
            "- If figures from multiple fiscal years are available, compare them.",
            "- Use only explicitly stated numbers. Do not estimate."
        ])

        if answer_template:
            instructions += "\n\nPlease follow these steps:\n"
            instructions += "\n".join(f"{i+1}. {step}" for i, step in enumerate(answer_template))

        return f"""You are a financial analyst specializing in SEC filings.

Below is context from {ticker}'s 10-K report across multiple years:

{context_text}

Question: {query}

Instructions:
{instructions}

Answer:
"""

    def answer(self, query: str, ticker: str, top_k: int = config.TOP_K_FINAL, answer_template: list[str] | None = None) -> str:
        docs: List[Document] = retrieve_relevant_chunks(query, ticker, top_k=top_k)
        prompt = self.build_prompt(query, docs, ticker, answer_template=answer_template)
        response = self.llm.invoke(prompt)
        return response.content

def answer_question_with_context(
    query: str,
    ticker: str,
    top_k: int = config.TOP_K_FINAL,
    answer_template: list[str] | None = None) -> str:
    agent = LlmAgent()
    return agent.answer(query, ticker, top_k=top_k, answer_template=answer_template)

answer_with_agent = answer_question_with_context
