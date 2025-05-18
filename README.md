# 🧠 FinFusion: RAG-Based Financial Analysis Assistant


[![PDF](https://img.shields.io/badge/📄%20View-PDF-blue?logo=adobeacrobatreader&logoColor=white)](https://github.com/cha-suyeon/Finfusion/blob/master/FinFusion.pdf)

[![YouTube](https://img.shields.io/badge/Watch-Video-red?logo=youtube&logoColor=white)](링크삽입)


**FinFusion**은 SEC 10-K 보고서를 분석하고 요약하기 위해 설계된 **RAG 기반 금융 특화 QA 시스템**입니다.  
다단계 문서 검색, 임베딩 기반 벡터 검색, 고도화된 프롬프트 전략을 통해 **해석 가능한 투자 인사이트**를 제공합니다.

---

## 👩‍🔬 실험 결과 (Uber – Business Model & Revenue Drivers)

**Question:** *What is the company’s primary business model and revenue drivers?*  

<br>

**Model's Answer (based on SEC 10-K, 2024 filing for FY 2023):**
> “Uber is one of the largest open platforms for work in the world, providing accessible, flexible work in approximately 70 countries. Drivers are key parts of the marketplaces that Uber has created through its apps.”  
> “For the year ended December 31, 2023, the Company’s Mobility and Delivery revenue, net of incentives, was $32.0 billion and discounts, loyalty programs, promotions, refunds, and credits provided to end-users who are not customers totaled $1.7 billion.”

<br>

**평가 요약 (정성적 기준 기반):**
- ✅ 보고서 내 수치 ($32.0B, $1.7B)를 정확히 인용하고, 출처 항목까지 명확히 표기하여 **정확성(Accuracy)** 우수  
- ✅ "추정 금지", "단계별 설명" 등 프롬프트 지침을 충실히 따르며 **프롬프트 준수(Prompt Adherence)** 뛰어남  
- ✅ 질문 범위(사업 모델 + 수익원)를 빠짐없이 다루고, **사실 기반의 객관적 응답(Factuality)** 으로 **완결성(Completeness)** 충족

📂 실험 결과는 [result](https://github.com/cha-suyeon/Finfusion/tree/master/results) 폴더에서 확인하실 수 있습니다.
- CLICK! 👉 [ABNB](https://github.com/cha-suyeon/Finfusion/blob/master/results/ABNB/results_ABNB_20250518_183438.md), [COST](https://github.com/cha-suyeon/Finfusion/blob/master/results/COST/results_COST_20250517_223302.md), [NKE](https://github.com/cha-suyeon/Finfusion/blob/master/results/NKE/results_NKE_20250518_182254.md), [SBUX](https://github.com/cha-suyeon/Finfusion/blob/master/results/SBUX/results_SBUX_20250518_180241.md), [UBER](https://github.com/cha-suyeon/Finfusion/blob/master/results/UBER/results_UBER_20250518_175002.md), [V](https://github.com/cha-suyeon/Finfusion/blob/master/results/V/results_V_20250517_220135.md)

<br>

---

## 🧩 Key Features

- 🔍 **Hybrid Retrieval**: BM25 + FAISS + RRF (Reciprocal Rank Fusion) 기반 다단계 검색  
- 🧠 **LLM Reasoning**: ReAct, Tree-of-Thoughts 기반의 체계적 추론 및 Query-aware Re-ranking  
- 📑 **SEC Filing Parsing**: SEC 10-K 보고서 구조(Item 단위) 기반 파싱 및 처리  
- 🧾 **Item-Level Chunking**: PART/ITEM 기준으로 문서 구조화  
- 💡 **Investment Memo Generator**: 투자 인사이트 요약 및 리스크 분석 자동 생성

<br>

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

<br>

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

<br>

---

## 🚀 Usage

설정 완료 후, 다음과 같이 메인 파이프라인을 실행할 수 있습니다:

```bash
python main.py --query "What are the key risk factors in Apple's 2018 10-K?"
```

현재는 [SEC EDGAR](https://www.sec.gov/search-filings)에서 수집한 10-K 보고서에 최적화되어 있습니다.

<br>

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

<br>

---

## 📚 References

1. Yao et al., 2022.  
   [**ReAct: Synergizing Reasoning and Acting in Language Models**](https://arxiv.org/abs/2210.03629)

2. Jiang et al., 2023.  
   [**Prompt-as-Program: Interpreting and Executing Programs from Language Instructions**](https://arxiv.org/abs/2305.10855)

3. Yao et al., 2023.  
   [**Tree of Thoughts: Deliberate Problem Solving with Large Language Models**](https://arxiv.org/abs/2305.10601)

4. Aggarwal et al., 2024.  
   [**ChunkRAG: A Chunk-Level Filtering Method for Reliable Retrieval-Augmented Generation**](https://arxiv.org/abs/2410.19572)

5. Villardar, 2025.  
   [**Semantic Decomposition and Selective Context Filtering for LLM-based QA**](https://arxiv.org/abs/2502.14048)

6. Cormack et al., 2009.  
   [**Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods**](https://dl.acm.org/doi/10.1145/1571941.1572114)

7. Pillai et al., 2023.  
   [**Hybrid Question Answering System: A FAISS and BM25 Approach**](https://arxiv.org/abs/2308.07733)

8. Lewis et al., 2020.  
   [**Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (RAG)**](https://arxiv.org/abs/2005.11401)

9. Izacard & Grave, 2020.  
   [**Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering (FiD)**](https://arxiv.org/abs/2007.01282)

10. Longpre et al., 2023.  
    [**The Flipped QA Paradigm for Answering Complex Questions**](https://arxiv.org/abs/2305.13792)