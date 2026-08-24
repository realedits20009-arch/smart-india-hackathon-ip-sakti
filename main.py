"""
IP-SAKTI: Ministry of Ayush AI Assistant for Intellectual Property & Regulatory Guidance
FastAPI Production Server with Multilingual RAG, Prior Art Search, Biopiracy Detection,
20+ Ancestral Indian Medicine Provenance E-Documents, and Integrated Frontend Static UI Serving.
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from vector_store import get_vector_store
from rag_chain import get_rag_chain
from document_loader import Document, AyushDocumentLoader

app = FastAPI(
    title="IP-SAKTI — Ministry of Ayush AI Engine",
    description="Multilingual RAG-based AI assistant for Intellectual Property, Section 3(p) compliance, and Regulatory Guidance in Ayurveda.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware for external Vercel frontend / local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- PYDANTIC REQUEST & RESPONSE SCHEMAS -----------------

class ChatRequest(BaseModel):
    query: str = Field(..., example="Can I patent a topical wound healing cream formulated with Curcuma longa and honey?")
    language: str = Field(default="auto", example="auto")
    top_k: int = Field(default=4, ge=1, le=10)

class CitationCard(BaseModel):
    id: str
    title: str
    source: str
    category: str
    section: Optional[str] = None
    botanical_name: Optional[str] = None
    sanskrit_name: Optional[str] = None
    confidence: float
    excerpt: str

class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[CitationCard]
    confidence_score: float
    language: str
    retrieved_count: int

class PatentAnalysisRequest(BaseModel):
    title: str = Field(..., example="A novel herbal cream composition for accelerated diabetic wound healing")
    abstract: str = Field(default="", example="The formulation comprises Haridra extract, Nimba oil, and honey in a topical emulsion.")
    claims: List[str] = Field(default=[], example=["A composition comprising 5-15% Curcuma longa extract and 10% Azadirachta indica seed oil for topical application."])
    ingredients: List[str] = Field(default=[], example=["Curcuma longa (Haridra)", "Azadirachta indica (Neem)", "Honey (Madhu)"])
    proposed_use: str = Field(default="Wound healing and antimicrobial treatment", example="Wound healing and antimicrobial treatment")

class BiopiracyCheckRequest(BaseModel):
    jurisdiction: str = Field(..., example="USPTO / EPO / WIPO")
    applicant_country: str = Field(..., example="United States / Germany / multinational")
    biological_resources: List[str] = Field(..., example=["Azadirachta indica (Neem)", "Curcuma longa (Turmeric)"])
    claim_summary: str = Field(..., example="A method for protecting crops against phytopathogenic fungi using hydrophobic neem oil extract.")

class IngestDocumentRequest(BaseModel):
    title: str
    category: str
    source: str
    text: str
    section_3p_risk: Optional[str] = "MODERATE"
    sanskrit_name: Optional[str] = None
    botanical_name: Optional[str] = None

# ----------------- API ENDPOINTS -----------------

@app.get("/api/info")
def api_info():
    return {
        "name": "IP-SAKTI AI Engine",
        "description": "AI-First Sovereign Legal & Regulatory Intelligence for Ministry of Ayush",
        "status": "online",
        "version": "1.0.0",
        "ancestral_provenance_documents_count": 21,
        "jurisdiction_coverage": [
            "Indian Patents Act 1970 (Section 3p, 3d, 3e, 10)",
            "Biological Diversity Act 2002 (Section 6, NBA Form III)",
            "Drugs and Cosmetics Act 1940 (Rule 158-B ASU Licensing)",
            "Traditional Knowledge Digital Library (TKDL)",
            "Ayurvedic Pharmacopoeia of India (API)",
            "Classical Samhitas (Charaka, Sushruta, Vagbhata, Kashyapa, Sharangdhara)"
        ],
        "endpoints": {
            "chat": "POST /api/chat",
            "patent_analysis": "POST /api/analyze-patent",
            "biopiracy_check": "POST /api/biopiracy-check",
            "documents": "GET /api/documents",
            "provenance_documents": "GET /api/provenance-documents",
            "statistics": "GET /api/statistics",
            "ingest": "POST /api/ingest",
            "lexicon": "GET /api/lexicon"
        }
    }

@app.get("/health")
def health():
    vs = get_vector_store()
    return {
        "status": "healthy",
        "indexed_chunks": len(vs.documents),
        "vocab_terms": len(vs.doc_freq),
        "ancestral_provenance_indexed": True,
        "module": "IP-SAKTI Backend"
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Multilingual Grounded RAG Chatbot:
    Answers user queries with strict source citations from Ayurvedic Pharmacopoeia,
    Ancient Samhita Shlokas, Section 3(p) Patent Act statutes, and biopiracy precedents.
    """
    try:
        rag = get_rag_chain()
        result = rag.ask(query=req.query, top_k=req.top_k, language=req.language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing error: {str(e)}")

@app.post("/api/analyze-patent")
def analyze_patent_endpoint(req: PatentAnalysisRequest):
    """
    Section 3(p), 3(d), 3(e) Patentability & Prior Art Risk Assessment Engine:
    Evaluates claims and formulations against classical Ayurvedic literature and TKDL references,
    computing granular risk scores and attorney-grade recommendations.
    """
    try:
        rag = get_rag_chain()
        report = rag.analyze_patentability(
            title=req.title,
            abstract=req.abstract,
            claims=req.claims,
            ingredients=req.ingredients,
            proposed_use=req.proposed_use
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patent analysis error: {str(e)}")

@app.post("/api/biopiracy-check")
def biopiracy_check_endpoint(req: BiopiracyCheckRequest):
    """
    Biopiracy & NBA Regulatory Compliance Scanner:
    Evaluates foreign/domestic patent applications for potential misappropriation of
    Indian biological resources and verifies NBA Form III compliance.
    """
    try:
        rag = get_rag_chain()
        report = rag.check_biopiracy(
            jurisdiction=req.jurisdiction,
            applicant_country=req.applicant_country,
            biological_resources=req.biological_resources,
            claim_summary=req.claim_summary
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Biopiracy assessment error: {str(e)}")

@app.get("/api/provenance-documents")
def get_provenance_documents_endpoint():
    """
    Returns 20+ Ancestral Indian Medicine Provenance E-Documents proving classical Indian origin,
    ancient Sanskrit shlokas, ancient authors/sages, eras, and anti-biopiracy prior-art proof.
    """
    loader = AyushDocumentLoader()
    docs = loader.load_ancestral_raw()
    return {
        "count": len(docs),
        "sovereign_country": "Republic of India (Bharat)",
        "earliest_period": "c. 1000 BCE (Vedic Antiquity)",
        "documents": docs
    }

@app.get("/api/documents")
def get_documents_endpoint():
    """Returns all foundational documents and monographs in the IP-SAKTI knowledge repository."""
    vs = get_vector_store()
    return {
        "count": len(vs.get_all_documents()),
        "documents": vs.get_all_documents()
    }

@app.get("/api/statistics")
def get_statistics_endpoint():
    """Returns real-time corpus telemetry and knowledge base distribution."""
    vs = get_vector_store()
    loader = AyushDocumentLoader()
    ancestral_docs = loader.load_ancestral_raw()
    docs = vs.get_all_documents()
    categories = {}
    for d in docs:
        c = d.get("category", "Other")
        categories[c] = categories.get(c, 0) + 1

    return {
        "total_documents": len(docs),
        "total_ancestral_provenance_edocuments": len(ancestral_docs),
        "total_indexed_chunks": len(vs.documents),
        "total_lexicon_synonyms": len(vs.alias_map),
        "categories_distribution": categories,
        "supported_languages": ["English", "Hindi (हिन्दी)", "Sanskrit (संस्कृत)", "Tamil (தமிழ்)", "Botanical Latin"],
        "landmark_cases_covered": ["US 5,401,504 (Turmeric)", "EP 0436257 (Neem)", "EP 2879685 (Ashwagandha)", "US 5,663,484 (Basmati Rice)", "EP 1912644 (Kalmegh)"],
        "statutes_integrated": [
            "Indian Patents Act 1970 (Section 3p, 3d, 3e, 3i, 10)",
            "Biological Diversity Act 2002 (Section 6, 19, 20)",
            "Drugs & Cosmetics Rules 1945 (Rule 158-B)",
            "WTO TRIPS Agreement (Article 27.3b)"
        ]
    }

@app.post("/api/ingest")
def ingest_document_endpoint(req: IngestDocumentRequest):
    """Dynamically ingests custom Ayurvedic / Patent literature into the live index."""
    try:
        vs = get_vector_store()
        doc_id = f"USER-DOC-{len(vs.documents)+1:03d}"
        doc = Document(
            page_content=f"Title: {req.title}\nCategory: {req.category}\nSource: {req.source}\nContent: {req.text}\nSanskrit: {req.sanskrit_name or 'N/A'}\nBotanical: {req.botanical_name or 'N/A'}",
            metadata={
                "id": doc_id,
                "title": req.title,
                "category": req.category,
                "source": req.source,
                "section_3p_risk": req.section_3p_risk,
                "sanskrit_name": req.sanskrit_name,
                "botanical_name": req.botanical_name,
                "type": "custom_user_upload"
            }
        )
        vs.add_documents([doc])
        return {
            "status": "success",
            "message": f"Document '{req.title}' indexed successfully with ID {doc_id}.",
            "new_total_chunks": len(vs.documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@app.get("/api/lexicon")
def get_lexicon_endpoint():
    """Returns Sanskrit botanical dictionary and legal terms lookup."""
    from document_loader import AyushDocumentLoader
    loader = AyushDocumentLoader()
    return loader.load_lexicon()

# ----------------- STATIC FRONTEND SERVING -----------------

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "IP-SAKTI Engine Online. Docs at /docs"}

    @app.get("/{full_path:path}")
    def serve_frontend_assets(full_path: str):
        asset_file = os.path.join(frontend_dir, full_path)
        if os.path.exists(asset_file) and os.path.isfile(asset_file):
            return FileResponse(asset_file)
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Not Found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
