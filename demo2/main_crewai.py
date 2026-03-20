import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 1. Setup base directory and load .env as a fallback
base = Path(__file__).resolve().parent
load_dotenv(base / ".env")

# 2. --- SET YOUR PROJECT CONFIG HERE (Overrides .env) ---
os.environ["VERTEXAI_PROJECT"] = ""
os.environ["VERTEXAI_LOCATION"] = "us-central1"
os.environ["LLM_BACKEND"] = "vertex_ai"
os.environ["MODEL_NAME"] = "gemini-2.5-flash-lite"
os.environ["CREWAI_TRACING_ENABLED"] = "false"

# 3. Import CrewAI components AFTER the environment is fully configured
from crew_demo import build_second_demo_crew

def main() -> None:
    """Run the second CrewAI demo."""
    
    # Optional debug prints to prove the overrides worked
    print("--- Environment Variables ---")
    print(f"LLM_BACKEND={os.getenv('LLM_BACKEND')}")
    print(f"MODEL_NAME={os.getenv('MODEL_NAME')}")
    print(f"VERTEXAI_PROJECT={os.getenv('VERTEXAI_PROJECT')}")

    data_dir = base / "data"
    out_dir = base / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = {
        "protocol_path": str(data_dir / "protocol.docx"),
        "template_path": str(data_dir / "sap_template.docx"),
        "protocol_json_path": str(out_dir / "protocol_parsed.json"),
        "template_json_path": str(out_dir / "sap_template_parsed.json"),
        "protocol_tables_json_path": str(out_dir / "protocol_tables.json"),
        "update_units_json_path": str(out_dir / "update_units.json"),
    }

    # Use the Demo 2 Crew
    crew = build_second_demo_crew()
    result = crew.kickoff(inputs=inputs)

    # Save to a demo2 specific file
    summary_path = out_dir / "crewai_demo2_result.txt"
    summary_path.write_text(str(result), encoding="utf-8")

    deterministic_summary = {
        "protocol_json_path": inputs["protocol_json_path"],
        "template_json_path": inputs["template_json_path"],
        "protocol_tables_json_path": inputs["protocol_tables_json_path"],
        "update_units_json_path": inputs["update_units_json_path"],
        "crewai_result_path": str(summary_path),
    }

    (out_dir / "crewai_demo2_summary.json").write_text(
        json.dumps(deterministic_summary, indent=2),
        encoding="utf-8",
    )

    print("\n--- CrewAI Demo 2 completed successfully. ---")
    print(f"Result summary saved to: {summary_path}")

if __name__ == "__main__":
    main()