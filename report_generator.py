import os
import json
from datetime import datetime

def generate_markdown_report(result_path: str, output_dir: str = "reports", report_name: str | None = None):
    with open(result_path, "r") as f:
        data = json.load(f)

    if not data:
        raise ValueError("Empty result file.")

    ticker = data[0].get("ticker", "Unknown")
    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = report_name or f"{ticker}_report_{ts}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        f.write(f"# {ticker} SEC 10-K QA Report\n\n")
        for item in data:
            qid = item.get("id", "?")
            question = item.get("question", "(No question)")
            answer = item.get("answer", "(No answer)")
            tables = item.get("relevant_tables", [])

            f.write(f"## Q{qid}: {question}\n\n")
            f.write(f"**Answer:**\n\n{answer.strip()}\n\n")

            if tables:
                f.write(f"**Relevant Tables:**\n\n")
                for t in tables[:3]:
                    f.write(f"> {t.replace('\n', '\n> ')}\n\n")

    print(f"[✓] Markdown report saved to: {filepath}")
    return filepath

if __name__ == "__main__":
    input_path = "/Users/suyeoncha/Finfusion/results/SBUX/results_SBUX.json"
    output_dir = "reports"
    generate_markdown_report(input_path, output_dir, report_name="2023_SBUX_report.md")

    print(f"[DONE] Report saved to {output_dir}/2023_SBUX_report.md")
