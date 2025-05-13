import argparse
import json
from datetime import datetime
from pathlib import Path

from fusion_pipeline import FusionPipeline
from batch_runner import BatchQueryRunner
from chat_mode import chat_loop, chat_loop_with_history

def main():
    parser = argparse.ArgumentParser(description="Finfusion 질의 인터페이스")
    parser.add_argument("--ticker", required=True, help="조회할 기업 티커")
    parser.add_argument("--query", help="자연어 질의문 (단일 모드)")
    parser.add_argument("--query_set", help="쿼리셋 JSON 경로 (일괄 모드)")
    parser.add_argument("--limit", type=int, default=1, help="가져올 10-K 보고서 수 (기본 1)")
    parser.add_argument("--chat", action="store_true", help="기존 결과 기반 채팅 모드")
    parser.add_argument("--result", help="기존 결과 JSON 경로 (chat 모드와 함께 사용)")
    args = parser.parse_args()

    if args.chat:
        if not args.result:
            raise ValueError("--chat 모드 사용 시 --result 파일 경로가 필요합니다.")
        chat_loop(args.ticker, args.result)
        return

    if args.query_set:
        print(f"[MODE] Batch Query Mode with {args.query_set}")
        runner = BatchQueryRunner(args.ticker, args.query_set, limit=args.limit)
        results = runner.run()

        output_dir = Path("results") / args.ticker
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"results_{args.ticker}_{ts}.json"

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"[✓] Saved results to: {output_path}")

        for r in results:
            print(f"\n=== Q{r['id']} ===\n{r['question']}\n\n{r['answer']}\n")

        follow_up = input("\n💬 Would you like to enter chat mode for follow-up questions? [y/n]: ")
        if follow_up.lower() == "y":
            chat_loop(args.ticker, output_path)

    elif args.query:
        print(f"[MODE] Single Query Mode")
        pipe = FusionPipeline()
        pipe.ensure_index(args.ticker, limit=args.limit)
        result = pipe.answer(args.ticker, args.query, limit=args.limit)

        print("\n=== Finfusion 응답 ===")
        print(result["answer"])

        follow_up = input("\n💬 Would you like to enter chat mode for follow-up questions? [y/n]: ")
        if follow_up.lower() == "y":
            chat_history = [{"question": args.query, "answer": result["answer"]}]
            chat_loop_with_history(args.ticker, chat_history)

    else:
        raise ValueError("Either --query, --query_set, or --chat with --result must be provided.")

if __name__ == "__main__":
    main()