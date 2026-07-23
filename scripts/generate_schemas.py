"""Generate matching public and packaged Draft 2020-12 schemas."""

from __future__ import annotations

import json
from pathlib import Path

from academic_application_generator.models import (
    CandidateProfile,
    GeneratedMaterial,
    ProgrammeProfile,
    ValidationSummary,
)

SCHEMAS = {
    "candidate-profile.schema.json": CandidateProfile.model_json_schema(),
    "generated-material.schema.json": GeneratedMaterial.model_json_schema(),
    "programme-profile.schema.json": ProgrammeProfile.model_json_schema(),
    "validation-summary.schema.json": ValidationSummary.model_json_schema(),
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for filename, schema in SCHEMAS.items():
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        payload = json.dumps(schema, indent=2, sort_keys=True) + "\n"
        for directory in (
            root / "schemas",
            root / "src/academic_application_generator/schemas",
        ):
            directory.mkdir(parents=True, exist_ok=True)
            (directory / filename).write_text(payload, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
