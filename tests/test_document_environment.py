from core.document_environment import DocumentRequest, DocumentResult, BaseDocumentDriver


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
