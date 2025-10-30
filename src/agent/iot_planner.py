# src/agent/iot_planner.py
from src.agent.base_agent import create_iot_agent
from src.agent.tools.research_tool import search_iot_research
from src.agent.tools.iot_blueprint_generator import iot_blueprint_generator
from src.agent.tools.component_sourcing_tool import component_sourcing_tool
from src.agent.tools.power_battery_estimator import power_battery_estimator

def build_iot_planner():
    """Build the full IoT Planner Agent with all tools"""
    tools = [
        search_iot_research,
        iot_blueprint_generator,
        component_sourcing_tool,
        power_battery_estimator
    ]
    return create_iot_agent(tools)