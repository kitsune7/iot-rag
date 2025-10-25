import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


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


def get_text_chunks(text, chunk_size=1000, chunk_overlap=200):
    """
    Splits the extracted text into smaller chunks for processing.

    Args:
        text (str): The full text to be split.
        chunk_size (int): The maximum size of each chunk.
        chunk_overlap (int): The number of characters to overlap between chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "\u200b",  # Zero-width space
            "\uff0c",  # Fullwidth comma
            "\u3001",  # Ideographic comma
            "\uff0e",  # Fullwidth full stop
            "\u3002",  # Ideographic full stop
            "",
        ],
    )
    return text_splitter.split_text(_clean_text(text))


def _clean_text(text):
    # Remove page numbers (common pattern)
    text = re.sub(r"\n\d+\n", "", text)

    # Remove headers/footers if they repeat
    text = re.sub(r"Copyright.*?\n", "", text)

    # Remove special characters that add no value
    text = re.sub(r"[^\w\s\.\,\;\:\!\?\-\(\)]", "", text)

    # Fix hyphenated words at line breaks
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    return text.strip()
