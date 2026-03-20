import json
from pathlib import Path

from langgraph.graph import END, StateGraph

from state_schema import DemoState
from tools.docx_parser_tool import parse_docx
from tools.protocol_table_extractor import extract_tables
from tools.template_signal_detector import detect_update_units
from config.llm_config_langchain import get_llm


def _write_json(path: str, data) -> None:
    """Write JSON data to disk with UTF-8 encoding."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _write_text(path: str, text: str) -> None:
    """Write plain text to disk."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def parse_protocol_node(state: DemoState) -> DemoState:
    """Parse protocol.docx and save structured JSON."""
    parsed_protocol = parse_docx(state["protocol_path"])
    _write_json(state["protocol_json_path"], parsed_protocol)
    return {"parsed_protocol": parsed_protocol}


def parse_template_node(state: DemoState) -> DemoState:
    """Parse sap_template.docx and save structured JSON."""
    parsed_template = parse_docx(state["template_path"])
    _write_json(state["template_json_path"], parsed_template)
    return {"parsed_template": parsed_template}


def extract_tables_node(state: DemoState) -> DemoState:
    """Extract protocol tables from parsed protocol JSON."""
    protocol_tables = extract_tables(state["parsed_protocol"])
    _write_json(state["protocol_tables_json_path"], protocol_tables)
    return {"protocol_tables": protocol_tables}


def detect_signals_node(state: DemoState) -> DemoState:
    """Detect update units from the parsed SAP template."""
    update_units = detect_update_units(state["parsed_template"])
    _write_json(state["update_units_json_path"], update_units)
    return {"update_units": update_units}


def summarize_outputs_node(state: DemoState) -> DemoState:
    """
    Use the LLM only at the final step:
    - summarize what the workflow produced
    - lightly reformat the result into clean demo text
    """
    llm = get_llm()

    protocol_para_count = state["parsed_protocol"]["paragraph_count"]
    protocol_table_count = state["parsed_protocol"]["table_count"]
    template_para_count = state["parsed_template"]["paragraph_count"]
    template_table_count = state["parsed_template"]["table_count"]
    extracted_table_count = len(state["protocol_tables"])
    detected_unit_count = len(state["update_units"])

    prompt = f"""
You are helping explain a LangGraph demo for a short course on document automation in clinical trial documents.

Write a concise, clear summary in plain English for students.
Keep it short but informative. Use bullet points.

Facts:
- Protocol paragraphs: {protocol_para_count}
- Protocol tables found during parsing: {protocol_table_count}
- Protocol tables extracted into output artifact: {extracted_table_count}
- SAP template paragraphs: {template_para_count}
- SAP template tables: {template_table_count}
- Detected update units: {detected_unit_count}

Please explain:
1. What the workflow did
2. What files/artifacts were produced
3. Why this LangGraph version is more structured than pure Python
4. Why this version is more controlled than a CrewAI agent workflow
""".strip()

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        # Gemini models via VertexAI sometimes return a list of content blocks
        if isinstance(response.content, list):
            # Extract the actual text from the list of dictionaries
            summary_text = "\n".join([
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in response.content
            ])
        else:
            summary_text = response.content
    else:
        summary_text = str(response)

    _write_text(state["summary_txt_path"], summary_text)
    return {"summary_text": summary_text}


def build_graph():
    """
    Build a minimal teaching-friendly LangGraph workflow.

    Flow:
    parse_protocol -> parse_template -> extract_tables -> detect_signals -> summarize_outputs -> END
    """
    graph = StateGraph(DemoState)

    graph.add_node("parse_protocol", parse_protocol_node)
    graph.add_node("parse_template", parse_template_node)
    graph.add_node("extract_tables", extract_tables_node)
    graph.add_node("detect_signals", detect_signals_node)
    graph.add_node("summarize_outputs", summarize_outputs_node)

    graph.set_entry_point("parse_protocol")
    graph.add_edge("parse_protocol", "parse_template")
    graph.add_edge("parse_template", "extract_tables")
    graph.add_edge("extract_tables", "detect_signals")
    graph.add_edge("detect_signals", "summarize_outputs")
    graph.add_edge("summarize_outputs", END)

    return graph.compile()