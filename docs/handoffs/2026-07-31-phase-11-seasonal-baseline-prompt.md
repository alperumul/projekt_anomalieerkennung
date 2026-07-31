# Phase 11 implementation prompt — mandatory seasonal baseline and autoencoder-vs-baseline reference comparison

## Review and execution status

This is an implementation prompt for a future coding session. It does not
authorize execution merely because it exists. At the time this prompt is
written:

- Phase 8 validation scoring and threshold calibration are complete;
- the Phase 9 accepted source identity `27d8ebbd…` is captured, but **no Phase 9
  test inference, result directory or durable Phase 9 evidence exists**;
- no Phase 10 implementation or result exists;
- no baseline implementation, score table, threshold table, coverage table,
  comparison table or Phase 11 result manifest exists; and
- no numerical autoencoder test score has been produced or inspected by any
  person or agent.

This prompt is therefore authored **pre-test** with respect to every
autoencoder test result. That timing is the entire scientific point of the
phase and must be preserved in its accepted evidence.

This prompt does not modify, reinterpret or supersede the sealed Phase 9 or
Phase 10 prompts. It creates no drift in the 65-path Phase 9 accepted source
manifest and must not be added to it.

## Why this phase exists and why it is written now

`docs/handoffs/2026-07-24-implementation-handoff.md:337-341` defines the
mandatory comparison as containing the standard and sparse Conv1D
autoencoders, the partner-owned LSTM, **the frozen inexpensive series-specific
seasonal baseline**, and the analytical references. The baseline is not
optional context. It is a required component of the study's comparison.

The baseline is also fully specified and completely partner-independent. It
needs no LSTM specification, no common support, no injection, no labels and no
weights. It can therefore be executed while the partner's LSTM does not exist.

Preregistering it now closes a preregistration gap: if the baseline were
specified after Phase 9 or Phase 10 made autoencoder test scores visible, the
study's only currently-available comparator would have been designed after
unblinding. Every rule in this prompt is fixed before any test score exists.

Execution order is scientifically irrelevant for a deterministic comparator
whose rules are frozen in advance. This phase may run before or after Phase 10.
It depends only on the immutable Phase 9 result, never on Phase 10.

## Required reading and authority

Read completely, in this order:

1. `AGENTS.md`;
2. `docs/handoffs/2026-07-24-implementation-handoff.md`, especially sections
   10, 11, 12 and 13;
3. `docs/README.md`;
4. `docs/design/02-shared-data-contract.md`;
5. `docs/design/04-evaluation-and-injection.md`, especially the shared score
   table, threshold policy and seasonal baseline sections;
6. `docs/design/06-checklist-and-limitations.md`;
7. `docs/design/05-responsible-ai-and-evidence.md`;
8. the Phase 8 accepted evidence and validation-threshold result;
9. the immutable Phase 9 result and durable evidence; and
10. this prompt.

Do not inspect or use `diğer/`. Do not use the historical partner source as an
implementation authority. Stop on a conflict between current authorities; do
not blend rules.

`docs/design/04-evaluation-and-injection.md` may not override the handoff. Where
this prompt restates a rule, the handoff remains authoritative.

## Ownership and scope boundary

This phase is baseline-only plus a strictly descriptive autoencoder-vs-baseline
reference comparison on the clean continuous test period.

It must not:

- implement, specify, infer or constrain any partner-owned LSTM choice;
- freeze or approximate a cross-architecture common support;
- generate injections, injected copies, noise copies, labels or event tables;
- produce AP, ROC-AUC, F1, precision, recall, confusion matrices, event recall,
  overlap coefficients or any label-dependent metric;
- retrain, restore, modify or re-score any Conv1D autoencoder weight;
- recalibrate, replace or reinterpret any Phase 8 threshold;
- select a winning architecture, lambda, seed, route or threshold; or
- claim verified real-world anomaly-detection accuracy.

Every label-dependent metric in `handoff:348-357` remains blocked until the
partner supplies the LSTM specification and structural score coverage, exactly
as stated at `handoff:384`.

## Immutable prerequisites

Before implementation or accepted capture, independently hash and semantically
validate:

| Artifact | Required raw SHA-256 |
|---|---|
| `new-data/data/bad_nauheim_bereinigt.csv` | `af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f` |
| `docs/provenance/2026-07-29-phase-8-validation-scoring.json` | `e1bb2c19c576468cc8ff436ccc8346c79c5c302056485a282d373465985afb8c` |
| `runs/phase8-validation-scoring/result/validation-thresholds.csv` | `0f76681da235290fb76f31497a2b59eec037f47304c0af9e37b98c18b0e22790` |
| `docs/provenance/2026-07-30-phase-9-accepted-source-identity.json` | `e7ac92654aa2cee7b2387698d5616ced2648a9b5cb3e7fb6d4478e2fa29b19ab` |

Also require the accepted Phase 2 preprocessing-artifact raw SHA-256
`3830dcd54279bf94efff6ca9c170c534bf3f7461c027997a1d1bc5102d2e6d10`.

The Phase 9 result identity, durable-evidence raw SHA-256 and result-manifest
raw SHA-256 **cannot be pinned in this prompt** because Phase 9 had not executed
when this prompt was written. Do not invent them. Read them from
`docs/provenance/2026-07-30-phase-9-autoencoder-test-scoring.json` and
`runs/phase9-autoencoder-test-scoring/result/run-manifest.json`, verify every
declared semantic relationship, and record the observed values in the Phase 11
accepted readiness. Require:

- nine accepted `run_id` values matching the Phase 8 accepted run catalog;
- both routes present with `eligibility_rule` exactly `k=6` and `k=4`;
- exactly 47,196 `test-scores.csv` rows and 94,392 `threshold-exceedances.csv`
  rows;
- a single `unmodified_test_data_identity` shared by both routes; and
- result status `PHASE9_AUTOENCODER_TEST_SCORING_VERIFIED`.

Any mismatch closes Phase 11. Do not repair, replace or reinterpret Phase 8 or
Phase 9 evidence. This phase never writes inside
`runs/phase8-validation-scoring/` or `runs/phase9-autoencoder-test-scoring/`.

## Fixed scientific scope

### Model identity

The baseline is one deterministic model with no seed:

```text
model_family        = baseline
model_variant       = seasonal_median
model_config_id     = baseline-seasonal-median-hour-weekend-v1
run_id              = baseline-seasonal-median-hour-weekend-v1-r0
model_seed          = (empty)
```

`model_seed` is empty exactly because the baseline is deterministic
(`04:29`). Emitting any non-empty seed is a defect. The `run_id` is fixed by
this prompt and must not be derived from a source or environment hash, because
the baseline has no seeded initialization to distinguish.

### Fit population

Fit **only** on originally observed training visitor values in the final
accepted shared visitor representation (`handoff:344`):

- restrict to `true_split == training`;
- restrict to `target_observed_mask == true`;
- use `target_visitor_scaled`, never a patched, placeholder or raw value; and
- require exactly **2,440** contributing observations.

Never fit on validation, test, patched positions or the `0.0` unavailable-input
placeholder.

### Seasonal cell and the degenerate weekend dimension

Derive `local_hour` in `0..23` and `weekday` Monday `=0` through Sunday `=6`
in `Europe/Berlin` from `timestamp_utc`, exactly as
`docs/design/02-shared-data-contract.md:149-157` requires. Define
`is_weekend = weekday >= 5`.

The expected value is the median of the fit population for each
`series_id x local_hour x is_weekend` cell, with the fixed fallback chain
`series_id x local_hour`, then `series_id`, then the global originally observed
training median (`handoff:344`).

**Predeclared structural fact.** The training period
`[2025-06-30 01:00, 2025-07-04 00:00) UTC` contains Monday through Friday only.
Its observed weekday set is exactly `{0, 1, 2, 3, 4}` and it contains **zero**
observed weekend rows. Therefore:

- no `is_weekend = true` primary cell can ever be populated;
- every weekend validation/test hour necessarily falls back to the
  `series_id x local_hour` median, which is a **weekday** median; and
- the baseline carries no weekend information whatsoever.

This is a consequence of the frozen split, not a defect to repair. Do not add a
weekend cell, reweight, borrow adjacent days, extend the training period or
alter the fallback chain. Implement the contract chain exactly and disclose the
degeneracy.

Require these exact fit oracles:

| Quantity | Required value |
|---|---:|
| Fit observations | 2,440 |
| Observed weekend rows in fit population | 0 |
| Populated `series x local_hour x is_weekend` cells | 662 |
| Populated cells with `is_weekend = true` | 0 |
| Populated `series x local_hour` cells | 662 of 672 |
| Populated `series` cells | 28 of 28 |
| Global fallback ever used | no |

A median over an even count uses the ordinary linear interpolation of the two
central order statistics; compute it deterministically over the sorted binary64
fit values and record the per-cell contributing count.

### Score definition

For every originally observed validation and continuous-test series-hour
(`handoff:344`, `04:275`):

```text
anomaly_score          = abs(target_visitor_scaled - expected_scaled)
n_contributing_windows = 1
```

Score **every** originally observed series-hour. The baseline has no window
eligibility, so its support is strictly broader than either autoencoder route.
Never restrict the baseline to autoencoder eligibility when producing its own
score or threshold tables.

Require these exact support oracles:

| Population | Required rows |
|---|---:|
| Validation scores | 1,155 |
| Continuous-test scores | 3,159 |
| — Condition A | 1,127 |
| — Condition B | 2,032 |
| Fallback level `series x local_hour` (val + test) | 1,685 |
| Fallback level `series` (val + test) | 42 |
| Fallback level global (val + test) | 0 |
| Primary-cell hits (val + test) | 2,587 |

The validation support of 1,155 equals the autoencoder's `k=6` scored hours per
run, so the two threshold populations have equal size. This is a factual
coincidence of this dataset, not a design guarantee; do not encode it as an
invariant beyond the literal counts above.

### Thresholds

Calibrate exactly as `handoff` section 11 and `04:71-86` require, using the
baseline's own validation scores:

- pool all 1,155 validation scores across the 28 series;
- compute the `0.98` and `0.99` empirical quantiles with
  `quantile(..., method="linear")`;
- apply both unchanged to the clean test scores;
- classify anomalous only when `score > threshold`; equality is non-anomalous;
- do not recalibrate on test data; and
- do not tune by condition, series, date or weekday.

The threshold table key is `(run_id, threshold_quantile)` and records method,
comparator, score count, threshold value and the number of validation
observations above it.

Baseline threshold **values** are not comparable to autoencoder threshold
values: each run pools its own validation scores (`04:76`), and the two score
definitions have different units of reconstruction difficulty. Only exceedance
behaviour on a shared population may be compared.

### Reference comparison

Compare the baseline against the nine accepted autoencoder runs **only** on the
intersection of scored keys, per route, using the immutable Phase 9 test scores.

Because the baseline scores every originally observed test hour and each
autoencoder route scores a subset, the autoencoder route population is exactly
the intersection:

| Route | Comparison population |
|---|---:|
| `k=6` | 2,689 |
| `k=4` | 2,555 |

Verify this subset relationship rather than assuming it; if any autoencoder
scored key is absent from the baseline population, fail the run and report the
coverage loss. Never silently drop a key (`handoff:380`).

Report, per route and per model `run_id` including the baseline:

- exceedance counts and rates at both frozen thresholds;
- stratified by `evaluation_condition`, UTC date, `series_id`, the
  trailing-24-hour missingness bucket, and **local weekday/weekend**; and
- the baseline's own value alongside each autoencoder run without ranking,
  scoring a winner or declaring superiority.

The weekday/weekend stratum is predeclared here because the weekend dimension
of the baseline is structurally degenerate, and pooling weekend with weekday
hours would hide that. It is additive reporting only. It changes no score, no
threshold, no population and no eligibility rule.

Each model is evaluated at **its own** frozen thresholds. Do not apply the
baseline's threshold to an autoencoder score or the reverse.

This comparison is descriptive. It is not a common-support comparison in the
sense of `handoff:374-380`, because no LSTM exists and no common intersection
has been frozen. Label it explicitly as an autoencoder-vs-baseline reference
comparison on the autoencoder's own clean support.

## Exact result schemas and canonical CSV bytes

All CSVs use UTF-8 without BOM, comma delimiter, LF line endings, Python
`csv.writer(dialect="excel", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")`,
one header and a final LF. Serialize `None` as empty, finite binary64 values
with `format(value, ".17g")`, integers as base-10 text without leading `+` or
unnecessary leading zero, timestamps exactly `YYYY-MM-DDTHH:MM:SSZ`, and
booleans as lowercase `true` or `false`. The only nonempty nonnumeric missing
token is exact ASCII `NA`. Reject NaN, infinity, CR, BOM, extra columns,
missing columns and noncanonical round trips.

Timestamps are serialized in the exact `YYYY-MM-DDTHH:MM:SSZ` form. A
`pandas`/`datetime` default such as `2025-07-04 00:00:00+00:00` is a defect,
not a cosmetic difference.

Common orders: run (`run_id` Unicode code point), route (`k=6` then `k=4`),
series (canonical `series_id` Unicode code point), timestamp ascending,
condition (`validation`, `condition_a`, `condition_b`), threshold (`0.98` then
`0.99`), missingness bucket (`boundary_lt_24h`, `0`, `1-2`, `3-4`, `5-6`,
`7-12`, `13-24`), daytype (`weekday` then `weekend`).

### `baseline-seasonal-reference.csv`

The fitted model, published so the baseline is inspectable and reproducible:

```text
series_id,local_hour,is_weekend,cell_level,expected_scaled,contributing_observations
```

Unique key `(series_id, local_hour, is_weekend)`. Materialize the full
`28 x 24 x 2 = 1,344` universe. `cell_level` is exactly one of `primary`,
`series_hour`, `series`, `global`, naming the level that supplies
`expected_scaled` for that cell. `contributing_observations` is the count at the
supplying level. Exactly 662 rows have `cell_level=primary`, and every row with
`is_weekend=true` has `cell_level` other than `primary`.

### `baseline-validation-scores.csv` and `baseline-test-scores.csv`

Both use the canonical shared score schema (`04:13-27`) plus the reference
columns:

```text
model_family,model_variant,model_config_id,run_id,model_seed,evaluation_copy_id,evaluation_condition,injection_seed,noise_seed,series_id,timestamp_utc,anomaly_score,n_contributing_windows,expected_scaled,observed_target_scaled,cell_level
```

`model_seed`, `injection_seed` and `noise_seed` are empty. Unique key
`(run_id, evaluation_copy_id, series_id, timestamp_utc)`. Require exactly 1,155
and 3,159 rows respectively. Require
`anomaly_score == abs(observed_target_scaled - expected_scaled)` bit-for-bit and
`n_contributing_windows == 1` on every row.

Use these exact copy identities:

| Table | `evaluation_copy_id` | `evaluation_condition` |
|---|---|---|
| validation | `clean-validation-v1` | `validation` |
| test | `clean-continuous-test-v1` | `condition_a`, `condition_b` |

`evaluation_copy_id` identifies the **data copy and scenario**, not the model
(`04:29`). The baseline scores the same clean validation copy that Phase 8
scored, so it reuses Phase 8's exact published `clean-validation-v1` token and
its rows concatenate with Phase 8's without reconciliation. Do **not** mint a
baseline-specific copy id: `run_id` already distinguishes the model, and the
label key `(evaluation_copy_id, series_id, timestamp_utc)` in `04:35` requires
every model scoring one copy to share that copy's id, or later injected-copy
labels will not join across models.

`clean-continuous-test-v1` denotes the unrestricted clean continuous-test copy.
Phase 9's `clean-continuous-test-k6-v1` and `clean-continuous-test-k4-v1` are
eligibility-restricted views of that same underlying data, not different data.
The reference comparison therefore joins baseline to autoencoder rows by
`(series_id, timestamp_utc)` **within a route**, never by `evaluation_copy_id`.

### `baseline-validation-thresholds.csv`

```text
model_family,model_variant,model_config_id,run_id,model_seed,threshold_quantile,quantile_method,comparator,validation_score_count,threshold_value,validation_scores_above_threshold
```

This header is **byte-identical to the published Phase 8 threshold table**
`runs/phase8-validation-scoring/result/validation-thresholds.csv`, including
column order and the exact name `validation_scores_above_threshold`. The
baseline threshold rows must be schema-compatible with the autoencoder threshold
rows so the two can be concatenated without reconciliation, as the shared
threshold key `(run_id, threshold_quantile)` in `04:36` implies. Do not rename,
reorder or drop a column. `model_seed` is empty for the baseline.

Unique key `(run_id, threshold_quantile)`; exactly 2 rows; exact tokens
`linear` and `>`; `validation_score_count` exactly 1,155 on both rows. Phase 8
records the same 1,155 validation-score count for every autoencoder run, so the
two threshold populations are equal in size.

### `baseline-coverage.csv`

```text
evaluation_copy_id,stratum_kind,stratum_value,originally_observed_hours,scored_hours,coverage_rate
```

Unique key `(evaluation_copy_id, stratum_kind, stratum_value)`. `stratum_kind`
is one of `overall`, `condition`, `utc_date`, `series`, `missingness_bucket`,
`daytype`. The `overall` kind has the single `stratum_value` `all` and carries
the pooled row for that copy.

Materialize the full declared universe per copy:

| Copy | overall | condition | utc_date | series | bucket | daytype | rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| `clean-validation-v1` | 1 | 1 | 2 | 28 | 7 | 2 | 41 |
| `clean-continuous-test-v1` | 1 | 2 | 8 | 28 | 7 | 2 | 48 |
| **total** | | | | | | | **89** |

Validation UTC dates are `2025-07-04` and `2025-07-05`; test UTC dates are
`2025-07-06` through `2025-07-13`. Require exactly 89 rows.

Because the baseline scores every originally observed hour, every
`coverage_rate` must be exactly `1` wherever the denominator is positive.
Materialize declared zero-denominator strata with both counts `0` and
`coverage_rate=NA`; never omit them or serialize the rate as numeric zero.

### `reference-comparison.csv`

```text
evaluation_route_id,eligibility_rule,unmodified_test_data_identity,comparison_population,model_family,model_variant,model_config_id,run_id,model_seed,threshold_quantile,threshold_value,stratum_kind,stratum_value,scored_hours,exceedance_count,exceedance_rate
```

Unique key
`(evaluation_route_id, run_id, threshold_quantile, stratum_kind, stratum_value)`.

`unmodified_test_data_identity` is copied unchanged from the immutable Phase 9
result and must be identical on every row, binding this comparison to the exact
continuous-test data Phase 9 scored. Reject a row whose value differs from the
single identity recorded in the Phase 9 run manifest.

Covers both routes, all ten models (nine autoencoder runs plus the baseline),
both thresholds and the full stratum universe:

| overall | condition | utc_date | series | bucket | daytype | strata |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | 8 | 28 | 7 | 2 | 48 |

`2 routes x 10 models x 2 thresholds x 48 strata = 1,920 rows`. Require exactly
1,920 rows, materializing zero-denominator strata with `scored_hours=0`,
`exceedance_count=0` and `exceedance_rate=NA`.

`comparison_population` is 2,689 for `k=6` and 2,555 for `k=4`. `threshold_value`
is that model's **own** frozen threshold — the baseline's from
`baseline-validation-thresholds.csv`, each autoencoder run's from the immutable
Phase 8 table. Validate that each model's `overall` `scored_hours` equals its
route's `comparison_population`, that every other stratum kind's `scored_hours`
sums to that same total, and that `0 <= exceedance_count <= scored_hours`.

## Prompt review and authorization gate

Before accepted Phase 11 source capture and before any fitting or scoring:

1. this prompt must have completed prospective review with no open Critical,
   High or Medium finding, evidenced only by
   `docs/reviews/2026-07-31-phase-11-baseline-prompt-review.md`;
2. that record must contain the exact schema identifier
   `phase11-prompt-review-v1`, this prompt's repository-relative path and raw
   SHA-256, reviewer identity, ISO-8601 review time with UTC offset, verdict
   `PROMPT PASS`, and exact counts `Critical findings: 0`, `High findings: 0`,
   `Medium findings: 0`;
3. **`docs/decisions/2026-07-31-phase-11-baseline-preregistration.md` must be
   signed.** Its `Status:` line must not contain `UNSIGNED`, and its
   Authorization section must contain Alper's verbatim words rather than the
   placeholder block. Reject a record whose authorization text still contains
   the token `PLACEHOLDER`, or whose authorization was written by an
   implementation agent. This mirrors the rule in
   `docs/decisions/2026-07-27-phase-7-sparsity-diagnostics.md:22-23`: authorization
   may not be inferred from an agent-created prompt, from silence, or from the
   fact that a session used it;
4. record the raw SHA-256 of this prompt, the signed decision record and the
   review record in the Phase 11 accepted readiness; and
5. require the same bytes immediately before scoring and during every
   post-publication verification.

Reject a missing, unreadable, stale, hash-mismatched, non-PASS or internally
inconsistent review record. A review of an earlier prompt byte is not evidence
for the current bytes.

After accepted capture, any change to this prompt or the decision record closes
the phase. Stop; do not silently recapture.

## Accepted Phase 11 source identity

Create a bounded accepted source transition independent of the Phase 9 and
Phase 10 bundles.

The Phase 11 accepted source manifest contains the Phase 9 accepted 65 paths
plus exactly these **five** new paths:

1. `docs/handoffs/2026-07-31-phase-11-seasonal-baseline-prompt.md`;
2. `docs/decisions/2026-07-31-phase-11-baseline-preregistration.md`;
3. `src/anomaly_detection/phase11.py`;
4. `scripts/run_phase11_seasonal_baseline.py`; and
5. `tests/test_phase11.py`.

`65 + 5 = 70`. The Phase 11 accepted source identity therefore contains exactly
**70** unique, sorted, repository-relative paths. Reject a manifest of any other
size.

This manifest is constructed independently. Do not modify
`PHASE9_SOURCE_ADDITIONS`, `PHASE9_SOURCE_FILE_COUNT` or any Phase 9 constant.
The Phase 9 identity remains exactly 65 paths.

Before any implementation edit, record the exact current drift of every Phase 9
accepted path. Candidate implementation may change only:

```text
scripts/verify_design_contract.py
src/anomaly_detection/__init__.py
src/anomaly_detection/verification.py
tests/test_verifier.py
```

Permit creation of only the three new implementation paths and the two new
documentation paths named above. This prompt and the decision record must exist
and be hash-pinned at session start and remain read-only throughout. Keep every
Phase 8 and Phase 9 implementation module, result and provenance artifact
read-only. Pin the session-start bytes of `AGENTS.md`, `README.md`,
`docs/README.md` and `docs/design/06-checklist-and-limitations.md`; no pre-result
edit to those four is permitted.

Create:

- `docs/provenance/2026-07-31-phase-11-accepted-source-identity.json`;
- `docs/provenance/2026-07-31-phase-11-accepted-readiness.json`; and
- `runs/phase11-seasonal-baseline/accepted-source-snapshot-<identity-prefix>/`.

The accepted source artifact records the exact sorted `path<TAB>sha256<LF>`
manifest, count, deterministic aggregate, base commit, dirty status, this
prompt's and the decision record's raw hashes, the observed Phase 9 result and
durable-evidence identities, the unchanged accepted environment identity and the
snapshot identity. The snapshot must reproduce every manifest path
byte-for-byte.

## Live-runtime gate

Compare the live environment with the accepted inference environment identity
`557ca9527ba46523f29dcaf6bbb6e7e8ec0b24626d36bfee94818fc60c1f20ee` during
accepted capture, immediately before scoring, immediately before publication and
during restored recomputation. Require exact accepted policy and identity for
Python, NumPy, pandas, the recorded distribution inventory, platform and
CPU/device policy. Reject a GPU or other forbidden accelerator.

The baseline performs no TensorFlow inference. It must still run under the
accepted environment so its provenance is comparable, and it must not install,
upgrade or mutate either accepted environment.

## Atomic execution and publication

The runner has distinct non-mutating planning/validation and explicit
`--execute` modes. The default mode writes no accepted artifact and prints no
score summary.

On `--execute`:

1. pass every prerequisite, source, runtime and protected-inventory gate;
2. create a fresh staging directory on the same filesystem as the final result;
3. refuse any pre-existing final result, staging residue or partial evidence;
4. fit, score, calibrate and compare into staging;
5. validate all expected paths, rows, keys, hashes, finite values, fallback
   levels, subset relationships and stratum reconciliation;
6. create one deterministic `run-manifest.json` covering exactly the six staged
   non-manifest result files and all scientific identities; the manifest must
   not contain its own byte size or SHA-256;
7. atomically rename the staged directory to
   `runs/phase11-seasonal-baseline/result/`; and
8. durably publish
   `docs/provenance/2026-07-31-phase-11-seasonal-baseline.json` through the same
   recoverable one-way completion protocol used by Phases 8 and 9.

The final result directory contains exactly `baseline-seasonal-reference.csv`,
`baseline-validation-scores.csv`, `baseline-test-scores.csv`,
`baseline-validation-thresholds.csv`, `baseline-coverage.csv`,
`reference-comparison.csv` and `run-manifest.json`.

Do not overwrite, append, resume, merge or silently repair a partial result. A
failure before the atomic rename leaves no visible result. A failure after the
rename but before durable evidence completion is a recoverable one-way state: a
rerun may verify and complete only the identical already-published result.

## Post-publication verification

After publication: hash every result and evidence byte; validate every schema,
key, count and semantic relationship from restored files; refit the baseline
from the canonical source; recompute all 1,155 validation scores, 3,159 test
scores, both thresholds, every coverage row and every comparison row in a fresh
temporary area; require exact canonical byte equality; require the
result-manifest and durable-evidence identities to agree; recheck the accepted
environment, the 70-file source identity and every protected Phase 8/9
inventory; and remove all temporary material.

The design-contract verifier must reproduce the accepted Phase 1–9 evidence,
validate Phase 11, and still report LSTM, common-support, injection, synthetic
evaluation and student-signoff gates as pending.

## Required behavioral tests

Add focused tests that fail on at least these counterexamples:

- fitting on validation, test, patched or placeholder values;
- fit population other than 2,440 observations;
- any populated `is_weekend = true` primary cell;
- a repaired, reweighted, borrowed or extended weekend cell;
- an altered fallback chain or fallback order;
- wrong cell counts `662`/`662 of 672`/`28`, or any use of the global fallback;
- wrong median convention on an even-sized cell;
- score defined as anything other than `abs(observed - expected)`;
- `n_contributing_windows` other than `1`;
- validation or test row counts other than 1,155 and 3,159, or condition counts
  other than 1,127 and 2,032;
- fallback-level counts other than 2,587/1,685/42/0;
- a non-empty `model_seed`, `injection_seed` or `noise_seed`;
- threshold recalibrated on test, tuned by any stratum, or using a comparator
  other than strict `>`;
- a baseline threshold applied to an autoencoder score or the reverse;
- an autoencoder scored key absent from the baseline population and silently
  dropped;
- comparison population other than 2,689 for `k=6` or 2,555 for `k=4`;
- an unsigned decision record, a `Status:` line still containing `UNSIGNED`, or
  an authorization section still containing `PLACEHOLDER`, accepted at capture;
- a missing, stale, hash-mismatched or non-PASS prompt-review record accepted;
- a threshold table whose header, column order or column names diverge from the
  published Phase 8 `validation-thresholds.csv` schema;
- a baseline-specific `evaluation_copy_id` minted instead of `clean-validation-v1`
  and `clean-continuous-test-v1`;
- the reference comparison joined by `evaluation_copy_id` rather than by
  `(series_id, timestamp_utc)` within a route;
- a missing `overall` stratum row, or an `overall` `scored_hours` not equal to
  the route's `comparison_population`;
- coverage or comparison row counts other than 89 and 1,920;
- `unmodified_test_data_identity` absent, empty, or not identical on every
  comparison row, or not equal to the Phase 9 run-manifest value;
- a coverage rate serialized as numeric zero for a zero denominator, or a
  missing declared stratum;
- any published header, canonical scalar token, unique key or row ordering
  differing from this contract;
- a timestamp serialized as anything other than `YYYY-MM-DDTHH:MM:SSZ`;
- a manifest self-entry, self-hash or coverage of other than the exact six
  payloads;
- score output visible before the atomic transaction completes;
- overwrite, resume or repair of a partial result;
- any mutation of Phase 8 or Phase 9 artifacts, or of `PHASE9_SOURCE_ADDITIONS`,
  `PHASE9_SOURCE_FILE_COUNT` or the 65-path Phase 9 identity;
- unenumerated Phase 11 source drift accepted;
- any label, injection, LSTM, common-support or label-dependent metric produced;
- a ranking, winner or superiority claim emitted; and
- post-publication restored recomputation mismatch.

Rerun all earlier tests plus the complete design-contract verifier.

## Documentation and claims

The durable Phase 11 evidence records exact source, prompt, decision-record,
runtime, data, Phase 9 result, threshold and result identities; all commands and
exit codes; the complete fit oracles including the zero-weekend fact; all score,
threshold, coverage and comparison counts; atomic publication and restored
recomputation evidence; pre-test decision timing; and all remaining gates.

Permitted conclusion:

> The mandatory deterministic seasonal baseline was fitted on originally
> observed training values only, scored on the clean validation and continuous
> test periods, calibrated at its own predeclared `0.98` and `0.99` validation
> exceedance thresholds, and compared descriptively against the nine accepted
> Conv1D autoencoder runs on the autoencoder's own clean support.

Not permitted:

- best model, best lambda, accepted winner or superiority;
- verified real-world anomaly accuracy;
- precision, recall, F1, AP, ROC-AUC or any label-dependent metric;
- cross-architecture or LSTM comparison;
- a common-support claim in the sense of `handoff:374-380`;
- injected-anomaly performance;
- statistical significance or independent-hour confidence intervals; or
- completion of the project's joint evaluation.

Use a result status such as `PHASE11_SEASONAL_BASELINE_VERIFIED`.

## Required report limitations added by this phase

Carry these forward into the final report alongside the existing list in
`docs/design/06-checklist-and-limitations.md:127-147`:

1. The training split contains no weekend hours, so the mandatory baseline's
   `is_weekend` dimension is structurally degenerate and every weekend hour is
   predicted by a weekday median.
2. 561 of 1,155 validation hours and 1,147 of 3,159 test hours are weekend
   hours, so the baseline's thresholds are calibrated on a population that is
   roughly half weekend while the baseline holds no weekend information.
3. Both the baseline and the autoencoders extrapolate to weekends never seen in
   training; a baseline deficit on weekend hours reflects the split, not only
   model capacity.
4. The baseline scores `Kurpark - Eingang Parkstraße` from 73 observed training
   hours, whereas the autoencoders have no eligible Kurpark training window;
   their Kurpark results are not like-for-like.
5. The comparison uses the autoencoder's own clean support, not a frozen
   cross-architecture common support, and is therefore descriptive only.

## Stop conditions

Stop without scoring or publication on any prerequisite, prompt, decision-record,
environment, unauthorized source drift, protected inventory, count, hash, schema
or semantic mismatch. Preserve exact diagnostics. Do not adapt the scientific
rules after seeing results.

Completion of Phase 11 does not unblock LSTM intake, common support, event
placement, injection, synthetic metrics or final joint claims.
