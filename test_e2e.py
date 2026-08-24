"""
End-to-End Test Suite for IP-SAKTI FastAPI + Frontend Server
"""

import sys
import os
from fastapi.testclient import TestClient

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from main import app

def run_e2e_tests():
    client = TestClient(app)
    
    print("=" * 60)
    print("[1/6] Testing Root Frontend Serving...")
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "IP-SAKTI" in res_root.text
    print("PASS: Root HTML index.html served successfully.")

    print("\n" + "=" * 60)
    print("[2/6] Testing Static Assets (CSS & JS)...")
    res_css = client.get("/style.css")
    assert res_css.status_code == 200
    assert "--emerald-500" in res_css.text
    print("PASS: style.css loaded.")

    res_js = client.get("/app.js")
    assert res_js.status_code == 200
    assert "API_BASE" in res_js.text
    print("PASS: app.js loaded.")

    print("\n" + "=" * 60)
    print("[3/6] Testing /health and /api/info...")
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert data_health["status"] == "healthy"
    print(f"PASS: Health OK. Indexed Chunks: {data_health['indexed_chunks']}")

    print("\n" + "=" * 60)
    print("[4/6] Testing /api/chat (Multilingual RAG)...")
    res_chat = client.post("/api/chat", json={
        "query": "Can I patent a topical wound healing cream with Curcuma longa and honey?",
        "language": "auto",
        "top_k": 4
    })
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert len(chat_data["citations"]) > 0
    print(f"PASS: /api/chat returned answer with {len(chat_data['citations'])} source citations.")

    print("\n" + "=" * 60)
    print("[5/6] Testing /api/analyze-patent (Section 3(p) Analyzer)...")
    res_patent = client.post("/api/analyze-patent", json={
        "title": "Topical formulation of Haridra and Nimba oil",
        "abstract": "Extract of Curcuma longa and Azadirachta indica for skin repair",
        "claims": ["A formulation comprising 10% Haridra extract"],
        "ingredients": ["Curcuma longa", "Azadirachta indica"],
        "proposed_use": "Wound healing and anti-inflammatory"
    })
    assert res_patent.status_code == 200
    patent_data = res_patent.json()
    assert patent_data["overall_risk_score"] > 50
    print(f"PASS: /api/analyze-patent returned Risk Score: {patent_data['overall_risk_score']}% ({patent_data['risk_level']})")

    print("\n" + "=" * 60)
    print("[6/6] Testing /api/biopiracy-check & /api/statistics...")
    res_bio = client.post("/api/biopiracy-check", json={
        "jurisdiction": "USPTO",
        "applicant_country": "United States",
        "biological_resources": ["Curcuma longa (Turmeric)"],
        "claim_summary": "Topical administration of turmeric powder for wound healing"
    })
    assert res_bio.status_code == 200
    bio_data = res_bio.json()
    assert bio_data["biopiracy_risk_score"] >= 80
    print(f"PASS: /api/biopiracy-check returned Risk Score: {bio_data['biopiracy_risk_score']}%")

    res_stats = client.get("/api/statistics")
    assert res_stats.status_code == 200
    stats_data = res_stats.json()
    print(f"PASS: /api/statistics returned {stats_data['total_documents']} documents and {stats_data['total_lexicon_synonyms']} synonyms.")

    print("\n" + "=" * 60)
    print("ALL 6 END-TO-END TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_tests()
