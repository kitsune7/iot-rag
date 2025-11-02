from langchain.tools import tool
from typing import Optional, Literal
import chromadb
import json

from rag.tool import rag_query


@tool
def research_tool(
    query: str,
    max_results: int = 5,
) -> str:
    """
    Research Tool: Search through IoT research papers for evidence-based information.

    This is your MAIN source of IoT knowledge. Always use this tool FIRST when users ask about:
    - IoT technologies, architectures, or implementations
    - Sensor types, specifications, or applications
    - IoT security, protocols, or standards
    - Smart city, industrial IoT, or agricultural IoT projects
    - Edge computing, cloud integration, or data processing
    - Any technical IoT planning or design questions

    Args:
        query: The research question or topic to search for. Use specific IoT terms for best results.
               Examples: "humidity sensors greenhouse", "LoRaWAN industrial applications",
               "edge computing smart cities", "IoT security protocols"
        max_results: Number of results to return (1-10). More results provide broader context.

    Returns:
        JSON string with research-backed information including:
        - Relevant paper excerpts and technical details
        - Source citations and metadata (authors, year, section)
        - Relevance scores to help prioritize information

    IMPORTANT: Base your IoT recommendations primarily on the content returned by this tool.
    """

    results = rag_query(query, max_results)

    # Serialize QueryResult objects to JSON for LangChain compatibility and evaluation tracking
    serialized_results = [
        {
            "id": r.id,
            "document": r.document,
            "source_file": r.metadata.source_file,
        }
        for r in results
    ]

    return json.dumps({
        "query": query,
        "num_results": len(serialized_results),
        "results": serialized_results,
    }, indent=2)
