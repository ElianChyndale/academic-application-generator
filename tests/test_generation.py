from __future__ import annotations

import re

import pytest

from academic_application_generator.generation import (
    GENERIC_KINDS,
    PROGRAMME_KINDS,
    generate_materials,
)
from academic_application_generator.models import (
    CandidateProfile,
    GeneratedMaterial,
    MaterialKind,
    ProgrammeId,
    ProgrammeProfile,
)
from academic_application_generator.reporting import render_material


def test_generation_has_complete_matrix(
    profile: CandidateProfile, programmes: list[ProgrammeProfile]
) -> None:
    materials = generate_materials(profile, programmes)
    assert len(materials) == len(GENERIC_KINDS) + len(PROGRAMME_KINDS) * 3
    assert {item.kind for item in materials if item.programme_id is None} == set(GENERIC_KINDS)
    assert {
        (item.programme_id, item.kind) for item in materials if item.programme_id is not None
    } == {(programme, kind) for programme in ProgrammeId for kind in PROGRAMME_KINDS}


def test_every_rendered_material_requires_human_review(
    materials: list[GeneratedMaterial],
) -> None:
    assert all("human verification required" in render_material(item).lower() for item in materials)


@pytest.mark.parametrize("programme", list(ProgrammeId))
@pytest.mark.parametrize("kind", PROGRAMME_KINDS)
def test_programme_material_uses_programme_evidence(
    materials: list[GeneratedMaterial],
    programme: ProgrammeId,
    kind: MaterialKind,
) -> None:
    material = next(
        item for item in materials if item.programme_id == programme and item.kind == kind
    )
    assert any(block.programme_fact_ids for block in material.blocks)


@pytest.mark.parametrize("kind", GENERIC_KINDS)
def test_generic_material_has_no_programme_facts(
    materials: list[GeneratedMaterial], kind: MaterialKind
) -> None:
    material = next(item for item in materials if item.programme_id is None and item.kind == kind)
    assert all(not block.programme_fact_ids for block in material.blocks)


def test_planned_claims_are_future_only(materials: list[GeneratedMaterial]) -> None:
    planned = {
        "ecoquant-external-validation",
        "auralynq-user-efficacy",
        "gbl-deployment-audit",
        "ai-lab-external-study",
    }
    for material in materials:
        for block in material.blocks:
            if planned & set(block.claim_ids):
                assert str(block.temporal_mode) == "future"


def test_no_locked_personal_claim_pattern(materials: list[GeneratedMaterial]) -> None:
    text = "\n".join(block.text for item in materials for block in item.blocks)
    forbidden = [
        r"\bI published\b",
        r"\bmy GPA\b",
        r"\bI won an award\b",
        r"\bscholarship recipient\b",
    ]
    assert all(re.search(pattern, text, re.IGNORECASE) is None for pattern in forbidden)


def test_project_descriptions_are_exact_frozen_narratives(
    profile: CandidateProfile, materials: list[GeneratedMaterial]
) -> None:
    material = next(item for item in materials if item.kind == MaterialKind.PROJECT_DESCRIPTIONS)
    expected = {
        f"{project.project_id}-{narrative.target_words}-words": narrative.text
        for project in profile.projects
        for narrative in project.narratives
    }
    assert {item.block_id: item.text for item in material.blocks} == expected
