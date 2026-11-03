# FinLit AI — Digital Financial Literacy Agent

> **IBM Problem Statement #7** | Powered by **IBM Granite** (watsonx.ai) + **RAG** (ChromaDB)

```
 ██████╗ ██╗███╗   ██╗██╗     ██╗████████╗     █████╗ ██╗
 ██╔════╝ ██║████╗  ██║██║     ██║╚══██╔══╝    ██╔══██╗██║
 █████╗   ██║██╔██╗ ██║██║     ██║   ██║       ███████║██║
 ██╔══╝   ██║██║╚██╗██║██║     ██║   ██║       ██╔══██║██║
 ██║      ██║██║ ╚████║███████╗██║   ██║       ██║  ██║██║
 ╚═╝      ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝   ╚═╝       ╚═╝  ╚═╝╚═╝
```

An AI-powered financial literacy assistant that helps users across India understand
UPI payments, avoid online scams, navigate interest rates, and manage personal finances —
in **10 Indian languages** with IBM Granite AI and Retrieval-Augmented Generation (RAG).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Browser)                           │
│            HTML/CSS/JS SPA  ·  6 Tabs  ·  Voice Input          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP REST
┌────────────────────────────▼────────────────────────────────────┐
│                    Flask API  (app.py)                           │
│  /api/chat  /api/scam-check  /api/analytics  /api/run-tests     │
└──────┬──────────────────────────┬──────────────────────────────┘
       │                          │
┌──────▼──────────┐     ┌─────────▼────────────┐
│   Agent Core    │     │   Scam Checker        │
│   (agent.py)    │     │  (scam_checker.py)    │
│                 │     │  19 regex patterns    │
│  ┌───────────┐  │     │  + IBM Granite deepen │
│  │ Language  │  │     └─────────┬─────────────┘
│  │ Detection │  │               │
│  │ (10 lang) │  │               │
│  └─────┬─────┘  │               │
│        │        │               │
│  ┌─────▼─────┐  │     ┌─────────▼────────────┐
│  │    RAG    │  │     │   IBM Granite 4        │
│  │ Pipeline  │◄─┼─────►   (watsonx.ai)        │
│  │ChromaDB   │  │     │  ibm/granite-4-h-small │
│  │ 20 docs   │  │     └──────────────────────┘
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │Knowledge  │  │
│  │   Base    │  │
│  │ 6 topics  │  │
│  │ 5 langs   │  │
│  └───────────┘  │
└─────────────────┘
```

---

## Features

| Feature | Description |
|---------|-------------|
| **IBM Granite AI** | `ibm/granite-4-h-small` via watsonx.ai chat API |
| **RAG Pipeline** | 20 documents, ChromaDB, sentence-transformers embeddings |
| **Multilingual** | 10 Indian languages: EN, HI, TA, TE, BN, MR, GU, KN, ML, PA |
| **Scam Checker** | 19 regex patterns + IBM Granite deep analysis, risk levels |
| **Voice Input** | Web Speech API — speak questions in any of 10 languages |
| **Calculators** | EMI, Simple/Compound Interest, 50/30/20 Budget Planner |
| **Dashboard** | Analytics: topics, languages, scam checks, satisfaction |
| **Test Suite** | 20 automated Q&A tests with keyword + source validation |
| **Spot the Scam Quiz** | 10-question interactive fraud awareness quiz |
| **Download Chat** | Export conversation as formatted HTML |
| **TTS** | Text-to-speech "Listen" button on all responses |
| **Dark Mode** | Full light/dark theme with localStorage persistence |

---

## Topics Covered

- **UPI & Digital Payments** — how to use UPI, safety tips, common UPI scams
- **Online Scam Prevention** — phishing, KYC fraud, fake loans, investment fraud
- **Interest Rates & Loans** — home/personal/credit card rates, EMI, CIBIL score
- **Budgeting & Savings** — 50/30/20 rule, emergency fund, PPF, SSY, NSC, NPS
- **Personal Finance** — insurance, SIP, mutual funds, tax saving (80C/80D)
- **Banking Basics** — account types, NEFT/RTGS/IMPS, DICGC, RBI rights

---

## Quick Start

### Prerequisites

- Python 3.10+
- IBM Cloud Lite account with Watson Machine Learning instance
- IBM watsonx.ai project with `ibm/granite-4-h-small` enabled

### 1. Clone & Install

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Create `.env` in the project root (copy from `.env.example`):

```bash
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-4-h-small
FLASK_PORT=5000
FLASK_ENV=development
```

> **Windows tip:** Write without BOM using PowerShell:
> ```powershell
> [System.IO.File]::WriteAllLines(".env", @("IBM_API_KEY=...", "IBM_PROJECT_ID=..."), [System.Text.UTF8Encoding]::new($false))
> ```

### 3. Initialize Knowledge Base

```bash
python setup.py
```

This builds the ChromaDB vector store from 20 curated financial documents.

### 4. Run the Server

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Server health + stats |
| `POST` | `/api/chat` | Main chat endpoint |
| `POST` | `/api/scam-check` | Scam analysis |
| `POST` | `/api/feedback` | Submit thumbs up/down |
| `GET` | `/api/analytics` | Usage analytics |
| `POST` | `/api/run-tests` | Run 20 test questions |
| `GET` | `/api/test-questions` | List test question stubs |
| `GET` | `/api/languages` | Supported languages |
| `GET` | `/api/topics` | Financial topics |
| `GET` | `/api/session/<id>/history` | Conversation history |
| `DELETE` | `/api/session/<id>/reset` | Clear session |

### Chat Request

```json
POST /api/chat
{
  "message": "How do I send money via UPI safely?",
  "session_id": "optional-session-uuid",
  "language": "en"
}
```

### Chat Response

```json
{
  "response": "To send money via UPI safely, follow these steps...",
  "detected_language": "en",
  "topic": "UPI",
  "sources": ["NPCI (National Payments Corporation of India)", "RBI Financial Literacy"],
  "session_id": "sess_abc123",
  "retrieved_chunks": 5
}
```

### Scam Check Request

```json
POST /api/scam-check
{
  "message": "Your KYC expired. Account blocked in 24hrs. Update: http://sbi-kyc.xyz"
}
```

### Scam Check Response

```json
{
  "risk_level": "HIGH",
  "verdict": "This is a KYC fraud attempt...",
  "scam_type": "Fake KYC / Account Block Threat",
  "red_flags": ["KYC update demanded with urgency", "Suspicious unofficial link"],
  "explanation": "The message uses urgency tactics typical of KYC scams...",
  "actions": ["Do NOT click any links...", "Call 1930 immediately..."],
  "helplines": [{"name": "National Cyber Crime Helpline", "number": "1930", "note": "..."}],
  "granite_enhanced": true
}
```

---

## Project Structure

```
AI Agent for Digital Financial Literacy/
├── .env                      ← Active credentials (BOM-free)
├── .env.example              ← Credential template
├── app.py                    ← Flask server + all 11 API routes
├── setup.py                  ← One-time knowledge base + vector store init
├── requirements.txt          ← Python dependencies
├── Procfile                  ← Cloud deployment (gunicorn)
├── README.md                 ← This file
│
├── src/
│   ├── agent.py              ← Core orchestrator: Granite + RAG + multilingual + memory
│   ├── granite_client.py     ← IBM Granite 4 H Small (chat API wrapper)
│   ├── knowledge_base.py     ← 20 curated documents (EN/HI/TA/TE/BN) across 6 topics
│   ├── multilingual.py       ← 10-language detection, translation, greetings
│   ├── rag_pipeline.py       ← ChromaDB ingestion + semantic retrieval
│   ├── scam_checker.py       ← 19 red-flag patterns + IBM Granite scam analysis
│   ├── analytics.py          ← Thread-safe JSON analytics store
│   └── test_suite.py         ← 20-question scored test suite
│
├── static/
│   └── index.html            ← 6-tab SPA (Chat/ScamChecker/Dashboard/Calc/Tests/Quiz)
│
├── tests/
│   └── test_agent.py         ← pytest unit + integration tests
│
└── data/
    ├── knowledge_base/       ← Generated JSON files per topic
    ├── vector_store/         ← ChromaDB persistent embeddings
    └── analytics.json        ← Auto-created on first query
```

---

## Knowledge Base

| ID | Topic | Language | Source |
|----|-------|----------|--------|
| upi_001 | UPI | English | NPCI India |
| upi_002 | UPI | English | RBI Financial Literacy |
| upi_hindi_001 | UPI | Hindi | NPCI India |
| upi_bengali_001 | UPI | Bengali | NPCI India |
| scam_001 | Online Scams | English | Ministry of Home Affairs |
| scam_002 | Online Scams | English | RBI, SEBI, IRDAI |
| scam_hindi_001 | Online Scams | Hindi | Cyber Crime Portal |
| scam_telugu_001 | Online Scams | Telugu | Cyber Crime Portal |
| interest_001 | Interest Rates | English | RBI Financial Education |
| interest_002 | Interest Rates | English | RBI Consumer Education |
| interest_hindi_001 | Interest Rates | Hindi | RBI Financial Literacy |
| budget_001 | Budgeting | English | FPSI India |
| budget_002 | Budgeting | English | India Post / Ministry of Finance |
| budget_tamil_001 | Budgeting | Tamil | SEBI Investor Education |
| pf_001 | Personal Finance | English | SEBI Investor Education |
| pf_002 | Personal Finance | English | AMFI India, SEBI |
| pf_hindi_001 | Personal Finance | Hindi | SEBI Investor Education |
| banking_001 | Banking | English | RBI Financial Literacy |
| banking_002 | Banking | English | RBI Payment Systems |

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | IBM Granite 4 H Small (`ibm/granite-4-h-small`) via IBM watsonx.ai |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (local) |
| **Vector Store** | ChromaDB (persistent, local) |
| **Framework** | Flask + Flask-CORS |
| **Frontend** | Vanilla HTML/CSS/JS (no build step) |
| **Voice Input** | Web Speech API (Chrome/Edge) |
| **TTS** | Web SpeechSynthesis API |
| **Deployment** | gunicorn (Procfile) |

---

## IBM Cloud Setup

1. Register at [cloud.ibm.com](https://cloud.ibm.com/registration) (free Lite tier)
2. Create a **Watson Machine Learning** instance
3. Create a **watsonx.ai project** and associate the WML instance
4. Copy your **API key** from IAM → API Keys
5. Copy the **Project ID** from watsonx.ai project settings
6. Confirm `ibm/granite-4-h-small` is available in your project

---

## Helplines Referenced

| Helpline | Number |
|----------|--------|
| National Cyber Crime Helpline | **1930** |
| Cyber Crime Portal | **cybercrime.gov.in** |
| RBI Helpline | **14440** |
| TRAI DND (Stop spam SMS) | **1909** |
| NPCI Helpline | **1800-120-1740** |

---

## Sample Interactions

**English:**
> "What is a safe interest rate for a home loan?"

**Hindi:**
> "UPI से पैसे कैसे भेजें?"

**Tamil:**
> "மாதாந்திர பட்ஜெட் எப்படி திட்டமிட வேண்டும்?"

**Bengali:**
> "অনলাইন স্ক্যাম থেকে কীভাবে বাঁচব?"

---

## Disclaimer

FinLit AI provides **general financial literacy information only**. It is not a licensed
financial advisor. All financial decisions should be verified with your bank, RBI, SEBI,
or a certified financial planner.

---

*Built for IBM Problem Statement #7 — AI Agent for Digital Financial Literacy*
*Powered by IBM Granite · RAG · ChromaDB · Flask*
