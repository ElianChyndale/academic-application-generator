from __future__ import annotations

import pytest
from pydantic import ValidationError

from academic_application_generator.models import (
    CandidateProfile,
    GeneratedMaterial,
    MaterialBlock,
    ProfileClaim,
    ProgrammeProfile,
    SourceRecord,
)


def _official(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "source_id": "official-source",
        "kind": "official-webpage",
        "locator": "https://example.edu/programme",
        "sha256": None,
        "verified_on": "2026-07-24",
        "volatile": True,
        "note": "official",
    }
    value.update(updates)
    return value


@pytest.mark.parametrize(
    "updates",
    [
        {"locator": "not-a-url"},
        {"volatile": False},
        {"sha256": "a" * 64},
    ],
)
def test_official_source_contract_rejects_invalid_values(
    updates: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        SourceRecord.model_validate(_official(**updates))


@pytest.mark.parametrize(
    "updates",
    [
        {"sha256": None},
        {"volatile": True},
        {"locator": "C:/private/profile.md"},
        {"locator": "../profile.md"},
    ],
)
def test_frozen_source_contract_rejects_invalid_values(
    updates: dict[str, object],
) -> None:
    value = {
        "source_id": "frozen-source",
        "kind": "public-profile",
        "locator": "fixtures/profile.md",
        "sha256": "a" * 64,
        "verified_on": "2026-07-24",
        "volatile": False,
        "note": "frozen",
        **updates,
    }
    with pytest.raises(ValidationError):
        SourceRecord.model_validate(value)


def test_planned_claim_must_be_future_only(profile: CandidateProfile) -> None:
    raw = profile.claims[-1].model_dump(mode="json")
    raw.update(
        {
            "claim_id": "planned-example",
            "state": "planned",
            "allowed_temporal_modes": ["present"],
        }
    )
    with pytest.raises(ValidationError):
        ProfileClaim.model_validate(raw)


def test_locked_absent_entities_must_be_empty(profile: CandidateProfile) -> None:
    raw = profile.model_dump(mode="json")
    raw["locked_absent_entities"]["publications"] = ["invented paper"]
    with pytest.raises(ValidationError):
        CandidateProfile.model_validate(raw)


def test_locked_absent_entity_categories_must_be_complete(
    profile: CandidateProfile,
) -> None:
    raw = profile.model_dump(mode="json")
    del raw["locked_absent_entities"]["grades"]
    with pytest.raises(ValidationError):
        CandidateProfile.model_validate(raw)


def test_profile_requires_all_four_projects(profile: CandidateProfile) -> None:
    raw = profile.model_dump(mode="json")
    raw["projects"] = raw["projects"][:-1]
    with pytest.raises(ValidationError):
        CandidateProfile.model_validate(raw)


def test_programme_requires_official_sources(
    programmes: list[ProgrammeProfile],
) -> None:
    raw = programmes[0].model_dump(mode="json")
    raw["official_sources"][0]["kind"] = "public-profile"
    raw["official_sources"][0]["sha256"] = "a" * 64
    raw["official_sources"][0]["volatile"] = False
    with pytest.raises(ValidationError):
        ProgrammeProfile.model_validate(raw)


@pytest.mark.parametrize(
    ("kind", "programme"),
    [
        ("academic-cv", "ucd"),
        ("sop-materials", None),
    ],
)
def test_material_programme_scope_must_match(kind: str, programme: str | None) -> None:
    with pytest.raises(ValidationError):
        GeneratedMaterial(
            material_id="bad-material",
            kind=kind,
            programme_id=programme,
            title="Bad",
            blocks=[
                MaterialBlock(
                    block_id="body",
                    heading="Body",
                    text="Text",
                    temporal_mode="neutral",
                )
            ],
        )


def test_material_rejects_duplicate_block_ids() -> None:
    block = MaterialBlock(
        block_id="body",
        heading="Body",
        text="Text",
        temporal_mode="neutral",
    )
    with pytest.raises(ValidationError):
        GeneratedMaterial(
            material_id="bad-material",
            kind="academic-cv",
            title="Bad",
            blocks=[block, block],
        )
