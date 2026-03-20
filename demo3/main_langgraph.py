import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 1. Setup base directory and load .env as a fallback
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".env")

# 2. --- SET YOUR PROJECT CONFIG HERE (Overrides .env) ---
os.environ["VERTEXAI_PROJECT"] = ""
os.environ["VERTEXAI_LOCATION"] = "us-central1"
os.environ["LLM_BACKEND"] = "vertex_ai"
os.environ["MODEL_NAME"] = "gemini-2.5-flash"
# LangSmith tracing (equivalent to CREWAI_TRACING_ENABLED for LangChain)
os.environ["LANGCHAIN_TRACING_V2"] = "false" 

# 3. Import workflow components AFTER the environment is fully configured
from workflow import build_graph

def main() -> None:
    # Optional debug prints
    print("--- Environment Variables ---")
    print(f"LLM_BACKEND={os.getenv('LLM_BACKEND')}")
    print(f"MODEL_NAME={os.getenv('MODEL_NAME')}")
    print(f"VERTEXAI_PROJECT={os.getenv('VERTEXAI_PROJECT')}")
    print(f"VERTEXAI_LOCATION={os.getenv('VERTEXAI_LOCATION')}")

    data_dir = base_dir / "data"
    output_dir = base_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    initial_state = {
        "protocol_path": str(data_dir / "protocol.docx"),
        "template_path": str(data_dir / "sap_template.docx"),
        "protocol_json_path": str(output_dir / "protocol_parsed.json"),
        "template_json_path": str(output_dir / "sap_template_parsed.json"),
        "protocol_tables_json_path": str(output_dir / "protocol_tables.json"),
        "update_units_json_path": str(output_dir / "update_units.json"),
        "summary_txt_path": str(output_dir / "summary.txt"),
    }

    app = build_graph()
    
    # --- NEW: Configure graph execution limits ---
    run_config = {
        "recursion_limit": 50,  # Standard safety net to prevent infinite loops
        "max_concurrency": 2    # Maximum number of parallel nodes to execute at once
    }

    # Pass the config dictionary into the invoke command
    final_state = app.invoke(initial_state, config=run_config)

    summary = {
        "protocol_paragraphs": final_state["parsed_protocol"]["paragraph_count"],
        "protocol_tables_from_parser": final_state["parsed_protocol"]["table_count"],
        "protocol_tables_extracted": len(final_state["protocol_tables"]),
        "sap_template_paragraphs": final_state["parsed_template"]["paragraph_count"],
        "sap_template_tables": final_state["parsed_template"]["table_count"],
        "detected_update_units": len(final_state["update_units"]),
        "summary_txt_path": final_state["summary_txt_path"],
    }

    summary_path = output_dir / "demo_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nLangGraph demo completed.")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()