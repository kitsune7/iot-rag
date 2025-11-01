"""Unit tests for the rag_query function in the rag.tool module."""

from rag.tool import rag_query
from rag.parser import PDFChunk


def test_tool(tmpdir, monkeypatch):
    """Test the rag_query function to ensure it returns results from the vector store."""

    # Mock os.listdir to return only a couple fake PDF files
    def mock_listdir(path):
        return ["iot_basics.pdf", "sensors.pdf"]

    # Mock extract_text_from_pdf to return text immediately
    def mock_extract_text(pdf_path):
        return "IoT refers to Internet of Things. Sensors collect data from devices."

    # Mock get_text_chunks to return pre-defined PDFChunk objects
    def mock_get_chunks(pdf_text, source_file, chunk_size=1000, chunk_overlap=200):
        return [
            PDFChunk(text="IoT refers to Internet of Things.", source_file=source_file),
            PDFChunk(text="Sensors collect data from devices.", source_file=source_file),
        ]

    monkeypatch.setattr("os.listdir", mock_listdir)
    monkeypatch.setattr("rag.tool.extract_text_from_pdf", mock_extract_text)
    monkeypatch.setattr("rag.tool.get_text_chunks", mock_get_chunks)

    query_text = "What is IoT?"
    results = rag_query(query_text=query_text, top_k=2, verbose=True, db_path=tmpdir)

    # Check that results are returned
    assert len(results) > 0, "Expected results from the vector store, but got none."

    # Check that each result has the expected structure
    for result in results:
        assert hasattr(result, "id"), "Result should have an 'id' attribute."
        assert hasattr(result, "document"), "Result should have a 'document' attribute."
        assert hasattr(result.metadata, "source_file"), (
            "Result metadata should have a 'source_file' attribute."
        )
