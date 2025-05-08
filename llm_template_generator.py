# llm_template_generator.py
from langchain_ollama import ChatOllama

def generate_answer_template_from_llm(question: str) -> list[str]:
    prompt = f"""
                You are a prompt engineer. Given the financial question below, create a 3-step answer template that helps an LLM structure its response clearly and accurately. Avoid generic steps; focus on the specific structure needed to answer the question well.

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

# Example usage:
# print(generate_answer_template_from_llm("What were the total revenue and net income for the latest fiscal year?"))