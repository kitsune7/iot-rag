import os
import re
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from evaluation.evaluation_tracker import EvaluationTracker, EvaluationCallbackHandler
from evaluation.evaluation_utils import save_evaluation_results, display_performance_summary


from .iot_planner import build_iot_planner


def run_agent(query: str):
    agent = build_iot_planner()
    response, evaluation_summary = process_query(agent, query)

    print(f"\n🤖 IoT Planner Response:")
    print(response)

    script_dir = os.path.dirname(__file__)
    response_filename = save_response_to_markdown(query, response)

    save_evaluation_results(query, evaluation_summary, response_filename, script_dir)
    display_performance_summary(evaluation_summary)


def process_query(agent, query) -> str:
    """Process a single query with the agent and return the response and evaluation metrics"""
    tracker = EvaluationTracker()
    tracker.start_tracking()

    callback_handler = EvaluationCallbackHandler(tracker)

    try:
        print("🔍 Searching IoT research database...")

        response = agent.invoke(
            {"messages": [HumanMessage(content=query)]}, config={"callbacks": [callback_handler]}
        )

        if hasattr(response, "get") and "messages" in response:
            agent_messages = response["messages"]
            if agent_messages:
                last_message = agent_messages[-1]
                if hasattr(last_message, "content"):
                    content = last_message.content

                    # Handle the case where content is a list of dictionaries with 'text' field
                    if isinstance(content, list) and len(content) > 0:
                        # Extract just the text content, ignoring extras
                        if isinstance(content[0], dict) and "text" in content[0]:
                            text_response = content[0]["text"]
                        else:
                            text_response = str(content[0])
                    elif isinstance(content, str):
                        text_response = content
                    else:
                        text_response = str(content)

                    # Extract token usage metadata from AIMessage if available
                    if isinstance(last_message, AIMessage) and hasattr(last_message, "usage_metadata"):
                        usage_metadata = last_message.usage_metadata
                        if usage_metadata:
                            tracker.metrics["tokens_used"]["input_tokens"] = (
                                usage_metadata.get("input_tokens", 0)
                            )
                            tracker.metrics["tokens_used"]["output_tokens"] = (
                                usage_metadata.get("output_tokens", 0)
                            )
                else:
                    text_response = str(last_message)
            else:
                text_response = "[No response generated]"
        else:
            text_response = str(response)

        tracker.metrics["tokens_used"]["total_tokens"] = (
            tracker.metrics["tokens_used"]["input_tokens"]
            + tracker.metrics["tokens_used"]["output_tokens"]
        )
        tracker.end_tracking()

        return text_response, tracker.get_summary()
    except Exception as e:
        tracker.track_error(e)
        tracker.end_tracking()
        error_response = f"❌ Error processing query: {e}"
        return error_response, tracker.get_summary()


def save_response_to_markdown(query: str, response):
    """Save the agent response to a markdown file in the temp directory"""
    try:
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(__file__), "../../results")
        os.makedirs(results_dir, exist_ok=True)

        # Generate filename based on query
        # Clean the query to make it filename-safe
        clean_query = re.sub(r"[^\w\s-]", "", query).strip()
        clean_query = re.sub(r"[-\s]+", "_", clean_query)

        max_filename_length = 50
        if len(clean_query) > max_filename_length:
            clean_query = clean_query[:max_filename_length]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_query}_{timestamp}.md"
        file_path = os.path.join(results_dir, filename)

        markdown_content = f"""# IoT Planner Response

**Query:** {query}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{response}
"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"\n💾 Response saved to: {os.path.normpath(file_path)}")
        return filename

    except Exception as e:
        print(f"\n⚠️ Warning: Could not save response to file: {e}")
        return None
