# 🔎 AI Investigation Engine

**An AI-powered, evidence-based document investigation system using Retrieval-Augmented Generation (RAG), hybrid search, Qdrant, and Google Gemini.**

The AI Investigation Engine allows users to upload, manage, search, and investigate collections of documents using artificial intelligence. Instead of simply generating answers, the system retrieves supporting evidence, cites its sources, identifies contradictions, and acknowledges when sufficient information is unavailable.

## Features

- **Document Management:** Upload, index, search, and delete documents.
- **Multiple File Formats:** Supports PDF, DOCX, TXT, Markdown, CSV, JSON, and JSONL.
- **Intelligent Chunking:** Character-based and paragraph-based text segmentation.
- **Persistent Vector Database:** Qdrant stores document embeddings and metadata.
- **Hybrid Search:** Combines semantic similarity and BM25 keyword retrieval.
- **Custom Ranking:** Uses Reciprocal Rank Fusion (RRF) and additional relevance scoring.
- **AI Investigation:** Google Gemini generates evidence-grounded responses.
- **Source Citations:** Answers reference retrieved documents using numbered citations.
- **Contradiction Detection:** Identifies conflicting information across documents.
- **Evidence-Based Abstention:** Avoids inventing answers when evidence is insufficient.
- **Function Calling:** Gemini can request additional document searches.
- **Web Interface:** Dark-mode dashboard built using Streamlit.
- **REST API:** FastAPI provides endpoints for document management and investigation.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Vector Database | Qdrant |
| Embeddings | Sentence Transformers |
| Keyword Retrieval | BM25 |
| AI Model | Google Gemini |
| Testing | Pytest |
| Version Control | Git and GitHub |

## System Architecture

The application follows a Retrieval-Augmented Generation (RAG) architecture.

**Document Processing**

1. A user uploads a document.
2. The system extracts its text.
3. The text is divided into manageable chunks.
4. Sentence Transformers generates vector embeddings.
5. Qdrant stores the embeddings and document metadata.

**Investigation Process**

1. The user submits a question.
2. Semantic and keyword searches retrieve relevant evidence.
3. The system combines and ranks the results.
4. Gemini analyzes the retrieved information.
5. Additional searches may be performed through function calling.
6. The system generates an answer with supporting citations or acknowledges insufficient evidence.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/SamderosaGabu/ai-investigation-engine.git
cd ai-investigation-engine
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project directory.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash-lite
QDRANT_DATA_PATH=data/qdrant
```

Replace the example API key with your own Google Gemini API key.

**Security:** Never upload your `.env` file or API credentials to GitHub.

### 5. Start the backend

```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

The API documentation is available at:

`http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open another terminal and run:

```bash
python -m streamlit run ui.py
```

Open the application at:

`http://localhost:8501`

**Note:** The local Qdrant database is not included in the GitHub repository. New installations must ingest documents to populate their database.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check backend status |
| GET | `/documents` | List indexed documents |
| POST | `/documents/upload` | Upload and index a file |
| POST | `/documents/text` | Index text directly |
| DELETE | `/documents/{doc_id}` | Delete a document |
| POST | `/search` | Retrieve relevant evidence |
| POST | `/investigate` | Generate an AI investigation |

## Evaluation

The retrieval system was evaluated using a dataset of 50 investigation questions.

### Recorded Retrieval Results

| Metric | Result |
|---|---:|
| Recall@10 | 0.660 |
| MRR@10 | 0.490 |
| CompleteEvidence@10 | 0.360 |

**Metric explanations:**

- **Recall@10:** Measures how much of the relevant evidence appears in the top 10 results.
- **MRR@10:** Measures how highly the first relevant result is ranked.
- **CompleteEvidence@10:** Measures whether all required evidence is present among the top 10 results.

The system was also tested for contradiction detection, evidence-based abstention, and Gemini function calling.

Character-based and paragraph-based chunking strategies were implemented and tested. Further controlled benchmarking is needed to establish their comparative retrieval performance.

These results demonstrate working retrieval and reasoning capabilities while highlighting opportunities to improve evidence coverage.

## Testing

Automated tests are included in the `tests/` directory.

Run the tests using:

```bash
python -m pytest tests/ -v
```

Tests cover document management, chunking, retrieval, AI reasoning, and tool functionality.

Some integration tests require a valid Gemini API key and may depend on external API availability.

## Project Structure

```text
ai-investigation-engine/
├── api.py
├── ui.py
├── engine/
│   ├── core.py
│   └── tools.py
├── scripts/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Limitations and Future Improvements

- Retrieval quality depends on the indexed documents and their coverage.
- Some complex multi-hop questions require additional retrieval improvements.
- Gemini responses depend on external API availability.
- Large document collections may require additional performance optimization.
- Public deployment requires appropriate persistent database storage.
- Additional controlled retrieval and answer-quality evaluations would strengthen the results.

## Project Status

The core application has been implemented and tested locally, including the frontend, backend, document management, hybrid retrieval, and AI reasoning.

Public deployment and final evaluation documentation are being completed.

## Author

**SamderosaGabu**

GitHub: https://github.com/SamderosaGabu

Developed as part of an Applied AI project focused on document intelligence, retrieval systems, and evidence-based AI reasoning.
