# Phase 11 seasonal-baseline preregistration and decision timing

**Date:** 2026-07-31

**Owner:** Alper, Conv1D autoencoder owner

**Status:** SIGNED — authorized by Alper before any Phase 9 test inference.

## Authorization

Alper supplied this explicit authorization in the coding session on
2026-07-31. Chat line wrapping is normalized below without changing the words:

```text
I authorize the Phase 11 seasonal baseline and reference comparison exactly as
written in docs/handoffs/2026-07-31-phase-11-seasonal-baseline-prompt.md
(SHA-256 f768dd32…). I confirm that at the time of this authorization no Phase 9
test inference has run and I have not seen any autoencoder test score, ranking,
candidate timestamp or plot. I authorize the weekday/weekend reporting stratum
as reporting-only, and I accept that the degenerate is_weekend dimension is
disclosed rather than repaired.
```

The prompt referenced above by its truncated digest has the complete raw
SHA-256
`f768dd3205f3ae552ed7db2b98950771c0e268f6e3384fc20fdf5cb43d04f738`
and byte size 33,655. Its paired prospective review is
`docs/reviews/2026-07-31-phase-11-baseline-prompt-review.md`, raw SHA-256
`c1d4ad8a3d98cb1fc5c5b18110992e0f47cb7e17364ef8a4150e651167864b70`, verdict
`PROMPT PASS` with zero Critical, High and Medium findings.

This record preserves Alper's message. It does not infer authorization from an
agent-created prompt, silence or session use.

At the moment of authorization the Phase 9 sealed 65-path accepted source
manifest showed zero drift and
`runs/phase9-autoencoder-test-scoring/result/` did not exist, independently
confirming that no Phase 9 test inference had occurred.

## Why this record exists

`docs/handoffs/2026-07-24-implementation-handoff.md:337-341` makes the frozen
seasonal baseline a mandatory component of the study's comparison, not optional
context. The baseline is fully specified at `handoff:344` and is completely
partner-independent: it requires no LSTM specification, no common support, no
injection, no labels and no trained weights.

The sealed Phase 10 prompt deferred baseline implementation to a later,
separately authorized phase
(`docs/handoffs/2026-07-30-phase-10-autoencoder-clean-test-analysis-prompt.md:1012-1014`).
Left unchanged, that ordering would have had the study's only currently
available comparator designed **after** Phase 9 and Phase 10 made autoencoder
test scores visible. This record and its paired prompt close that
preregistration gap without altering either sealed prompt.

## Decision timing

At the time this record and
`docs/handoffs/2026-07-31-phase-11-seasonal-baseline-prompt.md` were authored:

- the Phase 9 accepted source identity `27d8ebbd…` had been captured;
- Phase 9 test inference had **not** run, and no result directory or durable
  Phase 9 evidence existed;
- Phase 10 had not been implemented or executed; and
- no autoencoder test score had been produced or inspected by any person or
  agent.

The decision timing is therefore **pre-test** with respect to every autoencoder
test result.

`docs/handoffs/2026-07-30-phase-9-autoencoder-test-scoring-prompt.md:128-131`
states that after the accepted Phase 9 source capture, any change to the Phase 9
or Phase 10 prompt is test-informed and must stop. That rule is respected
literally: this work changes neither prompt's bytes, adds nothing to the 65-path
Phase 9 accepted source manifest, and leaves `PHASE9_SOURCE_ADDITIONS`,
`PHASE9_SOURCE_FILE_COUNT` and the Phase 9 identity untouched. The Phase 11
prompt is a new, independently captured document.

This record exists so that the timing question is settled by a dated artifact
rather than by later reconstruction.

## Frozen conventions authorized by this record

1. The baseline follows the `handoff:344` definition exactly: fit on originally
   observed training values only, median by
   `series_id x Europe/Berlin local_hour x is_weekend`, with the fixed fallback
   chain `series_id x local_hour`, then `series_id`, then the global originally
   observed training median.
2. The training split contains **zero** weekend hours, so the `is_weekend`
   dimension is structurally degenerate and every weekend hour is served by a
   weekday median through the fallback. This is implemented and disclosed as-is.
   The fallback chain, split, training period and cell definition are **not**
   modified to repair it.
3. A weekday/weekend reporting stratum is added to the reference comparison,
   parallel to the existing condition, UTC-date, series and missingness strata.
   It is reporting-only and changes no score, threshold, population or
   eligibility rule.
4. The comparison is evaluated on the autoencoder's own clean support, with each
   model judged at its own frozen thresholds. It is explicitly **not** the
   cross-architecture common support of `handoff:374-380`.

## Scope and limitations

This authorization does not:

- modify, reinterpret or supersede the sealed Phase 9 or Phase 10 prompts;
- alter any Phase 6, 7, 8 or 9 artifact, weight, score, threshold or identity;
- select, rank or tune an architecture, lambda, seed, route, weight,
  preprocessing policy or threshold;
- freeze or approximate a cross-architecture common support;
- authorize injection, labels, event placement or any label-dependent metric,
  all of which remain blocked until the partner supplies the LSTM specification
  and structural score coverage per `handoff:384`;
- decide any partner-owned LSTM choice; or
- establish anomaly-detection performance.

## Verified structural facts recorded at authorship

Computed read-only from the canonical dataset through the accepted Phase 2
preprocessing at authorship time:

| Quantity | Value |
|---|---:|
| Observed training rows (fit population) | 2,440 |
| Observed weekend rows in training | 0 |
| Training local weekday set | `{0, 1, 2, 3, 4}` |
| Observed validation rows | 1,155 |
| — of which weekend | 561 |
| Observed continuous-test rows | 3,159 |
| — Condition A / Condition B | 1,127 / 2,032 |
| — of which weekend | 1,147 |
| Populated `series x hour x weekend` cells | 662 |
| Populated cells with `is_weekend = true` | 0 |
| Populated `series x hour` cells | 662 of 672 |
| Kurpark observed training hours | 73 |

The test totals reproduce the coverage table in the sealed Phase 9 prompt
(`:320-322`) exactly, and the validation total equals the autoencoder's `k=6`
scored hours per run. These are structural counts derived from masks and
periods; they contain no anomaly score and no model output.
