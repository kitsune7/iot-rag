"""
Evaluation utilities for saving and managing IoT Planner Agent evaluation results.
"""

import os
import re
import json
import sys
from datetime import datetime


def save_evaluation_results(query, evaluation_summary, base_filename, script_dir):
    """Save evaluation results to a JSON file in temp/evaluation_results"""
    try:
        # Create evaluation results directory if it doesn't exist
        eval_dir = os.path.join(script_dir, 'temp', 'evaluation_results')
        os.makedirs(eval_dir, exist_ok=True)
        
        # Use the same base filename as the response, but with .json extension
        if base_filename:
            eval_filename = base_filename.replace('.md', '.json')
        else:
            # Fallback filename generation
            clean_query = re.sub(r'[^\w\s-]', '', query).strip()
            clean_query = re.sub(r'[-\s]+', '_', clean_query)
            if len(clean_query) > 50:
                clean_query = clean_query[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            eval_filename = f"{clean_query}_{timestamp}.json"
        
        # Full file path
        eval_file_path = os.path.join(eval_dir, eval_filename)
        
        # Create comprehensive evaluation data
        evaluation_data = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'evaluation_summary': evaluation_summary,
            'metadata': {
                'evaluator_version': '1.0',
                'python_version': sys.version,
                'evaluation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Write to JSON file
        with open(eval_file_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation_data, f, indent=2, default=str)
        
        print(f"📊 Evaluation results saved to: {eval_file_path}")
        return eval_file_path
        
    except Exception as e:
        print(f"⚠️ Warning: Could not save evaluation results: {e}")
        return None


def display_performance_summary(evaluation_summary):
    """Display key performance metrics in a user-friendly format"""
    if not evaluation_summary:
        return
        
    exec_summary = evaluation_summary.get('execution_summary', {})
    tool_perf = evaluation_summary.get('tool_performance', {})
    rag_perf = evaluation_summary.get('rag_performance', {})
    token_usage = evaluation_summary.get('token_usage', {})
    
    print(f"\n📊 Performance Summary:")
    print(f"   ⏱️  Total Runtime: {exec_summary.get('total_runtime_seconds', 0):.2f} seconds")
    print(f"   🔧 Tools Used: {len(tool_perf)} ({', '.join(tool_perf.keys())})")
    print(f"   🔍 RAG Queries: {rag_perf.get('total_queries', 0)}")
    print(f"   📄 Chunks Retrieved: {rag_perf.get('total_chunks_retrieved', 0)}")
    print(f"   🎯 Tokens Used: {token_usage.get('total_tokens', 0)} (in: {token_usage.get('input_tokens', 0)}, out: {token_usage.get('output_tokens', 0)})")
    
    # Show any errors
    errors = evaluation_summary.get('errors', {})
    if errors.get('error_count', 0) > 0:
        print(f"   ❌ Errors: {errors.get('error_count', 0)}")