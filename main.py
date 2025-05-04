# main.py

import argparse
from fusion_pipeline import FusionPipeline

def main():
    parser = argparse.ArgumentParser(description="Finfusion 질의 인터페이스")
    parser.add_argument("--ticker", required=True, help="조회할 기업 티커")
    parser.add_argument("--query", required=True, help="자연어 질의문")
    args = parser.parse_args()

    pipe = FusionPipeline()
    answer = pipe.answer(args.ticker, args.query)
    print("\n=== Finfusion 응답 ===")
    print(answer)

if __name__ == "__main__":
    main()