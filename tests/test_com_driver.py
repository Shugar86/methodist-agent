from unittest.mock import patch

from drivers.com_driver import COMDriver
from core.document_environment import DocumentRequest


def test_com_driver_available_on_windows_only():
    driver = COMDriver()
    with patch("drivers.com_driver.platform.system", return_value="Linux"):
        assert driver.supports(DocumentRequest(action="create", doc_type="docx")) is False
    with patch("drivers.com_driver.platform.system", return_value="Windows"):
        assert driver.supports(DocumentRequest(action="create", doc_type="docx")) is True
