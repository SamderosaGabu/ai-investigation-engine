# AI Investigation Engine — MVP

Evidence-based multi-document investigation, built with FastAPI, Streamlit, Qdrant, Sentence Transformers, BM25 and an OpenAI-compatible model client.

## Setup (Python 3.11 recommended)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# set OPENAI_API_KEY in your environment; do not commit it
uvicorn api:app --reload
# separate terminal:
streamlit run ui.py
```

UI: http://localhost:8501; API docs: http://localhost:8000/docs.

## Pipeline

1. Extract PDF/DOCX/TXT/MD/CSV/JSON/JSONL text.
2. Chunk with character-overlap or paragraph strategy.
3. Embed with MiniLM; store chunks and metadata in persistent local Qdrant or remote Qdrant Cloud.
4. Retrieve with vector similarity and BM25, then custom reciprocal rank fusion.
5. Decompose investigation into subqueries; retrieve multiple passages; generate an evidence-only response with numbered citations.

Document identity is filename-based; uploading the same name replaces existing content. Chunks are hashed but cross-document deduplication is not yet implemented. Local Qdrant persists across restarts on persistent disks. Remote Qdrant requires QDRANT_URL and QDRANT_API_KEY. Never commit secrets.

## Data

For HotpotQA ingestion: `pip install datasets` then `python -m scripts.import_hotpot --max-records 50000` (run from project root). This is a **slow baseline importer**: one record at a time, re-encoding each item. Optimize with batch embeddings/upserts before attempting the full dataset. Download and test the dataset schema first; network access is needed. Dataset is not bundled.

## Limitations / next steps

- Benchmark at least 40 labeled questions and two configurations; calculate Recall@K, MRR, answer correctness and citation accuracy.
- Add cross-document deduplication, metadata filters, true tool-calling, structured contradiction checks, and better abstention tests.
- Optimize 50k record ingestion and BM25: the current BM25 implementation scans all chunks per query and will be slow at scale.
- Add authentication/rate limits before exposing write/delete endpoints publicly.
- Deploy UI, API and persistent vector store; verify free-tier quotas and restarts.
- Add integration tests, evaluation report and AI usage report.

**Status:** scaffold/MVP, not a fully validated or deployed assignment submission.
