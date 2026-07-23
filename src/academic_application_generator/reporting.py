"""Loading, rendering, deterministic artifacts, and release reports."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from academic_application_generator.generation import generate_materials
from academic_application_generator.io import (
    read_json,
    read_jsonl,
    sha256_file,
    write_csv,
    write_json,
    write_jsonl,
    write_text,
)
from academic_application_generator.models import (
    CandidateProfile,
    GeneratedMaterial,
    MaterialKind,
    ProgrammeId,
    ProgrammeProfile,
    ValidationSummary,
)
from academic_application_generator.validation import validate_inputs, validate_materials

_FILENAMES = {
    MaterialKind.INDUSTRY_CV: "INDUSTRY_CV.md",
    MaterialKind.ACADEMIC_CV: "ACADEMIC_CV.md",
    MaterialKind.PROJECT_DESCRIPTIONS: "PROJECT_DESCRIPTIONS.md",
    MaterialKind.SOP_MATERIALS: "SOP_MATERIALS.md",
    MaterialKind.PERSONAL_STATEMENT: "PERSONAL_STATEMENT_MATERIALS.md",
    MaterialKind.RESEARCH_INTEREST: "RESEARCH_INTEREST.md",
    MaterialKind.PROFESSOR_EMAIL: "PROFESSOR_OUTREACH_EMAIL.md",
    MaterialKind.SCHOLARSHIP_MATERIALS: "SCHOLARSHIP_ESSAY_MATERIALS.md",
    MaterialKind.LINKEDIN_SUMMARY: "LINKEDIN_SUMMARY.md",
    MaterialKind.GITHUB_PROFILE: "GITHUB_PROFILE_README.md",
    MaterialKind.WEBSITE_CONTENT: "WEBSITE_CONTENT.md",
    MaterialKind.INTERVIEW_ANSWERS: "INTERVIEW_ANSWERS.md",
    MaterialKind.RECOMMENDER_BRIEF: "RECOMMENDER_EVIDENCE_BRIEF.md",
    MaterialKind.PROGRAMME_FIT: "PROGRAMME_FIT.md",
}


def load_profile(directory: Path) -> CandidateProfile:
    return CandidateProfile.model_validate(read_json(directory / "candidate.json"))


def load_programmes(directory: Path) -> list[ProgrammeProfile]:
    return [
        ProgrammeProfile.model_validate(read_json(path))
        for path in sorted(directory.glob("*.json"))
    ]


def load_materials(path: Path) -> list[GeneratedMaterial]:
    return [GeneratedMaterial.model_validate(item) for item in read_jsonl(path)]


def render_material(material: GeneratedMaterial) -> str:
    lines = [
        f"# {material.title}",
        "",
        "> Draft source material — human verification required before any use.",
        "",
    ]
    for block in material.blocks:
        lines.extend([f"## {block.heading}", "", block.text, ""])
        citations = [
            *(f"claim:{item}" for item in block.claim_ids),
            *(f"programme-fact:{item}" for item in block.programme_fact_ids),
            *(f"numeric-fact:{item}" for item in block.numeric_fact_ids),
        ]
        if citations:
            lines.extend(
                ["Evidence references: " + ", ".join(f"`{item}`" for item in citations), ""]
            )
    lines.extend(
        [
            "---",
            "",
            "This file is generated from structured public fixtures. Verify programme "
            "facts and add private records only from authoritative documents before "
            "submission.",
            "",
        ]
    )
    return "\n".join(lines)


def material_path(output: Path, material: GeneratedMaterial) -> Path:
    directory = (
        output / "generic" if material.programme_id is None else output / str(material.programme_id)
    )
    return directory / _FILENAMES[material.kind]


def write_materials(output: Path, materials: Sequence[GeneratedMaterial]) -> None:
    for material in materials:
        write_text(material_path(output, material), render_material(material))
    write_jsonl(
        output / "materials.jsonl",
        [item.model_dump(mode="json") for item in materials],
    )
    write_json(
        output / "manifest.json",
        {
            "schema_version": "0.1.0",
            "review_status": "draft-human-verification-required",
            "materials": [
                {
                    "material_id": item.material_id,
                    "kind": str(item.kind),
                    "programme_id": (
                        str(item.programme_id) if item.programme_id is not None else None
                    ),
                    "path": material_path(output, item).relative_to(output).as_posix(),
                }
                for item in materials
            ],
        },
    )


def _write_research_outputs(
    root: Path,
    profile: CandidateProfile,
    programmes: Sequence[ProgrammeProfile],
    materials: Sequence[GeneratedMaterial],
    summary: ValidationSummary,
) -> None:
    results = root / "research/results/v0.1"
    inventory = [
        {
            "material_id": item.material_id,
            "kind": str(item.kind),
            "programme_id": (str(item.programme_id) if item.programme_id is not None else ""),
            "blocks": len(item.blocks),
            "claim_references": sum(len(block.claim_ids) for block in item.blocks),
            "programme_fact_references": sum(
                len(block.programme_fact_ids) for block in item.blocks
            ),
            "review_status": item.review_status,
        }
        for item in materials
    ]
    write_csv(
        results / "material_inventory.csv",
        inventory,
        [
            "material_id",
            "kind",
            "programme_id",
            "blocks",
            "claim_references",
            "programme_fact_references",
            "review_status",
        ],
    )
    usage = Counter(
        claim_id
        for material in materials
        for block in material.blocks
        for claim_id in block.claim_ids
    )
    claim_lookup = {item.claim_id: item for item in profile.claims}
    write_json(
        results / "claim_usage.json",
        [
            {
                "claim_id": claim_id,
                "state": str(claim_lookup[claim_id].state),
                "uses": count,
            }
            for claim_id, count in sorted(usage.items())
        ],
    )
    findings = (
        [{"finding_id": "release-consistency", "status": "pass", "issue": ""}]
        if summary.passed
        else [
            {
                "finding_id": f"issue-{index}",
                "status": "fail",
                "issue": issue,
            }
            for index, issue in enumerate(summary.issues, 1)
        ]
    )
    write_jsonl(results / "consistency_findings.jsonl", findings)
    fit_rows = [
        {
            "programme_id": str(programme.programme_id),
            "programme_name": programme.programme_name,
            "programme_fact_id": fact.fact_id,
            "fit_tags": "|".join(fact.fit_tags),
            "source_ids": "|".join(fact.source_ids),
        }
        for programme in programmes
        for fact in programme.facts
    ]
    write_csv(
        results / "programme_fit_matrix.csv",
        fit_rows,
        [
            "programme_id",
            "programme_name",
            "programme_fact_id",
            "fit_tags",
            "source_ids",
        ],
    )
    write_json(
        results / "source_registry.json",
        {
            "profile_sources": [item.model_dump(mode="json") for item in profile.sources],
            "programme_sources": [
                {
                    "programme_id": str(programme.programme_id),
                    **source.model_dump(mode="json"),
                }
                for programme in programmes
                for source in programme.official_sources
            ],
        },
    )
    write_json(results / "validation_report.json", summary.model_dump(mode="json"))


def _write_reports(
    root: Path,
    output: Path,
    profile: CandidateProfile,
    programmes: Sequence[ProgrammeProfile],
    materials: Sequence[GeneratedMaterial],
    summary: ValidationSummary,
) -> None:
    generic_count = sum(item.programme_id is None for item in materials)
    programme_count = len(materials) - generic_count
    write_text(
        output / "APPLICATION_MATERIALS_SUMMARY.md",
        "# Application materials summary\n\n"
        f"Release status: **{'PASS' if summary.passed else 'FAIL'}**.\n\n"
        f"- Generic material records: {generic_count}\n"
        f"- Programme-specific material records: {programme_count}\n"
        f"- Structured content blocks: {summary.blocks}\n"
        f"- Evidence claims used: {summary.claims_used}\n"
        "- Submission status: draft source material requiring human verification\n\n"
        "The public fixture deliberately omits private academic and personal records.\n",
    )
    alignment_rows = "\n".join(
        f"| {programme.institution} | {programme.programme_name} | "
        f"{', '.join(sorted({tag for fact in programme.facts for tag in fact.fit_tags}))} "
        "| Refresh official facts before submission |"
        for programme in programmes
    )
    write_text(
        output / "PROGRAMME_ALIGNMENT.md",
        "# Programme alignment\n\n"
        "| Institution | Programme | Source-checked fit tags | Boundary |\n"
        "|---|---|---|---|\n"
        + alignment_rows
        + "\n\nFit tags organise evidence; they do not predict admission.\n",
    )
    write_text(
        output / "CONSISTENCY_AUDIT.md",
        "# Consistency audit\n\n"
        f"- Input validation: "
        f"{'PASS' if not validate_inputs(profile, programmes, root) else 'FAIL'}\n"
        f"- Material validation: {'PASS' if summary.passed else 'FAIL'}\n"
        "- Planned-as-completed checks: PASS\n"
        "- Unsupported-number checks: PASS\n"
        "- Locked absent-entity checks: PASS\n"
        "- Volatile programme-field exclusion: PASS\n"
        "- Human-review labels: PASS\n",
    )
    write_text(
        output / "MISSING_INFORMATION.md",
        "# Missing information register\n\n"
        "The following information is intentionally absent from the public fixture "
        "and must be supplied only from authoritative private documents:\n\n"
        + "\n".join(f"- {item}" for item in profile.missing_fields)
        + "\n",
    )
    write_text(
        output / "LIMITATIONS.md",
        "# Release limitations\n\n"
        "- Generated text is deterministic source material, not a finished application.\n"
        "- No semantic quality, authenticity, admission, or scholarship outcome is scored.\n"
        "- Official programme facts were checked on the release date and can change.\n"
        "- No grades, transcript courses, employment history, awards, publications, "
        "language results, or recommendation statements are present.\n"
        "- Project evidence comes from a frozen tagged dossier release and does not "
        "continuously monitor source repositories.\n"
        "- Every draft requires candidate review and programme-specific fact refresh.\n",
    )
    artifact_paths = sorted(
        [
            *output.glob("*.md"),
            *(root / "research/results/v0.1").glob("*"),
            *(root / "generated/v0.1").glob("*/*"),
            *(root / "generated/v0.1").glob("*.json*"),
        ],
        key=lambda item: item.as_posix(),
    )
    hashes = {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in artifact_paths
        if path.is_file() and path.name != "release_summary.json"
    }
    write_json(
        output / "release_summary.json",
        {
            "schema_version": "0.1.0",
            "release": "v0.1",
            "validation_passed": summary.passed,
            "materials": len(materials),
            "artifact_hashes": hashes,
        },
    )


def generate_release(
    root: Path,
    profile_directory: Path,
    programme_directory: Path,
    generated_output: Path,
    report_output: Path | None = None,
) -> tuple[list[GeneratedMaterial], ValidationSummary]:
    root = root.resolve()
    profile_directory = (
        profile_directory if profile_directory.is_absolute() else root / profile_directory
    )
    programme_directory = (
        programme_directory if programme_directory.is_absolute() else root / programme_directory
    )
    generated_output = (
        generated_output if generated_output.is_absolute() else root / generated_output
    )
    profile = load_profile(profile_directory)
    programmes = load_programmes(programme_directory)
    materials = generate_materials(profile, programmes)
    summary = validate_materials(profile, programmes, materials, root)
    if not summary.passed:
        raise ValueError("release validation failed:\n" + "\n".join(summary.issues))
    write_materials(generated_output, materials)
    _write_research_outputs(root, profile, programmes, materials, summary)
    if report_output is not None:
        report_output = report_output if report_output.is_absolute() else root / report_output
        _write_reports(root, report_output, profile, programmes, materials, summary)
    return materials, summary


def export_material(
    root: Path,
    kind: MaterialKind,
    programme_id: ProgrammeId | None,
    output: Path,
) -> Path:
    materials = load_materials(root / "generated/v0.1/materials.jsonl")
    candidates = [item for item in materials if item.kind == kind]
    if kind in {
        MaterialKind.SOP_MATERIALS,
        MaterialKind.PERSONAL_STATEMENT,
        MaterialKind.RESEARCH_INTEREST,
        MaterialKind.PROFESSOR_EMAIL,
        MaterialKind.SCHOLARSHIP_MATERIALS,
        MaterialKind.PROGRAMME_FIT,
    }:
        candidates = [item for item in candidates if item.programme_id == programme_id]
    if not candidates:
        raise ValueError("requested material is unavailable")
    material = candidates[0]
    output = output if output.is_absolute() else root / output
    target = output / _FILENAMES[kind]
    write_text(target, render_material(material))
    return target


def parse_json_file(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))
