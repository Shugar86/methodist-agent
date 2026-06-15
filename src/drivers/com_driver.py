import platform
from pathlib import Path

from core.document_environment import BaseDocumentDriver, DocumentRequest, DocumentResult

POWERPOINT_SLIDE_LAYOUT_BLANK = 12


class COMDriver(BaseDocumentDriver):
    def supports(self, request: DocumentRequest) -> bool:
        return platform.system() == "Windows" and request.doc_type in ("docx", "xlsx", "pptx")

    def execute(self, request: DocumentRequest) -> DocumentResult:
        if not self.supports(request):
            return DocumentResult(success=False, message="COM driver not available")
        try:
            import win32com.client
        except ImportError:
            return DocumentResult(success=False, message="pywin32 not installed")
        return self._create(request, win32com.client)

    def _create(self, request: DocumentRequest, win32com_client) -> DocumentResult:
        output_path = Path(request.output_path) if request.output_path else None
        if not output_path:
            return DocumentResult(success=False, message="output_path required")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        app_name = {
            "docx": "Word.Application",
            "xlsx": "Excel.Application",
            "pptx": "PowerPoint.Application",
        }[request.doc_type]
        app = win32com_client.DispatchEx(app_name)
        try:
            app.Visible = False
            if request.doc_type in ("docx", "xlsx"):
                app.DisplayAlerts = False
            title = request.parameters.get("title", "")
            if request.doc_type == "docx":
                doc = app.Documents.Add()
                if title:
                    doc.Content.Text = title
                doc.SaveAs(str(output_path))
                doc.Close()
            elif request.doc_type == "xlsx":
                wb = app.Workbooks.Add()
                ws = wb.Worksheets(1)
                ws.Cells(1, 1).Value = title
                wb.SaveAs(str(output_path))
                wb.Close()
            elif request.doc_type == "pptx":
                prs = app.Presentations.Add()
                slide = prs.Slides.Add(1, POWERPOINT_SLIDE_LAYOUT_BLANK)
                slide.Shapes(1).TextFrame.TextRange.Text = title
                prs.SaveAs(str(output_path))
                prs.Close()
        except Exception as exc:  # noqa: BLE001 - COM failures can vary; report gracefully
            return DocumentResult(success=False, message=f"COM operation failed: {exc}")
        finally:
            app.Quit()

        return DocumentResult(success=True, output_path=str(output_path), message="Created via COM")
