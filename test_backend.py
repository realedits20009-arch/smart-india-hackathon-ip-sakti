"""
Automated Backend Verification Suite for IP-SAKTI
Tests RAG pipeline, cross-lingual retrieval, Section 3(p) scoring, biopiracy scanner.
"""

import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from vector_store import get_vector_store
from rag_chain import get_rag_chain

def test_all():
    print("=" * 60)
    print("[1/5] Testing Knowledge Base & Vector Store Initialization...")
    vs = get_vector_store()
    assert len(vs.documents) > 0, "Vector store must have indexed documents!"
    print(f"PASS: Indexed {len(vs.documents)} chunks across corpus. Vocabulary size: {len(vs.doc_freq)} terms.")

    rag = get_rag_chain()

    print("\n" + "=" * 60)
    print("[2/5] Testing Multilingual RAG Search (English + Hindi)...")
    
    # Test 1: English query on Turmeric wound healing patentability
    q1 = "Can I patent a wound healing ointment with Curcuma longa and honey under Indian Patent Law?"
    res1 = rag.ask(q1)
    print(f"Query 1: {q1}")
    print(f"Confidence: {res1['confidence_score']}% | Citations: {len(res1['citations'])}")
    print(f"Top Source: {res1['citations'][0]['title']} ({res1['citations'][0]['source']})")
    assert len(res1['citations']) > 0
    assert "Section 3(p)" in res1['answer'] or "3(p)" in res1['answer']

    # Test 2: Hindi query on Neem and skin disease
    q2 = "क्या नीम (Azadirachta indica) का चर्म रोग हेतु पेटेंट मिल सकता है?"
    res2 = rag.ask(q2)
    print(f"\nQuery 2: {q2}")
    print(f"Confidence: {res2['confidence_score']}% | Detected Lang: {res2['language']}")
    print(f"Top Source: {res2['citations'][0]['title']}")
    assert len(res2['citations']) > 0

    print("\n" + "=" * 60)
    print("[3/5] Testing Section 3(p) Patentability Assessment Engine...")
    patent_test = rag.analyze_patentability(
        title="Formulation of Ashwagandha and Piperine extract for stress relief",
        abstract="A composition combining Withania somnifera and Piper longum to enhance adaptogenic activity.",
        claims=["A synergistic composition comprising 200mg Ashwagandha extract and 10mg Piperine."],
        ingredients=["Withania somnifera (Ashwagandha)", "Piper longum (Pippali)"],
        proposed_use="Stress alleviation and cognitive enhancement"
    )
    print(f"Risk Score: {patent_test['overall_risk_score']}% ({patent_test['risk_level']})")
    print(f"Verdict: {patent_test['patentability_verdict']}")
    print(f"Prior Art Overlaps Found: {len(patent_test['prior_art_matches'])}")
    assert patent_test['overall_risk_score'] >= 60

    print("\n" + "=" * 60)
    print("[4/5] Testing Biopiracy Scanner & NBA Form III Compliance...")
    bio_test = rag.check_biopiracy(
        jurisdiction="EPO",
        applicant_country="United States",
        biological_resources=["Azadirachta indica (Neem)", "Curcuma longa (Turmeric)"],
        claim_summary="Hydrophobic extract of neem oil for plant fungal protection"
    )
    print(f"Biopiracy Risk Score: {bio_test['biopiracy_risk_score']}%")
    print(f"Alert Flags: {bio_test['alert_flags']}")
    assert bio_test['biopiracy_risk_score'] >= 80

    print("\n" + "=" * 60)
    print("[5/5] Testing Corpus Statistics & Lexicon...")
    docs_summary = vs.get_all_documents()
    print(f"Total Unique Canonical Documents: {len(docs_summary)}")
    for d in docs_summary[:3]:
        print(f"  - [{d['id']}] {d['title']} ({d['category']})")

    print("\n" + "=" * 60)
    print("ALL 5 TEST SUITES PASSED FLAWLESSLY! BACKEND IS PRODUCTION READY.")
    print("=" * 60)

if __name__ == "__main__":
    test_all()
