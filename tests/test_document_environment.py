import tempfile
from pathlib import Path

from core.document_environment import DocumentRequest, DocumentResult, BaseDocumentDriver
from core.document_environment import DocumentEnvironment
from core.sandbox import Sandbox
from drivers.native_driver import NativeDriver


def test_document_request_defaults():
    req = DocumentRequest(action="create", doc_type="docx")
    assert req.action == "create"
    assert req.doc_type == "docx"


def test_document_result_fields():
    result = DocumentResult(success=True, output_path="out.docx")
    assert result.success is True
    assert result.output_path == "out.docx"


def test_base_driver_interface():
    driver = BaseDocumentDriver()
    req = DocumentRequest(action="create", doc_type="docx")
    assert driver.supports(req) is False
    try:
        driver.execute(req)
    except NotImplementedError:
        pass
    else:
        assert False, "execute should raise NotImplementedError"


def test_document_environment_selects_native_driver():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test.docx"
        env = DocumentEnvironment(
            sandbox=Sandbox(tmpdir),
            drivers=[NativeDriver()],
        )
        req = DocumentRequest(action="create", doc_type="docx", output_path=str(output), parameters={"title": "Test"})
        result = env.execute(req)
        assert result.success is True
        assert output.exists()
