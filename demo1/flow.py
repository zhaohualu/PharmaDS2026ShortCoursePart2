import json
from pathlib import Path
from tools.docx_parser_tool import parse_docx
from tools.protocol_table_extractor import extract_tables
from tools.template_signal_detector import detect_update_units


def run_flow(base_dir: str) -> dict:
    base = Path(base_dir)
    data_dir = base / 'data'
    out_dir = base / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)

    protocol = parse_docx(str(data_dir / 'protocol.docx'))
    template = parse_docx(str(data_dir / 'sap_template.docx'))
    tables = extract_tables(protocol)
    units = detect_update_units(template)

    (out_dir / 'protocol_parsed.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    (out_dir / 'sap_template_parsed.json').write_text(json.dumps(template, indent=2), encoding='utf-8')
    (out_dir / 'protocol_tables.json').write_text(json.dumps(tables, indent=2), encoding='utf-8')
    (out_dir / 'update_units.json').write_text(json.dumps(units, indent=2), encoding='utf-8')

    summary = {
        'protocol_paragraphs': protocol['paragraph_count'],
        'protocol_tables': protocol['table_count'],
        'sap_template_paragraphs': template['paragraph_count'],
        'sap_template_tables': template['table_count'],
        'detected_update_units': len(units),
    }
    (out_dir / 'demo_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return summary
    