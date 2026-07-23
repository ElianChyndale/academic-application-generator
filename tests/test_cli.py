from __future__ import annotations

import shutil
from pathlib import Path

from academic_application_generator.cli import main


def _fixture_root(tmp_path: Path, project_root: Path) -> Path:
    shutil.copytree(project_root / "fixtures", tmp_path / "fixtures")
    return tmp_path


def test_validate_cli(project_root: Path, monkeypatch: object, capsys: object) -> None:
    monkeypatch.chdir(project_root)  # type: ignore[attr-defined]
    assert main(["validate", "fixtures/profile"]) == 0
    assert "validation=PASS" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_generate_audit_report_and_export_cli(
    tmp_path: Path,
    project_root: Path,
    monkeypatch: object,
    capsys: object,
) -> None:
    root = _fixture_root(tmp_path, project_root)
    monkeypatch.chdir(root)  # type: ignore[attr-defined]
    assert (
        main(
            [
                "generate",
                "--profile",
                "fixtures/profile",
                "--programmes",
                "fixtures/programmes",
                "--output",
                "generated/v0.1",
            ]
        )
        == 0
    )
    assert main(["audit", "--materials", "generated/v0.1/materials.jsonl"]) == 0
    assert main(["report", "--output", "reports/v0.1"]) == 0
    assert (
        main(
            [
                "export",
                "--kind",
                "academic-cv",
                "--programme",
                "ucd",
                "--output",
                "exports",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "generation=PASS" in output
    assert "audit=PASS" in output
    assert "report=PASS" in output
    assert "export=PASS" in output


def test_malformed_profile_returns_error(
    tmp_path: Path, project_root: Path, monkeypatch: object
) -> None:
    root = _fixture_root(tmp_path, project_root)
    (root / "fixtures/profile/candidate.json").write_text("{", encoding="utf-8")
    monkeypatch.chdir(root)  # type: ignore[attr-defined]
    assert main(["validate", "fixtures/profile"]) == 2


def test_missing_materials_returns_error(
    tmp_path: Path, project_root: Path, monkeypatch: object
) -> None:
    root = _fixture_root(tmp_path, project_root)
    monkeypatch.chdir(root)  # type: ignore[attr-defined]
    assert main(["audit", "--materials", "missing.jsonl"]) == 2
