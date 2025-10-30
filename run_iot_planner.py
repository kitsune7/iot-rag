#!/usr/bin/env python3
"""
Script to run the IoT Planner Agent as a one-shot query processor with evaluation tracking
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
from evaluation import EvaluationTracker, EvaluationCallbackHandler, save_evaluation_results, display_performance_summary

def process_query(agent, query):
    """Process a single query with the agent and return the response and evaluation metrics"""
    # Create evaluation tracker
    tracker = EvaluationTracker()
    tracker.start_tracking()
    
    # Create callback handler
    callback_handler = EvaluationCallbackHandler(tracker)
    
    try:
        print("🔍 Searching IoT research database...")
        
        # Estimate input tokens from query
        tracker.metrics['tokens_used']['input_tokens'] += tracker.estimate_tokens(query)
        
        # Invoke the agent with the callback handler
        response = agent.invoke(
            {"messages": [HumanMessage(content=query)]},
            config={"callbacks": [callback_handler]}
        )
        
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
                            text_response = content[0]['text']
                        else:
                            text_response = str(content[0])
                    elif isinstance(content, str):
                        text_response = content
                    else:
                        text_response = str(content)
                    
                    # Estimate output tokens
                    tracker.metrics['tokens_used']['output_tokens'] += tracker.estimate_tokens(text_response)
                else:
                    text_response = str(last_message)
            else:
                text_response = "[No response generated]"
        else:
            text_response = str(response)
        
        # Calculate total tokens
        tracker.metrics['tokens_used']['total_tokens'] = (
            tracker.metrics['tokens_used']['input_tokens'] + 
            tracker.metrics['tokens_used']['output_tokens']
        )
        
        # End tracking here to capture total runtime
        tracker.end_tracking()
        
        return text_response, tracker.get_summary()
            
    except Exception as e:
        tracker.track_error(e)
        tracker.end_tracking()  # End tracking even on error
        error_response = f"❌ Error processing query: {e}"
        return error_response, tracker.get_summary()

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
        return filename  # Return just the filename for use in evaluation saving
        
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
        
        # Process the query (now returns both response and evaluation metrics)
        response, evaluation_summary = process_query(agent, query)
        
        # Display the response
        print(f"\n🤖 IoT Planner Response:")
        print(response)
        
        # Save response to markdown file
        response_filename = save_response_to_markdown(query, response)
        
        # Save evaluation results
        script_dir = os.path.dirname(__file__)
        save_evaluation_results(query, evaluation_summary, response_filename, script_dir)
        
        # Display performance summary
        display_performance_summary(evaluation_summary)
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to initialize IoT Planner Agent: {e}")
        print("Make sure you have:")
        print("- Set up your GEMINI_API_KEY in .env file")
        print("- Installed all required dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())
