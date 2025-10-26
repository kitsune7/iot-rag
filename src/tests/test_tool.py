"""Unit tests for the rag_query function in the iot_rag.tool module."""

from iot_rag.tool import rag_query


def test_tool(tmpdir):
    """Test the rag_query function to ensure it returns results from the vector store."""
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
