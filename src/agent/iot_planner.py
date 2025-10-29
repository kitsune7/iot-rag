# src/agent/iot_planner.py
from src.agent.base_agent import create_iot_agent
from src.agent.tools.research_tool import search_iot_research

def build_iot_planner():
    """Build the full IoT Planner Agent with all tools"""
    tools = [
        search_iot_research
    ]
    return create_iot_agent(tools)