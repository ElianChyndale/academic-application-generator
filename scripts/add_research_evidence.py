"""Add E0-E8 research evidence to the candidate profile (one-time migration)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "fixtures/profile/candidate.json"

BASE = "https://github.com/ElianChyndale/EcoQuant-Financial-Intelligence/blob/main/"

NEW_SOURCES = [
    {"source_id": "programme-overview", "kind": "tagged-repository",
     "locator": BASE + "research/reports/RESEARCH_PROGRAMME_OVERVIEW.md",
     "note": "E0-E8 research programme overview (committed on main).",
     "sha256": "1f24cd155e0886b3366499eaf6823ab3f458ea5947bad593c309430115023488",
     "verified_on": "2026-08-06", "volatile": False},
    {"source_id": "e1-retrieval", "kind": "tagged-repository",
     "locator": BASE + "research/results/e1_retrieval_summary.json",
     "note": "E1 retrieval baselines over FinanceBench.",
     "sha256": "4f018f443a4eb6386e363ce8aed3d2159a1cf4d7102b1eaeceb33764308e9490",
     "verified_on": "2026-08-06", "volatile": False},
    {"source_id": "e2-table", "kind": "tagged-repository",
     "locator": BASE + "research/results/e2_table_summary.json",
     "note": "E2 table reasoning over GRI-QA quant.",
     "sha256": "118d65165b8aa21d010e8334ab899e346a065397358d2cb0bc3e36cd1ed0d5fe",
     "verified_on": "2026-08-06", "volatile": False},
    {"source_id": "e3-temporal", "kind": "tagged-repository",
     "locator": BASE + "research/results/e3_temporal_summary.json",
     "note": "E3 temporal contradiction over SEC XBRL.",
     "sha256": "b10070dae5377676144916fbd66d00e80a09ce44500f8f82a6b7e75a8b31f30f",
     "verified_on": "2026-08-06", "volatile": False},
    {"source_id": "e4-verification", "kind": "tagged-repository",
     "locator": BASE + "research/results/e4_verification_summary.json",
     "note": "E4 evidence verification.",
     "sha256": "7432bc6a6d648a61e1613dde92e7174014af72430ee3c2f0bb0b34a4f6aad457",
     "verified_on": "2026-08-06", "volatile": False},
    {"source_id": "e5-calibration", "kind": "tagged-repository",
     "locator": BASE + "research/results/e5_calibration_summary.json",
     "note": "E5 calibration and selective prediction.",
     "sha256": "16424ea27daa4bb091a0faf96f2dc36b4af39214932a2bafe34406f2ce3b202d",
     "verified_on": "2026-08-06", "volatile": False},
    {"source_id": "e7-commercial", "kind": "tagged-repository",
     "locator": BASE + "research/results/e7_commercial_summary.json",
     "note": "E7 cross-domain commercial analysis.",
     "sha256": "4042d31129ff7584e9bc7cb8bc726e49baf5ebdc81d749f3b77e633ece2be7f7",
     "verified_on": "2026-08-06", "volatile": False},
    {"source_id": "e8-integration", "kind": "tagged-repository",
     "locator": BASE + "research/results/e8_integration_summary.json",
     "note": "E8 EcoQuant integration comparison.",
     "sha256": "2a17306150e7daad328a746bba9f8285c45d35be0346a96f440735726dc6dd3c",
     "verified_on": "2026-08-06", "volatile": False},
]

ALL_MATERIALS = [
    "industry-cv", "academic-cv", "project-descriptions", "sop-materials",
    "personal-statement", "research-interest", "professor-email",
    "scholarship-materials", "linkedin-summary", "github-profile",
    "website-content", "interview-answers", "recommender-brief", "programme-fit",
]

NEW_CLAIMS = [
    {"claim_id": "programme-research-question", "project_id": "ecoquant",
     "category": "research-programme", "state": "experimentally-supported",
     "text": ("I designed a multi-experiment research programme (E0-E8) around one "
              "central question: how retrieval, table reasoning, temporal contradiction "
              "handling, verification, calibration, and human oversight combine for "
              "reliable financial document intelligence."),
     "source_ids": ["programme-overview"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "Internal research on public data; not externally validated."},
    {"claim_id": "programme-e1-retrieval", "project_id": "ecoquant",
     "category": "retrieval", "state": "experimentally-supported",
     "text": ("On the FinanceBench public sample (150 real 10-K questions), dense "
              "retrieval achieved higher Recall@5 than BM25/TF-IDF/LSA/long-context, "
              "with company-clustered bootstrap CIs; method preference reversed "
              "across datasets."),
     "source_ids": ["e1-retrieval"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "Two datasets; reranker baseline blocked by external asset."},
    {"claim_id": "programme-e2-table", "project_id": "ecoquant",
     "category": "table-reasoning", "state": "experimentally-supported",
     "text": ("Separating deterministic calculation from retrieval answered 94% of "
              "266 real environmental-table questions within 1% when the correct "
              "table was known; retrieval error, not calculation error, dominated "
              "mistakes."),
     "source_ids": ["e2-table"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "GRI-QA quant subset only."},
    {"claim_id": "programme-e3-temporal", "project_id": "ecoquant",
     "category": "temporal", "state": "experimentally-supported",
     "text": ("On SEC EDGAR XBRL facts, source-time filtering eliminated future "
              "information (0.339 to 0.000) and valid-time filtering eliminated "
              "expired evidence (0.089 to 0.000); restatement-aware retrieval "
              "improved contradiction F1 by 76%."),
     "source_ids": ["e3-temporal"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "Three companies; small amended-filing class."},
    {"claim_id": "programme-e4-verification", "project_id": "ecoquant",
     "category": "verification", "state": "experimentally-supported",
     "text": ("A multi-layer deterministic verifier rejected every injected "
              "ungrounded number (false-pass rate 0.000) with scale-normalized "
              "matching; presence-based verification is bounded because most "
              "answers are derived values."),
     "source_ids": ["e4-verification"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "Benchmark of 60 cases; no LLM verifier."},
    {"claim_id": "programme-e5-calibration", "project_id": "ecoquant",
     "category": "calibration", "state": "experimentally-supported",
     "text": ("Retrieval confidence separated correct from incorrect predictions "
              "(AUROC 0.923); at 90% supported-answer precision, only ~0.6% of cases "
              "could be auto-accepted — calibration certifies precision but does not "
              "create it."),
     "source_ids": ["e5-calibration"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "FinanceBench only; correctness = top-1 hit."},
    {"claim_id": "programme-e7-commercial", "project_id": "ecoquant",
     "category": "commercial-analysis", "state": "experimentally-supported",
     "text": ("The evidence-to-decision method generalized to commercial analysis: "
              "6 companies across 4 domains analyzed from raw SEC XBRL with "
              "source-linked margins, FCFF, ROIC, and explicit fact/inference/"
              "assumption separation; values matched public financials."),
     "source_ids": ["e7-commercial"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "Public-data track only; simplified ratio conventions."},
    {"claim_id": "programme-e8-integration", "project_id": "ecoquant",
     "category": "integration", "state": "experimentally-supported",
     "text": ("Replacing the prompt-only honesty score with the evidence pipeline "
              "raised citation validity from 0 to 1.0 and review routing from 0 to "
              "67%; the AI/non-AI boundary holds (AI produces attestation + "
              "confidence + review status, never a spread)."),
     "source_ids": ["e8-integration"], "allowed_materials": ALL_MATERIALS,
     "allowed_temporal_modes": ["past", "present", "neutral"],
     "limitation": "Six demonstration cases."},
]


def main() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    existing_sources = {s["source_id"] for s in profile["sources"]}
    added_sources = 0
    for source in NEW_SOURCES:
        if source["source_id"] not in existing_sources:
            profile["sources"].append(source)
            added_sources += 1
    existing_claims = {cl["claim_id"] for cl in profile["claims"]}
    added_claims = 0
    for claim in NEW_CLAIMS:
        if claim["claim_id"] not in existing_claims:
            profile["claims"].append(claim)
            added_claims += 1
    PROFILE.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"added {added_sources} sources, {added_claims} claims")


if __name__ == "__main__":
    main()
