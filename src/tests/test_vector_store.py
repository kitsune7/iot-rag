from pathlib import Path
import pytest

from iot_rag.vector_store import VectorStore
from iot_rag.parser import PDFChunk


class TestVectorStore:
    def test_vector_store_initialization(self, tmpdir):
        """Test that VectorStore initializes correctly."""
        store = VectorStore(db_path=tmpdir)
        assert store is not None
        assert store.client is not None
        assert store.collection_name == "iot"

    def test_get_or_create_collection(self, tmpdir):
        """Test that get_or_create_collection creates and retrieves a collection."""
        store = VectorStore(db_path=tmpdir)
        collection = store.get_or_create_collection()

        assert collection is not None
        assert collection.name == "iot"

        # Verify we can retrieve the same collection
        collection2 = store.get_or_create_collection()
        assert collection2.name == collection.name

    def test_add_chunks(self, tmpdir):
        """Test adding chunks to the vector store."""
        store = VectorStore(db_path=tmpdir)

        # Create sample chunks
        chunks = [
            PDFChunk(text="This is a test chunk about IoT.", source_file="test1.pdf"),
            PDFChunk(text="Another chunk discussing sensors and devices.", source_file="test1.pdf"),
            PDFChunk(text="A third chunk from a different source.", source_file="test2.pdf"),
        ]

        # Add chunks to the store
        store.add_chunks(chunks)

        # Verify chunks were added by checking the collection
        collection = store.get_or_create_collection()
        result = collection.get()

        assert len(result["ids"]) == 3
        assert len(result["documents"]) == 3
        assert result["documents"][0] == "This is a test chunk about IoT."
        assert result["metadatas"][0]["source_file"] == "test1.pdf"
        assert result["metadatas"][2]["source_file"] == "test2.pdf"

    def test_add_chunks_with_batching(self, tmpdir):
        """Test adding many chunks with batching."""
        store = VectorStore(db_path=tmpdir)

        # Create more chunks than the default batch size
        chunks = [
            PDFChunk(text=f"Test chunk number {i}", source_file="test.pdf") for i in range(150)
        ]

        # Add chunks with small batch size
        store.add_chunks(chunks, batch_size=50)

        # Verify all chunks were added
        collection = store.get_or_create_collection()
        result = collection.get()

        assert len(result["ids"]) == 150
        assert len(result["documents"]) == 150

    def test_clear(self, tmpdir):
        """Test clearing the vector store."""
        store = VectorStore(db_path=tmpdir)

        chunks = [
            PDFChunk(text="Sample text to be cleared.", source_file="test.pdf"),
            PDFChunk(text="Another sample to be cleared.", source_file="test.pdf"),
        ]
        store.add_chunks(chunks)

        collection = store.get_or_create_collection()
        result = collection.get()
        assert len(result["ids"]) == 2

        store.clear()

        collection = store.get_or_create_collection()
        result = collection.get()
        assert len(result["ids"]) == 0

    def test_clear_nonexistent_collection(self, tmpdir):
        """Test that clearing a nonexistent collection doesn't raise an error."""
        store = VectorStore(db_path=tmpdir)
        collection = store.clear()
        assert collection is not None

    def test_count(self, tmpdir):
        """Test counting the number of documents in the collection."""
        store = VectorStore(db_path=tmpdir)
        assert store.count() == 0

        chunks = [
            PDFChunk(text="Count test chunk 1", source_file="test.pdf"),
            PDFChunk(text="Count test chunk 2", source_file="test.pdf"),
        ]
        store.add_chunks(chunks)
        assert store.count() == 2

    def test_query(self, tmpdir):
        """Test querying the vector store."""
        store = VectorStore(db_path=tmpdir)

        chunks = [
            PDFChunk(text="IoT devices are becoming more common.", source_file="test1.pdf"),
            PDFChunk(text="Sensors are crucial for IoT applications.", source_file="test2.pdf"),
            PDFChunk(text="This chunk is unrelated to IoT.", source_file="test3.pdf"),
        ]
        store.add_chunks(chunks)

        results = store.query(query_text="IoT", top_k=2)
        assert len(results) == 2
