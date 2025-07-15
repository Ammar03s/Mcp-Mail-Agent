
import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from llm import chat

STORE = pickle.loads(Path("embeddings.pkl").read_bytes())
EMB   = STORE["embeddings"]           # numpy array shape (N, d)
CHUNKS = STORE["chunks"]
print(f"vector store loaded = {len(CHUNKS)} chunks from embeddings.pkl")


_TOP_K        = 4
_REL_THRESHOLD = 0.25                 # cosine-sim cut-off
_Q_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def _embed(text: str) -> np.ndarray:
    """Unit-norm embedding for a single query string."""
    return _Q_MODEL.encode([text], convert_to_numpy = True,
                           normalize_embeddings = True)[0]


def _search(q_vec: np.ndarray, k: int = _TOP_K):
    """Return [(idx, sim)] for top-k most similar chunks."""
    sims = EMB @ q_vec                 # fast cosine (dot product) cuz unit-norm
    idxs = sims.argsort()[-k:][::-1]
    return [(i, sims[i]) for i in idxs]


def is_relevant(question: str) -> bool:
    """
    Fast classifier: ask the LLM YES/NO if the PDF is needed.
    """
    print(f"\n Checking relevance for question: '{question[:100]}...'")
    verdict = chat(
        "Answer YES or NO (just one word). "
        "Does the user's question require information from the reference PDF?\n\n"
        f"Question: {question}"
    ).strip().lower()
    print(f"llm relevance verdict: {verdict.upper()}")
    return verdict.startswith("y")


def answer(question: str) -> str:
    """
    Build context from top chunks, then invoke the LLM.
    """
    print("...pdf is relevant. using rag to generate answer.")
    q_vec = _embed(question)
    hits  = _search(q_vec)

    print(f"\nfound {len(hits)} most similar chunks from pdf(index)")
    for i, (idx, sim) in enumerate(hits):
        chunk_preview = CHUNKS[idx].replace('\n', ' ').strip()
        print(f"  - Hit {i+1} (Similarity: {sim:.2f}): \"{chunk_preview[:71]}...\"")

    context = "\n---\n".join(CHUNKS[i] for i, _ in hits)

    prompt = f""" You are **DataLiva's customer-support assistant**.

— **Answer ONLY** with facts you find in the **Context** section.  
— If the Context does **NOT** contain the answer, reply:  
  "I'm not sure based on our current records."  
— Keep the tone friendly, concise, and business-formal.  
— Use complete sentences and end with **"Best regards, DataLiva Support."**

─────────────────────
Context
{context}
─────────────────────

Customer question:
{question}

Draft reply:
"""
    print("\npassing retrieved context to llm to draft reply...")
    return chat(prompt)
