# Project design documentation

This directory is the entry point for the agreed anomaly-detection design. The documents are separated by responsibility so that each student can read the part relevant to the current task without searching through one large specification.

**Status:** shared contract revised after finalization review; preprocessing, executable acceptance verification and bundled partner reapproval still gate accepted model training

**Version:** 0.7

**Date:** 2026-07-24

## Workspace and authority boundary

The current data and implementation snapshot is `new-data/`, and the current
design is `docs/design/` under the authority of the consolidated implementation
handoff. `new-data/src/` is auditable input for the next implementation step,
not an implicit amendment to the contract or a frozen future package layout.

The root-level `diğer/` directory is an excluded historical project. Its nested
repository, source, documentation, tests, environment and agent skills must not
be loaded during current implementation work. The two root-level
`autoencoder design*.md` notes and the 2026-07-22 review are also historical.
They can explain how a decision evolved, but they cannot override the handoff or
documents 01–06.

Operational instructions for autonomous coding agents are in
[`AGENTS.md`](../AGENTS.md), with [`CLAUDE.md`](../CLAUDE.md) as the Claude Code
entry point.

## Reading order

| Document | Read it when... | Primary owner |
|---|---|---|
| [2026-07-24 consolidated implementation handoff](handoffs/2026-07-24-implementation-handoff.md) | You need the current normative shared contract or implementation gates. | Both students; revised bundle pending partner reapproval |
| [Partner decision summary](design/00-partner-decision-summary.md) | You need the concise shared decisions and current approval status. | Both students |
| [German split summary](design/00-kurzvorschlag-datenaufteilung-de.md) | You need a non-normative German explanation of the temporal split. | Explanatory only |
| [01 - Project scope and decisions](design/01-project-scope-and-decisions.md) | You need the research question, team boundary or explanation of why the design was chosen. | Both students |
| [02 - Shared data contract](design/02-shared-data-contract.md) | You implement or inspect detailed loading, missingness, splitting, scaling and shared evaluation definitions. | Technical reference |
| [03 - Conv1D autoencoder](design/03-conv1d-autoencoder.md) | You implement or explain the standard and sparse autoencoders. | Alper |
| [04 - Evaluation and injection](design/04-evaluation-and-injection.md) | You implement score export, thresholds, anomaly injection or model comparison after shared preprocessing is frozen. | Operational reference |
| [05 - Responsible AI and evidence](design/05-responsible-ai-and-evidence.md) | You document AI assistance or prepare to explain the development process. | Both students |
| [06 - Checklist and limitations](design/06-checklist-and-limitations.md) | You are about to implement, run final experiments or write the report. | Both students |
| [Pre-implementation environment audit](environment/2026-07-24-pre-implementation.md) | You need the interpreter/package versions used for the partner-pipeline dry run. | Technical provenance |
| [`new-data` SHA-256 manifest](provenance/2026-07-24-new-data.sha256) | You need to identify the complete partner snapshot inspected on 2026-07-24. | Technical provenance |
| [References](design/references.md) | You need the primary sources behind a methodological claim. | Both students |
| [2026-07-22 design evidence review](reviews/2026-07-22-design-evidence-review.md) | You need historical audit findings that predate the current population and split. | Historical evidence |

## Contract at a glance

- Authoritative data: `new-data/data/bad_nauheim_bereinigt.csv`, SHA-256 `af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`.
- Population: 28 retained temporal series; the two area-labelled series remain included.
- Split: training, validation and one continuous test timeline with higher-availability and severe-missingness reporting conditions.
- Missingness: patch only one- or two-hour runs within a true split; patched values may provide input context but never ground truth.
- Time features: calculated in `Europe/Berlin`; split boundaries remain UTC.
- Models: standard and sparse Conv1D autoencoders owned by Alper; the partner owns and documents every LSTM-specific design decision.
- Comparison: immutable run/configuration identities, unique score/label/threshold keys and clean-frozen common support.
- Missingness reporting: one model-independent trailing-24-hour numeric count and bucket alongside model-specific eligibility.
- Evaluation: controlled injection plus untouched-test analysis; synthetic F1 is not presented as real-world accuracy.

## How changes are made

The 2026-07-24 consolidated implementation handoff is the single current authority for shared population, time structure, missingness, interoperability and evaluation. Documents 01–06 implement narrower topics and may not override it. The German split summary is explanatory and non-normative.

A consequential change must record:

1. what changed;
2. why it changed;
3. whether it was made before or after test results were inspected; and
4. which student approved it.

Do not rewrite the pre-results design merely to make an observed result look better. Record deviations in the experiment log and discuss them honestly.

## Reproduce the current data-foundation claims

From the repository root, run:

```text
python scripts/verify_acceptance.py
```

Run the current tests with:

```text
python -m pytest
```

The Session 1 verifier checks the canonical hash, all 28 exact series names,
the complete hourly grid, original-missingness counts and the current half-open
split and reporting-condition definitions. It does not yet verify patching,
calendar features, model window coverage or accepted training readiness.

The retained `scripts/verify_design_contract.py` is historical evidence for the
superseded 26-series design and is not the current acceptance command. The
revised handoff's window and score-coverage values still require later current
executable verification before they become accepted-run evidence.
