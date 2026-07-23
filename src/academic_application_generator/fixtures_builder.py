"""Build the checked-in public profile and programme fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from academic_application_generator.io import read_json, sha256_file
from academic_application_generator.models import (
    CandidateProfile,
    ClaimState,
    MaterialKind,
    NumericFact,
    ProfileClaim,
    ProgrammeFact,
    ProgrammeId,
    ProgrammeProfile,
    ProjectId,
    ProjectNarrative,
    ProjectRecord,
    SourceKind,
    SourceRecord,
    TemporalMode,
)

_TAG = "v0.1.0"
_DOSSIER_BASE = f"https://github.com/ElianChyndale/project-evidence-dossiers/blob/{_TAG}/dossiers"

_SNAPSHOTS = {
    ProjectId.ECOQUANT: "ecoquant-manifest.json",
    ProjectId.AURALYNQ: "auralynq-manifest.json",
    ProjectId.GREEN_BOND_LENDING: "green-bond-lending-manifest.json",
    ProjectId.AI_RESEARCH_ENGINEERING_LAB: "ai-research-engineering-lab-manifest.json",
}

_PLANNED_MATERIALS = [
    MaterialKind.SOP_MATERIALS,
    MaterialKind.PERSONAL_STATEMENT,
    MaterialKind.RESEARCH_INTEREST,
    MaterialKind.PROFESSOR_EMAIL,
    MaterialKind.SCHOLARSHIP_MATERIALS,
    MaterialKind.INTERVIEW_ANSWERS,
    MaterialKind.PROGRAMME_FIT,
]


def _source_id(project_id: ProjectId) -> str:
    return f"{project_id}-dossier"


def build_profile(root: Path) -> CandidateProfile:
    snapshot_dir = root / "fixtures/source_snapshots"
    sources: list[SourceRecord] = []
    claims: list[ProfileClaim] = []
    numeric_facts: list[NumericFact] = []
    projects: list[ProjectRecord] = []
    all_materials = list(MaterialKind)

    for project_id, filename in _SNAPSHOTS.items():
        path = snapshot_dir / filename
        raw: dict[str, Any] = read_json(path)
        source_id = _source_id(project_id)
        sources.append(
            SourceRecord(
                source_id=source_id,
                kind=SourceKind.TAGGED_REPOSITORY,
                locator=f"{_DOSSIER_BASE}/{project_id}/manifest.json",
                sha256=sha256_file(path),
                verified_on="2026-07-24",
                volatile=False,
                note="Frozen from the public v0.1.0 evidence-dossier release.",
            )
        )
        raw_claims: list[dict[str, Any]] = raw["claims"]
        for raw_claim in raw_claims:
            state = ClaimState(raw_claim["state"])
            claims.append(
                ProfileClaim(
                    claim_id=raw_claim["claim_id"],
                    text=raw_claim["approved_text"],
                    category=raw_claim["category"],
                    state=state,
                    project_id=project_id,
                    source_ids=[source_id],
                    allowed_materials=(
                        _PLANNED_MATERIALS if state == ClaimState.PLANNED else all_materials
                    ),
                    allowed_temporal_modes=(
                        [TemporalMode.FUTURE]
                        if state == ClaimState.PLANNED
                        else [TemporalMode.PAST, TemporalMode.PRESENT, TemporalMode.NEUTRAL]
                    ),
                    limitation=raw_claim["limitations"][0],
                )
            )
            for index, assertion in enumerate(raw_claim["numeric_assertions"], 1):
                numeric_facts.append(
                    NumericFact(
                        fact_id=f"{raw_claim['claim_id']}-number-{index}",
                        token=assertion["token"],
                        meaning=assertion["meaning"],
                        source_ids=[source_id],
                        allowed_materials=all_materials,
                    )
                )
        projects.append(
            ProjectRecord(
                project_id=project_id,
                public_name=raw["public_name"],
                flagship_position=raw["flagship_position"],
                role=raw["role"],
                claim_ids=[item["claim_id"] for item in raw_claims],
                narratives=[ProjectNarrative.model_validate(item) for item in raw["narratives"]],
            )
        )

    public_profile_path = snapshot_dir / "public-profile.md"
    sources.append(
        SourceRecord(
            source_id="public-research-profile",
            kind=SourceKind.PUBLIC_PROFILE,
            locator="fixtures/source_snapshots/public-profile.md",
            sha256=sha256_file(public_profile_path),
            verified_on="2026-07-24",
            volatile=False,
            note="Frozen public portfolio profile; private academic records are excluded.",
        )
    )
    claims.extend(
        [
            ProfileClaim(
                claim_id="profile-research-identity",
                text=(
                    "I build reproducible AI research-engineering systems for "
                    "financial, enterprise, and learning decision intelligence."
                ),
                category="research-identity",
                state=ClaimState.PROFILE_FACT,
                source_ids=["public-research-profile"],
                allowed_materials=all_materials,
                allowed_temporal_modes=[TemporalMode.PRESENT, TemporalMode.NEUTRAL],
                limitation="This is a portfolio direction, not an employment title.",
            ),
            ProfileClaim(
                claim_id="profile-technical-scope",
                text=(
                    "The public portfolio demonstrates Python, TypeScript, Solidity, "
                    "retrieval evaluation, risk simulation, technical writing, and "
                    "reproducibility practices."
                ),
                category="technical-scope",
                state=ClaimState.PROFILE_FACT,
                source_ids=[
                    "public-research-profile",
                    *[_source_id(item) for item in ProjectId],
                ],
                allowed_materials=all_materials,
                allowed_temporal_modes=[TemporalMode.PAST, TemporalMode.PRESENT],
                limitation="Breadth is evidenced by bounded projects, not professional tenure.",
            ),
        ]
    )
    return CandidateProfile(
        research_identity=(
            "Trustworthy AI systems for financial, enterprise, and learning decision intelligence"
        ),
        sources=sources,
        claims=claims,
        numeric_facts=numeric_facts,
        projects=sorted(projects, key=lambda item: item.flagship_position),
        missing_fields=[
            "academic degree records",
            "verified transcript course names",
            "grades and GPA",
            "employment history and dates",
            "language-test results",
            "private contact details",
            "awards and scholarships received",
            "publications",
            "recommender-authored statements",
        ],
        locked_absent_entities={
            "awards": [],
            "employment": [],
            "grades": [],
            "language_tests": [],
            "publications": [],
            "recommendations": [],
            "transcript_courses": [],
        },
    )


def build_programmes() -> list[ProgrammeProfile]:
    common_exclusions = [
        "application deadlines",
        "fees",
        "contact names",
        "scholarship values",
        "rankings",
        "admission likelihood",
    ]
    return [
        ProgrammeProfile(
            programme_id=ProgrammeId.UCD,
            institution="University College Dublin",
            programme_name="MSc Computer Science (Negotiated Learning)",
            course_code="T150",
            official_sources=[
                SourceRecord(
                    source_id="ucd-official-course",
                    kind=SourceKind.OFFICIAL_WEBPAGE,
                    locator=("https://hub.ucd.ie/usis/%21W_HU_MENU.P_PUBLISH?MAJR=T150&p_tag=PROG"),
                    verified_on="2026-07-24",
                    volatile=True,
                    note="Official programme page; details require pre-submission refresh.",
                )
            ],
            facts=[
                ProgrammeFact(
                    fact_id="ucd-negotiated-path",
                    text=(
                        "The programme uses a negotiated-learning model that allows "
                        "students to tailor a computing pathway to prior experience "
                        "and career goals."
                    ),
                    source_ids=["ucd-official-course"],
                    fit_tags=["customisable-path", "computing-breadth"],
                ),
                ProgrammeFact(
                    fact_id="ucd-machine-learning-options",
                    text=(
                        "The official description includes machine learning, data "
                        "mining, programming, and information visualisation among its "
                        "computing options."
                    ),
                    source_ids=["ucd-official-course"],
                    fit_tags=["machine-learning", "data-systems"],
                ),
            ],
            excluded_volatile_fields=common_exclusions,
        ),
        ProgrammeProfile(
            programme_id=ProgrammeId.GALWAY,
            institution="University of Galway",
            programme_name="MSc Computer Science—Artificial Intelligence",
            course_code="MSC-MAI",
            official_sources=[
                SourceRecord(
                    source_id="galway-official-course",
                    kind=SourceKind.OFFICIAL_WEBPAGE,
                    locator=(
                        "https://www.universityofgalway.ie/courses/"
                        "taught-postgraduate-courses/"
                        "computer-science-artificial-intelligence.html"
                    ),
                    verified_on="2026-07-24",
                    volatile=True,
                    note="Official programme page; curriculum may change.",
                )
            ],
            facts=[
                ProgrammeFact(
                    fact_id="galway-core-ai",
                    text=(
                        "The official curriculum combines machine learning, deep "
                        "learning, natural language processing, information retrieval, "
                        "AI ethics, and agent-oriented study."
                    ),
                    source_ids=["galway-official-course"],
                    fit_tags=["machine-learning", "retrieval", "responsible-ai", "agents"],
                ),
                ProgrammeFact(
                    fact_id="galway-knowledge-systems",
                    text=(
                        "The programme lists knowledge representation, knowledge "
                        "graphs, and a substantial individual project among its "
                        "current study opportunities."
                    ),
                    source_ids=["galway-official-course"],
                    fit_tags=["knowledge-graphs", "research-project"],
                ),
            ],
            excluded_volatile_fields=common_exclusions,
        ),
        ProgrammeProfile(
            programme_id=ProgrammeId.UL,
            institution="University of Limerick",
            programme_name="MSc Artificial Intelligence & Machine Learning",
            course_code="MSAIMLTFA",
            official_sources=[
                SourceRecord(
                    source_id="ul-official-ml-module",
                    kind=SourceKind.OFFICIAL_WEBPAGE,
                    locator=(
                        "https://bookofmodules.ul.ie/Default.aspx?ModuleCodeParameter=%7CCE4051%7C"
                    ),
                    verified_on="2026-07-24",
                    volatile=True,
                    note="Official module record linked to the programme.",
                ),
                SourceRecord(
                    source_id="ul-official-project-module",
                    kind=SourceKind.OFFICIAL_WEBPAGE,
                    locator=(
                        "https://bookofmodules.ul.ie/Default.aspx?ModuleCodeParameter=%7CCS6143%7C"
                    ),
                    verified_on="2026-07-24",
                    volatile=True,
                    note="Official AI and machine-learning project module record.",
                ),
            ],
            facts=[
                ProgrammeFact(
                    fact_id="ul-applied-ml",
                    text=(
                        "Official programme-linked modules emphasise data engineering, "
                        "machine-learning implementation, evaluation, visualisation, "
                        "and potential data bias."
                    ),
                    source_ids=["ul-official-ml-module"],
                    fit_tags=["applied-machine-learning", "evaluation", "data-systems"],
                ),
                ProgrammeFact(
                    fact_id="ul-independent-project",
                    text=(
                        "The official AI and machine-learning project module emphasises "
                        "independent research, methodology, analysis, ethical concerns, "
                        "and professional presentation."
                    ),
                    source_ids=["ul-official-project-module"],
                    fit_tags=["research-project", "methodology", "responsible-ai"],
                ),
            ],
            excluded_volatile_fields=common_exclusions,
        ),
    ]
