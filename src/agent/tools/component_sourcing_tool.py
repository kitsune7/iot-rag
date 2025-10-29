from langchain.tools import tool
from typing import List, Dict
import os
import json

@tool
def component_sourcing_tool(component_types: str) -> str:
    """
    Component Sourcing Tool: Finds vendor listings, prices, stock, and technical specifications 
    for given component types based on results from the IoT Blueprint Generator tool.
    
    This tool searches through vendor inventories to find component pricing, availability, 
    and technical specifications including current consumption (mA) and voltage requirements.
    Use this tool after generating an initial component blueprint to get procurement details.
    
    Args:
        component_types: Comma-separated list of component names to search for. 
                        These should be specific component names like "ESP32-WROOM-32", 
                        "DHT22 Temperature & Humidity Sensor", "HC-SR501 PIR Motion Sensor".
                        
    Returns:
        JSON string containing vendor information for each component including:
        - vendor (str): Vendor name (Digi-Key, AliExpress)
        - vendor_url (str): Vendor website URL
        - price (float): Component price in USD
        - stock (int): Available inventory quantity
        - technical_specs (dict): Current consumption (mA) and voltage requirements
        - part_number (str): Vendor-specific part number
    """
    
    # Parse comma-separated component types
    component_list = [comp.strip() for comp in component_types.split(',') if comp.strip()]
    
    # Get the root directory of the project (three levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    inventory_files = {
        "Digi-Key": os.path.join(root_dir, "mock_inventory", "mock_digikey_inventory.json"),
        "AliExpress": os.path.join(root_dir, "mock_inventory", "mock_aliexpress_inventory.json")
    }
    vendor_urls = {
        "Digi-Key": "https://www.digikey.com/",
        "AliExpress": "https://www.aliexpress.com/"
    }
    
    # Load vendor inventories
    inventories = {}
    for vendor, path in inventory_files.items():
        try:
            with open(path, "r") as f:
                inventories[vendor] = json.load(f)
        except Exception as e:
            inventories[vendor] = {}
    
    # Search for components
    results = {}
    for comp in component_list:
        offers = []
        for vendor, inv in inventories.items():
            for category, items in inv.items():
                for item in items:
                    if item.get("name", "").strip().lower() == comp.strip().lower():
                        offer = {
                            "vendor": vendor,
                            "vendor_url": vendor_urls[vendor],
                            "price": item.get("price"),
                            "stock": item.get("stock"),
                            "technical_specs": {
                                "mA": item.get("mA"),
                                "voltage": item.get("voltage")
                            },
                            "part_number": item.get("part_number"),
                            "category": category
                        }
                        offers.append(offer)
        results[comp] = offers
    
    # Return formatted JSON string
    return json.dumps(results, indent=2)
