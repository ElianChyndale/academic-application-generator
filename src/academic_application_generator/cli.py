"""Command-line interface for evidence-constrained application materials."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from academic_application_generator.io import DataError
from academic_application_generator.models import MaterialKind, ProgrammeId
from academic_application_generator.reporting import (
    export_material,
    generate_release,
    load_materials,
    load_profile,
    load_programmes,
)
from academic_application_generator.validation import validate_inputs, validate_materials


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="academic-application",
        description="Generate and audit evidence-constrained application source material.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate public input fixtures")
    validate.add_argument("profile", type=Path)
    validate.add_argument("--programmes", type=Path, default=Path("fixtures/programmes"))

    generate = commands.add_parser("generate", help="generate all application materials")
    generate.add_argument("--profile", type=Path, required=True)
    generate.add_argument("--programmes", type=Path, required=True)
    generate.add_argument("--output", type=Path, required=True)

    audit = commands.add_parser("audit", help="audit structured generated materials")
    audit.add_argument("--materials", type=Path, required=True)
    audit.add_argument("--profile", type=Path, default=Path("fixtures/profile"))
    audit.add_argument("--programmes", type=Path, default=Path("fixtures/programmes"))

    export = commands.add_parser("export", help="export one rendered material")
    export.add_argument("--kind", choices=[str(item) for item in MaterialKind], required=True)
    export.add_argument("--programme", choices=[str(item) for item in ProgrammeId], required=False)
    export.add_argument("--output", type=Path, required=True)

    report = commands.add_parser("report", help="regenerate the release and reports")
    report.add_argument("--output", type=Path, required=True)
    return parser


def _print_issues(issues: list[str]) -> None:
    for issue in issues:
        print(f"ERROR: {issue}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path.cwd().resolve()
    try:
        if args.command == "validate":
            profile = load_profile(args.profile)
            programmes = load_programmes(args.programmes)
            issues = validate_inputs(profile, programmes, root)
            if issues:
                _print_issues(issues)
                return 1
            print(
                f"validation=PASS profiles=1 programmes={len(programmes)} "
                f"claims={len(profile.claims)} projects={len(profile.projects)}"
            )
            return 0
        if args.command == "generate":
            materials, summary = generate_release(
                root,
                args.profile,
                args.programmes,
                args.output,
            )
            print(
                f"generation=PASS materials={len(materials)} blocks={summary.blocks} "
                f"output={args.output.as_posix()}"
            )
            return 0
        if args.command == "audit":
            profile = load_profile(args.profile)
            programmes = load_programmes(args.programmes)
            materials = load_materials(args.materials)
            summary = validate_materials(profile, programmes, materials, root)
            if not summary.passed:
                _print_issues(summary.issues)
                return 1
            print(
                f"audit=PASS materials={summary.materials} blocks={summary.blocks} "
                f"claims-used={summary.claims_used}"
            )
            return 0
        if args.command == "export":
            programme = ProgrammeId(args.programme) if args.programme is not None else None
            target = export_material(root, MaterialKind(args.kind), programme, args.output)
            print(f"export=PASS path={target.relative_to(root).as_posix()}")
            return 0
        if args.command == "report":
            materials, summary = generate_release(
                root,
                Path("fixtures/profile"),
                Path("fixtures/programmes"),
                Path("generated/v0.1"),
                args.output,
            )
            print(
                f"report=PASS materials={len(materials)} blocks={summary.blocks} "
                f"output={args.output.as_posix()}"
            )
            return 0
    except (DataError, OSError, ValidationError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
