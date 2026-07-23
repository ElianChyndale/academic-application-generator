from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import jsonschema
import pytest

from academic_application_generator.generation import GENERIC_KINDS, PROGRAMME_KINDS
from academic_application_generator.models import MaterialKind, ProgrammeId
from academic_application_generator.reporting import (
    export_material,
    generate_release,
    load_materials,
    material_path,
)


@pytest.fixture()
def built_root(tmp_path: Path, project_root: Path) -> Path:
    shutil.copytree(project_root / "fixtures", tmp_path / "fixtures")
    generate_release(
        tmp_path,
        Path("fixtures/profile"),
        Path("fixtures/programmes"),
        Path("generated/v0.1"),
        Path("reports/v0.1"),
    )
    return tmp_path


@pytest.mark.parametrize("kind", GENERIC_KINDS)
def test_generic_output_exists(built_root: Path, kind: MaterialKind) -> None:
    material = next(
        item
        for item in load_materials(built_root / "generated/v0.1/materials.jsonl")
        if item.kind == kind and item.programme_id is None
    )
    path = material_path(built_root / "generated/v0.1", material)
    assert path.is_file()
    assert "human verification required" in path.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("programme", list(ProgrammeId))
@pytest.mark.parametrize("kind", PROGRAMME_KINDS)
def test_programme_output_exists(
    built_root: Path, programme: ProgrammeId, kind: MaterialKind
) -> None:
    material = next(
        item
        for item in load_materials(built_root / "generated/v0.1/materials.jsonl")
        if item.kind == kind and item.programme_id == programme
    )
    assert material_path(built_root / "generated/v0.1", material).is_file()


def test_machine_artifacts_parse_and_have_records(built_root: Path) -> None:
    results = built_root / "research/results/v0.1"
    for filename in ("material_inventory.csv", "programme_fit_matrix.csv"):
        with (results / filename).open(encoding="utf-8", newline="") as handle:
            assert list(csv.DictReader(handle))
    for filename in (
        "claim_usage.json",
        "source_registry.json",
        "validation_report.json",
    ):
        assert json.loads((results / filename).read_text(encoding="utf-8"))
    rows = [
        json.loads(line)
        for line in (results / "consistency_findings.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert rows


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    paths = sorted(
        [
            *(root / "generated/v0.1").glob("**/*"),
            *(root / "research/results/v0.1").glob("*"),
            *(root / "reports/v0.1").glob("*"),
        ],
        key=lambda item: item.as_posix(),
    )
    for path in paths:
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def test_repeated_release_is_byte_deterministic(built_root: Path) -> None:
    before = _tree_hash(built_root)
    generate_release(
        built_root,
        Path("fixtures/profile"),
        Path("fixtures/programmes"),
        Path("generated/v0.1"),
        Path("reports/v0.1"),
    )
    assert _tree_hash(built_root) == before


def test_export_material(built_root: Path) -> None:
    target = export_material(
        built_root,
        MaterialKind.ACADEMIC_CV,
        ProgrammeId.UCD,
        Path("exports"),
    )
    assert target.is_file()
    assert "Academic CV" in target.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "filename",
    [
        "candidate-profile.schema.json",
        "generated-material.schema.json",
        "programme-profile.schema.json",
        "validation-summary.schema.json",
    ],
)
def test_public_and_packaged_schemas_match(project_root: Path, filename: str) -> None:
    assert (project_root / "schemas" / filename).read_bytes() == (
        project_root / "src/academic_application_generator/schemas" / filename
    ).read_bytes()


def test_candidate_schema_validates_fixture(project_root: Path) -> None:
    schema = json.loads(
        (project_root / "schemas/candidate-profile.schema.json").read_text(encoding="utf-8")
    )
    instance = json.loads(
        (project_root / "fixtures/profile/candidate.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema).validate(instance)


def test_material_schema_validates_generated_records(project_root: Path) -> None:
    schema = json.loads(
        (project_root / "schemas/generated-material.schema.json").read_text(encoding="utf-8")
    )
    validator = jsonschema.Draft202012Validator(schema)
    for item in load_materials(project_root / "generated/v0.1/materials.jsonl"):
        validator.validate(item.model_dump(mode="json"))
