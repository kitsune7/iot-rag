import os
from .parser import extract_text_from_pdf, get_text_chunks
from .vector_store import VectorStore


def rag_query(query_text: str, top_k=5, verbose=False, db_path="./chroma_db"):
    """Runs the RAG query against the vector store."""

    def log(message: str):
        """Utility function for logging messages when verbose mode is enabled."""
        if verbose:
            print(message)

    # Index vector store if it doesn't already exist
    store = VectorStore(db_path=db_path)
    if not store.get_or_create_collection().count():
        log("No existing vector store found. Indexing PDF files in 'assets' directory...")
        for file in os.listdir("assets"):
            if file.endswith(".pdf"):
                log(f"Processing {file}...")
                pdf_text = extract_text_from_pdf(os.path.join("assets", file))
                chunks = get_text_chunks(pdf_text, source_file=file)
                store.add_chunks(chunks)
                log(f"Added {len(chunks)} chunks from {file} to the vector store.")

    return store.query(query_text=query_text, top_k=top_k)
