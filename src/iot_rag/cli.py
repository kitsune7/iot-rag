import sys
from .assets import extract_text_from_pdf, get_text_chunks


def main():
    pdf_text = extract_text_from_pdf("assets/Study of Iot.pdf")
    chunks = get_text_chunks(pdf_text)
    print(chunks[0])


if __name__ == "__main__":
    sys.exit(main())
