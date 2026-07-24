# Project instructions for coding agents

## Mission

Build the current Bad Nauheim pedestrian-count anomaly-detection study from the
approved design, with reproducible data handling, leak-safe evaluation, readable
code, and evidence that both students can explain.

The study compares:

- Alper's standard and sparse Conv1D reconstruction autoencoders; and
- the project partner's separately specified LSTM detector.

The comparison is a short, context-bound case study of detector families under
shared data and evaluation rules. It is not a production system, a
classification task, or proof that one architecture is generally superior.

## Authority and workspace boundaries

Use this priority order. A lower item may not override a higher one.

1. [`docs/handoffs/2026-07-24-implementation-handoff.md`](docs/handoffs/2026-07-24-implementation-handoff.md)
   is the normative shared contract.
2. [`docs/design/`](docs/design) contains the current topic-specific design:
   scope, shared data contract, Conv1D model, evaluation, responsible-AI process,
   checklist, and references.
3. [`docs/README.md`](docs/README.md) is the documentation index and status
   summary.
4. [`new-data/data/bad_nauheim_bereinigt.csv`](new-data/data/bad_nauheim_bereinigt.csv)
   is the pinned canonical dataset. Code in [`new-data/src/`](new-data/src) is a
   partner snapshot and audit input; it is not automatically contract-compliant.

These sources are historical and non-authoritative unless a task explicitly asks
for archaeology:

- `diğer/` in its entirety, including its nested Git repository, source, docs,
  tests, virtual environment, and Claude skills;
- `autoencoder design and alternatives.md`;
- `autoencoder design decisions.md`;
- `docs/reviews/2026-07-22-design-evidence-review.md`;
- the earlier 26-series design encoded by `scripts/verify_design_contract.py`.

Do not search, import, execute, repair, or copy from `diğer/` during current
implementation work. Exclude it from broad searches. If historical material is
consulted at the user's request, label every resulting claim against the current
contract before using it.

If two active documents disagree about population, periods, masks,
preprocessing, ownership, or evaluation, stop that line of implementation.
Report the conflict and update the appropriate current document; never blend the
rules.

## Current state

The design is consolidated but accepted model training has not started. Existing
`new-data/src/windowing.py` output is dry-run evidence only and is known to
conflict with the current contract.

Before the first accepted training run, the open gates in the handoff and
`docs/design/06-checklist-and-limitations.md` must be closed. In particular:

- obtain the bundled partner reapproval recorded as pending in the revised
  handoff;
- record the visitor transform, scaling scope, fitting population,
  zero-variance/unseen-series behavior, and neutral placeholder;
- replace or extend the historical verifier for the current 28-series snapshot;
- pass mask, patching, timezone, and true-split-boundary tests;
- reproduce continuous-test coverage for autoencoder `k=6` and sensitivity
  `k=4`; and
- capture data/source hashes and the accepted environment.

Do not present pre-gate weights or metrics as study results. Do not invent a
framework, package layout, dependency, command, or model decision that the
current design has not frozen.

## Non-negotiable current contract

- Canonical data:
  `new-data/data/bad_nauheim_bereinigt.csv`, SHA-256
  `af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`.
- Population: all 28 retained temporal series, including `Innenstadt` and
  `Kurpark`; do not call all 28 point sensors.
- True UTC splits are half-open:
  - training: `2025-06-30 01:00` to `2025-07-04 00:00`;
  - validation: `2025-07-04 00:00` to `2025-07-06 00:00`;
  - continuous test: `2025-07-06 00:00` to `2025-07-14 00:00`.
- July 8 is a reporting boundary inside the continuous test, not a split:
  Condition A ends and Condition B begins at `2025-07-08 00:00 UTC`.
  Windowing and permitted test-only patching remain continuous across it.
- Restore every `war_fehlend=True` visitor position to missing before downstream
  patching.
- Keep `input_available_mask` separate from `target_observed_mask`. Patched
  values may supply input context but never loss targets, threshold observations,
  or evaluation ground truth.
- Patch only maximal one- or two-hour missing runs within one true split, exactly
  as specified in the shared data contract. Long or unanchored gaps remain
  unavailable.
- Store, split, and join in UTC; derive behavioral calendar features in
  `Europe/Berlin`.
- Fit learned preprocessing on originally observed training values only.
- Autoencoder examples are 24-hour, stride-one reconstruction windows. Training
  uses `k=0`, primary validation/test uses `k=6`, and `k=4` is the stricter
  sensitivity. Autoencoder eligibility must not depend on an LSTM target.
- Alper owns autoencoder-specific choices. The partner owns all LSTM-specific
  choices. Shared code must not silently freeze a partner-owned decision.
- Every detector and the mandatory baseline export the canonical series-hour
  schema with immutable `model_config_id` and `run_id`. Score, label, and
  threshold keys must be unique.
- For each declared model-configuration pair, freeze structural support on the
  clean copy before injection. Every seed and derived copy uses that same
  population; missing or non-finite required scores fail the run/copy and are
  never silently dropped.
- Never train on injected anomalies or use test/injection results to choose
  preprocessing, architecture, weights, sparsity, or thresholds.
- Synthetic evaluation measures response to predefined perturbations, not
  verified real-world anomaly accuracy. Unverified real detections are anomaly
  candidates.

For details and exceptions, read the handoff and the relevant design document;
this summary is not a substitute for them.

## Autonomous working style

Work as an end-to-end implementation agent by default:

1. inspect the current contract, code, data schema, and nearby tests;
2. make the smallest contract-compliant design choice that is already within the
   task's authority;
3. implement the complete requested slice, including tests and documentation;
4. run proportionate verification and inspect failures;
5. iterate until the slice is working or a genuine external decision blocks it;
6. report the outcome, evidence, remaining gates, and exact files changed.

Do not pause for routine approval, ask the user to choose ordinary engineering
details, or stop after producing a plan when the requested work can safely be
completed. Resolve discoverable questions from the repository and current design.
Prefer simple, explicit, teachable code over clever abstractions.

Ask or stop only when proceeding would:

- change the research question or a jointly approved shared contract;
- decide an open partner-owned LSTM choice;
- depend on professor clarification or an unavailable human approval record;
- choose the still-open preprocessing policy using information not authorized by
  the design;
- overwrite/delete material data, publish externally, expose secrets, or make
  another consequential action outside the requested scope; or
- require choosing between genuinely conflicting current authorities.

When blocked on one item, continue any independent, safe work that does not
prejudge it.

## Implementation and verification standards

- Use repository-relative paths resolved from the current file, not assumptions
  about the process working directory.
- Keep shared preparation separate from model-specific example construction.
- Represent masks explicitly; never infer observation state from finiteness.
- Fail loudly on changed hashes/schema, duplicate `(series_id, timestamp_utc)` keys,
  invalid UTC timestamps, leakage, all-masked loss batches, or impossible
  evaluation invariants.
- Keep seed namespaces, configurations, coverage, exclusions, environment, and
  source/data provenance machine-readable.
- Add focused tests with every behavioral change. Include boundary cases for
  one-/two-/three-hour gaps, split edges, July 8 continuity, local-time features,
  masked targets, and common-score support where relevant.
- Treat failed experiments and inconvenient results as evidence; do not tune the
  written protocol after inspecting test outcomes.
- Keep documentation concise and link to the single authority instead of copying
  large specifications into new files.
- Do not claim that a check passed unless it was executed successfully.

The historical verifier can be run only as historical evidence:

```text
python scripts/verify_design_contract.py
```

It is not the current acceptance command. The current implementation must provide
and document its own verified commands as they are created.

## Research integrity and handoff

Agents may implement autonomously, but the students remain accountable for
methodological decisions and submitted claims. Record material AI-assisted
scientific or engineering decisions according to
`docs/design/05-responsible-ai-and-evidence.md`; routine edits do not need a
ceremonial log entry.

Generated code must be readable enough for both students to trace data from the
canonical CSV through masks, windows, scores, and metrics. Preserve limitations,
decision timing, and human-approval status exactly. Never backfill student
verification or partner approval that is not evidenced.

Do not commit, push, or open external changes unless the user asks. If asked to
commit, do not add AI co-author or session trailers.
