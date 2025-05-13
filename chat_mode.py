import json
from llm_agent import answer_followup_with_retrieval

def load_chat_history(result_path):
    with open(result_path, "r") as f:
        data = json.load(f)

    chat_history = []
    for item in data:
        if "question" in item and "answer" in item:
            chat_history.append({
                "question": item["question"],
                "answer": item["answer"]
            })
    return chat_history

def chat_loop(ticker: str, result_path: str):
    print(f"[CHAT MODE] Chatting with {ticker} using results from {result_path}")
    chat_history = load_chat_history(result_path)
    _chat_session(ticker, chat_history)

def chat_loop_with_history(ticker: str, chat_history: list[dict]):
    print(f"[CHAT MODE] Continuing conversation with {ticker} based on previous answer.")
    _chat_session(ticker, chat_history)

def _chat_session(ticker: str, chat_history: list[dict]):
    while True:
        followup_question = input("\nYou (follow-up): ")
        if followup_question.lower() in ["exit", "quit", "bye", "종료", "끝"]:
            print("👋 Chat session ended.")
            break

        print(f"\n[DEBUG] Prior Question: {chat_history[-1]['question']}")
        print(f"[DEBUG] Prior Answer Summary: {chat_history[-1]['answer'][:100]}...")

        answer = answer_followup_with_retrieval(
            followup_question,
            ticker=ticker,
            chat_history=chat_history
        )

        print(f"=== Finfusion 응답 ===:\n{answer}")
        chat_history.append({"question": followup_question, "answer": answer})
