# chat_mode.py
import json
import argparse
from llm_agent import answer_with_followup


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
    with open(result_path, "r") as f:
        results = json.load(f)

    chat_history = []
    while True:
        followup_question = input("\nYou (follow-up): ")
        if followup_question.lower() in ["exit", "quit", "bye", "종료", "끝"]:
            print("👋 Chat session ended.")
            break

        answer = answer_with_followup(
            followup_question,
            ticker=ticker,
            chat_history=chat_history
        )
        print(f"\nFinfusion:\n{answer}")
        chat_history.append({"question": followup_question, "answer": answer})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finfusion Chat Mode")
    parser.add_argument("--ticker", required=True, help="기업 티커")
    parser.add_argument("--result", required=True, help="사전 생성된 result JSON 경로")
    args = parser.parse_args()

    chat_loop(args.ticker, args.result)
