from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class DocumentRequest:
    action: str
    doc_type: str
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentResult:
    success: bool
    output_path: Optional[str] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    events: list = field(default_factory=list)


class BaseDocumentDriver:
    def supports(self, request: DocumentRequest) -> bool:
        return False

    def execute(self, request: DocumentRequest) -> DocumentResult:
        raise NotImplementedError
