from core.environment_check import run_environment_check


def test_run_environment_check():
    report = run_environment_check()
    assert len(report.items) == 3
    assert report.items[0].name == "Microsoft Office (COM)"
    assert isinstance(report.items[0].available, bool)


def test_environment_report_string():
    report = run_environment_check()
    text = report.to_user_string()
    assert "Microsoft Office" in text
    assert "Tesseract" in text
