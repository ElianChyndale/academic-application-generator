"""Strict contracts for profiles, programme facts, and generated materials."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator

StableId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProjectId(StrEnum):
    ECOQUANT = "ecoquant"
    AURALYNQ = "auralynq"
    GREEN_BOND_LENDING = "green-bond-lending"
    AI_RESEARCH_ENGINEERING_LAB = "ai-research-engineering-lab"


class ProgrammeId(StrEnum):
    UCD = "ucd"
    GALWAY = "galway"
    UL = "ul"


class SourceKind(StrEnum):
    TAGGED_REPOSITORY = "tagged-repository"
    OFFICIAL_WEBPAGE = "official-webpage"
    PUBLIC_PROFILE = "public-profile"


class ClaimState(StrEnum):
    IMPLEMENTED = "implemented"
    VALIDATED = "validated"
    EXPERIMENTALLY_SUPPORTED = "experimentally-supported"
    PROTOTYPE_ONLY = "prototype-only"
    PLANNED = "planned"
    PROFILE_FACT = "profile-fact"


class TemporalMode(StrEnum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    NEUTRAL = "neutral"


class MaterialKind(StrEnum):
    INDUSTRY_CV = "industry-cv"
    ACADEMIC_CV = "academic-cv"
    PROJECT_DESCRIPTIONS = "project-descriptions"
    SOP_MATERIALS = "sop-materials"
    PERSONAL_STATEMENT = "personal-statement"
    RESEARCH_INTEREST = "research-interest"
    PROFESSOR_EMAIL = "professor-email"
    SCHOLARSHIP_MATERIALS = "scholarship-materials"
    LINKEDIN_SUMMARY = "linkedin-summary"
    GITHUB_PROFILE = "github-profile"
    WEBSITE_CONTENT = "website-content"
    INTERVIEW_ANSWERS = "interview-answers"
    RECOMMENDER_BRIEF = "recommender-brief"
    PROGRAMME_FIT = "programme-fit"


class SourceRecord(StrictModel):
    source_id: StableId
    kind: SourceKind
    locator: str = Field(min_length=1)
    sha256: Sha256 | None = None
    verified_on: date
    volatile: bool
    note: str = Field(min_length=1)

    @model_validator(mode="after")
    def coherent_source(self) -> SourceRecord:
        if self.kind == SourceKind.OFFICIAL_WEBPAGE:
            HttpUrl(self.locator)
            if not self.volatile or self.sha256 is not None:
                raise ValueError("official webpages must be volatile and omit a hash")
        else:
            if self.sha256 is None or self.volatile:
                raise ValueError("frozen local/repository sources require a hash")
            if (
                "\\" in self.locator
                or self.locator.startswith("/")
                or ":" in self.locator
                or ".." in self.locator.split("/")
            ):
                if not self.locator.startswith("https://github.com/"):
                    raise ValueError("source locators must be relative or tagged GitHub URLs")
        return self


class ProfileClaim(StrictModel):
    claim_id: StableId
    text: str = Field(min_length=1)
    category: StableId
    state: ClaimState
    project_id: ProjectId | None = None
    source_ids: list[StableId] = Field(min_length=1)
    allowed_materials: list[MaterialKind] = Field(min_length=1)
    allowed_temporal_modes: list[TemporalMode] = Field(min_length=1)
    limitation: str = Field(min_length=1)

    @model_validator(mode="after")
    def planned_is_future_only(self) -> ProfileClaim:
        if self.state == ClaimState.PLANNED and set(self.allowed_temporal_modes) != {
            TemporalMode.FUTURE
        }:
            raise ValueError("planned claims must be future-only")
        return self


class NumericFact(StrictModel):
    fact_id: StableId
    token: str = Field(pattern=r"^[0-9]+(?:\.[0-9]+)?$")
    meaning: str = Field(min_length=1)
    source_ids: list[StableId] = Field(min_length=1)
    allowed_materials: list[MaterialKind] = Field(min_length=1)


class ProjectNarrative(StrictModel):
    target_words: Literal[100, 250, 500]
    text: str = Field(min_length=1)
    claim_ids: list[StableId] = Field(min_length=1)


class ProjectRecord(StrictModel):
    project_id: ProjectId
    public_name: str = Field(min_length=1)
    flagship_position: int = Field(ge=1, le=4)
    role: str = Field(min_length=1)
    claim_ids: list[StableId] = Field(min_length=4)
    narratives: list[ProjectNarrative] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def narrative_targets(self) -> ProjectRecord:
        if {item.target_words for item in self.narratives} != {100, 250, 500}:
            raise ValueError("project narratives must cover 100, 250, and 500 words")
        return self


class CandidateProfile(StrictModel):
    schema_version: Literal["0.1.0"] = "0.1.0"
    candidate_id: Literal["yuxin-chen"] = "yuxin-chen"
    public_name: Literal["Yuxin Chen"] = "Yuxin Chen"
    as_of: Literal["2026-07-24"] = "2026-07-24"
    research_identity: str = Field(min_length=1)
    sources: list[SourceRecord] = Field(min_length=5)
    claims: list[ProfileClaim] = Field(min_length=20)
    numeric_facts: list[NumericFact] = Field(default_factory=list)
    projects: list[ProjectRecord] = Field(min_length=4, max_length=4)
    missing_fields: list[str] = Field(min_length=1)
    locked_absent_entities: dict[
        Literal[
            "awards",
            "employment",
            "grades",
            "language_tests",
            "publications",
            "recommendations",
            "transcript_courses",
        ],
        list[str],
    ]

    @model_validator(mode="after")
    def unique_and_complete(self) -> CandidateProfile:
        for label, values in (
            ("sources", [item.source_id for item in self.sources]),
            ("claims", [item.claim_id for item in self.claims]),
            ("numeric facts", [item.fact_id for item in self.numeric_facts]),
            ("projects", [str(item.project_id) for item in self.projects]),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} IDs must be unique")
        if {item.project_id for item in self.projects} != set(ProjectId):
            raise ValueError("profile must contain exactly the four flagship projects")
        if {item.flagship_position for item in self.projects} != {1, 2, 3, 4}:
            raise ValueError("flagship positions must be 1 through 4")
        required_absent = {
            "awards",
            "employment",
            "grades",
            "language_tests",
            "publications",
            "recommendations",
            "transcript_courses",
        }
        if set(self.locked_absent_entities) != required_absent:
            raise ValueError("locked absent entity categories are incomplete")
        if any(self.locked_absent_entities.values()):
            raise ValueError("locked absent entities must remain empty")
        return self


class ProgrammeFact(StrictModel):
    fact_id: StableId
    text: str = Field(min_length=1)
    source_ids: list[StableId] = Field(min_length=1)
    fit_tags: list[StableId] = Field(min_length=1)


class ProgrammeProfile(StrictModel):
    schema_version: Literal["0.1.0"] = "0.1.0"
    programme_id: ProgrammeId
    institution: str = Field(min_length=1)
    programme_name: str = Field(min_length=1)
    course_code: str = Field(min_length=1)
    verified_on: Literal["2026-07-24"] = "2026-07-24"
    refresh_required: Literal[True] = True
    official_sources: list[SourceRecord] = Field(min_length=1)
    facts: list[ProgrammeFact] = Field(min_length=2)
    excluded_volatile_fields: list[str] = Field(min_length=4)

    @model_validator(mode="after")
    def unique_programme_records(self) -> ProgrammeProfile:
        source_ids = [item.source_id for item in self.official_sources]
        fact_ids = [item.fact_id for item in self.facts]
        if len(source_ids) != len(set(source_ids)) or len(fact_ids) != len(set(fact_ids)):
            raise ValueError("programme source and fact IDs must be unique")
        if any(item.kind != SourceKind.OFFICIAL_WEBPAGE for item in self.official_sources):
            raise ValueError("programme sources must be official webpages")
        return self


class MaterialBlock(StrictModel):
    block_id: StableId
    heading: str = Field(min_length=1)
    text: str = Field(min_length=1)
    temporal_mode: TemporalMode
    claim_ids: list[StableId] = Field(default_factory=list)
    programme_fact_ids: list[StableId] = Field(default_factory=list)
    numeric_fact_ids: list[StableId] = Field(default_factory=list)


class GeneratedMaterial(StrictModel):
    schema_version: Literal["0.1.0"] = "0.1.0"
    material_id: StableId
    candidate_id: Literal["yuxin-chen"] = "yuxin-chen"
    kind: MaterialKind
    programme_id: ProgrammeId | None = None
    title: str = Field(min_length=1)
    review_status: Literal["draft-human-verification-required"] = (
        "draft-human-verification-required"
    )
    as_of: Literal["2026-07-24"] = "2026-07-24"
    blocks: list[MaterialBlock] = Field(min_length=1)

    @model_validator(mode="after")
    def programme_scope(self) -> GeneratedMaterial:
        programme_kinds = {
            MaterialKind.SOP_MATERIALS,
            MaterialKind.PERSONAL_STATEMENT,
            MaterialKind.RESEARCH_INTEREST,
            MaterialKind.PROFESSOR_EMAIL,
            MaterialKind.SCHOLARSHIP_MATERIALS,
            MaterialKind.PROGRAMME_FIT,
        }
        if (self.kind in programme_kinds) != (self.programme_id is not None):
            raise ValueError("programme-scoped material and programme ID must match")
        block_ids = [item.block_id for item in self.blocks]
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("block IDs must be unique within a material")
        return self


class ValidationSummary(StrictModel):
    schema_version: Literal["0.1.0"] = "0.1.0"
    profiles: int = Field(ge=0)
    programmes: int = Field(ge=0)
    materials: int = Field(ge=0)
    blocks: int = Field(ge=0)
    claims_used: int = Field(ge=0)
    issues: list[str] = Field(default_factory=list)
    passed: bool
