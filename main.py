# main.py

import argparse
import json
from fusion_pipeline import FusionPipeline
from batch_runner import BatchQueryRunner

def main():
    parser = argparse.ArgumentParser(description="Finfusion 질의 인터페이스")
    parser.add_argument("--ticker", required=True, help="조회할 기업 티커")
    parser.add_argument("--query", help="자연어 질의문 (단일 모드)")
    # parser.add_argument("--query_set", default="/Users/suyeoncha/Finfusion/query_set.json", help="쿼리셋 JSON 경로 (일괄 모드)")
    parser.add_argument("--query_set", help="쿼리셋 JSON 경로 (일괄 모드)")
    parser.add_argument("--limit", type=int, default=1, help="가져올 10-K 보고서 수 (기본 1)")
    args = parser.parse_args()

    if args.query_set:
        print(f"[MODE] Batch Query Mode with {args.query_set}")
        runner = BatchQueryRunner(args.ticker, args.query_set, limit=args.limit)
        results = runner.run()
        for r in results:
            print(f"\n=== Q{r['id']} ===\n{r['question']}\n\n{r['answer']}\n")

    elif args.query:
        print(f"[MODE] Single Query Mode")
        pipe = FusionPipeline()
        pipe.ensure_index(args.ticker, limit=args.limit)
        answer = pipe.answer(args.ticker, args.query, limit=args.limit)
        print("\n=== Finfusion 응답 ===")
        print(answer)

    else:
        raise ValueError("Either --query or --query_set must be provided.")

if __name__ == "__main__":
    main()