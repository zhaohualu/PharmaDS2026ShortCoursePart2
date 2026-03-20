from typing import Any, Dict, List, TypedDict


class DemoState(TypedDict, total=False):

    # Input paths
    protocol_path: str
    template_path: str
    protocol_json_path: str
    template_json_path: str
    protocol_tables_json_path: str
    update_units_json_path: str
    summary_txt_path: str

    # Intermediate / output objects
    parsed_protocol: Dict[str, Any]
    parsed_template: Dict[str, Any]
    protocol_tables: List[Dict[str, Any]]
    update_units: List[Dict[str, Any]]
    summary_text: str