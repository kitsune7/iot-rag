import tempfile
import shutil
from pathlib import Path
import pytest

from iot_rag.vector_store import VectorStore
from iot_rag.parser import PDFChunk


class TestVectorStore:
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up a temporary directory for testing and clean up after."""
        self.temp_dir = tempfile.mkdtemp()
        yield
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_vector_store_initialization(self):
        """Test that VectorStore initializes correctly."""
        store = VectorStore(db_path=self.temp_dir)
        assert store is not None
        assert store.client is not None
        assert store.collection_name == "iot"

    def test_get_or_create_collection(self):
        """Test that get_or_create_collection creates and retrieves a collection."""
        store = VectorStore(db_path=self.temp_dir)
        collection = store.get_or_create_collection()

        assert collection is not None
        assert collection.name == "iot"

        # Verify we can retrieve the same collection
        collection2 = store.get_or_create_collection()
        assert collection2.name == collection.name

    def test_add_chunks(self):
        """Test adding chunks to the vector store."""
        store = VectorStore(db_path=self.temp_dir)

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

    def test_add_chunks_with_batching(self):
        """Test adding many chunks with batching."""
        store = VectorStore(db_path=self.temp_dir)

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

    def test_clear(self):
        """Test clearing the vector store."""
        store = VectorStore(db_path=self.temp_dir)

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

    def test_clear_nonexistent_collection(self):
        """Test that clearing a nonexistent collection doesn't raise an error."""
        store = VectorStore(db_path=self.temp_dir)
        collection = store.clear()
        assert collection is not None
