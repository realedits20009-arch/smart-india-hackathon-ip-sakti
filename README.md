# IP-SAKTI (आयुष-शक्ति) — Ministry of Ayush AI Assistant
### Multilingual, RAG-Based AI Assistant for Intellectual Property & Regulatory Guidance in Ayurveda
**Smart India Hackathon (SIH 2024 / 2025 / 2026) — Problem Statement ID: SIH26045**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg?style=flat&logo=python)](https://www.python.org)
[![Vercel](https://img.shields.io/badge/Frontend-Vercel-black.svg?style=flat&logo=vercel)](https://vercel.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🏛️ Executive Summary & Impact Story
India possesses a 5,000-year-old traditional healthcare heritage codified in classical texts like *Charaka Samhita*, *Sushruta Samhita*, and the *Ayurvedic Pharmacopoeia of India (API)*. However, our sovereign bio-resources have historically suffered from **global biopiracy** — from the notorious USPTO Turmeric patent (US 5,401,504) to the European Neem antifungal patent (EP 0436257). 

Simultaneously, Indian Ayush startups and researchers face an **80%+ rejection rate** under **Section 3(p)** (Traditional Knowledge exclusion), **Section 3(d)** (efficacy standard), and **Section 3(e)** (mere admixture) of the Indian Patents Act, 1970 because they lack explainable prior-art intelligence.

**IP-SAKTI** is an AI-first, explainable, multilingual legal-scientific intelligence engine that:
1. **Defends Sovereignty**: Detects biopiracy in foreign patent filings against 4.3 lakh TKDL formulations.
2. **Accelerates Ayush Startups**: Provides automated Section 3(p) prior-art risk scoring and attorney-grade claim remediation.
3. **Guides Regulatory Licensing**: Demystifies **Rule 158-B** (ASU licensing) and **NBA Form III** (Access & Benefit Sharing) compliance.

---

## 🚀 Key Innovations

```
                               ┌────────────────────────┐
                               │   IP-SAKTI AI ENGINE   │
                               └───────────┬────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐              ┌──────────────────┐
│  MULTILINGUAL    │             │  SECTION 3(p)    │              │  BIOPIRACY &     │
│  GROUNDED RAG    │             │  PATENTABILITY   │              │  NBA SCANNER     │
├──────────────────┤             ├──────────────────┤              ├──────────────────┤
│• Sanskrit-Hindi  │             │• Risk Score (0%) │              │• Form III Alert  │
│  Synonym Engine  │             │• Prior-Art Match │              │• Global Filing   │
│• Exact Paragraph │             │• Synergy Advice  │              │  Misappropriation│
│  Citations       │             │• Claim Rewriting │              │• TKDL Case Laws  │
└──────────────────┘             └──────────────────┘              └──────────────────┘
```

- **Zero-Hallucination Grounded RAG**: Generates answers synthesized strictly from authoritative pharmacopoeias and statutes.
- **Multilingual Botanical Lexicon**: Maps classical Sanskrit terms (*Haridra, Vranaropana, Mehaghna*) to Hindi vernacular (*हल्दी, घाव भरना*) and scientific Latin binomials (*Curcuma longa*).
- **Interactive Citation Cards**: Inspectable source cards linking each claim to its exact chapter, rule, and classical monograph.
- **Offline Resilient Architecture**: Operates 100% locally with high-speed BM25 + dense semantic scoring or connects with Google Gemini / OpenAI.

---

## 🛠️ Project Structure
```
sih-project1/
├── backend/
│   ├── data/
│   │   ├── ayush_knowledge_base.json        # Classical texts & API monographs
│   │   ├── patent_laws_and_cases.json       # Patent Act 1970 & Biopiracy cases
│   │   ├── regulatory_compliance.json       # BDA 2002, Rule 158-B, TKDL
│   │   └── sanskrit_multilingual_lexicon.json # Sanskrit-Hindi-English lexicon
│   ├── main.py                              # FastAPI backend router & endpoints
│   ├── rag_chain.py                         # Grounded RAG & Patent risk engine
│   ├── vector_store.py                      # Hybrid BM25 & Semantic vector index
│   └── document_loader.py                   # Ingestion & chunking pipeline
├── docs/
│   ├── PPT_SLIDE_CONTENT.md                 # 18-Slide complete presentation deck
│   ├── PITCH_SCRIPT_5MIN.md                 # 5-Minute timed hackathon pitch script
│   ├── DEMO_STRATEGY.md                     # Live demo playbook & Q&A defense
│   └── SYSTEM_ARCHITECTURE.md               # Architecture diagrams & schemas
├── requirements.txt                         # Backend Python dependencies
├── test_backend.py                          # Automated 5-suite verification test
└── README.md                                # Root documentation
```

---

## ⚡ Quickstart Guide

### 1. Backend Setup & Run
```bash
# Clone the repository
git clone https://github.com/your-org/ip-sakti.git
cd ip-sakti

# Create & activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated verification tests
python test_backend.py

# Start the FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:
- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Reference & Endpoints

### 1. Multilingual Grounded Chat
`POST /api/chat`
```json
{
  "query": "Can I patent a wound healing cream with Curcuma longa and honey under Indian Patent Law?",
  "language": "auto",
  "top_k": 4
}
```
**Response**:
```json
{
  "query": "Can I patent a wound healing cream...",
  "answer": "Under Section 3(p) of the Indian Patents Act, 1970, an invention which in effect is traditional knowledge...",
  "citations": [
    {
      "id": "AYUSH-API-001",
      "title": "Curcuma longa (Haridra / Turmeric) Monograph",
      "source": "Ayurvedic Pharmacopoeia of India, Part-I, Vol I, Monograph 23",
      "confidence": 94.4,
      "excerpt": "Haridra consists of dried, cured rhizome of Curcuma longa Linn..."
    }
  ],
  "confidence_score": 94.4,
  "language": "en"
}
```

### 2. Section 3(p) Patentability Analyzer
`POST /api/analyze-patent`
```json
{
  "title": "Novel composition of Ashwagandha and Pippali for stress relief",
  "abstract": "Synergistic extract formulation to enhance adaptogenic activity.",
  "claims": ["A composition comprising 200mg Withania somnifera and 10mg Piper longum."],
  "ingredients": ["Withania somnifera", "Piper longum"],
  "proposed_use": "Stress reduction and cognitive enhancement"
}
```
**Response**:
```json
{
  "overall_risk_score": 85.0,
  "risk_level": "CRITICAL",
  "statutory_risk_breakdown": {
    "section_3p_traditional_knowledge": 85,
    "section_3d_evergreening_efficacy": 70,
    "section_3e_mere_admixture": 75
  },
  "recommendations": [
    "Conduct Synergistic Isobologram Analysis (Combination Index CI < 1.0) to overcome Section 3(e).",
    "Mandatory NBA Form III Filing under Section 6 of Biological Diversity Act 2002."
  ],
  "patentability_verdict": "REJECTION LIKELY UNDER SECTION 3(p)/3(e) WITHOUT EXPERIMENTAL SYNERGY DATA"
}
```

### 3. Biopiracy Scanner
`POST /api/biopiracy-check`
```json
{
  "jurisdiction": "EPO",
  "applicant_country": "United States",
  "biological_resources": ["Azadirachta indica (Neem)"],
  "claim_summary": "Hydrophobic neem oil extract for plant fungal protection"
}
```

---

## 🌐 Deployment Guide

### Deploying Backend (Railway / Render / AWS EC2)
1. Push repository to GitHub.
2. Link your repository in [Railway.app](https://railway.app) or [Render.com](https://render.com).
3. Set start command:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
4. Set optional environment variable:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   ```

### Deploying Frontend (Vercel)
1. Navigate to the frontend directory (`/frontend`).
2. Deploy directly with `vercel` CLI or link repo on [Vercel](https://vercel.com).
3. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

---

## 🏆 Smart India Hackathon Resources
- 📑 **Slide Deck Content (18 Slides)**: [`docs/PPT_SLIDE_CONTENT.md`](docs/PPT_SLIDE_CONTENT.md)
- 🎙️ **5-Minute Pitch Script**: [`docs/PITCH_SCRIPT_5MIN.md`](docs/PITCH_SCRIPT_5MIN.md)
- 🎯 **Demo Playbook & Q&A Defense**: [`docs/DEMO_STRATEGY.md`](docs/DEMO_STRATEGY.md)
- 🏗️ **Technical Architecture Specification**: [`docs/SYSTEM_ARCHITECTURE.md`](docs/SYSTEM_ARCHITECTURE.md)

---

## 📜 License & Acknowledgements
- Developed for **Smart India Hackathon (Ministry of Ayush)**.
- Classical Ayurvedic data referenced from the **Ayurvedic Pharmacopoeia of India (API)** and **Ayurvedic Formulary of India (AFI)** published by the Ministry of Ayush, Government of India.
