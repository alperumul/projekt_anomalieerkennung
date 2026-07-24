# 02 — Shared data contract

[Back to documentation index](../README.md)

## Purpose and authority

This file gives technical implementation detail for the [consolidated implementation handoff](../handoffs/2026-07-24-implementation-handoff.md). The handoff is authoritative if a conflict is found. This document may not introduce a new shared obligation or prescribe the partner's LSTM design.

## Canonical source

```text
Path:   new-data/data/bad_nauheim_bereinigt.csv
SHA-256:
af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f
```

Verified snapshot facts:

- 9,380 rows;
- 28 retained temporal series;
- 335 hourly timestamps;
- first timestamp `2025-06-30 01:00:00+00:00`;
- last timestamp `2025-07-13 23:00:00+00:00`;
- 2,626 originally missing series-hours;
- 790 `war_fehlend=True` rows containing stored values.

CSV is the source of truth. A Parquet file may be a disposable cache but cannot become a second authority.

Loading must fail if:

- the canonical hash changes without a new accepted snapshot record;
- `(series_id, timestamp_utc)` is not unique;
- timestamps are invalid or not normalized to UTC;
- the expected 28 series or 335 timestamps change unexpectedly.

Define `series_id` as the exact Unicode value in the canonical CSV `name` column. This is the shared join identifier. If a model needs numeric indices, generate them from one versioned mapping artifact; never join outputs using independently factorized integers.

A derived feature file may be a disposable cache only when the pipeline regenerates it from, or verifies its source hash and transformation manifest against, the canonical CSV before use.

## Population

Retain all 28 series, including `Innenstadt` and `Kurpark`. The CSV contains no verified flag proving that the two area-labelled series should be excluded. This is a conservative inclusion decision, not a semantic claim.

Reports and plots must identify them by name, avoid calling the population 28 point sensors and disclose their unresolved observational meaning.

## Chronological periods

All filters are half-open.

```text
training:
    2025-06-30 01:00:00+00:00 <= timestamp
    < 2025-07-04 00:00:00+00:00

validation:
    2025-07-04 00:00:00+00:00 <= timestamp
    < 2025-07-06 00:00:00+00:00

continuous test:
    2025-07-06 00:00:00+00:00 <= timestamp
    < 2025-07-14 00:00:00+00:00

condition_a:
    2025-07-06 00:00:00+00:00 <= scored_timestamp
    < 2025-07-08 00:00:00+00:00

condition_b:
    2025-07-08 00:00:00+00:00 <= scored_timestamp
    < 2025-07-14 00:00:00+00:00
```

Training, validation and test are true splits. Windowing, input patching and learned preprocessing artifacts may not cross or combine them.

Conditions A and B are reporting strata within the same test split. Do not reset window construction or patching at July 8. Assign `evaluation_condition` using the scored timestamp.

## Restore original missingness

Parse `war_fehlend` robustly as a boolean and define:

```text
target_observed_mask = (~war_fehlend) AND visitors.notna()
```

Before input patching:

```text
visitors_working = visitors
visitors_working[target_observed_mask == False] = missing
```

This deliberately discards stored interpolations as measurements. A stored value at an originally missing position cannot enter loss, thresholds or evaluation ground truth.

## Exact patching algorithm

Apply this algorithm independently to each series and true split:

1. Reindex to the complete hourly grid for the split.
2. Use `target_observed_mask` to identify maximal consecutive missing runs.
3. Patch a run only when it is one or two hours long and has at least one originally observed anchor in the same split.
4. With observed anchors immediately before and after the run, linearly interpolate between the two anchor values.
5. At the beginning or end of a true split, carry the only available within-split anchor across the one- or two-hour run.
6. Leave runs longer than two hours and wholly unanchored runs unavailable.
7. Never use an anchor from another series or true split.

The July 8 condition boundary is not a true split. A short run that crosses July 8 may use anchors from both sides because both anchors remain inside the continuous test split.

Run detection occurs before patching and is always based on original observations. Interpolation occurs in the final agreed visitor representation. Therefore the transform/scaling decision below must be recorded first.

## Two masks

```text
input_available_mask:
    true for an original observation or a successfully patched short gap

target_observed_mask:
    true only for an original visitor observation
```

- Use `input_available_mask` for window eligibility and expose it as a model input.
- Use `target_observed_mask` for autoencoder loss and evaluable target positions.
- Use a finite neutral placeholder where `input_available_mask=False`.
- Never infer observation status from whether the working numeric value is finite.

## Shared feature concepts

The shared layer exposes:

```text
visitor representation
input_available_mask
target_observed_mask
local_hour_sin
local_hour_cos
local_weekday_sin
local_weekday_cos
series_id
timestamp_utc
evaluation_condition
```

UTC is the storage and splitting clock. Convert to the IANA timezone `Europe/Berlin` before deriving behavioural calendar features.

The autoencoder input is exactly the visitor representation, `input_available_mask` and the four calendar channels. `target_observed_mask` is loss and evaluation metadata, not a model input.

The autoencoder does not use `avgDuration`. The partner owns whether and how the LSTM consumes any additional field, but must document its observation, missingness and scaling semantics. A separate LSTM target transform or scaler is permitted only when the frozen LSTM specification defines it, fits it using training-only eligible targets and records it as model-specific configuration; shared preprocessing may not hardcode it.

## Visitor representation — open acceptance gate

The students must add a dated decision before accepted model training that freezes:

1. the named transform, such as raw, `log1p` or Anscombe;
2. per-series versus pooled scaling;
3. fitting on originally observed training values only;
4. zero-variance and unseen-series behavior;
5. the finite neutral placeholder after scaling.

No validation/test values, anomaly scores, injected labels or injection results may choose this policy.

The historical per-series `log1p` design and the partner snapshot's pooled raw `StandardScaler` are candidates, not simultaneous authorities.

## Model-specific construction

The shared layer ends before model-specific examples are constructed.

For the autoencoder:

- context and reconstruction length are 24 hours;
- stride is one hour;
- training uses `k=0`;
- validation and primary test scoring use `k=6`;
- `k=4` is a stricter test sensitivity;
- eligibility does not depend on an LSTM target.

For the LSTM, the partner owns context, target, features, layout, loss, eligibility, aggregation and score formula. The LSTM specification must consume the canonical source and preserve shared timestamp, mask and split meanings.

## Autoencoder window eligibility

For one 24-hour window:

```text
unavailable_count = count(input_available_mask == False)

training eligible       iff unavailable_count == 0
validation/test primary iff unavailable_count <= 6
strict sensitivity      iff unavailable_count <= 4
```

An eligible reconstruction window may contain patched positions, but only original positions contribute to masked loss and series-hour scores.

## Descriptive missingness fields

For every validation/test series-hour, derive a model-independent fixed trailing context after permitted split-safe patching:

```text
trailing_context_hours
trailing_24h_unavailable_count
trailing_24h_missingness_bucket
```

The context ends at the scored timestamp and covers `[timestamp_utc - 23 hours, timestamp_utc]` within the same true split. `trailing_context_hours` records how many of those hours exist inside the split. `trailing_24h_unavailable_count` counts `input_available_mask=False` positions in that available context.

Assign the bucket as follows:

| Condition | Bucket |
|---|---|
| `trailing_context_hours < 24` | `boundary_lt_24h` |
| unavailable count `0` | `0` |
| unavailable count `1` or `2` | `1-2` |
| unavailable count `3` or `4` | `3-4` |
| unavailable count `5` or `6` | `5-6` |
| unavailable count `7` through `12` | `7-12` |
| unavailable count `13` through `24` | `13-24` |

The test is one continuous true split, so July 8 does not create `boundary_lt_24h`. These fields describe data availability consistently across architectures and never replace model-specific eligibility.

## Shared score interface

The canonical columns are:

```text
model_family
model_variant
model_config_id
run_id
model_seed
evaluation_copy_id
evaluation_condition
injection_seed
noise_seed
series_id
timestamp_utc
anomaly_score
n_contributing_windows
```

Every row represents an eligible, originally observed series-hour. Higher `anomaly_score` means more anomalous within that model; absolute score scales are not compared between models.

`model_config_id` identifies the complete frozen model configuration. `run_id` identifies that configuration together with its model seed, accepted source/data manifest and environment. A deterministic baseline has `model_seed=null`.

Required keys are:

```text
unique score key = (run_id, evaluation_copy_id, series_id, timestamp_utc)
label key        = (evaluation_copy_id, series_id, timestamp_utc)
threshold key    = (run_id, threshold_quantile)
```

Duplicate keys are fatal.

For each declared pair of `model_config_id` values, derive structural support once per configuration on the corresponding clean copy and freeze their common intersection before injection. Every `run_id` belonging to those configurations is evaluated on that same population, and every derived-copy score is left-joined onto it. A missing or non-finite score is a failed run/copy and reported coverage loss, not permission to drop the row and recalculate the metric population.

Also report run-specific and common coverage by condition, date, series and the descriptive missingness fields above.

## Reproducibility outputs

Before accepting a run, save:

- canonical CSV hash;
- complete consumed-file hash manifest;
- row/series/timestamp/missingness counts;
- exact split and condition boundaries;
- patching and mask-test results;
- preprocessing decision and fitted-statistics provenance;
- versioned series mapping if numeric model indices are used;
- `model_config_id`, `run_id`, model configuration and all seed namespaces;
- Python and dependency versions;
- score, label and threshold key validation;
- clean structural support, derived-copy coverage and exclusion reasons.

The current [`verify_design_contract.py`](../../scripts/verify_design_contract.py) verifies the pinned 28-series snapshot and the locked training, validation, Condition A and Condition B boundaries. Later acceptance sessions must extend executable verification to the remaining patching, window-coverage and score-support gates before accepted training.
