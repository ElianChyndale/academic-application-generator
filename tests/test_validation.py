from __future__ import annotations

from pathlib import Path

from academic_application_generator.models import (
    CandidateProfile,
    GeneratedMaterial,
    ProgrammeProfile,
)
from academic_application_generator.validation import validate_inputs, validate_materials


def _replace_block(
    materials: list[GeneratedMaterial],
    material_index: int,
    block_index: int,
    **updates: object,
) -> list[GeneratedMaterial]:
    changed = list(materials)
    material = changed[material_index]
    blocks = list(material.blocks)
    blocks[block_index] = blocks[block_index].model_copy(update=updates)
    changed[material_index] = material.model_copy(update={"blocks": blocks})
    return changed


def test_valid_release_passes(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    summary = validate_materials(profile, programmes, materials, project_root)
    assert summary.passed
    assert summary.materials == 26
    assert summary.blocks == 80
    assert summary.claims_used == 22


def test_input_source_hash_drift_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
) -> None:
    sources = list(profile.sources)
    sources[0] = sources[0].model_copy(update={"sha256": "0" * 64})
    changed = profile.model_copy(update={"sources": sources})
    issues = validate_inputs(changed, programmes, project_root)
    assert any("hash mismatch" in item for item in issues)


def test_missing_programme_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
) -> None:
    issues = validate_inputs(profile, programmes[:-1], project_root)
    assert any("exactly the UCD" in item for item in issues)


def test_unofficial_programme_host_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
) -> None:
    sources = list(programmes[0].official_sources)
    sources[0] = sources[0].model_copy(update={"locator": "https://unofficial.example/course"})
    programmes[0] = programmes[0].model_copy(update={"official_sources": sources})
    issues = validate_inputs(profile, programmes, project_root)
    assert any("approved official host" in item for item in issues)


def test_project_claim_cross_reference_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
) -> None:
    projects = list(profile.projects)
    projects[0] = projects[0].model_copy(
        update={"claim_ids": [*projects[0].claim_ids[:-1], "auralynq-memory"]}
    )
    changed = profile.model_copy(update={"projects": projects})
    issues = validate_inputs(changed, programmes, project_root)
    assert any("invalid project claim" in item for item in issues)


def test_pdf_manager_outside_ecoquant_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
) -> None:
    projects = list(profile.projects)
    projects[1] = projects[1].model_copy(update={"role": "PDF Manager flagship"})
    changed = profile.model_copy(update={"projects": projects})
    issues = validate_inputs(changed, programmes, project_root)
    assert any("EcoQuant support" in item for item in issues)


def test_planned_claim_in_present_block_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    changed = _replace_block(
        materials,
        0,
        0,
        claim_ids=["ecoquant-external-validation"],
        temporal_mode="present",
    )
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("incompatible temporal mode" in item for item in summary.issues)


def test_unknown_claim_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    changed = _replace_block(materials, 0, 0, claim_ids=["unknown-claim"])
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("unknown claims" in item for item in summary.issues)


def test_unsupported_number_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    text = materials[0].blocks[0].text + " Unsupported result: 99."
    changed = _replace_block(materials, 0, 0, text=text)
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("numeric tokens" in item for item in summary.issues)


def test_unused_numeric_citation_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    changed = _replace_block(
        materials,
        0,
        0,
        numeric_fact_ids=[profile.numeric_facts[0].fact_id],
    )
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("numeric tokens" in item for item in summary.issues)


def test_cross_programme_fact_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    programme_material = next(
        index for index, item in enumerate(materials) if str(item.programme_id) == "galway"
    )
    changed = _replace_block(
        materials,
        programme_material,
        0,
        programme_fact_ids=["ucd-negotiated-path"],
    )
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("cross-programme fact" in item for item in summary.issues)


def test_unsupported_personal_assertion_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    changed = _replace_block(materials, 0, 0, text="I published a paper.")
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("unsupported personal assertion" in item for item in summary.issues)


def test_volatile_programme_assertion_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    programme_material = next(
        index for index, item in enumerate(materials) if item.programme_id is not None
    )
    changed = _replace_block(
        materials,
        programme_material,
        0,
        text="The application deadline is tomorrow.",
    )
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("volatile programme assertion" in item for item in summary.issues)


def test_incomplete_material_matrix_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    summary = validate_materials(profile, programmes, materials[:-1], project_root)
    assert any("matrix is incomplete" in item for item in summary.issues)


def test_project_description_word_drift_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    description_index = next(
        index for index, item in enumerate(materials) if str(item.kind) == "project-descriptions"
    )
    changed = _replace_block(materials, description_index, 0, text="too short")
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("word band drift" in item for item in summary.issues)


def test_absolute_path_in_material_fails(
    project_root: Path,
    profile: CandidateProfile,
    programmes: list[ProgrammeProfile],
    materials: list[GeneratedMaterial],
) -> None:
    changed = _replace_block(materials, 0, 0, text="See C:/private/transcript.pdf")
    summary = validate_materials(profile, programmes, changed, project_root)
    assert any("absolute path" in item for item in summary.issues)
