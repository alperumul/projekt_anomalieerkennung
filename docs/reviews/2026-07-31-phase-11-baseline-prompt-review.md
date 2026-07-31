# Phase 11 seasonal-baseline prompt prospective review

Review artifact: phase11-prompt-review-v1
Reviewer: Anthropic Claude, implementation-prompt prospective reviewer
Reviewed at: 2026-07-31T14:47:54.177131+02:00
Verdict: PROMPT PASS
Critical findings: 0
High findings: 0
Medium findings: 0

## Reviewed prompt identity

| Path | Raw SHA-256 |
|---|---|
| `docs/handoffs/2026-07-31-phase-11-seasonal-baseline-prompt.md` | `f768dd3205f3ae552ed7db2b98950771c0e268f6e3384fc20fdf5cb43d04f738` |

The verdict applies to these exact bytes only. Any edit voids this record.

## Scope and conclusion

This was a prospective review of the exact prompt bytes above. No Phase 11
implementation, accepted capture, fitting, scoring or publication was performed.
No Phase 9 test inference was performed, and no autoencoder test score was
produced or inspected during this review.

The review checked the normative handoff and design authorities, the Phase 8 and
Phase 9 boundary, ownership limits, the baseline fit rule and its degenerate
weekend dimension, fallback behaviour, score and threshold definitions, schema
interoperability with published Phase 8 output, comparison population derivation,
stratum universes and row-count oracles, accepted source identity arithmetic,
atomic publication, restored verification, claim limits and downstream gates.

Premise checks executed read-only against the canonical dataset through the
accepted Phase 2 preprocessing, and against published Phase 8 result bytes.
They establish the fit, support, fallback and stratum oracles the prompt pins.
They do not establish any future Phase 11 result.

## Findings raised and closed for these bytes

Six defects were found in the pre-review draft and are closed in the reviewed
bytes. They are recorded here because the draft was authored in this same
session and the find-and-fix cycle is part of this review's evidence.

**H1 — threshold schema diverged from published Phase 8 output.** The draft
header reordered columns, dropped `model_seed` and renamed
`validation_scores_above_threshold`. Published Phase 8
`runs/phase8-validation-scoring/result/validation-thresholds.csv` uses a fixed
header, and `04:36` makes `(run_id, threshold_quantile)` a shared key.
Consequence: baseline and autoencoder threshold rows could not be concatenated
without reconciliation, and a later joint table would silently mismatch.
Closed: the prompt now mandates the byte-identical Phase 8 header and forbids
renaming, reordering or dropping a column.

**H2 — accepted-source path arithmetic was self-contradictory.** The draft said
"exactly these four new paths", listed four, then added `tests/test_phase11.py`
in prose while requiring a 70-path manifest. Consequence: a literal
implementation builds a 69-path manifest and fails its own count check.
Closed: five paths are enumerated, `65 + 5 = 70` is stated explicitly.

**H3 — no pooled stratum and no row-count oracles.** The draft defined only
disaggregated strata, leaving the headline pooled exceedance rate without a
defined home, and pinned no row totals for the coverage or comparison tables.
Consequence: two implementations could produce different stratum universes and
both pass. Closed: an `overall` / `all` stratum is required, the full universes
are tabulated, and exactly 89 coverage rows and 1,920 comparison rows are pinned,
with reconciliation of every stratum kind to the route total.

**M1 — invented baseline-specific `evaluation_copy_id`.** The draft minted
`clean-validation-baseline-v1` and `clean-continuous-test-baseline-v1`.
`04:29` defines the copy id as identifying the data copy and scenario, not the
model, and the label key at `04:35` is `(evaluation_copy_id, series_id,
timestamp_utc)`. Consequence: later injected-copy labels would not join across
models, breaking the eventual joint evaluation. Closed: the baseline reuses
Phase 8's published `clean-validation-v1`, uses `clean-continuous-test-v1` for
the unrestricted clean test copy, and the comparison is required to join by
`(series_id, timestamp_utc)` within a route rather than by copy id.

**M2 — comparison not bound to the Phase 9 data identity.** The draft's
comparison table omitted `unmodified_test_data_identity`, which Phase 9 requires
on every route-dependent table. Consequence: a comparison could be produced
against a different or unverified test construction with no detectable trace.
Closed: the column is required, must be identical on every row, and must equal
the Phase 9 run-manifest value.

**M3 — no prospective-review or signed-authorization gate.** The draft required
the decision record to exist and be hash-pinned, but not to be *signed*, and
mandated no prompt review at all — unlike Phase 9 at `:105-107`. Consequence: an
implementation agent could capture an unsigned placeholder record as
authorization, exactly the inference forbidden by
`docs/decisions/2026-07-27-phase-7-sparsity-diagnostics.md:22-23`. Closed: a
review-and-authorization gate now requires this record, requires the decision
record's `Status:` to be signed and its authorization to be free of the
`PLACEHOLDER` token, and adds counterexample tests for both.

## Correct coverage worth preserving

- The ownership boundary is exact: no LSTM choice, no common support, no
  injection, no labels, and every label-dependent metric of `handoff:348-357`
  remains blocked per `handoff:384`.
- The fit population is restricted to originally observed training targets in
  the accepted scaled representation, never patched values or the `0.0`
  unavailable-input placeholder.
- The degenerate weekend dimension is predeclared as a structural consequence of
  the frozen split and explicitly must not be repaired by reweighting, borrowing
  adjacent days, extending training or altering the fallback chain.
- Thresholds are calibrated on the baseline's own validation scores, applied
  unchanged to test, with strict `>` and no stratum tuning; each model is
  compared at its own threshold.
- Timestamp serialization is pinned to `YYYY-MM-DDTHH:MM:SSZ`, with the
  `2025-07-04 00:00:00+00:00` form named as a defect — the exact failure that
  halted the Phase 9 attempt.
- Phase 9 result hashes are deliberately unpinned and must be read and
  semantically validated at execution, because Phase 9 had not run when the
  prompt was authored. This avoids fabricated provenance.
- The phase writes nothing inside the Phase 8 or Phase 9 run directories and
  leaves `PHASE9_SOURCE_ADDITIONS`, `PHASE9_SOURCE_FILE_COUNT` and the 65-path
  Phase 9 identity untouched.

## Premise-check commands executed

Read-only, against the canonical dataset and published Phase 8 bytes:

- fit/support/fallback/stratum derivation through
  `anomaly_detection.preprocessing.fit_and_prepare_canonical_data`, establishing
  2,440 fit observations with zero weekend rows, 1,155 validation and 3,159 test
  observed hours, 1,127/2,032 by condition, 662 populated primary cells with
  none at `is_weekend=true`, 662-of-672 `series x hour` cells, all 28 series
  populated, and fallback counts 2,587/1,685/42/0;
- header and content inspection of
  `runs/phase8-validation-scoring/result/validation-scores.csv` and
  `validation-thresholds.csv`, establishing the published threshold header, the
  `clean-validation-v1` copy token, the `2025-07-04T00:00:00Z` timestamp form
  and `validation_score_count = 1155`;
- UTC-date and condition universes: validation `2025-07-04`–`2025-07-05`, test
  `2025-07-06`–`2025-07-13`; and
- Phase 9 sealed-manifest drift check: 65 paths, zero drift, no result
  directory.

Two independent cross-checks passed: test totals `1,127 + 2,032 = 3,159`
reproduce the sealed Phase 9 coverage table, and validation `1,155` equals both
the autoencoder `k=6` scored hours per run and the Phase 8 threshold table's
recorded `validation_score_count`.

## Residual risk and intentionally open items

- **This is a self-review.** The reviewed prompt was authored by the same agent
  in the same session. Project precedent for
  `phase9-phase10-prompt-review-v1` is also agent self-review with an iterative
  find-and-fix cycle, so this record is consistent with established practice, but
  an independent pass — for example via the Codex
  `review-implementation-prompt` skill — would be stronger evidence. Recommended
  before accepted capture, not required by any current authority.
- **The paired decision record is unsigned.** As of this review,
  `docs/decisions/2026-07-31-phase-11-baseline-preregistration.md`
  (`c7340dff6651d10d4404c9eb6f9c3a612df415723824ccf98a0b4981edb9fd5b`) carries
  `Status: UNSIGNED DRAFT` and a `PLACEHOLDER` authorization block. The prompt's
  own gate blocks capture until Alper supplies verbatim authorization. Signing
  changes that file's hash; this review does not cover the decision record's
  bytes.
- Phase 11 execution additionally depends on a completed and verified Phase 9
  result, which does not yet exist.
- Injection, labels, common support, LSTM intake and all label-dependent metrics
  remain out of scope and blocked.
- The weekday/weekend reporting stratum is an addition beyond the literal
  contract text. It is reporting-only, changes no score, threshold, population or
  eligibility rule, and is recorded in the paired decision record for Alper's
  approval.

## Readiness

The prompt is ready to execute for these exact bytes, subject to the two gates
it declares: a signed decision record, and a completed verified Phase 9 result.
No Critical, High or Medium finding remains open.
