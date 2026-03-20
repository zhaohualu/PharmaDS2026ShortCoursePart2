import json
from pathlib import Path
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from tools.docx_parser_tool import parse_docx
from tools.protocol_table_extractor import extract_tables
from tools.template_signal_detector import detect_update_units


class ParseDocxToolInput(BaseModel):
    file_path: str = Field(..., description="Path to the DOCX file to parse.")
    output_json_path: str = Field(..., description="Path to save the parsed JSON output.")


class ParseDocxTool(BaseTool):
    name: str = "parse_docx_tool"
    description: str = (
        "Parse a DOCX document into structured JSON including paragraphs, runs, "
        "basic formatting, and tables, then save the JSON to a file."
    )
    args_schema: Type[BaseModel] = ParseDocxToolInput

    def _run(self, file_path: str, output_json_path: str) -> str:
        parsed = parse_docx(file_path)
        output_path = Path(output_json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
        return json.dumps(
            {
                "status": "success",
                "source_file": file_path,
                "output_json_path": str(output_path),
                "paragraph_count": parsed["paragraph_count"],
                "table_count": parsed["table_count"],
            },
            indent=2,
        )


class ExtractProtocolTablesToolInput(BaseModel):
    parsed_protocol_json_path: str = Field(..., description="Path to parsed protocol JSON.")
    output_json_path: str = Field(..., description="Path to save extracted protocol tables.")


class ExtractProtocolTablesTool(BaseTool):
    name: str = "extract_protocol_tables_tool"
    description: str = (
        "Read parsed protocol JSON, extract protocol tables, and save them as JSON."
    )
    args_schema: Type[BaseModel] = ExtractProtocolTablesToolInput

    def _run(self, parsed_protocol_json_path: str, output_json_path: str) -> str:
        parsed = json.loads(Path(parsed_protocol_json_path).read_text(encoding="utf-8"))
        tables = extract_tables(parsed)
        output_path = Path(output_json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(tables, indent=2), encoding="utf-8")
        return json.dumps(
            {
                "status": "success",
                "parsed_protocol_json_path": parsed_protocol_json_path,
                "output_json_path": str(output_path),
                "table_count": len(tables),
            },
            indent=2,
        )


class DetectTemplateSignalsToolInput(BaseModel):
    parsed_template_json_path: str = Field(..., description="Path to parsed SAP template JSON.")
    output_json_path: str = Field(..., description="Path to save detected update units JSON.")


class DetectTemplateSignalsTool(BaseTool):
    name: str = "detect_template_signals_tool"
    description: str = (
        "Read parsed SAP template JSON, detect template signals, and save update units as JSON. "
        "Current logic: blue text = update placeholder, green text = guidance/remove. "
        "Fallback rules also detect bracket placeholders and example-text markers."
    )
    args_schema: Type[BaseModel] = DetectTemplateSignalsToolInput

    def _run(self, parsed_template_json_path: str, output_json_path: str) -> str:
        parsed = json.loads(Path(parsed_template_json_path).read_text(encoding="utf-8"))
        units = detect_update_units(parsed)
        output_path = Path(output_json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(units, indent=2), encoding="utf-8")
        return json.dumps(
            {
                "status": "success",
                "parsed_template_json_path": parsed_template_json_path,
                "output_json_path": str(output_path),
                "update_unit_count": len(units),
            },
            indent=2,
        )

        