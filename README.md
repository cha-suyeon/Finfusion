
# 🧠 Finfusion: RAG-Based Financial Analysis Assistant

**Finfusion** is a retrieval-augmented generation (RAG) system designed to analyze and summarize financial reports—specifically SEC 10-K filings. It integrates multi-stage document retrieval, dense embedding-based search, and advanced prompting strategies to provide interpretable, investment-grade insights.

## 🧩 Features

- 🔍 **Hybrid Retriever**: BM25 + FAISS + RRF (Reciprocal Rank Fusion)
- 🧠 **LLM Reasoning**: ReAct prompting, Tree-of-Thoughts, Query-Aware Re-ranking
- 🧾 **SEC Filing Support**: Handles structured parsing of 10-K documents
- 📄 **Item-Level Chunking**: Organizes documents by PART/ITEM sections
- 💡 **Investment Memo Generator**: Generates concise summaries and risk assessments

## 🛠️ Tech Stack

- **Language Model**: [Ollama](https://ollama.com/) + `openhermes`
- **Vector Database**: FAISS
- **Sparse Retriever**: BM25 via `rank_bm25`
- **Programming**: Python 3.10+
- **Prompting**: ReAct, Tree-of-Thoughts (ToT)
- **Others**: LangChain, tqdm, PyMuPDF, BeautifulSoup


## 🔧 Setup Instructions

1. Create and Activate Virtual Environment

```bash
python -m venv rag-finance
source rag-finance/bin/activate
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`` includes all necessary Python packages for this project.

3. Start Ollama Server (for local LLM)
This project uses a local language model via Ollama. Make sure Ollama is installed.

```bash
ollama serve
ollama run openhermes
```

## ⚙️ Usage
After setup, you can run the main pipeline script:

```bash
python app.py --query "What are the key risk factors in Apple's 2018 10-K?"
```

Or integrate into your own application using the provided modules:

- `retriever/` for document indexing and search
- `prompter/` for reasoning and generation
- `parser/` for SEC filing structure handling

Currently optimized for 10-K filings from the [SEC EDGAR database](https://www.sec.gov/search-filings).

## 📂 Folder Structure

```kotlin
Finfusion/
│
├── app.py
├── requirements.txt
├── retriever/
├── prompter/
├── parser/
└── data/
```

## References
