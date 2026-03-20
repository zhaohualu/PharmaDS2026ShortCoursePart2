from __future__ import annotations

from typing import Any, Dict, List


def extract_tables(parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert parsed DOCX tables into a flattened JSON-friendly form."""
    out = []
    for t in parsed_doc.get("tables", []):
        flat_lines = []
        n_rows = len(t["rows"])
        n_cols = max((len(r) for r in t["rows"]), default=0)
        for row in t["rows"]:
            flat_lines.append(" | ".join(cell["text"] for cell in row))
        out.append(
            {
                "table_id": f"table_{t['table_index']}",
                "table_index": t["table_index"],
                "n_rows": n_rows,
                "n_cols": n_cols,
                "flattened_text": "\n".join(flat_lines),
                "rows": t["rows"],
            }
        )
    return out
