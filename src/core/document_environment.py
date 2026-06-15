from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.sandbox import Sandbox


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


class DocumentEnvironment:
    def __init__(self, sandbox: Sandbox, drivers: Optional[List[BaseDocumentDriver]] = None, event_bus=None):
        self.sandbox = sandbox
        self.drivers = drivers or []
        self.event_bus = event_bus

    def execute(self, request: DocumentRequest) -> DocumentResult:
        if request.output_path:
            self.sandbox.normalize(request.output_path)
        driver = self._select_driver(request)
        if not driver:
            return DocumentResult(success=False, message="No suitable driver found")
        self._publish("before_execute", {"request": asdict(request)})
        result = driver.execute(request)
        self._publish("after_execute", {"request": asdict(request), "result": asdict(result)})
        return result

    def _select_driver(self, request: DocumentRequest) -> Optional[BaseDocumentDriver]:
        for driver in self.drivers:
            if driver.supports(request):
                return driver
        return None

    def _publish(self, topic: str, payload: dict) -> None:
        if self.event_bus:
            self.event_bus.publish(topic, payload)
