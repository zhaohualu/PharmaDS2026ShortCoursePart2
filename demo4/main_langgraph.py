import os
import json
from pathlib import Path
from dotenv import load_dotenv

# --- SET PROJECT CONFIG HERE ---
os.environ["VERTEXAI_PROJECT"] = ""
os.environ["VERTEXAI_LOCATION"] = "us-central1"
os.environ["LLM_BACKEND"] = "vertex_ai"
os.environ["MODEL_NAME"] = "gemini-2.5-flash"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Load fallback .env
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".env")

from workflow import build_graph

def main() -> None:
    print(f"--- Starting LangGraph Demo 4 ---")
    print(f"Using Model: {os.getenv('MODEL_NAME')}")

    data_dir = base_dir / "data"
    output_dir = base_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Add the drafted_sap_json_path to the initial state
    initial_state = {
        "protocol_path": str(data_dir / "protocol.docx"),
        "template_path": str(data_dir / "sap_template.docx"),
        "protocol_json_path": str(output_dir / "protocol_parsed.json"),
        "template_json_path": str(output_dir / "sap_template_parsed.json"),
        "protocol_tables_json_path": str(output_dir / "protocol_tables.json"),
        "update_units_json_path": str(output_dir / "update_units.json"),
        "drafted_sap_json_path": str(output_dir / "drafted_sap_updates.json"), 
        "summary_txt_path": str(output_dir / "summary.txt"),
    }

    app = build_graph()
    
    # Concurrency limit of 1 ensures pure sequential execution
    final_state = app.invoke(initial_state, config={"recursion_limit": 50, "max_concurrency": 1})

    summary = {
        "protocol_paragraphs": final_state.get("parsed_protocol", {}).get("paragraph_count", 0),
        "protocol_tables": len(final_state.get("protocol_tables", [])),
        "detected_update_units": len(final_state.get("update_units", [])),
        "drafted_sap_updates": len(final_state.get("drafted_sap_updates", [])),
        "drafted_file_saved_at": final_state.get("drafted_sap_json_path", "")
    }

    summary_path = output_dir / "demo4_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n✅ LangGraph Pipeline Completed Successfully!")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    # --- NEW: Build the final Word Document ---
    print("\n--- Generating Final Word Document ---")
    from sap_document_builder import build_final_sap_docx
    final_docx_path = str(output_dir / "Draft_SAP_v1.docx")
    
    build_final_sap_docx(
        template_docx_path=initial_state["template_path"],
        update_units_path=initial_state["update_units_json_path"],
        draft_json_path=initial_state["drafted_sap_json_path"],
        output_docx_path=final_docx_path
    )

if __name__ == "__main__":
    main()