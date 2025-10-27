# iot-rag

A Retrieval-Augmented Generation (RAG) system for Internet of Things (IoT) applications.

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. First, install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the project dependencies:

```bash
uv sync
```

## Usage

This is the command-line interface for the iot-rag application.

```bash
uv run iot-rag [-h] [--top_k TOP_K] [--verbose VERBOSE] query
```

Simple version run example:

```bash
uv run iot-rag "What is IoT?"
```
