"""ChromaDB Vector Store for IoT RAG"""

import chromadb
from dataclasses import dataclass
from pathlib import Path

from .parser import PDFChunk


@dataclass
class QueryMetadata:
    source_file: str


@dataclass
class QueryResult:
    id: str
    document: str
    metadata: QueryMetadata


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

    def query(self, query_text: str, top_k: int = 5) -> list[QueryResult]:
        """
        Queries the vector store for similar documents based on the input query text.

        Args:
            query_text (str): The text to query against the vector store.
            top_k (int): The number of top results to return. Defaults to 5.
        """
        collection = self.get_or_create_collection()
        results = collection.query(query_texts=[query_text], n_results=top_k)

        # Ensure that the results are in the expected format and handle cases where there are no results
        return [
            QueryResult(
                id=result_id,
                document=document,
                metadata=QueryMetadata(source_file=metadata["source_file"]),
            )
            for result_id, document, metadata in zip(
                results["ids"][0] if results["ids"] else [],
                results["documents"][0] if results["documents"] else [],
                results["metadatas"][0] if results["metadatas"] else [],
            )
        ]

    def count(self):
        """
        Returns the number of documents in the collection.

        Returns:
            int: The number of documents in the collection.
        """
        collection = self.get_or_create_collection()
        return collection.count()
