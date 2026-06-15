from unittest.mock import MagicMock, patch

from drivers.com_driver import COMDriver
from core.document_environment import DocumentRequest


def test_com_driver_available_on_windows_only():
    driver = COMDriver()
    with patch("drivers.com_driver.platform.system", return_value="Linux"):
        assert driver.supports(DocumentRequest(action="create", doc_type="docx")) is False
    with patch("drivers.com_driver.platform.system", return_value="Windows"):
        assert driver.supports(DocumentRequest(action="create", doc_type="docx")) is True


def test_execute_returns_not_available_on_linux():
    driver = COMDriver()
    with patch("drivers.com_driver.platform.system", return_value="Linux"):
        result = driver.execute(DocumentRequest(action="create", doc_type="docx"))
    assert result.success is False
    assert result.message == "COM driver not available"


def test_execute_returns_pywin32_not_installed_on_import_error():
    driver = COMDriver()
    with patch("drivers.com_driver.platform.system", return_value="Windows"):
        with patch("builtins.__import__", side_effect=ImportError("No module named win32com")):
            result = driver.execute(DocumentRequest(action="create", doc_type="docx"))
    assert result.success is False
    assert result.message == "pywin32 not installed"


def test_execute_returns_output_path_required():
    driver = COMDriver()
    win32com_client = MagicMock()
    request = DocumentRequest(action="create", doc_type="docx", output_path="")
    result = driver._create(request, win32com_client)
    assert result.success is False
    assert result.message == "output_path required"


def _make_save_as_create_file(output_path):
    def _save_as(path):
        output_path.write_bytes(b"mocked")

    return _save_as


def test_create_docx_saves_file(tmp_path):
    driver = COMDriver()
    win32com_client = MagicMock()
    app_mock = win32com_client.DispatchEx.return_value
    doc_mock = app_mock.Documents.Add.return_value

    output_path = tmp_path / "test.docx"
    doc_mock.SaveAs.side_effect = _make_save_as_create_file(output_path)

    request = DocumentRequest(
        action="create",
        doc_type="docx",
        output_path=str(output_path),
        parameters={"title": "Hello"},
    )
    result = driver._create(request, win32com_client)

    assert result.success is True
    assert result.output_path == str(output_path)
    win32com_client.DispatchEx.assert_called_once_with("Word.Application")
    app_mock.Documents.Add.assert_called_once()
    app_mock.Visible = False
    assert app_mock.DisplayAlerts is False
    doc_mock.SaveAs.assert_called_once_with(str(output_path))
    doc_mock.Close.assert_called_once()
    assert output_path.exists()
    app_mock.Quit.assert_called_once()


def test_create_xlsx_saves_file(tmp_path):
    driver = COMDriver()
    win32com_client = MagicMock()
    app_mock = win32com_client.DispatchEx.return_value
    wb_mock = app_mock.Workbooks.Add.return_value
    ws_mock = wb_mock.Worksheets.return_value

    output_path = tmp_path / "test.xlsx"
    wb_mock.SaveAs.side_effect = _make_save_as_create_file(output_path)

    request = DocumentRequest(
        action="create",
        doc_type="xlsx",
        output_path=str(output_path),
        parameters={"title": "Hello"},
    )
    result = driver._create(request, win32com_client)

    assert result.success is True
    assert result.output_path == str(output_path)
    win32com_client.DispatchEx.assert_called_once_with("Excel.Application")
    app_mock.Workbooks.Add.assert_called_once()
    app_mock.Visible = False
    assert app_mock.DisplayAlerts is False
    ws_mock.Cells.assert_called_once_with(1, 1)
    wb_mock.SaveAs.assert_called_once_with(str(output_path))
    wb_mock.Close.assert_called_once()
    assert output_path.exists()
    app_mock.Quit.assert_called_once()


def test_create_pptx_saves_file_without_display_alerts(tmp_path):
    driver = COMDriver()
    win32com_client = MagicMock()
    app_mock = win32com_client.DispatchEx.return_value
    prs_mock = app_mock.Presentations.Add.return_value
    slide_mock = prs_mock.Slides.Add.return_value

    output_path = tmp_path / "test.pptx"
    prs_mock.SaveAs.side_effect = _make_save_as_create_file(output_path)

    request = DocumentRequest(
        action="create",
        doc_type="pptx",
        output_path=str(output_path),
        parameters={"title": "Hello"},
    )
    result = driver._create(request, win32com_client)

    assert result.success is True
    assert result.output_path == str(output_path)
    win32com_client.DispatchEx.assert_called_once_with("PowerPoint.Application")
    app_mock.Presentations.Add.assert_called_once()
    app_mock.Visible = False
    # PowerPoint does not expose DisplayAlerts in this driver
    assert isinstance(app_mock.DisplayAlerts, MagicMock)
    prs_mock.Slides.Add.assert_called_once_with(1, 12)
    slide_mock.Shapes.return_value.TextFrame.TextRange.Text = "Hello"
    prs_mock.SaveAs.assert_called_once_with(str(output_path))
    prs_mock.Close.assert_called_once()
    assert output_path.exists()
    app_mock.Quit.assert_called_once()


def test_create_returns_failure_on_com_exception(tmp_path):
    driver = COMDriver()
    win32com_client = MagicMock()
    app_mock = win32com_client.DispatchEx.return_value
    app_mock.Documents.Add.side_effect = RuntimeError("COM error")

    output_path = tmp_path / "test.docx"
    request = DocumentRequest(
        action="create",
        doc_type="docx",
        output_path=str(output_path),
    )
    result = driver._create(request, win32com_client)

    assert result.success is False
    assert "COM operation failed" in result.message
    app_mock.Quit.assert_called_once()
