import sys
from .assets import extract_text_from_pdf


def main():
    print(extract_text_from_pdf("assets/Study of Iot.pdf"))


if __name__ == "__main__":
    sys.exit(main())
