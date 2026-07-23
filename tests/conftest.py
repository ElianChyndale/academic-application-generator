from __future__ import annotations

from pathlib import Path

import pytest

from academic_application_generator.generation import generate_materials
from academic_application_generator.models import (
    CandidateProfile,
    GeneratedMaterial,
    ProgrammeProfile,
)
from academic_application_generator.reporting import load_profile, load_programmes


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def profile(project_root: Path) -> CandidateProfile:
    return load_profile(project_root / "fixtures/profile")


@pytest.fixture()
def programmes(project_root: Path) -> list[ProgrammeProfile]:
    return load_programmes(project_root / "fixtures/programmes")


@pytest.fixture()
def materials(
    profile: CandidateProfile, programmes: list[ProgrammeProfile]
) -> list[GeneratedMaterial]:
    return generate_materials(profile, programmes)
