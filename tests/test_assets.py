from iot_rag.assets import extract_text_from_pdf, get_text_chunks


class TestAssets:
    def test_extract_text_from_pdf(self):
        text = extract_text_from_pdf("assets/Intro to IoT.pdf")

        assert text is not None
        assert "Internet of Things" in text
        assert "IoT" in text

    def test_get_text_chunks(self):
        chunk_size = 500
        chunk_overlap = 100

        text = extract_text_from_pdf("assets/Intro to IoT.pdf")
        chunks = get_text_chunks(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, str)
            assert len(chunk) <= 500
