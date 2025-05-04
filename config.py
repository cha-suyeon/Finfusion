"""
config.py

Finfusion 프로젝트 전역 설정.
환경변수를 통해 값 조정 가능하며, 기본값은 아래와 같습니다.
"""

import os

# ── SEC EDGAR Downloader 설정 ──────────────────────────────────────────
# Downloader 사용자명/이메일 (환경변수: SEC_EDGAR_USERNAME, SEC_EDGAR_EMAIL)
SEC_EDGAR_USERNAME = os.getenv("SEC_EDGAR_USERNAME", "SoosungEng")
SEC_EDGAR_EMAIL    = os.getenv("SEC_EDGAR_EMAIL",    "dronesquare@soosungeng.com")

# 10-K 보고서 저장 기본 경로 (환경변수: SEC_EDGAR_BASE_DIR)
SEC_EDGAR_BASE_DIR = os.getenv("SEC_EDGAR_BASE_DIR", "sec-edgar-filings")


# ── 청킹 (Chunking) 설정 ──────────────────────────────────────────────
# 텍스트 분할 크기 및 오버랩 (환경변수: CHUNK_SIZE, CHUNK_OVERLAP)
CHUNK_SIZE      = int(os.getenv("CHUNK_SIZE",      1024))
CHUNK_OVERLAP   = int(os.getenv("CHUNK_OVERLAP",   100))
# langchain.text_splitter 사용 시 구분자
CHUNK_SEPARATORS = ["\n\n", "\n", ". ", " "]


# ── 임베딩 & 인덱스 저장 설정 ─────────────────────────────────────────
# 로컬 FAISS 인덱스 루트 디렉터리 (환경변수: INDEX_ROOT)
INDEX_ROOT = os.getenv("INDEX_ROOT", "data/index")

# 사용할 임베딩 모델 이름 (환경변수: EMBEDDING_MODEL_NAME)
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/e5-base-v2")


# ── 검색 (Retrieval) 설정 ─────────────────────────────────────────────
# 초기 BM25/FAISS 결합 후 반환할 문서 수
TOP_K_INITIAL = int(os.getenv("TOP_K_INITIAL",  100))
# 최종 사용자 응답용 상위 청크 개수
TOP_K_FINAL   = int(os.getenv("TOP_K_FINAL",      5))

# RRF 하이퍼파라미터 (k: weight 조정값)
RRF_K = int(os.getenv("RRF_K", 60))


# ── LLM Agent 설정 ───────────────────────────────────────────────────
# 사용할 LLM 모델 (환경변수: LLM_MODEL_NAME)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "openhermes")
# 응답 생성 시 온도 (환경변수: LLM_TEMPERATURE)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
# ReAct / ToT 체인 단계별 최대 토큰 수
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 2048))


# ── 로깅 & 일반 설정 ─────────────────────────────────────────────────
# 로깅 레벨 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

