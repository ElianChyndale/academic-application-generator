# Academic Application Generator

Academic Application Generator is an offline, evidence-constrained system for
preparing consistent MSc/RA application source material. It generates drafts
from one public candidate profile, four frozen project dossiers, and three
source-checked programme profiles.

It is a supporting portfolio asset, not a fifth flagship project. It does not
use an LLM, submit forms, send email, select professors, predict admission, or
invent missing personal records.

## Release scope

Version 0.1 generates:

- industry and academic CV source material;
- short, medium, and long descriptions for each flagship project;
- LinkedIn, GitHub profile, and website copy;
- interview answers and a recommender evidence brief;
- programme-fit, statement-of-purpose, personal-statement, research-interest,
  professor-email, and scholarship-essay material for UCD, University of
  Galway, and University of Limerick.

Every file is marked `Draft source material — human verification required`.
Structured JSONL keeps the exact claim and programme-fact references behind
each paragraph.

## Quick start

```bash
python -m pip install -e ".[dev]"
academic-application validate fixtures/profile/
academic-application generate \
  --profile fixtures/profile \
  --programmes fixtures/programmes \
  --output generated/v0.1
academic-application audit --materials generated/v0.1/materials.jsonl
academic-application report --output reports/v0.1
```

Export one rendered artifact:

```bash
academic-application export \
  --kind academic-cv \
  --programme ucd \
  --output exports/
```

## Evidence boundary

Project claims are frozen from
[Project Evidence Dossiers v0.1.0](https://github.com/ElianChyndale/project-evidence-dossiers/tree/v0.1.0).
The public profile deliberately omits grades, transcript courses, employment
history, language-test results, private contact details, awards, publications,
and recommender-authored statements.

Programme facts were checked on 24 July 2026 against official sources:

- [UCD MSc Computer Science (Negotiated Learning)](https://hub.ucd.ie/usis/%21W_HU_MENU.P_PUBLISH?MAJR=T150&p_tag=PROG)
- [University of Galway MSc Computer Science—Artificial Intelligence](https://www.universityofgalway.ie/courses/taught-postgraduate-courses/computer-science-artificial-intelligence.html)
- [University of Limerick machine-learning module record](https://bookofmodules.ul.ie/Default.aspx?ModuleCodeParameter=%7CCE4051%7C)
- [University of Limerick AI/ML project module record](https://bookofmodules.ul.ie/Default.aspx?ModuleCodeParameter=%7CCS6143%7C)

Programme facts are volatile. Refresh them from official pages before using a
draft in an application.

## Safety rules

- Planned work is permitted only in future-work blocks.
- Every standalone numeric result requires an exact registered source.
- Programme fees, deadlines, rankings, contact names, and admission
  probabilities are excluded.
- Locked absent entity types must remain empty.
- Professor names remain placeholders until the candidate verifies fit.
- The recommender brief supplies evidence but never authors or attributes a
  recommendation.

## Repository map

- `fixtures/profile/`: the public candidate profile.
- `fixtures/programmes/`: source-checked, refreshable programme profiles.
- `fixtures/source_snapshots/`: frozen public evidence inputs.
- `generated/v0.1/`: generic and programme-specific Markdown plus JSONL.
- `research/results/v0.1/`: machine-readable consistency and provenance output.
- `reports/v0.1/`: release-level review reports.
- `schemas/`: public Draft 2020-12 schemas.
- `src/academic_application_generator/`: models, generation, validation, CLI,
  and reporting.
- `tests/`: contract, mutation, CLI, schema, and reproducibility checks.

See [HUMAN_REVIEW_CHECKLIST.md](HUMAN_REVIEW_CHECKLIST.md) before any real use.

## License

MIT.
