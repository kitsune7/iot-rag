"""ChromaDB Vector Store for IoT RAG"""

from pathlib import Path
from .parser import PDFChunk

import chromadb


class VectorStore:
    """A simple wrapper around ChromaDB for storing and retrieving vectors."""

    def __init__(self, db_path: str = "./chroma_db"):
        """
        Initializes a persistent ChromaDB VectorStore.

        Args:
            db_path (str): Path to the ChromaDB database directory. Defaults to "./chroma_db".
        """
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = "iot"

    def get_or_create_collection(self):
        """
        Retrieves the collection if it exists, otherwise creates a new one.

        Returns:
            chromadb.Collection: The ChromaDB collection for IoT data.
        """
        return self.client.get_or_create_collection(name=self.collection_name)

    def add_chunks(self, chunks: list[PDFChunk], batch_size: int = 100):
        """
        Adds text chunks to the vector store with optional metadata.

        Args:
            chunks (List[str]): A list of text chunks to be added.
            metadata (List[dict], optional): A list of metadata dictionaries corresponding to each chunk.
        """
        collection = self.get_or_create_collection()
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i : i + batch_size]
            ids = [f"{chunk.source_file}_{i + j}" for j, chunk in enumerate(batch_chunks)]
            texts = [chunk.text for chunk in batch_chunks]
            metadata = [{"source_file": chunk.source_file} for chunk in batch_chunks]

            collection.add(ids=ids, documents=texts, metadatas=metadata)

    def clear(self):
        """
        Clears the vector store by deleting the collection and creating a new one.
        """
        try:
            self.client.delete_collection("iot")
        except Exception:
            pass  # Collection doesn't exist, that's fine

        return self.get_or_create_collection()
