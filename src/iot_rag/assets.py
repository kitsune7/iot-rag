import pymupdf


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.
    """

    try:
        doc = pymupdf.open(pdf_path)
        full_text = ""
        for page in doc:
            text = page.get_text()
            full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"An error occurred while extracting text from the PDF: {e}")
        return None
