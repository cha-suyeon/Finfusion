# llm_template_generator.py
from langchain_ollama import ChatOllama

def generate_answer_template_from_llm(question: str, ticker: str | None = None) -> list[str]:
    context = f"The company is {ticker}." if ticker else ""
    prompt = f"""
                You are a prompt engineer helping design financial question templates for an LLM.

                Given the question below, and considering the company in question is "{ticker}", generate a 3-step answer template that helps the LLM answer accurately using SEC 10-K filings.

                Do not default to vague summaries. Instead, generate specific, context-aware steps tailored to how the question would be answered from a 10-K.

                {context}
                Question: "{question}"

                Template:
                1.
                2.
                3.
            """
    llm = ChatOllama(model="openhermes")  # or your preferred LLM model
    response = llm.invoke(prompt).content.strip()
    lines = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]
    return lines[:3] if len(lines) >= 2 else []