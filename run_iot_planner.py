#!/usr/bin/env python3
"""
Script to run the IoT Planner Agent as a one-shot query processor
"""

import sys
import os
import argparse
import re
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.iot_planner import build_iot_planner
from langchain_core.messages import HumanMessage

def process_query(agent, query):
    """Process a single query with the agent and return the response"""
    try:
        print("🔍 Searching IoT research database...")
        
        # Invoke the agent with the user input wrapped in proper state format
        response = agent.invoke({"messages": [HumanMessage(content=query)]})
        
        # Extract the response content
        if hasattr(response, 'get') and 'messages' in response:
            # Get the last message from the agent
            agent_messages = response['messages']
            if agent_messages:
                last_message = agent_messages[-1]
                if hasattr(last_message, 'content'):
                    content = last_message.content
                    # Handle the case where content is a list of dictionaries with 'text' field
                    if isinstance(content, list) and len(content) > 0:
                        # Extract just the text content, ignoring extras
                        if isinstance(content[0], dict) and 'text' in content[0]:
                            return content[0]['text']
                        else:
                            return str(content[0])
                    elif isinstance(content, str):
                        return content
                    else:
                        return str(content)
                else:
                    return str(last_message)
            else:
                return "[No response generated]"
        else:
            return str(response)
            
    except Exception as e:
        return f"❌ Error processing query: {e}"

def save_response_to_markdown(query, response):
    """Save the agent response to a markdown file in the temp directory"""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate filename based on query
        # Clean the query to make it filename-safe
        clean_query = re.sub(r'[^\w\s-]', '', query).strip()
        clean_query = re.sub(r'[-\s]+', '_', clean_query)
        # Limit filename length
        if len(clean_query) > 50:
            clean_query = clean_query[:50]
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_query}_{timestamp}.md"
        
        # Full file path
        file_path = os.path.join(temp_dir, filename)
        
        # Create markdown content
        markdown_content = f"""# IoT Planner Response

**Query:** {query}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{response}
"""
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"💾 Response saved to: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"⚠️ Warning: Could not save response to file: {e}")
        return None

def main():
    """Run the IoT Planner Agent as a one-shot query processor"""
    parser = argparse.ArgumentParser(
        description="IoT Planner Agent - Research-powered IoT recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_iot_planner.py "What sensors are best for smart agriculture?"
  python run_iot_planner.py "How to implement automatic door systems?"
  python run_iot_planner.py --query "temperature monitoring in greenhouses"
        """
    )
    
    parser.add_argument(
        'query', 
        nargs='?', 
        help='The IoT question or query to process'
    )
    parser.add_argument(
        '--query', '-q',
        dest='query_flag',
        help='Alternative way to specify the query'
    )
    
    args = parser.parse_args()
    
    # Get the query from command line arguments or prompt user
    query = args.query or args.query_flag
    
    if not query:
        print("🤖 IoT Planner Agent - One-Shot Mode")
        print("=" * 50)
        print("💡 Be specific about your IoT domain for better research results.")
        print("📖 Example: 'temperature sensors for greenhouse monitoring' vs 'temperature sensors'\n")
        
        query = input("🙋 Enter your IoT question: ").strip()
        
        if not query:
            print("❌ No query provided. Exiting.")
            return 1
    
    try:
        print(f"\n🤖 Processing query: {query}")
        print("=" * 50)
        
        # Build the agent
        agent = build_iot_planner()
        
        # Process the query
        response = process_query(agent, query)
        
        # Display the response
        print(f"\n🤖 IoT Planner Response:")
        print(response)
        
        # Save response to markdown file
        save_response_to_markdown(query, response)
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to initialize IoT Planner Agent: {e}")
        print("Make sure you have:")
        print("- Set up your GEMINI_API_KEY in .env file")
        print("- Installed all required dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())
