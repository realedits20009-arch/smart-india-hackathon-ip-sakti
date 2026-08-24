"""
IP-SAKTI Document Ingestion and Semantic Preprocessing Pipeline
Handles loading, parsing, multilingual metadata tagging, and hierarchical chunking
for Ayurvedic Pharmacopoeia texts, 20+ Ancestral Indian Provenance Documents,
Indian Patent Statutes, Case Precedents, and TKDL references.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional

class Document:
    def __init__(self, page_content: str, metadata: Optional[Dict[str, Any]] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_content": self.page_content,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        doc_id = self.metadata.get("id", "unknown")
        title = self.metadata.get("title", "Untitled")
        return f"<Document id='{doc_id}' title='{title}'>"


class AyushDocumentLoader:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            candidates = [
                os.path.join(os.path.dirname(__file__), "backend", "data"),
                os.path.join(os.path.dirname(__file__), "data"),
                os.path.join(os.getcwd(), "backend", "data"),
                os.path.join(os.getcwd(), "data"),
            ]
            self.data_dir = None
            for c in candidates:
                if os.path.exists(c):
                    self.data_dir = c
                    break
            if not self.data_dir:
                self.data_dir = os.path.join(os.getcwd(), "backend", "data")
        else:
            self.data_dir = data_dir

    def load_all(self) -> List[Document]:
        """Loads and returns all documents from JSON data files."""
        documents: List[Document] = []
        
        if not os.path.exists(self.data_dir):
            return documents

        # 1. Load Ayurvedic Pharmacopoeia & Formulations
        ayush_file = os.path.join(self.data_dir, "ayush_knowledge_base.json")
        if os.path.exists(ayush_file):
            documents.extend(self._load_ayush_kb(ayush_file))

        # 2. Load 20+ Ancestral Indian Provenance E-Documents
        provenance_file = os.path.join(self.data_dir, "ancestral_medicine_provenance.json")
        if os.path.exists(provenance_file):
            documents.extend(self._load_ancestral_provenance(provenance_file))

        # 3. Load Patent Laws & Landmark Cases
        patent_file = os.path.join(self.data_dir, "patent_laws_and_cases.json")
        if os.path.exists(patent_file):
            documents.extend(self._load_patent_laws(patent_file))

        # 4. Load Regulatory Compliance & BDA / DCA
        regulatory_file = os.path.join(self.data_dir, "regulatory_compliance.json")
        if os.path.exists(regulatory_file):
            documents.extend(self._load_regulatory(regulatory_file))

        return documents

    def _load_ancestral_provenance(self, filepath: str) -> List[Document]:
        """Loads 20+ historical ancestral Indian medicine proof documents with Sanskrit shlokas."""
        docs = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                text = f"Title: {item.get('title')}\n"
                text += f"Ancient Sanskrit Title: {item.get('ancient_name_sanskrit', 'N/A')}\n"
                text += f"Ancient Treatise / Manuscript: {item.get('ancient_treatise', '')}\n"
                text += f"Ancient Sage / Author: {item.get('ancient_author', '')}\n"
                text += f"Historical Era / Period: {item.get('historical_period', '')}\n"
                text += f"Geographic Origin in India: {item.get('geographic_origin', '')}\n"
                text += f"Classical Sanskrit Shloka: {item.get('sanskrit_shloka', '')}\n"
                text += f"English Translation: {item.get('english_translation', '')}\n"
                text += f"Indian Provenance Proof: {item.get('provenance_evidence', '')}\n"
                text += f"Defensive Legal Anti-Biopiracy Status: {item.get('defensive_patent_status', '')}\n"
                text += f"TKRC / IPC Code: {item.get('tkrc_code', '')}\n"
                text += f"Biological Species: {item.get('biological_resource', '')}"

                metadata = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "category": "Ancestral Indian Medicine Provenance",
                    "source": item.get("ancient_treatise"),
                    "ancient_author": item.get("ancient_author"),
                    "historical_period": item.get("historical_period"),
                    "geographic_origin": item.get("geographic_origin"),
                    "sanskrit_name": item.get("ancient_name_sanskrit"),
                    "botanical_name": item.get("biological_resource"),
                    "section_3p_risk": "CRITICAL (Ancient Indian Prior Art)",
                    "type": "ancestral_indian_provenance"
                }
                docs.append(Document(page_content=text.strip(), metadata=metadata))
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        return docs

    def _load_ayush_kb(self, filepath: str) -> List[Document]:
        docs = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                text_content = f"Title: {item.get('title')}\n"
                text_content += f"Sanskrit Name: {item.get('sanskrit_name', 'N/A')}\n"
                text_content += f"Hindi Name: {item.get('hindi_name', 'N/A')}\n"
                text_content += f"Botanical/Latin: {item.get('botanical_name', 'N/A')}\n"
                text_content += f"Source/Classical Reference: {item.get('source', '')}\n"
                
                if "traditional_uses" in item:
                    text_content += "Traditional Uses & Indications: " + ", ".join(item['traditional_uses']) + "\n"
                if "composition" in item:
                    text_content += f"Composition: {item['composition']}\n"
                if "chemical_constituents" in item:
                    text_content += f"Phytochemical Constituents: {item['chemical_constituents']}\n"
                
                text_content += f"Detailed Overview: {item.get('text', '')}\n"
                text_content += f"Patentability & Section 3(p) Analysis: {item.get('patentability_notes', '')}\n"
                text_content += f"Risk Level: {item.get('section_3p_risk', 'MODERATE')}"

                metadata = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "category": item.get("category", "Ayurvedic Knowledge"),
                    "source": item.get("source"),
                    "sanskrit_name": item.get("sanskrit_name"),
                    "hindi_name": item.get("hindi_name"),
                    "botanical_name": item.get("botanical_name"),
                    "section_3p_risk": item.get("section_3p_risk"),
                    "type": "pharmacopoeia_monograph" if "API" in item.get("id", "") else "classical_formulation"
                }
                docs.append(Document(page_content=text_content.strip(), metadata=metadata))
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        return docs

    def _load_patent_laws(self, filepath: str) -> List[Document]:
        docs = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                text_content = f"Title: {item.get('title')}\n"
                if "act" in item:
                    text_content += f"Statute: {item.get('act')}, {item.get('section', '')}\n"
                    text_content += f"Statutory Text: {item.get('statutory_text', '')}\n"
                    text_content += f"Legal Analysis & Examination Standard: {item.get('analysis', '')}\n"
                    text_content += f"Official Guidelines: {item.get('guidelines_ref', '')}\n"
                    if "landmark_citations" in item:
                        text_content += "Landmark Citations: " + ", ".join(item['landmark_citations'])
                elif "patent_number" in item:
                    text_content += f"Case / Patent No: {item.get('patent_number')} ({item.get('jurisdiction')})\n"
                    text_content += f"Assignee: {item.get('assignee', '')}\n"
                    text_content += f"Challenged By: {item.get('challenge_by', '')}\n"
                    text_content += f"Outcome: {item.get('outcome', '')}\n"
                    text_content += f"Claims: {item.get('claims', '')}\n"
                    text_content += f"Evidence Presented: {item.get('legal_evidence_presented', '')}\n"
                    text_content += f"Strategic Takeaway for Ayush: {item.get('strategic_takeaway', '')}"

                metadata = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "category": item.get("category", "Patent Law"),
                    "source": item.get("act", item.get("jurisdiction", "Indian Patent Office")),
                    "section": item.get("section"),
                    "type": "patent_statute" if "LAW" in item.get("id", "") else "biopiracy_case"
                }
                docs.append(Document(page_content=text_content.strip(), metadata=metadata))
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        return docs

    def _load_regulatory(self, filepath: str) -> List[Document]:
        docs = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                text_content = f"Title: {item.get('title')}\n"
                if "act" in item:
                    text_content += f"Statute: {item.get('act')}, {item.get('section', '')}\n"
                    text_content += f"Legal Provision: {item.get('statutory_text', '')}\n"
                    text_content += f"Analysis: {item.get('analysis', '')}\n"
                    if "procedure" in item:
                        text_content += "Procedure & Compliance Steps:\n" + "\n".join(item['procedure']) + "\n"
                    if "licensing_categories" in item:
                        text_content += "Licensing Categories under Rule 158-B:\n"
                        for k, v in item['licensing_categories'].items():
                            text_content += f"- {k}: {v}\n"
                elif "agency" in item:
                    text_content += f"Agency / Initiative: {item.get('agency')}\n"
                    text_content += f"Corpus Scope: {item.get('corpus_details', '')}\n"
                    text_content += f"Defensive Mechanism: {item.get('defensive_mechanism', '')}\n"
                    text_content += f"Global Impact Statistics: {item.get('statistics', '')}"
                elif "treaty" in item:
                    text_content += f"Treaty: {item.get('treaty')}, {item.get('article', '')}\n"
                    text_content += f"Text: {item.get('statutory_text', '')}\n"
                    text_content += f"Analysis: {item.get('analysis', '')}"

                metadata = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "category": item.get("act", item.get("agency", item.get("treaty", "Regulatory Framework"))),
                    "source": item.get("act", item.get("agency", item.get("treaty", "AYUSH Regulatory"))),
                    "type": "regulatory_statute"
                }
                docs.append(Document(page_content=text_content.strip(), metadata=metadata))
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
        return docs

    def load_lexicon(self) -> Dict[str, Any]:
        lexicon_file = os.path.join(self.data_dir, "sanskrit_multilingual_lexicon.json")
        if os.path.exists(lexicon_file):
            try:
                with open(lexicon_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading lexicon: {e}")
        return {}

    def load_ancestral_raw(self) -> List[Dict[str, Any]]:
        """Loads raw JSON of ancestral provenance records for direct API serving."""
        provenance_file = os.path.join(self.data_dir, "ancestral_medicine_provenance.json")
        if os.path.exists(provenance_file):
            try:
                with open(provenance_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading raw ancestral docs: {e}")
        return []


def chunk_documents(documents: List[Document], chunk_size: int = 600, overlap: int = 100) -> List[Document]:
    chunked_docs = []
    for doc in documents:
        content = doc.page_content
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]
        
        current_chunk = []
        current_length = 0
        chunk_idx = 1
        
        for para in paragraphs:
            para_len = len(para.split())
            if current_length + para_len > chunk_size and current_chunk:
                chunk_text = "\n".join(current_chunk)
                new_meta = doc.metadata.copy()
                new_meta["chunk_id"] = f"{doc.metadata.get('id', 'doc')}_chk{chunk_idx}"
                chunked_docs.append(Document(page_content=chunk_text, metadata=new_meta))
                chunk_idx += 1
                current_chunk = [para]
                current_length = para_len
            else:
                current_chunk.append(para)
                current_length += para_len
                
        if current_chunk:
            chunk_text = "\n".join(current_chunk)
            new_meta = doc.metadata.copy()
            new_meta["chunk_id"] = f"{doc.metadata.get('id', 'doc')}_chk{chunk_idx}"
            chunked_docs.append(Document(page_content=chunk_text, metadata=new_meta))
            
    return chunked_docs
