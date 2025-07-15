import pickle
from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm



PDF_PATH    = Path("Enbudgetdestek.pdf")
VEC_PATH    = Path("embeddings.pkl")
EMB_MODEL   = "all-MiniLM-L6-v2"    #SBERT model (~~100mb)
CHUNK_SIZE  = 1_000
OVERLAP     = 100                         



def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP):
    """sliding-window chunker (character based)."""
    step = size - overlap
    for start in range(0, len(text), step):
        yield text[start : start + size]


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"{PDF_PATH} not found")

    # 1) Extract full text from all pages
    pages = [p.extract_text() or "" for p in PdfReader(str(PDF_PATH)).pages]
    full_text = "\n".join(pages)

    # 2) Split into overlapping chunks
    chunks = list(_chunk_text(full_text))
    print(f"chunking done — {len(chunks)} chunks")

    # 3) Embed with Sentence-Transformers
    model = SentenceTransformer(EMB_MODEL)
    embeddings = model.encode(
        chunks,
        show_progress_bar = True,
        convert_to_numpy = True,
        normalize_embeddings = True,   # unit-norm for cheap cosine
    )

    # 4) Persist
    with open(VEC_PATH, "wb") as f:
        pickle.dump({"chunks": chunks, "embeddings": embeddings}, f)
    print(f"saved vector store in {VEC_PATH.resolve()}")



if __name__ == "__main__":
    main()
