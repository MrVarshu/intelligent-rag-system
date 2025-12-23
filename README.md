# 🤖 Advanced RAG System for Research Papers

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Groq](https://img.shields.io/badge/LLM-Groq-green.svg)](https://groq.com/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange.svg)](https://www.trychroma.com/)

A production-ready **Retrieval-Augmented Generation (RAG)** system optimized for academic research papers. Automatically extracts key sections (Abstract, Introduction, Conclusion) from PDFs and web content, stores them in a vector database, and enables intelligent querying using Groq's LLM.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [How to Run](#-how-to-run)
  - [1. Data Ingestion](#1-data-ingestion)
  - [2. Query Interfaces](#2-query-interfaces)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### Core Capabilities

- 🎯 **Intelligent PDF Extraction**: Advanced scraper with 4 fallback strategies for extracting Abstract, Introduction, and Conclusion
- 🧠 **Smart Section Detection**: Handles Roman numerals (I-X), Arabic numbers, IEEE/ACM/arXiv formats
- 🌐 **Web Content Ingestion**: Fetch and process articles from URLs
- 🔍 **Vector Search**: Semantic search using Sentence Transformers with ChromaDB
- 💬 **Multiple Query Options**: 
  - LangChain ChatGroq (recommended)
  - Direct Groq API client
  - Streamlit web UI
- 📊 **Section-Aware Chunking**: Maintains section metadata for better retrieval
- 🔄 **Upsert Semantics**: Re-ingest documents without duplicates

---

## 📁 Project Structure

```
RAG_Model/
│
├── 📄 README.md                          # This file
├── 📄 requirements.txt                   # Python dependencies
├── 📄 .env                               # Environment variables (API keys)
│
├── 📂 data_storage/                      # Data persistence
│   ├── 📂 chroma_db/                     # ChromaDB vector database
│   └── 📂 raw_pdfs/                      # Place your PDF files here
│
├── 📂 src/                               # Core application code
│   ├── 📄 groq_rag_pipeline.py          # LangChain ChatGroq RAG ⭐
│   ├── 📄 query_system.py               # Direct Groq API client ⭐
│   │
│   ├── 📂 config/
│   │   ├── settings.py                   # API keys, models
│   │   └── paths.py                      # Path constants
│   │
│   ├── 📂 data/
│   │   ├── data_ingest_pipeline.py      # Ingestion orchestrator ⭐
│   │   ├── 📂 ingestion/
│   │   │   ├── pdf_scraper.py           # PDF extraction (4 strategies) ⭐
│   │   │   ├── web_crawler.py           # Web scraping
│   │   │   └── text_cleaner.py          # Text normalization
│   │   ├── 📂 embedding/
│   │   │   └── embedder.py              # Sentence Transformers
│   │   └── 📂 vectorstore/
│   │       ├── chroma_client.py         # ChromaDB operations
│   │       └── vector_utils.py          # ID generation
│   │
│   └── 📂 ui/
│       └── streamlit_app.py             # Web UI ⭐
│
├── 📂 tests/                             # Test suite
│   ├── test_scraper.py
│   ├── test_groq.py
│   └── test_crawler.py
│
├── 📄 ingest_pdfs.py                    # Ingest PDFs (simple) ⭐
├── 📄 ingest_urls.py                    # Ingest URLs only ⭐
├── 📄 ingest_research_papers.py         # Ingest with analysis ⭐
├── 📄 ingest_data.py                    # Bulk ingestion (PDFs + URLs) ⭐
├── 📄 interactive_groq_rag.py           # CLI (LangChain) ⭐
├── 📄 interactive_query.py              # CLI (Direct API) ⭐
├── 📄 test_full_ingestion.py            # E2E ingestion test
└── 📄 test_query_system.py              # Query test
```

### 🔑 Key Files

| File | Purpose |
|------|---------|
| `src/data/ingestion/pdf_scraper.py` | Extracts Abstract, Introduction, Conclusion from PDFs |
| `src/groq_rag_pipeline.py` | LangChain-based RAG pipeline (recommended) |
| `src/query_system.py` | Direct Groq API query system |
| `src/ui/streamlit_app.py` | Web UI for queries |
| `ingest_research_papers.py` | Best way to ingest PDFs (with preview) |

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Groq API key ([Get one free](https://console.groq.com/))
- 2GB+ RAM

### Steps

```bash
# 1. Clone/Download the project
cd RAG_Model

# 2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo GROQ_API_KEY=your_api_key_here > .env
echo GROQ_MODEL=llama-3.3-70b-versatile >> .env
echo EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 >> .env
echo CHROMA_PERSIST_PATH=./data_storage/chroma_db >> .env
```

### Verify Installation

```bash
python -c "from src.config.settings import GROQ_API_KEY; print('✅ Setup complete!' if GROQ_API_KEY else '❌ GROQ_API_KEY not set')"
```

---

## 🎯 Quick Start

### 1. Add Your PDFs

```bash
# Place PDF files in:
data_storage/raw_pdfs/
```

### 2. Ingest Documents

```bash
# Best option: Research papers with analysis
python ingest_research_papers.py
```

### 3. Query the System

```bash
# Option A: Web UI (Recommended)
streamlit run src/ui/streamlit_app.py

# Option B: Interactive CLI (LangChain)
python interactive_groq_rag.py

# Option C: Interactive CLI (Direct API)
python interactive_query.py
```

---

## 💻 How to Run

### 1. Data Ingestion

Choose the ingestion script based on your needs:

#### Option A: Research Papers with Analysis (⭐ Recommended)

```bash
python ingest_research_papers.py
```

**What it does:**
- Shows which sections are found (Abstract, Introduction, Conclusion)
- Displays character counts for each section
- Provides detailed statistics
- Asks for confirmation before ingesting

**Example output:**
```
[1/5] Processing: paper.pdf
📊 Analyzing paper structure...
  📑 Title: Deep Learning Advances
  📄 Sections found:
     Abstract: ✅ (345 chars)
     Introduction: ✅ (789 chars)
     Conclusion: ✅ (456 chars)

🔄 Ingesting paper into ChromaDB...
  ✅ Successfully ingested 5 chunks
```

#### Option B: Simple PDF Ingestion

```bash
python ingest_pdfs.py
```

**What it does:**
- Quick ingestion without analysis
- No prompts, just processes all PDFs
- Good for batch processing

#### Option C: Web URLs Only

```bash
python ingest_urls.py
```

**Before running:**
Edit the file and add your URLs:
```python
urls_to_ingest = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://your-url-here.com",
    # Add more URLs
]
```

#### Option D: Bulk Ingestion (PDFs + URLs)

```bash
python ingest_data.py
```

**What it does:**
- Ingests both PDFs and URLs in one run
- Edit the file first to add URLs

---

### 2. Query Interfaces

You have **3 ways** to query your ingested documents:

---

#### Option A: 🖥️ Streamlit Web UI (⭐ **Recommended**)

```bash
streamlit run src/ui/streamlit_app.py
```

**Features:**
- Beautiful web interface
- Chat-like UI
- Shows retrieved context
- Easy to use
- Runs on `http://localhost:8501`

**Screenshot:**
```
┌─────────────────────────────────────────┐
│  RAG System - Ask Questions            │
├─────────────────────────────────────────┤
│                                         │
│  Your Query:                            │
│  ┌─────────────────────────────────┐   │
│  │ What is machine learning?       │   │
│  └─────────────────────────────────┘   │
│                                         │
│  💬 Answer:                             │
│  Machine learning is a method of...    │
│                                         │
│  📚 Sources: paper1.pdf, paper2.pdf    │
└─────────────────────────────────────────┘
```

**Backend:** Uses `src/groq_rag_pipeline.py` (LangChain ChatGroq)

---

#### Option B: 💬 Interactive CLI with LangChain (Recommended for CLI)

```bash
python interactive_groq_rag.py
```

**Features:**
- Terminal-based interface
- Uses LangChain ChatGroq
- Shows method used
- Can display retrieved context
- Configurable number of documents

**Example session:**
```
================================================================================
Groq RAG Pipeline - Interactive Mode
================================================================================

Enter your query: What are the main findings about deep learning?
Number of documents to retrieve (default: 3, max recommended: 5): 3

================================================================================
QUERY: What are the main findings about deep learning?
METHOD: ChatGroq with PromptTemplate (LCEL)
================================================================================

ANSWER:
Based on the research papers, the main findings about deep learning include...

Show retrieved context? (y/n): y

RETRIEVED CONTEXT:
--------------------------------------------------------------------------------
Document 1 (from paper.pdf - introduction):
Deep learning has revolutionized...
```

**Backend:** Uses `src/groq_rag_pipeline.py` (LangChain)

---

#### Option C: 💬 Interactive CLI with Direct API

```bash
python interactive_query.py
```

**Features:**
- Simple terminal interface
- Direct Groq API calls (no LangChain)
- Lightweight and fast
- Good for quick testing

**Example session:**
```
================================================================================
RAG Query System - Interactive Mode
================================================================================

Enter your query: Explain neural networks
Number of documents to retrieve (default: 3, max recommended: 5): 3

================================================================================
QUERY: Explain neural networks
================================================================================

ANSWER:
Neural networks are computational models...

Show retrieved context? (y/n): n
```

**Backend:** Uses `src/query_system.py` (Direct API)

---

### Query Interface Comparison

| Feature | Streamlit Web UI | LangChain CLI | Direct API CLI |
|---------|-----------------|---------------|----------------|
| **File** | `streamlit_app.py` | `interactive_groq_rag.py` | `interactive_query.py` |
| **Interface** | Web browser | Terminal | Terminal |
| **Backend** | LangChain ChatGroq | LangChain ChatGroq | Direct Groq API |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Features** | Rich UI, chat history | Full featured | Basic |
| **Best For** | End users | Developers, testing | Quick queries |
| **Shows Method** | ✅ Yes | ✅ Yes | ❌ No |
| **Prompt Template** | ✅ Yes (LCEL) | ✅ Yes (LCEL) | ❌ Manual |

**Recommendation:** 
- **For regular use:** Streamlit Web UI
- **For development/testing:** LangChain CLI
- **For simple queries:** Direct API CLI

---

## ⚙️ Configuration

### Environment Variables (.env file)

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (with defaults)
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_PATH=./data_storage/chroma_db
```

### Customization

**Chunk Size** (in `src/data/data_ingest_pipeline.py`):
```python
def ingest_pdf_file(path: str, max_chars: int = 1500):
    # Change max_chars to adjust chunk size (500-2000 recommended)
```

**Number of Retrieved Documents** (in query scripts):
```python
n_results = 3  # Change this (1-10)
```

**LLM Parameters** (in `src/groq_rag_pipeline.py`):
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,  # 0.0-1.0 (lower = more deterministic)
    max_tokens=1000   # Response length
)
```

---

## 🏗️ Architecture

### System Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   PDF/URL   │─────>│  Extraction  │─────>│   Cleaning  │
└─────────────┘      └──────────────┘      └─────────────┘
                                                    │
                                                    ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  ChromaDB   │<─────│  Embedding   │<─────│  Chunking   │
└─────────────┘      └──────────────┘      └─────────────┘
      │
      ▼ (Query)
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Retrieval  │─────>│   Groq LLM   │─────>│   Response  │
└─────────────┘      └──────────────┘      └─────────────┘
```

### Key Components

1. **PDF Scraper** (`src/data/ingestion/pdf_scraper.py`)
   - 4 extraction strategies with fallbacks
   - Heading-only matching (not inline keywords)
   - Handles Roman numerals I-X, Arabic 1-10

2. **Ingestion Pipeline** (`src/data/data_ingest_pipeline.py`)
   - Clean → Chunk → Embed → Store
   - Section-aware chunking
   - Deterministic ID generation (upsert-safe)

3. **Vector Store** (`src/data/vectorstore/chroma_client.py`)
   - ChromaDB for vector storage
   - Sentence Transformers embeddings (384-dim)
   - Metadata: source, section, chunk_index

4. **Query Systems**
   - **LangChain** (`groq_rag_pipeline.py`): PromptTemplate + ChatGroq
   - **Direct API** (`query_system.py`): Manual prompt construction

---

### Debug Mode

Enable detailed logging in any script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Testing

### Run Tests

```bash
# Test PDF scraper
python tests/test_scraper.py

# Test Groq API
python tests/test_groq.py

# Full end-to-end test
python test_full_ingestion.py

# Test query system
python test_query_system.py
```

---

## 🎯 Usage Examples

### Example 1: Ingest Research Papers

```bash
# 1. Place PDFs in data_storage/raw_pdfs/
# 2. Run ingestion with analysis
python ingest_research_papers.py

# Follow prompts:
# - Press Enter for default folder
# - Press Enter for default chunk size (1500)
# - Type 'y' for structure analysis
# - Type 'y' to proceed
```

### Example 2: Query via Streamlit

```bash
streamlit run src/ui/streamlit_app.py

# In browser (http://localhost:8501):
# 1. Type your question
# 2. Click "Ask" or press Enter
# 3. See answer with sources
```

### Example 3: Query via CLI (LangChain)

```bash
python interactive_groq_rag.py

# Enter query: What is deep learning?
# Number of documents: 3
# Shows answer with method used
# Option to show retrieved context
```

### Example 4: Query via CLI (Direct API)

```bash
python interactive_query.py

# Enter query: Explain machine learning
# Number of documents: 3
# Shows answer (simpler output)
```

---

## 📝 Tips & Best Practices

### For Best Results

1. **PDF Quality**: Use text-based PDFs (not scanned images)
2. **Chunk Size**: 1000-1500 chars works well for most papers
3. **Number of Documents**: 3-5 for retrieval (more = more tokens)
4. **Query Phrasing**: Be specific ("What are the main findings of the paper?" vs "Tell me about it")
5. **Re-ingestion**: You can re-run ingestion scripts - duplicates are handled via upsert

### Performance Tips

- **First run**: Embedding model downloads (~90MB), takes 1-2 minutes
- **Subsequent runs**: Much faster
- **Large PDFs**: May take 5-10 seconds to process
- **Query speed**: ~3-6 seconds end-to-end

---

## 🙏 Acknowledgments

- **Groq** - Ultra-fast LLM inference
- **ChromaDB** - Vector database
- **LangChain** - RAG framework
- **Sentence Transformers** - Embeddings
- **Streamlit** - Web UI

---

<div align="center">

### ⭐ Ready to start? Run the Quick Start steps above!

**Made with ❤️ for Research Paper Analysis**

</div>
