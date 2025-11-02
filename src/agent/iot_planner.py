from .base_agent import create_iot_agent
from .tools.research_tool import research_tool
from .tools.iot_blueprint_generator import iot_blueprint_generator
from .tools.component_sourcing_tool import component_sourcing_tool
from .tools.power_battery_estimator import power_battery_estimator


def build_iot_planner():
    """Build the full IoT Planner Agent with all tools"""
    tools = [
        research_tool,
        iot_blueprint_generator,
        component_sourcing_tool,
        power_battery_estimator,
    ]
    return create_iot_agent(tools)
