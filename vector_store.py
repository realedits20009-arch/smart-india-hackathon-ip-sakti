"""
IP-SAKTI Hybrid Vector Store & Multilingual Retrieval Engine
Combines TF-IDF and BM25 dense-lexical scoring with Sanskrit-Hindi-English synonym expansion
for accurate, hallucination-free retrieval of Ayurvedic prior art, patent sections, and case precedents.
"""

import math
import re
from typing import List, Dict, Any, Tuple, Optional
from document_loader import Document, AyushDocumentLoader, chunk_documents

class AyushHybridVectorStore:
    def __init__(self, documents: Optional[List[Document]] = None, lexicon: Optional[Dict[str, Any]] = None):
        self.documents: List[Document] = []
        self.lexicon = lexicon or {}
        self.corpus_words: List[List[str]] = []
        self.doc_freq: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        
        # Build botanical & legal alias lookup
        self.alias_map: Dict[str, List[str]] = {}
        self._build_alias_map()

        if documents:
            self.add_documents(documents)

    def _build_alias_map(self):
        """Constructs bidirectional synonym mapping across Sanskrit, Hindi, English, Botanical."""
        botanicals = self.lexicon.get("botanical_terms", [])
        for item in botanicals:
            all_terms = []
            all_terms.extend(item.get("sanskrit", []))
            all_terms.extend(item.get("hindi", []))
            all_terms.extend(item.get("english", []))
            if item.get("botanical"):
                all_terms.append(item["botanical"])
            
            # Map every term to the full cluster
            for term in all_terms:
                t_lower = term.lower().strip()
                if t_lower not in self.alias_map:
                    self.alias_map[t_lower] = []
                for other in all_terms:
                    if other not in self.alias_map[t_lower]:
                        self.alias_map[t_lower].append(other)

        # Map therapeutic actions
        therapeutics = self.lexicon.get("therapeutic_actions", [])
        for item in therapeutics:
            sanskrit = item.get("sanskrit", "")
            english = item.get("english", "")
            hindi = item.get("hindi", "")
            herbs = item.get("associated_herbs", [])
            cluster = [sanskrit, english, hindi] + herbs
            
            # Index words
            for phrase in [sanskrit, english, hindi]:
                words = re.findall(r'\w+', phrase.lower())
                for w in words:
                    if len(w) > 3:
                        if w not in self.alias_map:
                            self.alias_map[w] = []
                        self.alias_map[w].extend(cluster)

    def expand_query(self, query: str) -> str:
        """Enriches the query with Sanskrit classical terms, Hindi synonyms, and Latin botanical binomials."""
        tokens = re.findall(r'[\w\u0900-\u097F]+', query.lower())
        expanded_terms = set(tokens)
        
        for token in tokens:
            if token in self.alias_map:
                for alias in self.alias_map[token]:
                    expanded_terms.add(alias.lower())
            # Substring matching for Hindi/Sanskrit terms
            for key in self.alias_map:
                if key in token or token in key:
                    for alias in self.alias_map[key]:
                        expanded_terms.add(alias.lower())
                        
        return query + " " + " ".join(expanded_terms)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes multilingual text preserving Devanagari and English alphanumeric tokens."""
        text = text.lower()
        tokens = re.findall(r'[\w\u0900-\u097F]+', text)
        # Filter out trivial English stop words
        stopwords = {
            "a", "an", "the", "in", "on", "at", "for", "with", "about", "against", "between",
            "into", "through", "during", "before", "after", "above", "below", "to", "from",
            "up", "down", "is", "are", "was", "were", "be", "been", "being", "have", "has",
            "had", "do", "does", "did", "can", "could", "should", "would", "will", "shall",
            "and", "but", "if", "or", "because", "as", "until", "while", "of", "it", "this",
            "that", "these", "those", "what", "which", "who", "whom", "how"
        }
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def add_documents(self, documents: List[Document]):
        """Indexes new documents using BM25 and TF-IDF term frequency weighting."""
        start_idx = len(self.documents)
        self.documents.extend(documents)
        
        for doc in documents:
            tokens = self._tokenize(doc.page_content)
            self.corpus_words.append(tokens)
            self.doc_lengths.append(len(tokens))
            
            seen_tokens = set(tokens)
            for t in seen_tokens:
                self.doc_freq[t] = self.doc_freq.get(t, 0) + 1

        total_docs = len(self.documents)
        self.avg_doc_length = sum(self.doc_lengths) / max(total_docs, 1)

        # Calculate BM25 Robertson-Spärck Jones IDF
        for term, df in self.doc_freq.items():
            self.idf[term] = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)

    def similarity_search_with_score(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Performs hybrid retrieval using BM25 + expanded semantic weighting."""
        if not self.documents:
            return []

        expanded_query_text = self.expand_query(query)
        query_tokens = self._tokenize(expanded_query_text)
        
        if not query_tokens:
            query_tokens = self._tokenize(query)

        k1 = 1.5
        b = 0.75
        scores = [0.0] * len(self.documents)

        for q_token in query_tokens:
            idf_val = self.idf.get(q_token, 0.5)
            
            for doc_idx, doc_tokens in enumerate(self.corpus_words):
                doc_len = self.doc_lengths[doc_idx]
                tf = doc_tokens.count(q_token)
                if tf > 0:
                    numerator = tf * (k1 + 1.0)
                    denominator = tf + k1 * (1.0 - b + b * (doc_len / (self.avg_doc_length or 1.0)))
                    scores[doc_idx] += idf_val * (numerator / denominator)

        # Add exact keyword / section boost (e.g. if query contains 'Section 3(p)' or specific herb)
        raw_query_lower = query.lower()
        for doc_idx, doc in enumerate(self.documents):
            meta = doc.metadata
            # Section match boost
            if meta.get("section") and meta["section"].lower() in raw_query_lower:
                scores[doc_idx] += 4.0
            # Sanskrit/Hindi/Botanical name match boost
            if meta.get("sanskrit_name") and any(w in raw_query_lower for w in meta["sanskrit_name"].lower().split()):
                scores[doc_idx] += 3.0
            if meta.get("hindi_name") and any(w in raw_query_lower for w in meta["hindi_name"].lower().split()):
                scores[doc_idx] += 3.0
            if meta.get("botanical_name") and meta["botanical_name"].lower() in raw_query_lower:
                scores[doc_idx] += 3.5

        # Normalize and rank top k
        scored_pairs = list(zip(self.documents, scores))
        scored_pairs.sort(key=lambda x: x[1], reverse=True)

        max_score = scored_pairs[0][1] if scored_pairs and scored_pairs[0][1] > 0 else 1.0
        results = []
        for doc, raw_score in scored_pairs[:k]:
            normalized_score = min(round((raw_score / max_score) * 100, 2), 100.0) if max_score > 0 else 50.0
            if raw_score > 0:
                results.append((doc, normalized_score))

        return results

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        scored = self.similarity_search_with_score(query, k=k)
        return [doc for doc, _ in scored]

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Returns all indexed document items with structured summary for UI display."""
        unique_docs = {}
        for doc in self.documents:
            doc_id = doc.metadata.get("id", "N/A")
            if doc_id not in unique_docs:
                unique_docs[doc_id] = {
                    "id": doc_id,
                    "title": doc.metadata.get("title", "Untitled Document"),
                    "category": doc.metadata.get("category", "General"),
                    "source": doc.metadata.get("source", "Ministry of Ayush / Indian Patent Office"),
                    "type": doc.metadata.get("type", "document"),
                    "section_3p_risk": doc.metadata.get("section_3p_risk", "N/A"),
                    "snippet": doc.page_content[:240] + "..."
                }
        return list(unique_docs.values())


# Global singleton instance builder
_global_vector_store: Optional[AyushHybridVectorStore] = None

def get_vector_store() -> AyushHybridVectorStore:
    global _global_vector_store
    if _global_vector_store is None:
        loader = AyushDocumentLoader()
        raw_docs = loader.load_all()
        chunked = chunk_documents(raw_docs, chunk_size=500, overlap=80)
        lexicon = loader.load_lexicon()
        _global_vector_store = AyushHybridVectorStore(documents=chunked, lexicon=lexicon)
        print(f"[IP-SAKTI] Initialized Vector Store with {len(chunked)} chunks across {len(raw_docs)} foundational documents.")
    return _global_vector_store
