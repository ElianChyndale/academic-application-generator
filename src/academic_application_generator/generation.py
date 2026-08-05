"""Deterministic generation of structured application source materials."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from academic_application_generator.models import (
    CandidateProfile,
    GeneratedMaterial,
    MaterialBlock,
    MaterialKind,
    ProfileClaim,
    ProgrammeId,
    ProgrammeProfile,
    ProjectId,
    TemporalMode,
)

GENERIC_KINDS = (
    MaterialKind.INDUSTRY_CV,
    MaterialKind.ACADEMIC_CV,
    MaterialKind.PROJECT_DESCRIPTIONS,
    MaterialKind.LINKEDIN_SUMMARY,
    MaterialKind.GITHUB_PROFILE,
    MaterialKind.WEBSITE_CONTENT,
    MaterialKind.INTERVIEW_ANSWERS,
    MaterialKind.RECOMMENDER_BRIEF,
)
PROGRAMME_KINDS = (
    MaterialKind.PROGRAMME_FIT,
    MaterialKind.SOP_MATERIALS,
    MaterialKind.PERSONAL_STATEMENT,
    MaterialKind.RESEARCH_INTEREST,
    MaterialKind.PROFESSOR_EMAIL,
    MaterialKind.SCHOLARSHIP_MATERIALS,
)

_PROJECT_HIGHLIGHTS = {
    ProjectId.ECOQUANT: ("ecoquant-docintel", "ecoquant-valuation"),
    ProjectId.AURALYNQ: ("auralynq-memory", "auralynq-review-validation"),
    ProjectId.GREEN_BOND_LENDING: ("gbl-threshold", "gbl-contract"),
    ProjectId.AI_RESEARCH_ENGINEERING_LAB: (
        "ai-lab-runners",
        "ai-lab-current-verification",
    ),
}
_PROGRAMME_PROJECTS = {
    ProgrammeId.UCD: (
        "ecoquant-docintel",
        "ecoquant-valuation",
        "ai-lab-runners",
        "programme-research-question",
        "programme-e1-retrieval",
        "programme-e5-calibration",
    ),
    ProgrammeId.GALWAY: (
        "ecoquant-docintel",
        "auralynq-memory",
        "ai-lab-results",
        "programme-research-question",
        "programme-e2-table",
        "programme-e7-commercial",
    ),
    ProgrammeId.UL: (
        "ecoquant-valuation",
        "gbl-threshold",
        "ai-lab-runners",
        "programme-research-question",
        "programme-e3-temporal",
        "programme-e4-verification",
    ),
}
_PROGRAMME_FUTURE = {
    ProgrammeId.UCD: "ecoquant-external-validation",
    ProgrammeId.GALWAY: "auralynq-user-efficacy",
    ProgrammeId.UL: "gbl-deployment-audit",
}


def _claim_lookup(profile: CandidateProfile) -> dict[str, ProfileClaim]:
    return {item.claim_id: item for item in profile.claims}


def _block(
    block_id: str,
    heading: str,
    text: str,
    temporal_mode: TemporalMode,
    claim_ids: Iterable[str] = (),
    programme_fact_ids: Iterable[str] = (),
) -> MaterialBlock:
    return MaterialBlock(
        block_id=block_id,
        heading=heading,
        text=text,
        temporal_mode=temporal_mode,
        claim_ids=list(claim_ids),
        programme_fact_ids=list(programme_fact_ids),
    )


def _material(
    material_id: str,
    kind: MaterialKind,
    title: str,
    blocks: Sequence[MaterialBlock],
    programme_id: ProgrammeId | None = None,
) -> GeneratedMaterial:
    return GeneratedMaterial(
        material_id=material_id,
        kind=kind,
        programme_id=programme_id,
        title=title,
        blocks=list(blocks),
    )


def _project_blocks(
    profile: CandidateProfile,
    *,
    prefix: str,
    include_boundaries: bool,
) -> list[MaterialBlock]:
    claims = _claim_lookup(profile)
    blocks: list[MaterialBlock] = []
    for project in profile.projects:
        selected = _PROJECT_HIGHLIGHTS[project.project_id]
        text = " ".join(claims[claim_id].text for claim_id in selected)
        if include_boundaries:
            text += " Boundaries: " + " ".join(claims[claim_id].limitation for claim_id in selected)
        blocks.append(
            _block(
                f"{prefix}-{project.project_id}",
                project.public_name,
                text,
                TemporalMode.PRESENT,
                selected,
            )
        )
    return blocks


def _generic_materials(profile: CandidateProfile) -> list[GeneratedMaterial]:
    claims = _claim_lookup(profile)
    identity = claims["profile-research-identity"].text
    technical = claims["profile-technical-scope"].text

    industry = _material(
        "generic-industry-cv",
        MaterialKind.INDUSTRY_CV,
        "Industry CV source material",
        [
            _block(
                "industry-profile",
                "Profile",
                identity + " " + technical,
                TemporalMode.PRESENT,
                ["profile-research-identity", "profile-technical-scope"],
            ),
            *_project_blocks(profile, prefix="industry", include_boundaries=False),
        ],
    )
    academic = _material(
        "generic-academic-cv",
        MaterialKind.ACADEMIC_CV,
        "Academic CV source material",
        [
            _block(
                "academic-focus",
                "Research focus",
                (
                    identity + " My work emphasises evidence traceability, deterministic "
                    "evaluation, explicit failure cases, and reproducible artifacts."
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity"],
            ),
            *_project_blocks(profile, prefix="academic", include_boundaries=True),
        ],
    )

    description_blocks: list[MaterialBlock] = []
    length_labels = {100: "Short", 250: "Medium", 500: "Long"}
    for project in profile.projects:
        for narrative in project.narratives:
            description_blocks.append(
                _block(
                    f"{project.project_id}-{narrative.target_words}-words",
                    f"{project.public_name} — {length_labels[narrative.target_words]} description",
                    narrative.text,
                    TemporalMode.PRESENT,
                    narrative.claim_ids,
                )
            )
    descriptions = _material(
        "generic-project-descriptions",
        MaterialKind.PROJECT_DESCRIPTIONS,
        "Evidence-bound project descriptions",
        description_blocks,
    )

    linkedin = _material(
        "generic-linkedin-summary",
        MaterialKind.LINKEDIN_SUMMARY,
        "LinkedIn summary source material",
        [
            _block(
                "linkedin-about",
                "About",
                (
                    identity
                    + " "
                    + technical
                    + " I focus on turning applied decision problems into "
                    "reviewable systems with bounded claims and visible limitations."
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity", "profile-technical-scope"],
            )
        ],
    )
    github = _material(
        "generic-github-profile",
        MaterialKind.GITHUB_PROFILE,
        "GitHub profile README source material",
        [
            _block(
                "github-introduction",
                "Research-engineering portfolio",
                identity + " " + technical,
                TemporalMode.PRESENT,
                ["profile-research-identity", "profile-technical-scope"],
            ),
            *_project_blocks(profile, prefix="github", include_boundaries=False),
        ],
    )
    website = _material(
        "generic-website-content",
        MaterialKind.WEBSITE_CONTENT,
        "Portfolio website source material",
        [
            _block(
                "website-thesis",
                "Portfolio thesis",
                (
                    identity + " The portfolio connects document evidence, decision support, "
                    "risk simulation, and reproducible AI foundations."
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity"],
            ),
            *_project_blocks(profile, prefix="website", include_boundaries=True),
        ],
    )
    interview = _material(
        "generic-interview-answers",
        MaterialKind.INTERVIEW_ANSWERS,
        "Interview answer bank",
        [
            _block(
                "interview-direction",
                "What is your research direction?",
                identity + " " + technical,
                TemporalMode.PRESENT,
                ["profile-research-identity", "profile-technical-scope"],
            ),
            _block(
                "interview-verification",
                "How do you avoid overstating project maturity?",
                (
                    claims["ai-lab-current-verification"].text
                    + " I retain failed or blocked verification as evidence of a "
                    "boundary instead of rewriting it as success."
                ),
                TemporalMode.PRESENT,
                ["ai-lab-current-verification"],
            ),
            _block(
                "interview-future",
                "What would you evaluate next?",
                " ".join(
                    claims[claim_id].text
                    for claim_id in (
                        "ecoquant-external-validation",
                        "auralynq-user-efficacy",
                        "gbl-deployment-audit",
                    )
                ),
                TemporalMode.FUTURE,
                [
                    "ecoquant-external-validation",
                    "auralynq-user-efficacy",
                    "gbl-deployment-audit",
                ],
            ),
        ],
    )
    recommender = _material(
        "generic-recommender-brief",
        MaterialKind.RECOMMENDER_BRIEF,
        "Evidence brief for a potential recommender",
        [
            _block(
                "recommender-scope",
                "Candidate direction",
                (
                    identity + " This brief supplies source-backed project evidence for an "
                    "independent recommender; it does not draft or attribute a "
                    "recommendation."
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity"],
            ),
            *_project_blocks(profile, prefix="recommender", include_boundaries=True),
        ],
    )
    return [
        industry,
        academic,
        descriptions,
        linkedin,
        github,
        website,
        interview,
        recommender,
    ]


def _programme_materials(
    profile: CandidateProfile, programme: ProgrammeProfile
) -> list[GeneratedMaterial]:
    claims = _claim_lookup(profile)
    fact_ids = [item.fact_id for item in programme.facts]
    fact_text = " ".join(item.text for item in programme.facts)
    project_claim_ids = list(_PROGRAMME_PROJECTS[programme.programme_id])
    project_text = " ".join(claims[item].text for item in project_claim_ids)
    future_claim_id = _PROGRAMME_FUTURE[programme.programme_id]
    prefix = str(programme.programme_id)
    institution = programme.institution
    programme_name = programme.programme_name

    fit = _material(
        f"{prefix}-programme-fit",
        MaterialKind.PROGRAMME_FIT,
        f"{institution} programme-fit source material",
        [
            _block(
                f"{prefix}-programme-evidence",
                programme_name,
                fact_text,
                TemporalMode.NEUTRAL,
                programme_fact_ids=fact_ids,
            ),
            _block(
                f"{prefix}-portfolio-evidence",
                "Portfolio evidence",
                (
                    project_text + " These bounded systems provide material for discussing fit; "
                    "they do not predict admission."
                ),
                TemporalMode.PRESENT,
                project_claim_ids,
                fact_ids,
            ),
        ],
        programme.programme_id,
    )
    sop = _material(
        f"{prefix}-sop-materials",
        MaterialKind.SOP_MATERIALS,
        f"{institution} statement-of-purpose source material",
        [
            _block(
                f"{prefix}-sop-direction",
                "Academic direction",
                (
                    claims["profile-research-identity"].text
                    + " I want to deepen the theoretical and experimental discipline "
                    "behind these applied systems."
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity"],
                fact_ids[:1],
            ),
            _block(
                f"{prefix}-sop-fit",
                "Programme connection",
                fact_text + " " + project_text,
                TemporalMode.PRESENT,
                project_claim_ids,
                fact_ids,
            ),
            _block(
                f"{prefix}-sop-future",
                "Proposed development",
                claims[future_claim_id].text,
                TemporalMode.FUTURE,
                [future_claim_id],
                fact_ids[-1:],
            ),
        ],
        programme.programme_id,
    )
    personal = _material(
        f"{prefix}-personal-statement",
        MaterialKind.PERSONAL_STATEMENT,
        f"{institution} personal-statement source material",
        [
            _block(
                f"{prefix}-personal-motivation",
                "Motivation",
                (
                    claims["profile-research-identity"].text
                    + " I am motivated by work where a system must expose why a "
                    "decision is supported and where its evidence ends."
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity"],
                fact_ids[:1],
            ),
            _block(
                f"{prefix}-personal-practice",
                "Learning through projects",
                (
                    project_text + " The recurring lesson is that implementation, evaluation, "
                    "and limitation reporting must remain connected."
                ),
                TemporalMode.PRESENT,
                project_claim_ids,
                fact_ids,
            ),
        ],
        programme.programme_id,
    )
    research = _material(
        f"{prefix}-research-interest",
        MaterialKind.RESEARCH_INTEREST,
        f"{institution} research-interest source material",
        [
            _block(
                f"{prefix}-research-question",
                "Research direction",
                (
                    "My central interest is how evidence-grounded AI systems can "
                    "combine retrieval, structured knowledge, calibrated uncertainty, "
                    "and deterministic verification for decision support. "
                    + claims["profile-research-identity"].text
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity"],
                fact_ids,
            ),
            _block(
                f"{prefix}-research-foundation",
                "Existing foundation",
                project_text,
                TemporalMode.PRESENT,
                project_claim_ids,
                fact_ids,
            ),
            _block(
                f"{prefix}-research-next",
                "Next evidence step",
                claims[future_claim_id].text,
                TemporalMode.FUTURE,
                [future_claim_id],
                fact_ids[-1:],
            ),
        ],
        programme.programme_id,
    )
    email = _material(
        f"{prefix}-professor-email",
        MaterialKind.PROFESSOR_EMAIL,
        f"{institution} professor-outreach email draft",
        [
            _block(
                f"{prefix}-email-body",
                "Email body",
                (
                    "Dear [Professor name], I am preparing an application to "
                    f"{programme_name} and am exploring research directions in "
                    "evidence-grounded AI systems. "
                    + claims["profile-research-identity"].text
                    + " "
                    + project_text
                    + " I would value guidance on whether this bounded direction "
                    "connects with current supervised project opportunities. "
                    "Kind regards, Yuxin Chen"
                ),
                TemporalMode.PRESENT,
                ["profile-research-identity", *project_claim_ids],
                fact_ids,
            )
        ],
        programme.programme_id,
    )
    scholarship = _material(
        f"{prefix}-scholarship-materials",
        MaterialKind.SCHOLARSHIP_MATERIALS,
        f"{institution} scholarship-essay source material",
        [
            _block(
                f"{prefix}-scholarship-contribution",
                "Evidence of preparation",
                (
                    claims["profile-technical-scope"].text
                    + " "
                    + project_text
                    + " This material documents preparation and intended contribution; "
                    "it does not assert a scholarship outcome."
                ),
                TemporalMode.PRESENT,
                ["profile-technical-scope", *project_claim_ids],
                fact_ids,
            ),
            _block(
                f"{prefix}-scholarship-development",
                "Development goal",
                claims[future_claim_id].text,
                TemporalMode.FUTURE,
                [future_claim_id],
                fact_ids[-1:],
            ),
        ],
        programme.programme_id,
    )
    return [fit, sop, personal, research, email, scholarship]


def generate_materials(
    profile: CandidateProfile, programmes: Sequence[ProgrammeProfile]
) -> list[GeneratedMaterial]:
    materials = _generic_materials(profile)
    for programme in sorted(programmes, key=lambda item: str(item.programme_id)):
        materials.extend(_programme_materials(profile, programme))
    return materials
