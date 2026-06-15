from pathlib import Path
import tempfile

from drivers.native_driver import NativeDriver
from core.document_environment import DocumentRequest


def test_native_driver_creates_docx():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test.docx"
        driver = NativeDriver()
        req = DocumentRequest(
            action="create",
            doc_type="docx",
            output_path=str(output),
            parameters={"title": "Hello"},
        )
        result = driver.execute(req)
        assert result.success is True
        assert output.exists()
