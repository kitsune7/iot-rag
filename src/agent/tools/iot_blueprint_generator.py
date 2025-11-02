from langchain.tools import tool

# Static object for heuristics and component options
IOT_COMPONENT_HEURISTICS = {
    "microcontroller": [
        ("ESP32-WROOM-32", ["wifi", "wireless", "remote"]),
        ("ESP32 Mini DevKit", ["esp32 mini", "devkit"]),
        ("STM32F103C8T6", ["bluetooth", "ble", "bt", "stm32"]),
        ("STM32F103C8T6 Maple", ["maple"]),
        ("Nano V3.0 ATmega328P", ["ethernet", "wired network", "lan", "nano v3.0"]),
    ],
    "sensor": [
        ("HC-SR501 PIR Motion Sensor", ["motion", "presence", "pir"]),
        ("EKMB PIR Motion Detector", ["ekmb", "pir"]),
        ("DHT22 Temperature & Humidity Sensor", ["temperature", "humidity", "dht22"]),
        ("AM2302 Temp & Humidity", ["am2302"]),
        ("SEN0193 Soil Moisture", ["soil", "moisture", "sen0193"]),
    ],
    "actuator": [
        ("Songle SRD-05VDC-SL-C Relay", ["relay", "switch"]),
        ("JQC-3FF-S-Z Relay", ["jqc-3ff-s-z"]),
        ("Firgelli L12 Linear Actuator", ["linear actuator", "l12"]),
        ("Actuonix L12 Mini Actuator", ["actuonix"]),
        ("DFRobot Solenoid Valve", ["solenoid", "dfr"]),
    ],
    "display": [
        ("Nextion NX3224T024 Touchscreen", ["touchscreen", "nextion"]),
        ("Nextion 2.4in Touchscreen", ["nextion 2.4in"]),
        ("Waveshare 7inch HDMI LCD", ["hdmi lcd", "waveshare"]),
        ("Waveshare 7in HDMI LCD", ["waveshare 7in"]),
        ("Heltec 0.96in OLED", ["oled", "heltec"]),
    ],
    "power supply": [
        ("Lithium Ion Battery Pack", ["battery", "li-ion"]),
        ("Keeppower 18650 Battery", ["keeppower", "18650"]),
        ("USB Power Adapter", ["usb", "adapter"]),
        ("Anker USB Power Adapter", ["anker usb"]),
        ("ALLPOWERS 5V Solar Panel", ["solar panel", "allpowers"]),
    ],
    "device case": [
        ("IP65 Weatherproof Enclosure", ["weatherproof", "outdoor", "ip65"]),
        ("IP66 Outdoor Enclosure", ["ip66"]),
        ("Wall-Mount ABS Box", ["wall mount"]),
        ("SZOMK Wall-Mount Box", ["szomk"]),
        ("Hammond Clear Case", ["clear case", "hammond"]),
    ],
}


@tool
def iot_blueprint_generator(user_request: str) -> str:
    """
    IoT Blueprint Generator: This tool produces a starting component set by analyzing
    keywords in the user's request and matching them to appropriate IoT components.

    Args:
        user_request: User's natural language request for an IoT system describing
                     the desired functionality, environment, or specific requirements.

    Returns:
        A formatted string with bullet-pointed component recommendations including:
        - Microcontroller (processing unit)
        - Sensors (data collection)
        - Actuators (physical actions)
        - Display (user interface, if applicable)
        - Power supply (power source)
        - Device case (enclosure/housing)
    """
    req = user_request.lower()
    components = {}

    for comp_type, options in IOT_COMPONENT_HEURISTICS.items():
        found = False
        for label, keywords in options:
            if keywords and any(word in req for word in keywords):
                components[comp_type] = label
                found = True
                break
        if not found:
            # For display, only add if a keyword matched
            if comp_type == "display":
                continue
            # Otherwise, use the last (default) option
            components[comp_type] = options[-1][0]

    # Format as bullet-pointed string
    bullet_points = [
        f"- {comp_type.replace('_', ' ').title()}: {label}"
        for comp_type, label in components.items()
    ]
    return "\n".join(bullet_points)
