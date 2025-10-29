#!/usr/bin/env python3
"""
Script to run the IoT Planner Agent interactively
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.iot_planner import build_iot_planner
from langchain_core.messages import HumanMessage

def main():
    """Run the IoT Planner Agent interactively"""
    print("🤖 IoT Planner Agent Starting...")
    print("=" * 50)
    
    try:
        # Build the agent
        agent = build_iot_planner()
        
        print("✅ Research-Powered IoT Planner Agent initialized successfully!")
        print("� This agent bases ALL recommendations on IoT research papers in the database.")
        print("� For every question, the agent will search research first before responding.")
        print("💡 Be specific about your IoT domain for better research results.")
        print("📖 Example: 'temperature sensors for greenhouse monitoring' vs 'temperature sensors'")
        print("Type 'quit', 'exit', or 'bye' to stop the agent.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("🙋 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', '']:
                    print("👋 Goodbye!")
                    break
                
                # Process the query with the agent
                print("\n🔍 Searching IoT research database...")
                # Invoke the agent with the user input wrapped in proper state format
                response = agent.invoke({"messages": [HumanMessage(content=user_input)]})
                
                # Extract the response content
                if hasattr(response, 'get') and 'messages' in response:
                    # Get the last message from the agent
                    agent_messages = response['messages']
                    if agent_messages:
                        last_message = agent_messages[-1]
                        if hasattr(last_message, 'content'):
                            print(f"🤖 IoT Planner: {last_message.content}")
                        else:
                            print(f"🤖 IoT Planner: {last_message}")
                    else:
                        print("🤖 IoT Planner: [No response generated]")
                else:
                    print(f"🤖 IoT Planner: {response}")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again.")
                
    except Exception as e:
        print(f"❌ Failed to initialize IoT Planner Agent: {e}")
        print("Make sure you have:")
        print("- Set up your GEMINI_API_KEY in .env file")
        print("- Installed all required dependencies")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())