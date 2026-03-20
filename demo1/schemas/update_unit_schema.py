from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any

@dataclass
class TemplateSignal:
    action: str  # update_required | remove_guidance | mixed_edit
    font_color: Optional[str] = None
    highlight_color: Optional[str] = None
    rule_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class UpdateUnit:
    unit_id: str
    section_title: str
    paragraph_index: int
    run_index: Optional[int]
    instruction_type: str
    template_text: str
    signal: TemplateSignal
    status: str = 'pending'
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['signal'] = self.signal.to_dict()
        return data

        