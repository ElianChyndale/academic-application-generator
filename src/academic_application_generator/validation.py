"""Cross-record validation for profiles, programme facts, and materials."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from urllib.parse import urlparse

from academic_application_generator.io import sha256_file
from academic_application_generator.models import (
    CandidateProfile,
    ClaimState,
    GeneratedMaterial,
    MaterialKind,
    NumericFact,
    ProfileClaim,
    ProgrammeFact,
    ProgrammeId,
    ProgrammeProfile,
    ProjectId,
    TemporalMode,
    ValidationSummary,
)

_NUMBER = re.compile(r"(?<![A-Za-z0-9.-])\d+(?:\.\d+)?(?![A-Za-z0-9-])")
_ABSOLUTE_PATH = re.compile(r"(?:(?<![A-Za-z])[A-Za-z]:[\\/]|/(?:home|Users|tmp|var)/)")
_UNSUPPORTED_ASSERTIONS = (
    re.compile(r"\bi published\b", re.IGNORECASE),
    re.compile(r"\bmy publications?\b", re.IGNORECASE),
    re.compile(r"\bi (?:received|won) (?:an? )?award\b", re.IGNORECASE),
    re.compile(r"\bmy gpa\b", re.IGNORECASE),
    re.compile(r"\bi graduated\b", re.IGNORECASE),
    re.compile(r"\bi (?:work|worked|am employed) (?:at|by)\b", re.IGNORECASE),
    re.compile(r"\bscholarship recipient\b", re.IGNORECASE),
    re.compile(r"\bmy recommender (?:says|writes|confirms)\b", re.IGNORECASE),
)
_VOLATILE_OUTPUT_PATTERNS = (
    re.compile(r"\bapplication deadline\b", re.IGNORECASE),
    re.compile(r"\btuition fee\b", re.IGNORECASE),
    re.compile(r"\bprogramme ranking\b", re.IGNORECASE),
    re.compile(r"\badmission (?:chance|probability|likelihood)\b", re.IGNORECASE),
)
_OFFICIAL_HOSTS = {
    ProgrammeId.UCD: {"hub.ucd.ie", "www.ucd.ie"},
    ProgrammeId.GALWAY: {"www.universityofgalway.ie", "universityofgalway.ie"},
    ProgrammeId.UL: {"bookofmodules.ul.ie", "www.ul.ie"},
}
_SNAPSHOT_FILES = {
    "ecoquant-dossier": "ecoquant-manifest.json",
    "auralynq-dossier": "auralynq-manifest.json",
    "green-bond-lending-dossier": "green-bond-lending-manifest.json",
    "ai-research-engineering-lab-dossier": ("ai-research-engineering-lab-manifest.json"),
    "public-research-profile": "public-profile.md",
}
_GENERIC_KINDS = {
    MaterialKind.INDUSTRY_CV,
    MaterialKind.ACADEMIC_CV,
    MaterialKind.PROJECT_DESCRIPTIONS,
    MaterialKind.LINKEDIN_SUMMARY,
    MaterialKind.GITHUB_PROFILE,
    MaterialKind.WEBSITE_CONTENT,
    MaterialKind.INTERVIEW_ANSWERS,
    MaterialKind.RECOMMENDER_BRIEF,
}
_PROGRAMME_KINDS = set(MaterialKind) - _GENERIC_KINDS
_WORD_BANDS = {100: (90, 130), 250: (200, 320), 500: (400, 620)}


def validate_inputs(
    profile: CandidateProfile,
    programmes: Sequence[ProgrammeProfile],
    root: Path,
) -> list[str]:
    issues: list[str] = []
    source_lookup = {item.source_id: item for item in profile.sources}
    claim_lookup = {item.claim_id: item for item in profile.claims}

    for source_id, filename in _SNAPSHOT_FILES.items():
        source = source_lookup.get(source_id)
        path = root / "fixtures/source_snapshots" / filename
        if source is None:
            issues.append(f"missing frozen source: {source_id}")
        elif not path.is_file():
            issues.append(f"missing source snapshot file: {filename}")
        elif source.sha256 != sha256_file(path):
            issues.append(f"source snapshot hash mismatch: {source_id}")

    for claim in profile.claims:
        unknown = sorted(set(claim.source_ids) - set(source_lookup))
        if unknown:
            issues.append(f"{claim.claim_id}: unknown sources {', '.join(unknown)}")
        if claim.project_id is not None and _source_for_project(claim.project_id) not in {
            *claim.source_ids
        }:
            issues.append(f"{claim.claim_id}: project claim lacks its dossier source")
    for numeric_fact in profile.numeric_facts:
        if not set(numeric_fact.source_ids) <= set(source_lookup):
            issues.append(f"{numeric_fact.fact_id}: unknown numeric-fact source")

    for project in profile.projects:
        for claim_id in project.claim_ids:
            project_claim = claim_lookup.get(claim_id)
            if project_claim is None or project_claim.project_id != project.project_id:
                issues.append(f"{project.project_id}: invalid project claim {claim_id}")
        if project.project_id != ProjectId.ECOQUANT:
            public_text = " ".join(
                [
                    project.public_name,
                    project.role,
                    *(item.text for item in project.narratives),
                ]
            )
            if "pdf manager" in public_text.lower():
                issues.append(f"{project.project_id}: PDF Manager must remain EcoQuant support")
        for narrative in project.narratives:
            low, high = _WORD_BANDS[narrative.target_words]
            count = len(narrative.text.split())
            if not low <= count <= high:
                issues.append(
                    f"{project.project_id}/{narrative.target_words}: {count} words "
                    f"outside {low}-{high}"
                )
            if not set(narrative.claim_ids) <= set(project.claim_ids):
                issues.append(f"{project.project_id}: narrative cites another project")

    if len(programmes) != 3 or {item.programme_id for item in programmes} != set(ProgrammeId):
        issues.append("exactly the UCD, Galway, and UL programme profiles are required")
    global_programme_sources: set[str] = set()
    global_programme_facts: set[str] = set()
    for programme in programmes:
        local_sources = {item.source_id for item in programme.official_sources}
        local_facts = {item.fact_id for item in programme.facts}
        if global_programme_sources & local_sources:
            issues.append(f"{programme.programme_id}: duplicate global source ID")
        if global_programme_facts & local_facts:
            issues.append(f"{programme.programme_id}: duplicate global fact ID")
        global_programme_sources |= local_sources
        global_programme_facts |= local_facts
        for source in programme.official_sources:
            host = (urlparse(source.locator).hostname or "").lower()
            if host not in _OFFICIAL_HOSTS[programme.programme_id]:
                issues.append(f"{source.source_id}: source is not on an approved official host")
            if source.verified_on.isoformat() > profile.as_of:
                issues.append(f"{source.source_id}: verification occurs after profile date")
        for programme_fact in programme.facts:
            if not set(programme_fact.source_ids) <= local_sources:
                issues.append(f"{programme_fact.fact_id}: fact cites another programme source")
        required_exclusions = {
            "application deadlines",
            "fees",
            "contact names",
            "scholarship values",
            "rankings",
            "admission likelihood",
        }
        if not required_exclusions <= set(programme.excluded_volatile_fields):
            issues.append(f"{programme.programme_id}: volatile exclusions are incomplete")

    if any(profile.locked_absent_entities.values()):
        issues.append("locked absent entities contain invented records")
    if _ABSOLUTE_PATH.search(profile.model_dump_json()):
        issues.append("profile contains an absolute local path")
    return sorted(set(issues))


def validate_materials(
    profile: CandidateProfile,
    programmes: Sequence[ProgrammeProfile],
    materials: Sequence[GeneratedMaterial],
    root: Path,
) -> ValidationSummary:
    issues = validate_inputs(profile, programmes, root)
    claims: Mapping[str, ProfileClaim] = {item.claim_id: item for item in profile.claims}
    numbers: Mapping[str, NumericFact] = {item.fact_id: item for item in profile.numeric_facts}
    programme_lookup = {item.programme_id: item for item in programmes}
    programme_facts: dict[str, tuple[ProgrammeId, ProgrammeFact]] = {
        fact.fact_id: (programme.programme_id, fact)
        for programme in programmes
        for fact in programme.facts
    }

    material_ids = [item.material_id for item in materials]
    if len(material_ids) != len(set(material_ids)):
        issues.append("material IDs must be globally unique")
    observed_generic = {item.kind for item in materials if item.programme_id is None}
    if observed_generic != _GENERIC_KINDS:
        issues.append("generic material set is incomplete")
    observed_programme = {
        (item.programme_id, item.kind) for item in materials if item.programme_id is not None
    }
    expected_programme = {
        (programme_id, kind) for programme_id in ProgrammeId for kind in _PROGRAMME_KINDS
    }
    if observed_programme != expected_programme:
        issues.append("programme material matrix is incomplete")

    claims_used: set[str] = set()
    for material in materials:
        if material.programme_id is not None and material.programme_id not in programme_lookup:
            issues.append(f"{material.material_id}: unknown programme")
        for block in material.blocks:
            unknown_claims = sorted(set(block.claim_ids) - set(claims))
            if unknown_claims:
                issues.append(
                    f"{material.material_id}/{block.block_id}: unknown claims "
                    f"{', '.join(unknown_claims)}"
                )
                continue
            claims_used.update(block.claim_ids)
            for claim_id in block.claim_ids:
                claim = claims[claim_id]
                if material.kind not in claim.allowed_materials:
                    issues.append(
                        f"{material.material_id}/{block.block_id}: {claim_id} is "
                        "not allowed in this material"
                    )
                if block.temporal_mode not in claim.allowed_temporal_modes:
                    issues.append(
                        f"{material.material_id}/{block.block_id}: {claim_id} has "
                        "an incompatible temporal mode"
                    )
                if claim.state == ClaimState.PLANNED and block.temporal_mode != TemporalMode.FUTURE:
                    issues.append(
                        f"{material.material_id}/{block.block_id}: planned claim "
                        "appears as completed"
                    )

            unknown_facts = sorted(set(block.programme_fact_ids) - set(programme_facts))
            if unknown_facts:
                issues.append(f"{material.material_id}/{block.block_id}: unknown programme facts")
            for fact_id in block.programme_fact_ids:
                owner = programme_facts.get(fact_id)
                if owner is not None and owner[0] != material.programme_id:
                    issues.append(f"{material.material_id}/{block.block_id}: cross-programme fact")
            if material.programme_id is None and block.programme_fact_ids:
                issues.append(
                    f"{material.material_id}/{block.block_id}: generic material "
                    "contains programme facts"
                )

            unknown_numbers = sorted(set(block.numeric_fact_ids) - set(numbers))
            if unknown_numbers:
                issues.append(f"{material.material_id}/{block.block_id}: unknown numeric facts")
            cited_tokens = {
                numbers[fact_id].token for fact_id in block.numeric_fact_ids if fact_id in numbers
            }
            text_tokens = set(_NUMBER.findall(block.text))
            if cited_tokens != text_tokens:
                issues.append(
                    f"{material.material_id}/{block.block_id}: numeric tokens "
                    f"{sorted(text_tokens)} do not match citations {sorted(cited_tokens)}"
                )
            for fact_id in block.numeric_fact_ids:
                fact = numbers.get(fact_id)
                if fact is not None and material.kind not in fact.allowed_materials:
                    issues.append(
                        f"{material.material_id}/{block.block_id}: numeric fact "
                        "is not allowed in this material"
                    )

            for pattern in _UNSUPPORTED_ASSERTIONS:
                if pattern.search(block.text):
                    issues.append(
                        f"{material.material_id}/{block.block_id}: unsupported personal assertion"
                    )
            for pattern in _VOLATILE_OUTPUT_PATTERNS:
                if pattern.search(block.text):
                    issues.append(
                        f"{material.material_id}/{block.block_id}: volatile programme assertion"
                    )
            if _ABSOLUTE_PATH.search(block.text):
                issues.append(f"{material.material_id}/{block.block_id}: absolute path in output")
        if material.programme_id is not None and not any(
            block.programme_fact_ids for block in material.blocks
        ):
            issues.append(f"{material.material_id}: programme material lacks programme facts")

    description = next(
        (item for item in materials if item.kind == MaterialKind.PROJECT_DESCRIPTIONS),
        None,
    )
    if description is not None:
        for project in profile.projects:
            for narrative in project.narratives:
                block_id = f"{project.project_id}-{narrative.target_words}-words"
                description_block = next(
                    (item for item in description.blocks if item.block_id == block_id),
                    None,
                )
                if description_block is None:
                    issues.append(f"project descriptions missing {block_id}")
                else:
                    low, high = _WORD_BANDS[narrative.target_words]
                    if not low <= len(description_block.text.split()) <= high:
                        issues.append(f"{block_id}: generated word band drift")

    return ValidationSummary(
        profiles=1,
        programmes=len(programmes),
        materials=len(materials),
        blocks=sum(len(item.blocks) for item in materials),
        claims_used=len(claims_used),
        issues=sorted(set(issues)),
        passed=not issues,
    )


def _source_for_project(project_id: ProjectId) -> str:
    return f"{project_id}-dossier"
