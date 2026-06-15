# AI Sustainability Initiative Extractor

## Overview

AI-powered system that extracts Sustainability and ESG initiatives from corporate annual reports and maps them to relevant United Nations Sustainable Development Goals (SDGs).

The solution uses a Retrieval-Augmented Generation (RAG) pipeline to process large PDF reports, retrieve sustainability-related content, extract initiatives using a Large Language Model (LLM), and generate a structured Excel report.

---

## Problem Statement

Annual reports often contain hundreds of pages of information, with sustainability disclosures spread across multiple sections. Manually identifying and compiling these initiatives is time-consuming, repetitive, and difficult to scale.

This project automates the process by:

* Extracting text from annual reports
* Identifying sustainability-related content
* Extracting initiatives and supporting evidence
* Mapping initiatives to relevant UN SDGs
* Generating a structured Excel report

---

## Solution Architecture

```text
Annual Report PDF
        │
        ▼
PDF Parsing (PyMuPDF)
        │
        ▼
Chunking
        │
        ▼
Noise Filtering
        │
        ▼
Embedding Generation (BGE)
        │
        ▼
SQLite Vector Store
        │
        ▼
Semantic Retrieval
        │
        ▼
Groq Llama 3.3 70B
        │
        ▼
Initiative Extraction
        │
        ▼
Pydantic Validation
        │
        ▼
Excel Report Generation
```

---

## Features

* PDF text extraction
* Chunk-based document processing
* Local embedding generation using BGE
* Semantic retrieval using vector similarity
* Sustainability initiative extraction using LLMs
* SDG mapping
* Evidence extraction
* Page reference tracking
* Excel report generation

---

## Tech Stack

| Component    | Technology             |
| ------------ | ---------------------- |
| PDF Parsing  | PyMuPDF                |
| Embeddings   | BAAI/bge-small-en-v1.5 |
| Vector Store | SQLite                 |
| Retrieval    | Cosine Similarity      |
| LLM          | Groq (Llama 3.3 70B)   |
| Validation   | Pydantic               |
| Excel Export | OpenPyXL               |

---

## Project Structure

```text
AI-SDG-EXTRACTOR/
│
├── input/
├── output/
├── cache/
│
├── src/
│   ├── parser.py
│   ├── chunker.py
│   ├── filtering.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retrieval.py
│   ├── query_bank.py
│   ├── extractor.py
│   ├── validator.py
│   └── excel_writer.py
│
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

## Output

The system generates a structured sustainability report containing:

| Field           | Description                                                                |
| --------------- | -------------------------------------------------------------------------- |
| Initiative Name | Name of the sustainability initiative or program                           |
| Description     | Summary of the initiative and its objective                                |
| Metric          | Quantitative metric, target, or achievement associated with the initiative |
| SDG Mapping     | Relevant United Nations Sustainable Development Goals (SDGs)               |
| Evidence        | Supporting text extracted from the annual report                           |
| Page Reference  | Source page(s) from the report for traceability                            |

The generated report enables analysts to quickly review sustainability initiatives without manually reading the entire annual report.

---

## Future Enhancements

### KPI-Level Extraction

Enhance the extraction pipeline to capture individual sustainability KPIs, targets, achievements, and year-over-year performance metrics in addition to initiative-level summaries.

### Multi-Document Processing

Support processing multiple annual reports simultaneously to improve scalability and reduce analysis time.

### Cross-Company Benchmarking

Enable comparison of sustainability initiatives and performance metrics across multiple organizations.

### Interactive Analytics Dashboard

Provide visualizations and insights for sustainability initiatives, SDG coverage, and key ESG indicators.

### Advanced Vector Search

Integrate dedicated vector databases such as Qdrant or Pinecone to support larger document collections and faster retrieval.

### Human Review Workflow

Introduce a validation layer allowing analysts to review, edit, and approve extracted initiatives before final report generation.

### Automated Sustainability Scoring

Develop a scoring framework to evaluate sustainability performance based on extracted initiatives, disclosures, and measurable outcomes.

---

"# AI-SDG-Extraction" 
