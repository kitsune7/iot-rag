from langchain.tools import tool
from typing import Optional, Literal
import chromadb
import json

# Initialize Chroma persistent client (do this once, outside the tool)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="iot",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)

@tool
def search_iot_research(
    query: str,
    max_results: int = 5,
) -> str:
    """
    PRIMARY RESEARCH TOOL: Search through IoT research papers for evidence-based information.
    
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
    
    try:
        # Check if collection has any documents
        count = collection.count()
        if count == 0:
            return json.dumps({
                "query": query,
                "num_results": 0,
                "results": [],
                "message": "No documents found in the IoT collection. Please ensure the database is populated.",
                "guidance": "Cannot provide research-based recommendations without access to the research database."
            }, indent=2)
        
        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=min(max_results, count),
            include=["documents", "metadatas", "distances"]
        )
        
        # Process results
        formatted_results = []
        seen_sources = set()
        
        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
            distances = results["distances"][0] if results["distances"] else [0] * len(documents)
            
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                source = metadata.get("source", f"Document_{i}")
                if source in seen_sources:
                    continue
                seen_sources.add(source)
                
                formatted_results.append({
                    "content": doc[:500] + "..." if len(doc) > 500 else doc,  # Truncate long content
                    "source": source,
                    "authors": metadata.get("authors", []),
                    "year": metadata.get("year", "Unknown"),
                    "section": metadata.get("section", "Unknown"),
                    "relevance_score": 1 - distance,  # Convert distance to similarity score
                    "page": metadata.get("page", None)
                })
        
        # Return as formatted JSON string
        response = {
            "query": query,
            "num_results": len(formatted_results),
            "results": formatted_results,
            "guidance": "Base your response primarily on the research findings above. If no relevant results were found, acknowledge this limitation and suggest more specific search terms."
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "query": query,
            "num_results": 0,
            "results": [],
            "error": f"Error querying database: {str(e)}",
            "guidance": "Cannot provide research-based recommendations due to database error."
        }, indent=2)
