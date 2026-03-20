import json
from pathlib import Path
from langgraph.graph import StateGraph, END
from state_schema import GraphState

# Import Tools
from tools.docx_parser_tool import parse_docx
from tools.protocol_table_extractor import extract_tables
from tools.template_signal_detector import detect_update_units

# Import LLM Config
from config.llm_config_langchain import get_llm
from langchain_core.prompts import ChatPromptTemplate

def parse_documents_node(state: GraphState) -> GraphState:
    print("--- NODE: Parsing Documents ---")
    
    # 1. Parse the DOCX files (only takes 1 argument: the input path)
    parsed_protocol = parse_docx(state["protocol_path"])
    parsed_template = parse_docx(state["template_path"])
    
    # 2. Save the results to the output JSON paths for the next tools to use
    Path(state["protocol_json_path"]).write_text(json.dumps(parsed_protocol, indent=2), encoding="utf-8")
    Path(state["template_json_path"]).write_text(json.dumps(parsed_template, indent=2), encoding="utf-8")
    
    return {"parsed_protocol": parsed_protocol, "parsed_template": parsed_template}

def extract_tables_node(state: GraphState) -> GraphState:
    print("--- NODE: Extracting Tables ---")
    
    # FIX: Pass the actual parsed dictionary from memory, not the file path string
    tables = extract_tables(state["parsed_protocol"])
    
    # Save the result to the output JSON path
    Path(state["protocol_tables_json_path"]).write_text(json.dumps(tables, indent=2), encoding="utf-8")
    
    return {"protocol_tables": tables}

def detect_signals_node(state: GraphState) -> GraphState:
    print("--- NODE: Detecting Template Signals ---")
    
    # FIX: Pass the actual parsed dictionary from memory, not the file path string
    units = detect_update_units(state["parsed_template"])
    
    # Save the result to the output JSON path
    Path(state["update_units_json_path"]).write_text(json.dumps(units, indent=2), encoding="utf-8")
    
    return {"update_units": units}

def draft_sap_updates_node(state: GraphState) -> GraphState:
    print("--- NODE: Drafting SAP Updates (One-by-One) ---")
    llm = get_llm()
    
    protocol_str = json.dumps(state.get("parsed_protocol", {}))
    update_units = state.get("update_units", [])
    
    # NEW: Extract tables from the state and convert to a JSON string
    protocol_tables = state.get("protocol_tables", [])
    tables_str = json.dumps(protocol_tables, indent=2)

    # UPDATED PROMPT: Added the {tables} variable
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert clinical medical writer. Your job is to draft a specific SAP text update."),
        ("human", "Here is the parsed clinical protocol:\n{protocol}\n\n"
                  "Here are the tables extracted from the protocol:\n{tables}\n\n"
                  "Here is the specific placeholder/update unit from the SAP template that needs to be filled:\n{unit}\n\n"
                  "Find the corresponding information in the protocol and its tables, then draft the proposed SAP text for this specific unit. "
                  "If the unit's text represents green guidance instructions, the drafted text should be an empty string (\"\"). "
                  "If the info is missing from the protocol, write 'Not specified in protocol'.\n\n"
                  "Return ONLY a valid JSON object (not an array) with the keys 'unit_id' and 'proposed_sap_text'. No markdown formatting blocks.")
    ])

    chain = prompt | llm
    
    drafted_updates = []
    
    for i, unit in enumerate(update_units):
        unit_id = unit.get("unit_id", f"unknown_{i}")
        print(f"   -> Processing unit {i+1}/{len(update_units)} (ID: {unit_id})...")
        
        unit_str = json.dumps(unit, indent=2)
        
        try:
            # UPDATED INVOCATION: Pass the tables_str to the chain
            response = chain.invoke({
                "protocol": protocol_str,
                "tables": tables_str,
                "unit": unit_str
            })

            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            drafted_unit = json.loads(clean_json)
            
            drafted_unit["unit_id"] = unit_id
            
            drafted_updates.append(drafted_unit)
            print(f"      [Success] Drafted: {drafted_unit.get('proposed_sap_text')[:40]}...")
            
        except Exception as e:
            print(f"      [Error] Failed to draft unit {unit_id}: {e}")
            drafted_updates.append({
                "unit_id": unit_id, 
                "proposed_sap_text": ""
            })

    out_path = Path(state["drafted_sap_json_path"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(drafted_updates, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"drafted_sap_updates": drafted_updates}


def build_graph() -> StateGraph:
    workflow = StateGraph(GraphState)

    # 1. Add Nodes
    workflow.add_node("parse_documents", parse_documents_node)
    workflow.add_node("extract_tables", extract_tables_node)
    workflow.add_node("detect_signals", detect_signals_node)
    workflow.add_node("draft_sap_updates", draft_sap_updates_node)

    # 2. Define strictly sequential edges to protect against API Rate Limits
    workflow.set_entry_point("parse_documents")
    workflow.add_edge("parse_documents", "extract_tables")
    workflow.add_edge("extract_tables", "detect_signals")
    workflow.add_edge("detect_signals", "draft_sap_updates")
    workflow.add_edge("draft_sap_updates", END)

    return workflow.compile()