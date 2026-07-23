# Acceptance Criteria

## Contracts and source integrity

- [x] One public candidate profile and exactly three programme profiles validate.
- [x] Exactly four flagship projects are represented; PDF Manager is EcoQuant support only.
- [x] All profile claims and numeric facts resolve to registered sources.
- [x] Tagged repository-source hashes match their frozen fixture files.
- [x] Programme facts use official sources, carry verification dates, and remain refreshable.
- [x] Missing private academic and personal fields remain explicit and unfilled.

## Consistency and safety

- [x] Planned work cannot appear in past or present-tense achievement blocks.
- [x] Every standalone number in generated text has an exact cited source.
- [x] Project names, technology statements, dates, and programme titles do not drift.
- [x] No paper, publication, award, grade, employment, scholarship-win, or recommendation claim is invented.
- [x] Programme fees, deadlines, contact names, rankings, and admission predictions are absent.
- [x] Every output is labelled as draft material requiring human review.

## Outputs and reproducibility

- [x] Generic materials and all three programme packs contain every required asset.
- [x] Four projects have approximately 100/250/500-word descriptions within fixed bands.
- [x] Inventory, claim usage, consistency, programme-fit, source, and validation artifacts parse and contain records.
- [x] Repeated generation produces identical tracked output hashes.
- [x] Public and packaged Draft 2020-12 schemas match.
- [x] A clean wheel installation loads all packaged schemas.

## Engineering and release

- [x] `validate`, `generate`, `audit`, `export`, and `report` pass.
- [x] Pytest, Ruff, and strict mypy pass.
- [ ] CI passes on Ubuntu/Windows with Python 3.11/3.12.
- [ ] Public repository and `v0.1.0` tag point to the final validated commit.
- [ ] The portfolio task log records commands, CI, URL, and remaining risks.

## Release commands

```text
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests scripts
python -m mypy src/academic_application_generator
academic-application validate fixtures/profile/
academic-application generate --profile fixtures/profile --programmes fixtures/programmes --output generated/v0.1
academic-application audit --materials generated/v0.1/materials.jsonl
academic-application export --kind academic-cv --programme ucd --output exports/
academic-application report --output reports/v0.1
```
