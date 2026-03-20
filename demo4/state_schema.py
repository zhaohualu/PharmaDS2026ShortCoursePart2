from typing import TypedDict, Dict, Any, List

class GraphState(TypedDict):
    # File Paths
    protocol_path: str
    template_path: str
    protocol_json_path: str
    template_json_path: str
    protocol_tables_json_path: str
    update_units_json_path: str
    drafted_sap_json_path: str  # NEW: Where to save the drafts
    summary_txt_path: str

    # In-Memory Data Payloads
    parsed_protocol: Dict[str, Any]
    parsed_template: Dict[str, Any]
    protocol_tables: List[Dict[str, Any]]
    update_units: List[Dict[str, Any]]
    drafted_sap_updates: List[Dict[str, Any]]  # NEW: The drafted output