from iot_rag.assets import extract_text_from_pdf


class TestAssets:
    def test_extract_text_from_pdf(self):
        text = extract_text_from_pdf("assets/Intro to IoT.pdf")
        assert text is not None
        assert "Internet of Things" in text
        assert "IoT" in text
