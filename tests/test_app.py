from types import SimpleNamespace

import app


def test_main_analyzes_valid_image_and_prints_response(monkeypatch, capsys):
    calls = {}
    monkeypatch.setattr(
        "sys.argv", ["app.py", "proof.png"]
    )
    monkeypatch.setattr(
        app,
        "validate_image",
        lambda path: SimpleNamespace(valid=True, message=f"Valid image: {path}"),
    )

    def analyze(prompt, image_path=None):
        calls["prompt"] = prompt
        calls["image_path"] = image_path
        return "Amount: $25.00"

    monkeypatch.setattr(app, "request_ai_response", analyze)

    assert app.main() == 0
    assert calls["image_path"] == "proof.png"
    assert calls["prompt"]
    assert capsys.readouterr().out == "Success: Valid image: proof.png\nAmount: $25.00\n"


def test_main_preserves_validation_failure_and_skips_analysis(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["app.py", "bad.png"])
    monkeypatch.setattr(
        app,
        "validate_image",
        lambda path: SimpleNamespace(valid=False, message="File content is not a valid, decodable image."),
    )
    monkeypatch.setattr(
        app,
        "request_ai_response",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("AI must not be called")),
    )

    assert app.main() == 1
    assert capsys.readouterr().out == "Error: File content is not a valid, decodable image.\n"


def test_main_reports_ai_failure(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["app.py", "proof.png"])
    monkeypatch.setattr(
        app,
        "validate_image",
        lambda path: SimpleNamespace(valid=True, message=f"Valid image: {path}"),
    )
    monkeypatch.setattr(
        app,
        "request_ai_response",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("service unavailable")),
    )

    assert app.main() == 1
    assert capsys.readouterr().out == "Success: Valid image: proof.png\nAI error: service unavailable\n"
