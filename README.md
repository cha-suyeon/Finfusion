# 🧠 FinFusion: RAG-Based Financial Analysis Assistant


[![PDF](https://img.shields.io/badge/📄%20View-PDF-blue?logo=adobeacrobatreader&logoColor=white)](https://github.com/cha-suyeon/Finfusion/blob/master/FinFusion.pdf)

[![YouTube](https://img.shields.io/badge/Watch-Video-red?logo=youtube&logoColor=white)](링크삽입)


**FinFusion**은 SEC 10-K 보고서를 분석하고 요약하기 위해 설계된 **RAG 기반 금융 특화 QA 시스템**입니다.  
다단계 문서 검색, 임베딩 기반 벡터 검색, 고도화된 프롬프트 전략을 통해 **해석 가능한 투자 인사이트**를 제공합니다.

---

## 🧩 Key Features

- 🔍 **Hybrid Retrieval**: BM25 + FAISS + RRF (Reciprocal Rank Fusion) 기반 다단계 검색  
- 🧠 **LLM Reasoning**: ReAct, Tree-of-Thoughts 기반의 체계적 추론 및 Query-aware Re-ranking  
- 📑 **SEC Filing Parsing**: SEC 10-K 보고서 구조(Item 단위) 기반 파싱 및 처리  
- 🧾 **Item-Level Chunking**: PART/ITEM 기준으로 문서 구조화  
- 💡 **Investment Memo Generator**: 투자 인사이트 요약 및 리스크 분석 자동 생성

---

## 🛠️ Tech Stack

| Category         | Tools & Libraries                                      |
|------------------|--------------------------------------------------------|
| Language Model   | [Ollama](https://ollama.com/) + `openhermes` (로컬 LLM) |
| Vector Database  | FAISS (Facebook AI Similarity Search)                 |
| Sparse Retrieval | BM25 via `rank_bm25`                                  |
| Prompting        | ReAct, Tree-of-Thoughts                               |
| Framework        | LangChain                                             |
| Parsing          | PyMuPDF, BeautifulSoup                                |
| Programming      | Python 3.10+, tqdm 등                                 |

---

## ⚙️ Setup Instructions

1. **가상환경 생성 및 활성화**

```bash
python -m venv rag-finance
source rag-finance/bin/activate
```

2. 필요 패키지 설치

```bash
pip install -r requirements.txt
```
requirements.txt에는 본 프로젝트에 필요한 모든 Python 패키지가 포함되어 있습니다.

3. Ollama 서버 실행 (로컬 LLM)

```bash
ollama serve
ollama run openhermes
```

---

## 🚀 Usage

설정 완료 후, 다음과 같이 메인 파이프라인을 실행할 수 있습니다:

```bash
python main.py --query "What are the key risk factors in Apple's 2018 10-K?"
```

현재는 [SEC EDGAR](https://www.sec.gov/search-filings)에서 수집한 10-K 보고서에 최적화되어 있습니다.

---

## 📁 Folder Structure

```
FinFusion/
│
├── requirements.txt
├── retriever.py
├── embedder.py
├── chunker.py
├── llm_agent.py
├── fusion_pipeline.py
...
└── data/
```

---

## 📚 References

1. Yao et al., 2022.  
   **ReAct: Synergizing Reasoning and Acting in Language Models**  
   [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

2. Jiang et al., 2023.  
   **Prompt-as-Program: Interpreting and Executing Programs from Language Instructions**  
   [https://arxiv.org/abs/2305.10855](https://arxiv.org/abs/2305.10855)

3. Yao et al., 2023.  
   **Tree of Thoughts: Deliberate Problem Solving with Large Language Models**  
   [https://arxiv.org/abs/2305.10601](https://arxiv.org/abs/2305.10601)

4. Aggarwal et al., 2024.  
   **ChunkRAG: A Chunk-Level Filtering Method for Reliable Retrieval-Augmented Generation**  
   [https://arxiv.org/abs/2410.19572](https://arxiv.org/abs/2410.19572)

5. Villardar, 2025.  
   **Semantic Decomposition and Selective Context Filtering for LLM-based QA**  
   [https://arxiv.org/abs/2502.14048](https://arxiv.org/abs/2502.14048)

6. Cormack et al., 2009.  
   **Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods**  
   [https://dl.acm.org/doi/10.1145/1571941.1572114](https://dl.acm.org/doi/10.1145/1571941.1572114)

7. Pillai et al., 2023.  
   **Hybrid Question Answering System: A FAISS and BM25 Approach**  
   [https://arxiv.org/abs/2308.07733](https://arxiv.org/abs/2308.07733)

8. Lewis et al., 2020.  
   **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (RAG)**  
   [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

9. Izacard & Grave, 2020.  
   **Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering (FiD)**  
   [https://arxiv.org/abs/2007.01282](https://arxiv.org/abs/2007.01282)

10. Longpre et al., 2023.  
    **The Flipped QA Paradigm for Answering Complex Questions**  
    [https://arxiv.org/abs/2305.13792](https://arxiv.org/abs/2305.13792)