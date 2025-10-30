from langchain.tools import tool
from typing import Dict, Any
import json

@tool
def power_battery_estimator(components_json: str) -> str:
    """
    Power & Battery Estimator Tool: Estimates device power consumption and suggests suitable batteries
    based on component specifications.
    
    This tool calculates total power consumption, estimates daily energy usage, and recommends 
    appropriate battery types and sizes for IoT devices. Use this tool after getting component 
    specifications from the Component Sourcing Tool to plan power requirements.
    
    Args:
        components_json: JSON string containing component specifications with voltage and current values.
                        Format: '{"ESP32": {"voltage": 3.3, "mA": 120}, "DHT22": {"voltage": 3.3, "mA": 1.5}}'
                        
    Returns:
        JSON string containing power analysis including:
        - total_current_mA (float): Total current consumption in milliamps
        - voltage_V (float): Operating voltage in volts
        - total_power_W (float): Total power consumption in watts
        - estimated_daily_consumption_Wh (float): Daily energy consumption in watt-hours
        - recommended_battery (str): Suggested battery type and capacity
        - estimated_runtime_hours (float): Expected runtime with recommended battery
    """
    
    try:
        # Parse the JSON input
        components = json.loads(components_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON format for components"})
    
    # Calculate total current draw (mA) and power (W)
    total_current = 0.0
    voltage_set = set()
    
    for comp, vals in components.items():
        v = vals.get('voltage', 0)
        mA = vals.get('mA', 0)
        total_current += mA
        voltage_set.add(v)
    
    # Assume all components run at the same voltage (use max if mixed)
    voltage = max(voltage_set) if voltage_set else 0
    total_power_watts = (total_current / 1000.0) * voltage  # W = V * A
    
    # Estimate daily consumption (Wh)
    daily_consumption_Wh = total_power_watts * 24
    
    # Recommend battery (simple heuristics)
    if daily_consumption_Wh <= 10:
        battery = "Small Li-Ion (e.g. 2000mAh 3.7V)"
        runtime_hr = (2 * 3.7) / total_power_watts if total_power_watts else 0
    elif daily_consumption_Wh <= 50:
        battery = "Medium Li-Ion (e.g. 10000mAh 3.7V)"
        runtime_hr = (10 * 3.7) / total_power_watts if total_power_watts else 0
    else:
        battery = "Large Li-Ion or external supply (>20000mAh 3.7V)"
        runtime_hr = (20 * 3.7) / total_power_watts if total_power_watts else 0
    
    result = {
        "total_current_mA": total_current,
        "voltage_V": voltage,
        "total_power_W": round(total_power_watts, 2),
        "estimated_daily_consumption_Wh": round(daily_consumption_Wh, 2),
        "recommended_battery": battery,
        "estimated_runtime_hours": round(runtime_hr, 2)
    }
    
    return json.dumps(result, indent=2)
