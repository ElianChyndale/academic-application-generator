# Academic Application Generator v0.1 Specification

## Purpose

Academic Application Generator is a standalone, deterministic system for
building evidence-constrained source material for MSc/RA applications. It
turns one public candidate profile, four project dossiers, and three
source-checked programme profiles into consistent Markdown and machine-readable
provenance.

It is a supporting portfolio asset, not a fifth flagship project. It does not
import or modify source-project code, use an LLM, submit applications, contact
people, or infer private academic records.

## Public profile boundary

Version 0.1 contains only public portfolio information. Grades, transcripts,
course histories, employment dates, private contact details, recommendation
letters, awards, publications, language-test results, and legal identity
documents are deliberately absent. Generated materials expose a missing-data
register instead of inventing them.

## Evidence rules

Every reusable statement has a stable claim ID, evidence state, source IDs,
and permitted material kinds. Project wording is derived from the tagged
Project Evidence Dossiers v0.1 release. Programme fit uses source-checked
official pages captured on 24 July 2026 and marks programme facts as volatile.

The generator enforces:

- planned work cannot appear as completed work;
- every standalone number in generated text resolves to a cited numeric fact;
- project, technology, programme, and date statements cite registered sources;
- names, programme titles, project titles, and evidence states remain
  consistent across materials;
- absent grades, courses, publications, awards, and recommendation content stay
  absent;
- programme deadlines, fees, contacts, and scholarship values are excluded
  from generated drafts because they change frequently.

## Generated assets

Generic outputs:

- industry CV source material;
- academic CV source material;
- four project descriptions at approximately 100, 250, and 500 words;
- LinkedIn summary;
- GitHub profile README;
- website copy;
- interview answer bank;
- recommender evidence brief.

Each of the UCD, University of Galway, and University of Limerick packs adds:

- programme-fit matrix;
- statement-of-purpose material;
- personal-statement material;
- research-interest statement;
- professor-outreach email draft;
- scholarship-essay material.

All outputs are labelled as drafts requiring human verification. Semantic
quality is not automatically scored.

## CLI

```text
academic-application validate fixtures/profile/
academic-application generate --profile fixtures/profile --programmes fixtures/programmes --output generated/v0.1
academic-application audit --materials generated/v0.1/materials.jsonl
academic-application export --kind academic-cv --programme ucd --output exports/
academic-application report --output reports/v0.1
```

## Explicit exclusions

Version 0.1 does not generate DOCX/PDF files, scrape live admissions pages,
select professors, send email, complete application forms, write recommendation
letters, predict admission outcomes, rank universities, or create claims about
papers, awards, grades, employment, scholarships, or external impact.
