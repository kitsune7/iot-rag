import pymupdf
import re
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class PDFChunk:
    """
    Represents a chunk of text extracted from a document, along with its source information.
    """

    text: str
    source_file: str = ""


def extract_text_from_pdf(pdf_path: str):
    """
    Extracts text from a PDF file.
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


def get_text_chunks(pdf_text: str, source_file: str, chunk_size=1000, chunk_overlap=200):
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
    text_chunks = text_splitter.split_text(_clean_text(pdf_text))
    return [PDFChunk(text=text, source_file=source_file) for text in text_chunks]


def _clean_text(text: str):
    # Remove page numbers (common pattern)
    text = re.sub(r"\n\d+\n", "", text)

    # Remove headers/footers if they repeat
    text = re.sub(r"Copyright.*?\n", "", text)

    # Remove special characters that add no value
    text = re.sub(r"[^\w\s\.\,\;\:\!\?\-\(\)]", "", text)

    # Fix hyphenated words at line breaks
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    return text.strip()
