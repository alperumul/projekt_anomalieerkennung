# 04 - Evaluation and injection

[Back to documentation index](../README.md)

## Purpose

This is the detailed operational protocol for the [consolidated implementation handoff](../handoffs/2026-07-24-implementation-handoff.md) and [02 - Shared data contract](02-shared-data-contract.md). It expands common outputs, event copies and metrics without prescribing the partner's LSTM representation, context, loss, target or anomaly-score formula. It may not override the handoff.

## Shared score table

Every detector and the mandatory baseline export one score per eligible, originally observed series-hour:

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

`series_id` is the exact canonical CSV `name`. `model_config_id` identifies the complete frozen model configuration. `run_id` identifies that configuration together with the model seed, accepted source/data manifest and environment. `evaluation_copy_id` uniquely identifies the clean, injected or noise-perturbed copy and its scenario. `evaluation_condition` is `validation`, `condition_a` or `condition_b`. `injection_seed` is null for unmodified data; `noise_seed` is null outside the noise sensitivity; `model_seed` is null only for a deterministic baseline.

Required keys are:

```text
unique score key = (run_id, evaluation_copy_id, series_id, timestamp_utc)
label key        = (evaluation_copy_id, series_id, timestamp_utc)
threshold key    = (run_id, threshold_quantile)
```

Duplicate keys are fatal. Additional columns may be added, but these fields and meanings must remain shared.

### Autoencoder score

For each originally observed target in every eligible reconstruction window:

```text
raw_error = abs(observed_scaled - reconstructed_scaled)
```

The final series-hour score is the mean of errors from all covering windows. Record `n_contributing_windows` because boundaries and missingness change reconstruction support. Maximum aggregation is sensitivity analysis only and must be predeclared.

### Partner-model score

The partner owns the LSTM anomaly-score formula, eligibility rule and any aggregation from model outputs to series-hour scores. Those choices must be documented in the partner's specification and exported through the shared score table above. `n_contributing_windows` records the actual support defined by that implementation.

Absolute anomaly-score magnitudes are not directly comparable across architectures. Comparison uses each run's frozen threshold and ranking metrics on a frozen common set of series-hours.

## Common evaluation support

The two architectures may have different structural score support. For every declared pair of `model_config_id` values and condition:

1. derive each configuration's support on the corresponding clean copy from frozen eligibility and aggregation rules without labels, anomaly-score magnitudes or model seeds;
2. freeze their clean common intersection by `evaluation_copy_id`, `series_id` and `timestamp_utc`;
3. generate derived copies only after that support is frozen;
4. left-join every derived-copy score onto the frozen population;
5. evaluate every `run_id` belonging to those configurations on the same support, and mark a run/copy failed if any required score is missing or non-finite.

Never silently drop a row and recalculate ranking or threshold metrics on an easier injected-copy intersection. Labels are joined only after score and label key uniqueness and the frozen support are verified.

Also report each run's architecture-specific count and the common intersection by evaluation condition, UTC date, series and the numeric/bucketed trailing-24-hour missingness fields in the shared data contract. Metrics calculated on different populations must not be presented as a head-to-head comparison.

## Threshold policy

For each `run_id`, including the deterministic seasonal baseline:

1. Produce final validation series-hour scores.
2. Pool scores across the 28 series under the frozen preprocessing policy.
3. Calculate the 0.98 and 0.99 empirical quantiles using `quantile(..., method="linear")`.
4. Apply both thresholds unchanged to clean and injected test copies.
5. Classify a score as anomalous only when `score > threshold`; equality is non-anomalous.
6. Report per-series clean-test exceedance rates to show whether some series dominate the pooled threshold.

The thresholds are called **validation exceedance thresholds**, not false-positive thresholds, because validation is only assumed to be mostly normal.

The 0.98 and 0.99 quantiles are predeclared operating points, not literature-derived optima. Both are reported; neither may be selected after viewing test results.

The threshold table uses `(run_id, threshold_quantile)` as its unique key and records the method, comparator, score count, threshold value and number of validation observations above it. Do not add or select an extreme quantile after test inspection. Reusing validation for restored-weight selection and threshold calibration creates adaptive optimism and must be declared.

## Why synthetic injection is used

There are no verified real anomaly labels, but the assignment requires confusion matrices and label-dependent metrics. Controlled injection provides known event locations and supports a relative question:

> Under identical predefined perturbations, which detector reacts more reliably?

It does not establish the model's accuracy on every real pedestrian anomaly. [R1](references.md#r1) studies performance on injected anomalies as one of several imperfect surrogates for label-free model selection; it does not validate this project's perturbations or make synthetic labels equivalent to real ground truth.

Models are never trained on injected anomalies.

## Three anomaly families

All magnitude calculations use the final frozen visitor representation and training-only scaling statistics.

### Point spike

```text
Duration:  1 hour
Magnitude: signed offset of 2 or 4 normalized standard deviations
Rule:      scaled_injected = max(scaled_floor, scaled_original +/- magnitude)
```

`scaled_floor` is the final scaled value corresponding to a raw visitor count of zero.

### Level shift

```text
Duration:  4 or 8 consecutive hours
Magnitude: signed offset of 1 or 2 normalized standard deviations
Rule:      scaled_injected[t] = max(scaled_floor, scaled_original[t] +/- magnitude)
```

The local shape remains intact except where a negative shift reaches the zero-count floor.

### Observed-zero dropout

```text
Duration: 2 or 4 consecutive hours
Rule:     visitors_injected[t] = 0
```

The candidate span must have mean original traffic at least as high as that series' observed training median. This avoids labelling an ordinary near-zero night interval as an obvious dropout. Call it sensor-fault/closure-like because counts alone cannot distinguish those causes.

## Placement protocol

For every scenario and injection seed:

- inject into test only;
- use originally observed positions only;
- use the frozen clean common support for the declared pair of model configurations;
- require every labelled event hour to belong to that support;
- sample uniformly from eligible candidates using a recorded seed;
- reject a candidate whose mean realized scaled change is zero after clipping;
- avoid overlapping injected events;
- target five events on distinct series per scenario, reducing the count only if a pre-model capacity check proves this impossible;
- give both models identical series, timestamps, directions, magnitudes and durations;
- do not allow an event to cross `2025-07-08 00:00 UTC`.

Injection seeds:

```text
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
```

Create condition-specific clean-derived copies for every type/magnitude/duration/direction scenario. A Condition A copy contains only Condition A events, and a Condition B copy contains only Condition B events. Window generation remains continuous across July 8. Positive and negative point/level changes are separate scenario factors; dropout has only the downward direction. This prevents interactions between anomaly families and avoids an undocumented random direction mixture.

Score spillover outside an event but inside the same condition remains a false positive. Spillover crossing July 8 is retained in a separate diagnostic table and is not counted in the other condition's headline metrics.

The families, magnitudes, durations, five-event target and 15 injection seeds are predeclared project choices. They span point, sustained and sensor-fault/closure-like changes at two severities; no cited source is claimed to make these exact settings realistic or optimal.

## Event table

Each injected copy has a machine-readable companion table:

```text
series_id
start_timestamp_utc
end_timestamp_exclusive
anomaly_type
requested_magnitude
realized_magnitude_min
realized_magnitude_mean
realized_magnitude_max
duration_hours
direction
injection_seed
evaluation_copy_id
evaluation_condition
```

Event ranges are half-open: `[start_timestamp_utc, end_timestamp_exclusive)`. The difference between the two timestamps must equal `duration_hours`, and the range must contain exactly that many hourly positions. Realized magnitudes are absolute changes in the final scaled visitor representation; minimum, mean and maximum are retained because clipping and zero-dropout can make the change vary within one range event. An event with zero mean realized change is invalid. Results must retain both requested and realized severity so a heavily clipped downward event is not described only by its larger requested offset.

For binary point metrics, every event hour on the event's series is positive. Other hours in the frozen common evaluation support are negative, with the explicit limitation that unknown native anomalies may therefore be counted as negatives.

## Hybrid evaluation

### Part A - controlled synthetic comparison

Calculate metrics per `run_id` and injection copy, retaining anomaly type, requested and realized magnitude/duration, direction, model seed and injection seed:

- `sklearn.metrics.average_precision_score` as the primary imbalance-aware ranking metric ([R7](references.md#r7)); label it **average precision (AP)** rather than ambiguous PR-AUC;
- ROC-AUC because the assignment requires it, with an imbalance caveat;
- confusion matrix, precision, recall and F1 at both thresholds;
- the professor-confirmed or dual-reported range-overlap measure(s);
- mean, standard deviation and paired model differences.

AP depends on positive prevalence. Compare architectures within the same scenario copy; do not interpret raw AP differences between point and longer range scenarios as pure detector differences without reporting each copy's positive fraction and analytical prevalence reference.

Use confusion-matrix label order `[0, 1]`. Calculate precision, recall and F1 with `zero_division=0` and separately flag zero-denominator cases. Report AP and ROC-AUC as `NA` when the required classes are absent.

Average model-seed metrics within each copy, then pair detector-family differences by identical evaluation condition, scenario and injection seed. Event hours and overlapping window contributions are not independent replicates and are not the sample size for uncertainty summaries.

Do not use naive point adjustment; it can greatly inflate weak detectors ([R2](references.md#r2)). Contextual score spillover outside an injected interval therefore remains a false positive in point metrics; inspect and discuss this effect separately because the two architectures have different receptive fields.

For one range event, group consecutive predicted positive hours on the same series. If predicted ranges intersect the injected range, calculate:

```text
temporal_IoU = hours(injected range AND intersecting predicted ranges)
             / hours(injected range OR  intersecting predicted ranges)
```

IoU is zero if no predicted range intersects. Point anomalies are excluded from the range-overlap metric.

[R3](references.md#r3) supports range-aware evaluation but does not prescribe this IoU formula. The assignment does not define its requested overlap coefficient. Confirm the intended formula with the professor before freezing evaluation. If no clarification is available, report both temporal IoU and the Szymkiewicz-Simpson overlap `intersection / min(injected duration, predicted duration)` under explicit names rather than claiming either is the uniquely required coefficient.

### Part B - untouched-test exploration

Run every model on unmodified test data and show its highest-scoring real-data candidates. For each candidate include:

- series and local timestamp;
- observed count;
- reconstruction or the partner model's corresponding output;
- anomaly score and applicable threshold;
- nearby missingness and observation availability;
- agreement or disagreement between architectures;
- event, weather, closure or sensor-fault interpretations only where supporting evidence exists.

These are **anomaly candidates**, not confirmed anomalies.

### Part C - counterfactual score lift

For injected event positions:

```text
score_lift = score_on_injected_copy - score_on_clean_copy
```

This paired comparison asks whether the controlled change increased model surprise at the same location. It reduces, but does not eliminate, contamination from unknown native anomalies.

### Part D - lean noise-robustness sensitivity

Use one small test of robustness to background measurement noise:

- Use the moderate scenario from each family: point magnitude 2 in both directions, four-hour shift magnitude 1 in both directions and two-hour downward dropout.
- Add Gaussian noise `N(0, 0.1^2)` to a copy of originally observed scaled test measurements outside injected events, then clip at `scaled_floor`.
- Generate both models' windows and targets from the same perturbed copy.
- Use noise seeds `[101, 102, 103, 104, 105]`, separate from model and injection seeds.
- Reuse the exact event locations and labels from the corresponding no-noise copy.
- Report changes in AP and thresholded F1 plus mean absolute score change on non-injected positions.

This does not represent every kind of real sensor noise. It is a narrow, reproducible sensitivity check required by the project scope.

The Gaussian form and standard deviation 0.1 are test conditions chosen by the team, not an empirically estimated sensor-noise model. The report must call this a sensitivity analysis, not measured real-world robustness.

## Generalization claim

Generalization means performance on later chronologically held-out hours and consistency across the 28 retained series. Report pooled and per-series behaviour.

`Kurpark - Eingang Parkstraße` has no eligible autoencoder `k=0` training window. Report its autoencoder results separately as transfer to a series unseen during window-level training rather than ordinary within-population generalization.

The dataset cannot justify claims about other cities, seasons or long-term drift.

## Seasonal baseline

Include one inexpensive reference:

```text
expected = series-specific training seasonal reference
score    = abs(observed_scaled - expected_scaled)
```

Freeze it as follows:

1. Fit only on originally observed training visitor values in the final accepted shared visitor representation.
2. Define `is_weekend` from `Europe/Berlin` local time.
3. Use the median for each `series_id x local_hour x is_weekend` cell.
4. Fall back in order to the `series_id x local_hour` median, the `series_id` median and the global originally observed training median.
5. Score every originally observed validation/test series-hour with `n_contributing_windows=1`.
6. Export it through the canonical score schema with a deterministic `run_id` and `model_seed=null`.
7. Calibrate its 0.98 and 0.99 validation thresholds using the same linear quantile and strict-greater-than convention.
8. Include it in clean structural support and coverage reporting. Deep-model head-to-head results remain separately identifiable.

The baseline is a sanity check, not a third student-owned deep architecture. Failure to beat it is a meaningful result.

This grouping and fallback are project conventions chosen because the training slice contains too few repeated weekly cycles for a stable richer seasonal model.

Use the analytical positive fraction as the AP reference and `0.5` as the ROC-AUC reference. Do not add a random-score simulation unless it is explicitly declared as a non-normative sensitivity analysis. A variance-stabilized count residual or other additional simple baseline is a useful extension, not an acceptance gate.

## Evaluation outputs

- score tables for untouched and injected copies;
- event tables and seed configuration;
- threshold table keyed by `run_id` and threshold quantile;
- pooled and per-series clean-test exceedance rates;
- metric tables retaining `model_config_id`, `run_id`, type, severity, model seed and injection seed;
- clean structural-support and architecture-specific coverage tables for every evaluation copy, condition, UTC date, series and numeric/bucketed trailing missingness;
- plots connecting errors to timestamps and missingness;
- paired comparison summaries;
- a record of any deviation from this protocol.
