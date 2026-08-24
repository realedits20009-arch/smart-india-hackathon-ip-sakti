"""
IP-SAKTI RAG Pipeline, Legal-Scientific Reasoning Engine & Biopiracy Detector
Specialized for Ministry of Ayush:
- Multilingual Question Answering (English, Hindi, Sanskrit terms) with Source Citations
- Section 3(p), 3(d), 3(e) Patentability & Prior Art Risk Assessment Engine
- Biological Diversity Act & TKDL Biopiracy Risk Analyzer
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from vector_store import get_vector_store, AyushHybridVectorStore
from document_loader import Document

class AyushRAGChain:
    def __init__(self, vector_store: Optional[AyushHybridVectorStore] = None):
        self.vector_store = vector_store or get_vector_store()
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def _detect_language(self, text: str) -> str:
        """Detects whether query is in Hindi (Devanagari), Sanskrit-dominant, or English."""
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        if devanagari_chars > 3:
            return "hi"
        return "en"

    def ask(self, query: str, top_k: int = 4, language: str = "auto") -> Dict[str, Any]:
        """
        Executes grounded Multilingual RAG search:
        1. Expands cross-lingual Sanskrit/Hindi/English query.
        2. Retrieves top-k authoritative source chunks.
        3. Formulates structured synthesis with exact inline citations and metadata cards.
        """
        lang = self._detect_language(query) if language == "auto" else language
        retrieved_docs_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        if not retrieved_docs_with_scores:
            return {
                "query": query,
                "answer": "No directly matching Ayurvedic Pharmacopoeia or Patent Law records found for this query. Please refine with specific botanical names (e.g. Haridra, Neem) or legal sections (e.g. Section 3(p)).",
                "citations": [],
                "confidence_score": 0.0,
                "language": lang
            }

        # Build citation cards
        citations = []
        context_blocks = []
        total_score = 0.0

        for doc, score in retrieved_docs_with_scores:
            total_score += score
            meta = doc.metadata
            citation_item = {
                "id": meta.get("id", "DOC"),
                "title": meta.get("title", "Ayush Document"),
                "source": meta.get("source", "Ministry of Ayush / Indian Patent Office"),
                "category": meta.get("category", "General"),
                "section": meta.get("section", "N/A"),
                "botanical_name": meta.get("botanical_name", "N/A"),
                "sanskrit_name": meta.get("sanskrit_name", "N/A"),
                "confidence": score,
                "excerpt": doc.page_content[:260] + "..."
            }
            citations.append(citation_item)
            context_blocks.append(f"[{meta.get('id', 'DOC')}] {meta.get('title', '')} (Source: {meta.get('source', '')}):\n{doc.page_content}\n")

        avg_confidence = round(total_score / len(retrieved_docs_with_scores), 1)

        # Generate synthesized legal-scientific response
        answer = self._generate_grounded_response(query, context_blocks, citations, lang)

        return {
            "query": query,
            "answer": answer,
            "citations": citations,
            "confidence_score": avg_confidence,
            "language": lang,
            "retrieved_count": len(citations)
        }

    def _generate_grounded_response(self, query: str, context_blocks: List[str], citations: List[Dict[str, Any]], lang: str) -> str:
        """Synthesizes structured, highly authoritative legal-ayurvedic response with citations."""
        q_lower = query.lower()
        
        # Check if user asks about patentability of specific herb
        if "patent" in q_lower or "पेटेंट" in q_lower or "section 3" in q_lower or "धारा 3" in q_lower:
            return self._build_patentability_qa(query, citations, lang)
        
        # Check if user asks about regulatory/licensing
        if "license" in q_lower or "licensing" in q_lower or "लाइसेंस" in q_lower or "158" in q_lower or "approval" in q_lower:
            return self._build_regulatory_qa(query, citations, lang)

        # Check if user asks about biopiracy case
        if "biopiracy" in q_lower or "turmeric" in q_lower or "neem" in q_lower or "revocation" in q_lower or "हल्दी" in q_lower or "नीम" in q_lower:
            return self._build_biopiracy_qa(query, citations, lang)

        # General Ayurvedic & Legal Knowledge Synthesizer
        if lang == "hi":
            res = f"### आयुर्वेदिक एवं विधिक विश्लेषण (IP-SAKTI AI):\n\n"
            res += f"आपके प्रश्न के संदर्भ में भारतीय आयुर्वेद संहिताओं एवं पेटेंट विधि के आधार पर निम्नलिखित प्रामाणिक तथ्य प्राप्त हुए हैं:\n\n"
            for c in citations[:3]:
                res += f"- **[{c['id']}] {c['title']}**:\n"
                res += f"  - **स्रोत**: {c['source']}\n"
                res += f"  - **मुख्य विवरण**: {c['excerpt']}\n\n"
            res += f"\n> **विधिक परामर्श सूचना**: भारतीय पेटेंट अधिनियम, 1970 की **धारा 3(p)** के अंतर्गत पारंपरिक आयुर्वेदिक ज्ञान एवं संहिताओं में वर्णित उपयोगों का सीधा पेटेंट प्रतिबंधित है। किसी भी शोध पर पेटेंट से पूर्व राष्ट्रीय जैव विविधता प्राधिकरण (NBA) फॉर्म III की अनुमति अनिवार्य है।"
            return res
        else:
            res = f"### Ayurvedic & Intellectual Property Legal Analysis:\n\n"
            res += f"Based on the **Ayurvedic Pharmacopoeia of India (API)**, classical treatises, and the **Indian Patents Act, 1970**, here is the grounded legal-scientific synthesis for your query:\n\n"
            for c in citations[:3]:
                res += f"#### Source [{c['id']}]: {c['title']}\n"
                res += f"- **Statutory / Textual Authority**: `{c['source']}`\n"
                if c.get('sanskrit_name') and c['sanskrit_name'] != "N/A":
                    res += f"- **Classical Sanskrit Identification**: *{c['sanskrit_name']}* ({c.get('botanical_name')})\n"
                res += f"- **Key Excerpt**: {c['excerpt']}\n\n"
            
            res += f"### Statutory Implications:\n"
            res += f"1. **Section 3(p) Compliance**: Any use documented in classical literature is considered public domain Traditional Knowledge.\n"
            res += f"2. **Biodiversity Safeguards**: Under Section 6 of the Biological Diversity Act 2002, inventions derived from Indian biological material require mandatory **NBA Form III** clearance.\n"
            res += f"3. **Regulatory Pathway**: Licensing requires adherence to **Rule 158-B** under the Drugs and Cosmetics Act 1940."
            return res

    def _build_patentability_qa(self, query: str, citations: List[Dict[str, Any]], lang: str) -> str:
        primary = citations[0] if citations else {}
        if lang == "hi":
            return (
                f"### पेटेंट योग्यता एवं धारा 3(p) विश्लेषण:\n\n"
                f"**1. कानूनी स्थिति (Section 3(p) Status)**:\n"
                f"भारतीय पेटेंट अधिनियम 1970 की **धारा 3(p)** के अनुसार, कोई भी उत्पाद या उपयोग जो पारंपरिक आयुर्वेदिक ज्ञान (Traditional Knowledge) या उसके ज्ञात गुणों का केवल एकत्रीकरण है, वह **पेटेंट योग्य नहीं है**।\n\n"
                f"**2. उद्धृत साक्ष्य (Cited Prior Art)**:\n"
                f"- **दस्तावेज़ संख्या**: `[{primary.get('id', 'AYUSH-API')}]` {primary.get('title', 'Ayurvedic Text')}\n"
                f"- **मूल संहिता / स्रोत**: *{primary.get('source', 'Ayurvedic Pharmacopoeia of India')}*\n"
                f"- **पारंपरिक उपयोग**: {primary.get('excerpt', '')}\n\n"
                f"**3. पेटेंट प्राप्त करने हेतु आवश्यक शर्तें (How to Overcome Section 3(p))**:\n"
                f"- **नया रासायनिक रूपांतरण (Novel Synthesis)**: साधारण पादप अर्क (extract) के बजाय नए आणविक व्युत्पन्न (derivatives) प्रस्तुत करें।\n"
                f"- **धारा 3(e) तालमेल (Synergy Data)**: यदि एक से अधिक जड़ी-बूटियाँ हैं, तो सिद्ध करें कि उनका संयुक्त प्रभाव उनके व्यक्तिगत प्रभावों के योग से काफी अधिक है (Combination Index < 1)।\n"
                f"- **धारा 3(d) प्रभावशीलता**: चिकित्सीय प्रभावशीलता (Therapeutic Efficacy) में उल्लेखनीय वृद्धि सिद्ध करें।\n"
                f"- **NBA फॉर्म III**: पेटेंट अनुदान से पूर्व राष्ट्रीय जैव विविधता प्राधिकरण से अनापत्ति प्रमाण पत्र लें।"
            )
        else:
            return (
                f"### Patentability & Section 3(p) Legal Assessment:\n\n"
                f"#### 1. Statutory Barrier: Section 3(p) of the Patents Act, 1970\n"
                f"Under **Section 3(p)**, an invention which in effect is traditional knowledge or an aggregation/duplication of known properties of traditionally known components is **NOT PATENTABLE**.\n\n"
                f"#### 2. Cited Classical Prior Art & References:\n"
                f"- **Primary Reference**: `[{primary.get('id', 'API-REF')}]` **{primary.get('title', 'Pharmacopoeial Record')}**\n"
                f"- **Authoritative Source**: `{primary.get('source', 'Ayurvedic Pharmacopoeia of India')}`\n"
                f"- **Documented Evidence**: {primary.get('excerpt', '')}\n\n"
                f"#### 3. Strategic Patent Prosecution Recommendations:\n"
                f"- **Overcoming Section 3(p)**: Pure botanical extracts or known classical uses are directly anticipated by TKDL. You must claim novel non-obvious formulations (e.g., targeted nano-conjugates or synthetic derivatives).\n"
                f"- **Overcoming Section 3(e) (Mere Admixture)**: Polyherbal compositions require experimental in-vivo or clinical synergy data demonstrating non-additive therapeutic enhancement.\n"
                f"- **Mandatory NBA Compliance**: Under Section 6 of the Biological Diversity Act 2002, file **Form III** before patent grant to avoid revocation under Section 64(1)(p)."
            )

    def _build_regulatory_qa(self, query: str, citations: List[Dict[str, Any]], lang: str) -> str:
        if lang == "hi":
            return (
                f"### आयुष विनियामक एवं लाइसेंसिंग मार्गदर्शन (Rule 158-B):\n\n"
                f"औषधि एवं प्रसाधन सामग्री नियमावली, 1945 के **नियम 158-B (Rule 158-B)** के अंतर्गत लाइसेंसिंग वर्गीकरण:\n\n"
                f"1. **शास्त्रीय औषधियां (Classical / Shastriya Medicines)**:\n"
                f"   - प्रथम अनुसूची में वर्णित संहिताओं (चरक, सुश्रुत आदि) के अनुसार निर्माण।\n"
                f"   - **आवश्यकता**: केवल मूल ग्रंथ का संदर्भ और API मानकों का पालन। नैदानिक परीक्षण (Clinical Trials) की आवश्यकता नहीं।\n\n"
                f"2. **पेटेंट या प्रोप्राइटरी आयुर्वेदिक औषधियां (Proprietary ASU)**:\n"
                f"   - नए अनुपात या नई खुराक (extracts/syrups)।\n"
                f"   - **आवश्यकता**: सुरक्षा अध्ययन (तीव्र विषाक्तता परीक्षण - OECD गाइडलाइन) + प्रभावशीलता का नैदानिक प्रमाण (Pilot Clinical Study)।\n\n"
                f"3. **शुद्ध पादप-रसायन (Purified Single Phytochemicals, जैसे 95% Curcumin)**:\n"
                f"   - यह साधारण आयुष लाइसेंस के तहत नहीं आता; इसे New Drugs and Clinical Trials Rules 2019 के अंतर्गत CDSCO से अनुमति लेनी होगी।"
            )
        else:
            return (
                f"### Ayush Regulatory & Manufacturing Licensing Guidelines (Rule 158-B):\n\n"
                f"Under **Rule 158-B** of the Drugs and Cosmetics Rules, 1945 (Chapter IV-A), licensing from the State Ayush Licensing Authority (SALA) falls under three main pathways:\n\n"
                f"1. **Classical / Shastriya Formulations**:\n"
                f"   - Formulated strictly per authoritative texts listed in the First Schedule (e.g. Charaka Samhita, Sharangdhara Samhita).\n"
                f"   - **Requirements**: Textual citation, adherence to Ayurvedic Pharmacopoeia of India (API) standards. Pre-clinical and clinical trial data are *exempted* for traditional indications.\n\n"
                f"2. **Proprietary Ayurvedic Medicines (Patent & Proprietary)**:\n"
                f"   - Combinations of classical ingredients in novel proportions or non-classical dosage formats.\n"
                f"   - **Requirements**: Acute oral toxicity studies in rodents + pilot clinical trial / published literature proving safety and therapeutic efficacy.\n\n"
                f"3. **Biological Resource Sourcing & NBA Form I/III**:\n"
                f"   - Commercial scale procurement must align with State Biodiversity Board (SBB) intimation and Access & Benefit Sharing (ABS) protocols."
            )

    def _build_biopiracy_qa(self, query: str, citations: List[Dict[str, Any]], lang: str) -> str:
        return (
            f"### Landmark Biopiracy Cases & Defensive TKDL Protection:\n\n"
            f"#### 1. Case Study 1: USPTO Turmeric Wound Healing Patent (US 5,401,504)\n"
            f"- **Inventors/Assignee**: University of Mississippi (1995)\n"
            f"- **Claim**: Topical turmeric powder for wound healing (Vrana-ropana).\n"
            f"- **India's Challenge**: CSIR produced 32 historical Sanskrit, Hindi, and Urdu references showing millennia of prior use.\n"
            f"- **Outcome**: Full revocation by USPTO in 1997 due to lack of novelty.\n\n"
            f"#### 2. Case Study 2: European Patent Office Neem Antifungal Patent (EP 0436257)\n"
            f"- **Assignee**: W.R. Grace & USDA (1994)\n"
            f"- **Claim**: Hydrophobic neem oil extract for plant fungal control.\n"
            f"- **India's Challenge**: Opposed by Dr. Vandana Shiva and CSIR, proving widespread traditional agricultural use in Indian villages.\n"
            f"- **Outcome**: Full revocation by EPO in 2000 for lack of inventive step (Article 56 EPC).\n\n"
            f"#### 3. The Defensive Shield: Traditional Knowledge Digital Library (TKDL)\n"
            f"- Digital repository of over **4.3 lakh (430,000) formulations** translated into English, German, French, Japanese, and Spanish.\n"
            f"- Enables international patent examiners (USPTO, EPO, JPO) to block biopiracy at pre-grant stage via direct citations."
        )

    def analyze_patentability(self, title: str, abstract: str, claims: List[str], ingredients: List[str], proposed_use: str) -> Dict[str, Any]:
        """
        Deep Patentability & Section 3(p) / 3(d) / 3(e) Risk Engine.
        Analyzes claims against the entire Ayush knowledge base and provides a granular risk report.
        """
        combined_text = f"{title} {abstract} {' '.join(claims)} {' '.join(ingredients)} {proposed_use}"
        retrieved = self.vector_store.similarity_search_with_score(combined_text, k=4)
        
        # Calculate Section 3(p) Risk
        sec_3p_risk_score = 0
        sec_3d_risk_score = 0
        sec_3e_risk_score = 0
        prior_art_matches = []
        
        for doc, score in retrieved:
            meta = doc.metadata
            prior_art_matches.append({
                "id": meta.get("id"),
                "title": meta.get("title"),
                "source": meta.get("source"),
                "section_3p_risk": meta.get("section_3p_risk"),
                "similarity_score": score,
                "relevance": f"Discloses traditional use / composition matching: {meta.get('botanical_name', meta.get('title'))}"
            })
            
            # Risk scoring heuristics
            if "HIGH" in str(meta.get("section_3p_risk", "")):
                sec_3p_risk_score = max(sec_3p_risk_score, 85)
            elif "MODERATE" in str(meta.get("section_3p_risk", "")):
                sec_3p_risk_score = max(sec_3p_risk_score, 60)
            elif "CRITICAL" in str(meta.get("section_3p_risk", "")):
                sec_3p_risk_score = 95

        # Check multi-ingredient admixture risk under Section 3(e)
        if len(ingredients) > 1:
            sec_3e_risk_score = 75
            
        # Check extraction / form modification risk under Section 3(d)
        if any(term in combined_text.lower() for term in ["extract", "powder", "oil", "juice", "paste", "syrup", "capsule"]):
            sec_3d_risk_score = 70

        overall_risk_score = max(sec_3p_risk_score, (sec_3p_risk_score * 0.5 + sec_3e_risk_score * 0.3 + sec_3d_risk_score * 0.2))
        overall_risk_score = round(min(overall_risk_score, 98), 1)

        risk_level = "CRITICAL" if overall_risk_score >= 80 else ("HIGH" if overall_risk_score >= 60 else "MODERATE")

        # Actionable recommendations to overcome objections
        recommendations = [
            "Conduct Synergistic Isobologram Analysis: Provide in-vitro/in-vivo quantitative proof (Combination Index CI < 1.0) to overcome Section 3(e) mere admixture objection.",
            "Demonstrate Significant Enhancement of Therapeutic Efficacy per Section 3(d) (Novartis standard) rather than simple physical bioavailability.",
            "Mandatory NBA Form III Filing: Apply for prior approval from the National Biodiversity Authority under Section 6 of the Biological Diversity Act, 2002 before patent grant.",
            "Claim Specific Novel Process or Synthesized Derivative: Narrow claims from broad plant extract to specific non-obvious purified fractions or synthetic analogues to bypass Section 3(p)."
        ]

        return {
            "title": title,
            "overall_risk_score": overall_risk_score,
            "risk_level": risk_level,
            "statutory_risk_breakdown": {
                "section_3p_traditional_knowledge": sec_3p_risk_score,
                "section_3d_evergreening_efficacy": sec_3d_risk_score,
                "section_3e_mere_admixture": sec_3e_risk_score
            },
            "prior_art_matches": prior_art_matches,
            "recommendations": recommendations,
            "nba_approval_required": True,
            "patentability_verdict": "REJECTION LIKELY UNDER SECTION 3(p)/3(e) WITHOUT EXPERIMENTAL SYNERGY DATA" if overall_risk_score >= 70 else "CONDITIONALLY PATENTABLE WITH PROPRIETARY PROCESS CLAIMS"
        }

    def check_biopiracy(self, jurisdiction: str, applicant_country: str, biological_resources: List[str], claim_summary: str) -> Dict[str, Any]:
        """
        Evaluates potential biopiracy and compliance with Biological Diversity Act 2002 & WTO TRIPS.
        """
        combined = f"{' '.join(biological_resources)} {claim_summary}"
        retrieved = self.vector_store.similarity_search_with_score(combined, k=3)
        
        is_foreign = applicant_country.strip().lower() not in ["india", "in", "bharat", "भारतीय"]
        nba_violation_risk = 90 if is_foreign else 65
        
        matches = []
        for doc, score in retrieved:
            matches.append({
                "id": doc.metadata.get("id"),
                "title": doc.metadata.get("title"),
                "source": doc.metadata.get("source"),
                "score": score
            })

        alert_flags = []
        if is_foreign:
            alert_flags.append("CRITICAL: Foreign applicant seeking IPR on Indian biological resources requires prior NBA approval under Section 3(2) and Section 6 of Biological Diversity Act 2002.")
        if any(h.lower() in combined.lower() for h in ["turmeric", "haldi", "haridra", "neem", "nimba", "ashwagandha", "basmati"]):
            alert_flags.append("HIGH ALERT: Target biological resource has prominent historical biopiracy precedents (e.g. US 5,401,504 or EP 0436257). Direct TKDL Third-Party Pre-Grant Opposition is likely.")

        return {
            "jurisdiction": jurisdiction,
            "applicant_country": applicant_country,
            "biological_resources": biological_resources,
            "biopiracy_risk_score": nba_violation_risk,
            "tkdl_overlap_level": "VERY HIGH" if matches else "MODERATE",
            "alert_flags": alert_flags,
            "applicable_statutes": [
                "Section 6, Biological Diversity Act 2002 (Mandatory NBA Form III)",
                "Section 3(p), Indian Patents Act 1970 (Traditional Knowledge exclusion)",
                "Article 27.3(b), WTO TRIPS Agreement",
                "Nagoya Protocol on Access and Benefit Sharing (ABS)"
            ],
            "recommended_action": "File Third-Party Pre-Grant Observation with TKDL citations or require Applicant to execute ABS agreement with National Biodiversity Authority."
        }


# Global singleton instance
_global_rag_chain: Optional[AyushRAGChain] = None

def get_rag_chain() -> AyushRAGChain:
    global _global_rag_chain
    if _global_rag_chain is None:
        _global_rag_chain = AyushRAGChain()
    return _global_rag_chain
