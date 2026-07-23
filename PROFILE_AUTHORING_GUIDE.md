# Profile Authoring Guide

## Use authoritative inputs

Add private academic information only in a private derivative profile. Copy
degree names, institutions, course names, grades, language results, and dates
from authoritative records. Do not publish the derivative profile.

The checked-in profile is deliberately public-safe. It is a reproducibility
fixture, not a complete application record.

## Add claims

Each claim needs:

- stable ID;
- approved wording;
- evidence state;
- source IDs;
- allowed material kinds;
- allowed temporal modes;
- explicit limitation.

Use `planned` only for future work. Do not convert prototype or local-fixture
evidence into deployment, impact, employment, publication, or award claims.

## Add numeric facts

Register every standalone number with its exact token, meaning, source IDs, and
allowed material kinds. The validator rejects both unsupported numbers and
unused numeric citations.

## Preserve four-project scope

The public portfolio has exactly four flagship projects. PDF Manager remains
supporting document-intelligence infrastructure within EcoQuant Pro.
GreenFinanceBench and the other independent repositories are evidence and
training assets, not additional flagships.

## Regenerate

```bash
python scripts/generate_fixtures.py
python scripts/generate_schemas.py
academic-application report --output reports/v0.1
python -m pytest
```
