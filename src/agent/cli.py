"""
CLI for the IoT Planner Agent as a one-shot query processor
"""

import sys
import argparse

from agent.agent import run_agent


def main():
    """Run the IoT Planner Agent as a one-shot query processor"""
    parser = argparse.ArgumentParser(
        description="IoT Planner Agent - Research-powered IoT recommendations"
    )
    parser.add_argument("query", help="The IoT question or query to process")

    args = parser.parse_args()
    query = args.query

    if not query:
        print("🤖 IoT Planner Agent - One-Shot Mode")
        print("=" * 50)
        print("💡 Be specific about your IoT domain for better research results.")
        print(
            "📖 Example: 'temperature sensors for greenhouse monitoring' vs 'temperature sensors'\n"
        )

        query = input("Enter your IoT question: ").strip()

        if not query:
            print("No query provided. Exiting...")
            return 1

    run_agent(query)


if __name__ == "__main__":
    sys.exit(main())
