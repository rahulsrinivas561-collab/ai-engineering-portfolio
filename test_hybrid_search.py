import os
import chromadb
from rank_bm25 import BM25Okapi
from typing import List, Dict

# 1. Sample Enterprise Fraud Audit Dataset
documents = [
    "User 8821 initiated a refund request of 450 INR for missing items on Swiggy.",
    "CRITICAL ALERT: Account Takeover detected on transaction TXN_90412 with amount 14500 INR.",
    "Transaction TXN_90413 reported suspicious login from an unrecognized device in Mumbai.",
    "Customer requested cancellation due to late delivery on order TXN_77102.",
    "Account Takeover attempt blocked on user account 99120 before checkout."
]

# --- SEARCH ENGINE 1: BM25 (Exact Keyword Match) ---
tokenized_corpus = [doc.lower().split(" ") for doc in documents]
bm25 = BM25Okapi(tokenized_corpus)

def search_bm25(query: str, top_k: int = 3) -> List[int]:
    tokenized_query = query.lower().split(" ")
    scores = bm25.get_scores(tokenized_query)
    # Get top_k indices sorted by highest score
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return top_indices

# --- SEARCH ENGINE 2: ChromaDB (Semantic Vector Search) ---
client = chromadb.Client()
collection = client.create_collection(name="fraud_logs")

# Add documents to local vector DB
collection.add(
    documents=documents,
    ids=[f"id_{i}" for i in range(len(documents))]
)

def search_vector(query: str, top_k: int = 3) -> List[int]:
    results = collection.query(query_texts=[query], n_results=top_k)
    # Extract document indices from returned IDs
    returned_ids = results['ids'][0]
    indices = [int(doc_id.split('_')[1]) for doc_id in returned_ids]
    return indices

# --- HYBRID COMBINER: Reciprocal Rank Fusion (RRF) ---
def hybrid_search(query: str, top_k: int = 2) -> List[str]:
    bm25_ranks = search_bm25(query, top_k=3)
    vector_ranks = search_vector(query, top_k=3)
    
    rrf_scores: Dict[int, float] = {}
    k = 60 # RRF constant
    
    # Calculate RRF score for BM25 results
    for rank, doc_idx in enumerate(bm25_ranks):
        rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (k + rank + 1))
        
    # Calculate RRF score for Vector results
    for rank, doc_idx in enumerate(vector_ranks):
        rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (k + rank + 1))
        
    # Sort documents by combined RRF score
    sorted_doc_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)
    
    return [documents[i] for i in sorted_doc_indices[:top_k]]

if __name__ == "__main__":
    exact_id_query = "TXN_90412"
    
    print(f"🔍 Searching for query: '{exact_id_query}'\n")
    
    print("--- 1. Pure Vector Search Result ---")
    vector_results = [documents[i] for i in search_vector(exact_id_query, top_k=1)]
    print(f"Result: {vector_results[0]}\n")
    
    print("--- 2. Hybrid Search (BM25 + ChromaDB Vector RRF) ---")
    hybrid_results = hybrid_search(exact_id_query, top_k=1)
    print(f"Result: {hybrid_results[0]}\n")