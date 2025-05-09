# batch_runner.py
import json
from fusion_pipeline import FusionPipeline

class BatchQueryRunner:
    def __init__(self, ticker: str, query_set_path: str, limit: int = 1):
        self.ticker = ticker
        self.query_set_path = query_set_path
        self.limit = limit
        self.pipeline = FusionPipeline()

    def run(self) -> list[dict]:
        self.pipeline.ensure_index(self.ticker, limit=self.limit)

        with open(self.query_set_path, "r") as f:
            queries = json.load(f)

        results = []
        for q in queries:
            try:
                output = self.pipeline.answer(
                    ticker=self.ticker,
                    query=q["question"],
                    limit=self.limit,
                    answer_template=q.get("answer_template")
                )

                results.append({
                    "id": q.get("id"),
                    "question": q["question"],
                    "prompt": output.get("prompt", ""),
                    "answer": output.get("answer", ""),
                    "relevant_tables": output.get("relevant_tables", [])
                })

            except Exception as e:
                results.append({
                    "id": q.get("id"),
                    "question": q["question"],
                    "error": str(e)
                })

        return results