"""
Evaluation tracking system for IoT Planner Agent performance monitoring.
"""

import time
import json
import sys
from datetime import datetime
from collections import defaultdict
from langchain_core.callbacks import BaseCallbackHandler

from rag.vector_store import QueryResult


class EvaluationTracker:
    """Class to track agent evaluation metrics"""

    def __init__(self):
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "total_runtime": 0,
            "tool_runtimes": {},
            "tool_calls": [],
            "rag_queries": [],
            "rag_chunks_retrieved": 0,
            "tokens_used": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "error_count": 0,
            "errors": [],
        }

    def start_tracking(self):
        """Start tracking execution time"""
        self.metrics["start_time"] = time.time()

    def end_tracking(self):
        """End tracking and calculate total runtime"""
        self.metrics["end_time"] = time.time()
        if self.metrics["start_time"]:
            self.metrics["total_runtime"] = self.metrics["end_time"] - self.metrics["start_time"]

    def track_tool_call(self, tool_name, start_time, end_time, result=None):
        """Track individual tool call metrics"""
        runtime = end_time - start_time

        if tool_name not in self.metrics["tool_runtimes"]:
            self.metrics["tool_runtimes"][tool_name] = []
        self.metrics["tool_runtimes"][tool_name].append(runtime)

        call_info = {
            "tool": tool_name,
            "start_time": start_time,
            "end_time": end_time,
            "runtime": runtime,
            "timestamp": datetime.fromtimestamp(start_time).isoformat(),
        }

        self.metrics["tool_calls"].append(call_info)

    def track_error(self, error):
        """Track errors that occur during execution"""
        self.metrics["error_count"] += 1
        self.metrics["errors"].append(
            {"error": str(error), "timestamp": datetime.now().isoformat()}
        )

    def get_summary(self):
        """Get a summary of evaluation metrics"""
        # Calculate average tool runtimes
        avg_tool_runtimes = {}
        for tool, runtimes in self.metrics["tool_runtimes"].items():
            avg_tool_runtimes[tool] = {
                "average_runtime": sum(runtimes) / len(runtimes),
                "min_runtime": min(runtimes),
                "max_runtime": max(runtimes),
                "call_count": len(runtimes),
                "total_runtime": sum(runtimes),
            }

        return {
            "execution_summary": {
                "total_runtime_seconds": round(self.metrics["total_runtime"], 3),
                "start_time": datetime.fromtimestamp(self.metrics["start_time"]).isoformat()
                if self.metrics["start_time"]
                else None,
                "end_time": datetime.fromtimestamp(self.metrics["end_time"]).isoformat()
                if self.metrics["end_time"]
                else None,
            },
            "tool_performance": avg_tool_runtimes,
            "rag_performance": {
                "total_queries": len(self.metrics["rag_queries"]),
                "queries": self.metrics["rag_queries"],
                "total_chunks_retrieved": self.metrics["rag_chunks_retrieved"],
                "average_chunks_per_query": self.metrics["rag_chunks_retrieved"]
                / max(len(self.metrics["rag_queries"]), 1),
            },
            "token_usage": self.metrics["tokens_used"],
            "errors": {
                "error_count": self.metrics["error_count"],
                "errors": self.metrics["errors"],
            },
            "detailed_tool_calls": self.metrics["tool_calls"],
        }


class EvaluationCallbackHandler(BaseCallbackHandler):
    """Callback handler to track agent evaluation metrics"""

    def __init__(self, evaluation_tracker):
        super().__init__()
        self.tracker = evaluation_tracker
        self.tool_call_stack = []  # Stack to handle multiple concurrent tool calls

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when a tool starts running"""
        tool_name = serialized.get("name", "unknown_tool")

        # Try to extract query from various sources
        rag_query = None

        # Method 1: Check if input_str is a dict (direct dict)
        if isinstance(input_str, dict):
            rag_query = input_str.get("query", "")

        # Method 2: Check if input_str is a string representation of a dict
        elif isinstance(input_str, str) and "{" in input_str:
            try:
                # Try to parse as JSON first
                import ast
                parsed_input = ast.literal_eval(input_str)
                if isinstance(parsed_input, dict):
                    rag_query = parsed_input.get("query", "")
            except (ValueError, SyntaxError):
                pass

        # Method 3: Check kwargs inputs
        if not rag_query and "inputs" in kwargs:
            inputs = kwargs["inputs"]
            if isinstance(inputs, dict):
                rag_query = inputs.get("query", "")

        if rag_query and tool_name == "research_tool":
            self.tracker.metrics["rag_queries"].append(rag_query)

        start_time = time.time()

        # Push to stack to handle concurrent/nested tool calls
        call_info = {"tool_name": tool_name, "start_time": start_time, "input": input_str}
        self.tool_call_stack.append(call_info)

        # Log tool start
        print(f"🔧 Starting tool: {tool_name}")

    def on_tool_end(self, output, **kwargs):
        """Called when a tool finishes running"""
        if not self.tool_call_stack:
            return

        # Pop the most recent tool call
        call_info = self.tool_call_stack.pop()
        tool_name = call_info["tool_name"]
        start_time = call_info["start_time"]
        end_time = time.time()

        # Track the tool call
        self.tracker.track_tool_call(tool_name, start_time, end_time, output)

        # Special handling for research_tool to extract RAG queries
        if tool_name == "research_tool" and output:
            try:
                output_str = None

                # Extract string content from different output types
                if isinstance(output, str):
                    output_str = output
                elif hasattr(output, "content"):
                    # Handle ToolMessage or other message types
                    output_str = output.content

                if output_str:
                    rag_data = json.loads(output_str)
                    # Extract results array from the JSON structure
                    results = rag_data.get("results", [])
                    num_results = len(results)
                    self.tracker.metrics["rag_chunks_retrieved"] += num_results
            except (json.JSONDecodeError, TypeError, AttributeError):
                # If parsing fails, just continue
                pass

        print(f"✅ {tool_name} ({end_time - start_time:.2f}s)")

    def on_tool_error(self, error, **kwargs):
        """Called when a tool encounters an error"""
        # Track the error
        self.tracker.track_error(f"Tool error: {error}")

        # Clean up the most recent tool call
        if self.tool_call_stack:
            call_info = self.tool_call_stack.pop()
            tool_name = call_info["tool_name"]
            start_time = call_info["start_time"]
            end_time = time.time()
            self.tracker.track_tool_call(tool_name, start_time, end_time)

        print(f"❌ Tool error: {error}")

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when the LLM starts processing"""
        print("🤖 LLM processing...")

    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes - extract accurate token usage from response"""
        try:
            # Try to extract usage metadata from the LLM response
            # This is model-specific, but most modern LLMs provide this info
            if hasattr(response, "llm_output") and response.llm_output:
                usage = response.llm_output.get("token_usage", {})
                if usage:
                    # Accumulate tokens (multiple LLM calls may occur)
                    self.tracker.metrics["tokens_used"]["input_tokens"] += usage.get(
                        "prompt_tokens", 0
                    )
                    self.tracker.metrics["tokens_used"]["output_tokens"] += usage.get(
                        "completion_tokens", 0
                    )
                    self.tracker.metrics["tokens_used"]["total_tokens"] = (
                        self.tracker.metrics["tokens_used"]["input_tokens"]
                        + self.tracker.metrics["tokens_used"]["output_tokens"]
                    )
        except Exception as e:
            # If token extraction fails, continue without erroring
            pass
