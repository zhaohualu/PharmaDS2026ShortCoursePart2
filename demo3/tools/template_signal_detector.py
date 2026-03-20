import re
from typing import Any, Dict, List

BRACKET_RE = re.compile(r"\[[^\]]+\]")

def detect_update_units(parsed_template: Dict[str, Any]) -> List[Dict[str, Any]]:
    units: List[Dict[str, Any]] = []
    current_section = "ROOT"
    uid = 1

    for p in parsed_template.get("paragraphs", []):
        style = (p.get("style") or "").lower()
        text = (p.get("text") or "")
        if style.startswith("heading") and text.strip():
            current_section = text.strip()

        # --- NEW LOGIC: Merge consecutive identical runs ---
        current_signal_key = None
        current_signal_obj = None
        current_instruction = None
        current_text = ""
        current_run_indices = []

        def flush_runs():
            nonlocal uid, current_signal_key, current_signal_obj, current_instruction, current_text, current_run_indices
            if current_signal_obj and current_text.strip():
                units.append({
                    "unit_id": f"U{uid:04d}",
                    "section_title": current_section,
                    "paragraph_index": p["paragraph_index"],
                    "run_indices": current_run_indices, # Use a list of runs
                    "instruction_type": current_instruction,
                    "template_text": current_text.strip(),
                    "signal": current_signal_obj,
                    "status": "pending",
                    "notes": ["Merged consecutive runs"] if len(current_run_indices) > 1 else [],
                })
                uid += 1
            # Reset
            current_signal_key = None
            current_signal_obj = None
            current_instruction = None
            current_text = ""
            current_run_indices = []

        for r in p.get("runs", []):
            rtext = r.get("text", "")
            if not rtext:
                continue
            
            font = (r.get("font_color") or "").lower() or None
            hl = (r.get("highlight_color") or "").lower() or None

            signal_key = None
            signal_obj = None
            instruction_type = None

            if font == "blue":
                signal_key = "blue"
                signal_obj = {"action": "update_required", "font_color": "blue", "highlight_color": None, "rule_name": "blue_text"}
                instruction_type = "update_placeholder"
            elif font == "green":
                signal_key = "green"
                signal_obj = {"action": "remove_guidance", "font_color": "green", "highlight_color": None, "rule_name": "green_text"}
                instruction_type = "remove_guidance"
            elif hl == "yellow":
                signal_key = "yellow"
                signal_obj = {"action": "update_required", "font_color": None, "highlight_color": "yellow", "rule_name": "yellow_highlight"}
                instruction_type = "update_placeholder"

            if signal_key == current_signal_key and signal_key is not None:
                current_text += rtext
                current_run_indices.append(r["run_index"])
            else:
                flush_runs()
                if signal_key is not None:
                    current_signal_key = signal_key
                    current_signal_obj = signal_obj
                    current_instruction = instruction_type
                    current_text = rtext
                    current_run_indices = [r["run_index"]]
        
        flush_runs() # Flush any remaining at the end of the paragraph

        # --- Fallbacks ---
        if text and BRACKET_RE.search(text):
            for m in BRACKET_RE.finditer(text):
                units.append({
                    "unit_id": f"U{uid:04d}",
                    "section_title": current_section,
                    "paragraph_index": p["paragraph_index"],
                    "run_indices": None, # Null indicates it relies on paragraph text search
                    "instruction_type": "update_placeholder",
                    "template_text": m.group(0),
                    "signal": {"action": "update_required", "font_color": None, "highlight_color": None, "rule_name": "bracket_placeholder"},
                    "status": "pending",
                    "notes": ["Detected by fallback bracket rule"],
                })
                uid += 1

        lower_text = text.lower()
        if lower_text.startswith("start of example text") or lower_text.startswith("end of example text"):
            units.append({
                "unit_id": f"U{uid:04d}",
                "section_title": current_section,
                "paragraph_index": p["paragraph_index"],
                "run_indices": None,
                "instruction_type": "remove_guidance",
                "template_text": text,
                "signal": {"action": "remove_guidance", "font_color": None, "highlight_color": None, "rule_name": "example_text_marker"},
                "status": "pending",
                "notes": ["Detected by fallback example-text rule"],
            })
            uid += 1

    return units