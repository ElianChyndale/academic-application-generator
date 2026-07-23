# Data Model

## `SourceRecord`

A stable source ID identifies either an immutable tagged repository file or a
volatile official programme page. Repository sources include a SHA-256. Web
sources include an official HTTPS URL, verification date, and refresh flag.

## `ProfileClaim`

A claim has approved wording, a category, an evidence state, source IDs,
allowed material kinds, temporal mode, and explicit limitations. The evidence
states are `implemented`, `validated`, `experimentally-supported`,
`prototype-only`, `planned`, and `profile-fact`.

Planned claims may be used only in future-work blocks. Project claims may not
be silently rewritten into broader technical or impact claims.

## `NumericFact`

Every standalone number permitted in generated text is registered as an exact
token with meaning, source IDs, and allowed material kinds. A material block
must cite every numeric fact it uses, and may not cite an unused numeric fact.

## `CandidateProfile`

The profile records public identity, research direction, source registry,
claims, numeric facts, four flagship projects, skills, missing private fields,
and a fixed `as_of` date. It explicitly locks unsupported entity types such as
publications, awards, grades, and recommendation assertions to empty lists.

## `ProgrammeProfile`

A programme profile records stable identity, official sources, verified facts,
fit tags, volatility, and a refresh date. Programme facts may support fit
language but do not prove admission suitability.

## `MaterialBlock`

Each block contains text, temporal mode, and exact claim, programme-fact, and
numeric-fact citations. Cross-record validation resolves all references and
checks that temporal mode is compatible with claim state.

## `GeneratedMaterial`

A material has a stable ID, candidate, material kind, optional programme,
human-review label, blocks, and the same fixed `as_of` date as the profile.
Markdown is a deterministic rendering of this structured record.

## `ValidationSummary`

The summary records profile, programme, material, block, claim-usage, and issue
counts. A release passes only when all issues are empty.
