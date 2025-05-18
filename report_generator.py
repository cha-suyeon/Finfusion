import os
import json

def json_to_markdown(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_path, "w", encoding="utf-8") as md:
        md.write("# 📝 SEC 10-K QA Results\n\n")
        for i, item in enumerate(data, start=1):
            md.write(f"## Q{i}. {item['question'].strip()}\n\n")
            md.write(f"**Prompt**\n\n```\n{item['prompt'].strip()}\n```\n\n")
            md.write(f"**Answer**\n\n```\n{item['answer'].strip()}\n```\n\n")
            md.write("---\n\n")

def batch_process_results(root_dir="results"):
    for company in os.listdir(root_dir):
        company_dir = os.path.join(root_dir, company)
        if os.path.isdir(company_dir):
            for filename in os.listdir(company_dir):
                if filename.endswith(".json") and filename.startswith("results_"):
                    json_path = os.path.join(company_dir, filename)
                    base_name = os.path.splitext(filename)[0]
                    output_md = os.path.join(company_dir, f"{base_name}.md")

                    # 이미 .md 파일이 있으면 건너뜀
                    if os.path.exists(output_md):
                        print(f"[⏭️] Skipped (already exists): {output_md}")
                        continue

                    json_to_markdown(json_path, output_md)
                    print(f"[✅] Generated: {output_md}")

if __name__ == "__main__":
    batch_process_results("results")