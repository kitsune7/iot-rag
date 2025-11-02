# iot-rag

A **Retrieval-Augmented Generation (RAG) system for Internet of Things (IoT) applications**. This project combines a research database of 20 IoT academic papers with an AI agent that provides evidence-based recommendations for IoT hardware, components, and system design.

The IoT Planner Agent helps users design complete IoT systems by providing:

- Research-backed recommendations from academic literature
- Component selection and sourcing from vendor inventories
- Power consumption analysis and battery sizing
- System blueprints tailored to specific use cases

## Overview

This project is a sophisticated **research-powered IoT planning assistant** that combines multiple components:

### Architecture

- **RAG System**: Vector database (ChromaDB) storing 20 IoT research papers, enabling semantic search across academic literature
- **AI Agent**: LangChain-based agent powered by Google Gemini 2.5 Flash that orchestrates multiple tools
- **Specialized Tools**:
  - Research Tool: Query the academic paper database
  - Blueprint Generator: Heuristic-based component matching
  - Component Sourcing: Search mock vendor inventories (Digi-Key, AliExpress)
  - Power Estimator: Calculate power consumption and battery requirements
- **Evaluation System**: Comprehensive performance tracking and metrics

### Key Features

1. **Evidence-Based Recommendations**: All technical advice is grounded in research papers with proper citations
2. **Complete System Design**: From component selection to power budgeting
3. **Real-World Sourcing**: Pricing and availability from mock vendor databases
4. **Performance Monitoring**: Track execution time, tool usage, and token consumption
5. **Persistent Results**: Automatic saving of responses and evaluation metrics

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Prerequisites

- Python ≥3.13
- Google Gemini API key

### Setup

1. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd iot-rag
uv sync
```

3. Set up your environment variables:

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

The project provides two CLI commands:

### 1. IoT Planner Agent (Full System)

Use the `agent` command for comprehensive IoT system planning with all tools:

```bash
uv run agent "your IoT planning query"
```

**Examples:**

```bash
# Design a greenhouse monitoring system
uv run agent "I need a temperature and humidity monitoring system for a greenhouse that runs on battery power"

# Get hardware recommendations
uv run agent "What microcontroller and sensors should I use for a soil moisture monitoring system?"

# Plan a complete IoT deployment
uv run agent "Help me design a low-power air quality monitoring station for outdoor deployment"
```

The agent will:

- Search the research database for relevant information
- Generate a component blueprint
- Source components from vendor inventories
- Calculate power requirements and recommend battery sizing
- Save the response to `results/{query}_{timestamp}.md`
- Save evaluation metrics to `results/{query}_{timestamp}.json`

### 2. RAG Query Tool (Research Only)

Use the `rag` command to query the research database directly:

```bash
uv run rag "your research query" [--top_k TOP_K] [--verbose]
```

**Options:**

- `--top_k`: Number of results to return (default: 5)
- `--verbose`: Show detailed results with source files

**Examples:**

```bash
# Query IoT protocols
uv run rag "MQTT protocol for IoT" --top_k 3

# Research power consumption strategies
uv run rag "low power IoT devices" --verbose

# Find information about sensors
uv run rag "temperature and humidity sensors for agriculture"
```

## Features

### Research Tool

- Semantic search across 20 IoT academic papers
- Returns relevant excerpts with source citations
- Papers cover: IoT architectures, protocols, healthcare IoT, agricultural IoT, smart cities, security, and energy applications

### Blueprint Generator

- Heuristic-based component matching
- Suggests components based on use case keywords
- Categories: microcontrollers, sensors, actuators, displays, power supplies, device cases

### Component Sourcing

- Search mock vendor inventories (Digi-Key and AliExpress)
- Provides pricing, availability, and specifications
- Includes technical details: current consumption (mA) and voltage requirements
- 60+ components in the mock database

### Power Battery Estimator

- Calculates total system power consumption
- Estimates daily energy usage (Wh)
- Recommends appropriate battery type and capacity
- Predicts runtime based on usage patterns

### Evaluation Tracking

- Total runtime measurement
- Per-tool execution times
- RAG query count and chunks retrieved
- Token usage (input/output/total)
- Comprehensive JSON reports

## Project Structure

```
iot-rag/
├── assets/                    # IoT research papers (20 PDFs)
├── mock_inventory/            # Component databases (JSON)
│   ├── mock_digikey_inventory.json
│   └── mock_aliexpress_inventory.json
├── chroma_db/                 # Vector store (auto-created, gitignored)
├── results/                   # Agent outputs (gitignored)
├── src/
│   ├── agent/                 # Agent implementation
│   │   ├── agent.py           # Agent runner
│   │   ├── base_agent.py      # LangChain agent setup
│   │   ├── iot_planner.py     # Tool orchestration
│   │   ├── cli.py             # CLI interface
│   │   └── tools/             # Agent tools
│   │       ├── research_tool.py
│   │       ├── iot_blueprint_generator.py
│   │       ├── component_sourcing_tool.py
│   │       └── power_battery_estimator.py
│   ├── rag/                   # RAG system
│   │   ├── vector_store.py    # ChromaDB wrapper
│   │   ├── parser.py          # PDF processing
│   │   ├── tool.py            # RAG query orchestration
│   │   └── cli.py             # Standalone RAG CLI
│   ├── evaluation/            # Performance tracking
│   │   ├── evaluation_tracker.py
│   │   └── evaluation_callback_handler.py
│   └── tests/                 # Unit tests
├── pyproject.toml             # Dependencies and config
└── uv.lock                    # Dependency lock file
```

## Output & Results

When you run the agent, results are automatically saved to the `results/` directory:

### Response Files

- **Markdown files** (`{query}_{timestamp}.md`): The agent's complete response with recommendations, citations, and technical details
- Formatted for easy reading with bullet lists and clear sections

### Evaluation Metrics

- **JSON files** (`{query}_{timestamp}.json`): Comprehensive performance data including:
  - Total execution time
  - Individual tool execution times
  - RAG queries performed and chunks retrieved
  - Token usage (input, output, total)
  - Error tracking

Example JSON structure:

```json
{
  "total_runtime": 15.42,
  "tool_times": {
    "research_tool": 2.34,
    "component_sourcing_tool": 5.67
  },
  "rag_queries": 2,
  "total_chunks_retrieved": 10,
  "token_usage": {
    "input_tokens": 1523,
    "output_tokens": 687,
    "total_tokens": 2210
  }
}
```

## Technologies

### Core Technologies

- **LangChain**: Agent framework and tool orchestration
- **Google Gemini 2.5 Flash**: Large language model (temperature=0 for consistency)
- **ChromaDB**: Vector database for semantic search
- **PyMuPDF**: PDF text extraction and processing
- **Python 3.13+**: Modern Python with latest features

### Key Dependencies

- `langchain` (≥1.0.2): Agent framework
- `langchain-google-genai` (≥3.0.0): Gemini integration
- `chromadb` (≥1.2.1): Vector store
- `pymupdf` (≥1.26.5): PDF processing
- `arize-phoenix-otel` (≥0.13.1): OpenTelemetry tracing
- `python-dotenv` (≥1.1.1): Environment management

### LLM Configuration

- **Model**: `gemini-2.5-flash`
- **Max output tokens**: 2048
- **Top-p**: 0.95
- **Top-k**: 40
- **Target response length**: 500-800 tokens

## Example Use Cases

### 1. Agricultural IoT System

```bash
uv run agent "Design a soil moisture monitoring system for a vineyard with 50 sensors that needs to run for 6 months on battery"
```

**What the agent does:**

- Searches research papers for agricultural IoT and soil sensors
- Recommends appropriate moisture sensors and microcontrollers
- Calculates power consumption for 50 sensors
- Suggests battery capacity for 6-month operation
- Provides component sourcing with pricing

### 2. Smart Home Monitoring

```bash
uv run agent "I want to monitor temperature, humidity, and air quality in my home. What components do I need?"
```

**What the agent does:**

- Finds research on indoor environmental monitoring
- Suggests sensor combinations (DHT22, MQ-135, etc.)
- Recommends microcontroller (ESP32 for WiFi)
- Estimates power consumption
- Sources components from vendors

### 3. Industrial IoT

```bash
uv run agent "Plan a vibration monitoring system for predictive maintenance on industrial motors"
```

**What the agent does:**

- Researches industrial IoT and predictive maintenance
- Recommends vibration sensors and data acquisition
- Suggests robust industrial-grade components
- Calculates power and communication requirements
- Provides complete system blueprint

## Development

### Running Tests

```bash
uv run pytest
```

### Linting and Formatting

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Lint the codebase
uv run ruff check .

# Format the codebase
uv run ruff format .
```

### Project Configuration

All dependencies and tool configurations are managed in `pyproject.toml`.
