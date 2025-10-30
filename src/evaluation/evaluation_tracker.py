"""
Evaluation tracking system for IoT Planner Agent performance monitoring.
"""

import time
import json
import sys
from datetime import datetime
from collections import defaultdict
from langchain_core.callbacks import BaseCallbackHandler


class EvaluationTracker:
    """Class to track agent evaluation metrics"""
    
    def __init__(self):
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'total_runtime': 0,
            'tool_runtimes': {},
            'tool_calls': [],
            'rag_queries': [],
            'rag_chunks_retrieved': 0,
            'tokens_used': {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0
            },
            'error_count': 0,
            'errors': []
        }
    
    def start_tracking(self):
        """Start tracking execution time"""
        self.metrics['start_time'] = time.time()
    
    def end_tracking(self):
        """End tracking and calculate total runtime"""
        self.metrics['end_time'] = time.time()
        if self.metrics['start_time']:
            self.metrics['total_runtime'] = self.metrics['end_time'] - self.metrics['start_time']
    
    def track_tool_call(self, tool_name, start_time, end_time, result=None):
        """Track individual tool call metrics"""
        runtime = end_time - start_time
        
        # Add to tool runtimes
        if tool_name not in self.metrics['tool_runtimes']:
            self.metrics['tool_runtimes'][tool_name] = []
        self.metrics['tool_runtimes'][tool_name].append(runtime)
        
        # Add to tool calls log
        call_info = {
            'tool': tool_name,
            'start_time': start_time,
            'end_time': end_time,
            'runtime': runtime,
            'timestamp': datetime.fromtimestamp(start_time).isoformat()
        }
        
        # Track specific metrics for RAG tool
        if tool_name == 'search_iot_research' and result:
            try:
                # Try to parse RAG result if it's JSON
                if isinstance(result, str):
                    rag_data = json.loads(result)
                    call_info['rag_query'] = rag_data.get('query', '')
                    call_info['chunks_retrieved'] = rag_data.get('num_results', 0)
                    call_info['rag_results'] = rag_data.get('results', [])
                    
                    # Add to global metrics
                    self.metrics['rag_queries'].append(rag_data.get('query', ''))
                    self.metrics['rag_chunks_retrieved'] += rag_data.get('num_results', 0)
            except (json.JSONDecodeError, AttributeError):
                pass
        
        self.metrics['tool_calls'].append(call_info)
    
    def track_error(self, error):
        """Track errors that occur during execution"""
        self.metrics['error_count'] += 1
        self.metrics['errors'].append({
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
    
    def estimate_tokens(self, text):
        """Rough estimation of tokens (approximately 4 characters per token)"""
        if isinstance(text, str):
            return len(text) // 4
        return 0
    
    def get_summary(self):
        """Get a summary of evaluation metrics"""
        # Calculate average tool runtimes
        avg_tool_runtimes = {}
        for tool, runtimes in self.metrics['tool_runtimes'].items():
            avg_tool_runtimes[tool] = {
                'average_runtime': sum(runtimes) / len(runtimes),
                'min_runtime': min(runtimes),
                'max_runtime': max(runtimes),
                'call_count': len(runtimes),
                'total_runtime': sum(runtimes)
            }
        
        return {
            'execution_summary': {
                'total_runtime_seconds': round(self.metrics['total_runtime'], 3),
                'start_time': datetime.fromtimestamp(self.metrics['start_time']).isoformat() if self.metrics['start_time'] else None,
                'end_time': datetime.fromtimestamp(self.metrics['end_time']).isoformat() if self.metrics['end_time'] else None,
            },
            'tool_performance': avg_tool_runtimes,
            'rag_performance': {
                'total_queries': len(self.metrics['rag_queries']),
                'queries': self.metrics['rag_queries'],
                'total_chunks_retrieved': self.metrics['rag_chunks_retrieved'],
                'average_chunks_per_query': self.metrics['rag_chunks_retrieved'] / max(len(self.metrics['rag_queries']), 1)
            },
            'token_usage': self.metrics['tokens_used'],
            'errors': {
                'error_count': self.metrics['error_count'],
                'errors': self.metrics['errors']
            },
            'detailed_tool_calls': self.metrics['tool_calls']
        }


class EvaluationCallbackHandler(BaseCallbackHandler):
    """Callback handler to track agent evaluation metrics"""
    
    def __init__(self, evaluation_tracker):
        super().__init__()
        self.tracker = evaluation_tracker
        self.tool_call_stack = []  # Stack to handle multiple concurrent tool calls
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when a tool starts running"""
        tool_name = serialized.get('name', 'unknown_tool')
        start_time = time.time()
        
        # Push to stack to handle concurrent/nested tool calls
        call_info = {
            'tool_name': tool_name,
            'start_time': start_time,
            'input': input_str
        }
        self.tool_call_stack.append(call_info)
        
        # Log tool start
        print(f"🔧 Starting tool: {tool_name}")
    
    def on_tool_end(self, output, **kwargs):
        """Called when a tool finishes running"""
        if not self.tool_call_stack:
            return
            
        # Pop the most recent tool call
        call_info = self.tool_call_stack.pop()
        tool_name = call_info['tool_name']
        start_time = call_info['start_time']
        end_time = time.time()
        
        # Track the tool call
        self.tracker.track_tool_call(tool_name, start_time, end_time, output)
        
        # Special handling for search_iot_research tool to extract RAG queries
        if tool_name == 'search_iot_research' and output:
            try:
                # The research tool returns JSON string, let's parse it
                if isinstance(output, str):
                    rag_data = json.loads(output)
                    query = rag_data.get('query', '')
                    num_results = rag_data.get('num_results', 0)
                    
                    # Add to RAG tracking
                    if query:
                        self.tracker.metrics['rag_queries'].append(query)
                    self.tracker.metrics['rag_chunks_retrieved'] += num_results
                    
                    print(f"🔍 RAG Query: '{query}' → {num_results} chunks")
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, just continue
                pass
        
        print(f"✅ Completed tool: {tool_name} ({end_time - start_time:.2f}s)")
    
    def on_tool_error(self, error, **kwargs):
        """Called when a tool encounters an error"""
        # Track the error
        self.tracker.track_error(f"Tool error: {error}")
        
        # Clean up the most recent tool call
        if self.tool_call_stack:
            call_info = self.tool_call_stack.pop()
            tool_name = call_info['tool_name']
            start_time = call_info['start_time']
            end_time = time.time()
            self.tracker.track_tool_call(tool_name, start_time, end_time)
            
        print(f"❌ Tool error: {error}")
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts"""
        # Estimate input tokens from prompts
        for prompt in prompts:
            if isinstance(prompt, str):
                self.tracker.metrics['tokens_used']['input_tokens'] += self.tracker.estimate_tokens(prompt)
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes"""
        # Estimate output tokens from response
        if hasattr(response, 'generations'):
            for generation in response.generations:
                for gen in generation:
                    if hasattr(gen, 'text'):
                        self.tracker.metrics['tokens_used']['output_tokens'] += self.tracker.estimate_tokens(gen.text)