"""Regenerate the checked-in public input fixtures."""

from __future__ import annotations

from pathlib import Path

from academic_application_generator.fixtures_builder import build_profile, build_programmes
from academic_application_generator.io import write_json


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    profile = build_profile(root)
    write_json(root / "fixtures/profile/candidate.json", profile.model_dump(mode="json"))
    for programme in build_programmes():
        write_json(
            root / f"fixtures/programmes/{programme.programme_id}.json",
            programme.model_dump(mode="json"),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
