import argparse
import sys
from .tool import rag_query


def pretty_print_query_result(results):
    """Pretty print the results of a query."""
    for result in results:
        print(f"*** {result.metadata.source_file} ***")
        print(result.document)
        print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description="IoT RAG CLI - Extract text from PDF and create text chunks for vector storage."
    )
    parser.add_argument(
        "query",
        type=str,
        help="The query text to search for in the vector store.",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="The number of top results to return from the vector store query.",
    )
    parser.add_argument(
        "--verbose",
        type=bool,
        default=False,
        help="Enable verbose output for debugging purposes.",
    )
    args = parser.parse_args()
    results = rag_query(args.query, args.top_k, args.verbose)
    pretty_print_query_result(results)


if __name__ == "__main__":
    sys.exit(main())
