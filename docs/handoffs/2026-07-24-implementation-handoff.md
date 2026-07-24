# Consolidated implementation handoff — shared data and evaluation contract

**Date:** 2026-07-24

**Status:** revised shared contract; final visitor preprocessing, executable acceptance verification and bundled partner reapproval still gate accepted model training

**Approval record:** Alper confirmed on 2026-07-24 that his partner approved the earlier shared structure. On the same date, Alper authorized the score-identity, frozen-support, missingness-bucket, baseline and metric clarifications added after finalization review. Because these are material shared evaluation rules, one bundled partner reapproval of this revision remains required. The original approval or reapproval message should be linked when available.

**Canonical data snapshot:** [`new-data/data/bad_nauheim_bereinigt.csv`](../../new-data/data/bad_nauheim_bereinigt.csv)

**SHA-256:** `af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`

## 1. Authority

This file is the single normative contract for the current shared population, time structure, missingness semantics, interoperability and evaluation rules.

The remaining documents have narrower roles:

- [`00-partner-decision-summary.md`](../design/00-partner-decision-summary.md) is the concise human approval summary.
- [`01-project-scope-and-decisions.md`](../design/01-project-scope-and-decisions.md) defines the research question and meaning of the comparison.
- [`02-shared-data-contract.md`](../design/02-shared-data-contract.md) gives implementation detail for this contract.
- [`03-conv1d-autoencoder.md`](../design/03-conv1d-autoencoder.md) governs Alper's model-specific decisions only.
- [`04-evaluation-and-injection.md`](../design/04-evaluation-and-injection.md) gives operational evaluation detail.
- [`05-responsible-ai-and-evidence.md`](../design/05-responsible-ai-and-evidence.md) governs evidence and decision recording.
- [`06-checklist-and-limitations.md`](../design/06-checklist-and-limitations.md) is the execution gate.

Documents 00–06 may refine their assigned topic but may not override this file. If a conflict is found, stop, update the affected document and record the change; do not combine competing rules. The 2026-07-22 review and the earlier 26-series/train-core design are historical evidence, not implementation authority.

## 2. Meaning of the comparison and ownership

The study compares two detector families or anomaly-detection principles under shared data and evaluation rules. It does not claim to isolate architecture as the only differing causal factor.

- Alper owns the standard and sparse Conv1D autoencoders.
- The partner owns every LSTM-specific decision: context, target, consumed features, tensor layout, architecture, loss, eligibility, aggregation and anomaly-score formula.
- Shared code exposes source values, timestamps, masks and agreed calendar features. It must not force the LSTM into a 24-to-25-hour forecast or make autoencoder eligibility depend on an LSTM target.
- Both models export final series-hour scores through the shared schema in section 10.

## 3. Canonical snapshot and provenance

The source of truth is:

```text
new-data/data/bad_nauheim_bereinigt.csv
```

Verified facts for the pinned snapshot:

- 9,380 rows;
- 28 retained temporal series;
- 335 hourly timestamps from `2025-06-30 01:00 UTC` through `2025-07-13 23:00 UTC`;
- 2,626 originally missing series-hours;
- 790 `war_fehlend=True` positions containing a stored interpolation;
- Condition A original-observation coverage: approximately 83.854%;
- Condition B original-observation coverage: approximately 50.397%.

Daily original-observation coverage:

| UTC date | Condition | Coverage |
|---|---|---:|
| 2025-07-06 | A | 82.44% |
| 2025-07-07 | A | 85.27% |
| 2025-07-08 | B | 47.32% |
| 2025-07-09 | B | 54.76% |
| 2025-07-10 | B | 65.77% |
| 2025-07-11 | B | 45.54% |
| 2025-07-12 | B | 64.73% |
| 2025-07-13 | B | 24.26% |

The current snapshot is explicitly accepted as a new canonical input version. A row-level comparison with the unavailable earlier file is therefore not required for acceptance. The earlier hash `2e97d9…edd887` remains historical provenance only.

Before the first accepted run:

1. verify the canonical hash and counts;
2. verify or regenerate the complete [`new-data` snapshot manifest](../provenance/2026-07-24-new-data.sha256);
3. record the Python and dependency versions;
4. save the final run configuration and source revision or snapshot manifest.

The preliminary environment audit is recorded in [`2026-07-24-pre-implementation.md`](../environment/2026-07-24-pre-implementation.md). It is not a substitute for the first accepted run's environment manifest.

## 4. Population

Use all 28 retained temporal series.

`Innenstadt` and `Kurpark` remain included because the source contains no verified semantic flag that justifies excluding them. Their names and absent point coordinates do not prove that they share or differ from the observational meaning of the other series.

The report must:

- call them temporal series rather than claiming that all 28 are point sensors;
- disclose the unresolved meaning of the two area-labelled series;
- report per-series results so their influence is visible.

A 26-series sensitivity analysis is an optional improvement, not an acceptance gate. It becomes strongly advisable if pooled preprocessing or pooled thresholds make the two series influential.

## 5. UTC periods and reporting conditions

All boundaries are half-open: `start <= timestamp < end`.

| Role | UTC period |
|---|---|
| Training | `2025-06-30 01:00` to `2025-07-04 00:00` |
| Validation | `2025-07-04 00:00` to `2025-07-06 00:00` |
| Continuous test timeline | `2025-07-06 00:00` to `2025-07-14 00:00` |
| Condition A — higher availability | scored timestamps from `2025-07-06 00:00` to `2025-07-08 00:00` |
| Condition B — severe missingness | scored timestamps from `2025-07-08 00:00` to `2025-07-14 00:00` |

Training, validation and test are true split boundaries:

- no window crosses one of these boundaries;
- no patch uses an anchor from another split;
- no preprocessing statistic is learned from validation or test.

July 8 is only a reporting and injection-placement boundary inside one continuous test split:

- window generation does not reset at July 8;
- input patching may use valid test-split anchors on either side of July 8;
- a window may cross July 8;
- a score is assigned to a condition by the timestamp being scored;
- models, weights, preprocessing objects and thresholds remain frozen across both conditions.

Condition A is the main higher-availability comparison; it is not called complete or clean. Condition B is a separate missing-data robustness and score-coverage analysis. Their metrics remain separate and are never combined into one headline result.

The report must disclose that the periods and July 8 condition boundary were selected after inspecting future availability and window survival. This is not anomaly-label leakage, but it means the held-out period was not blind with respect to missingness.

## 6. Original observations and the two masks

Define:

```text
target_observed_mask = (~war_fehlend) AND visitors.notna()
```

A value stored where `war_fehlend=True` is not an observation. It may be regenerated under the patching rule for input context, but it never becomes ground truth.

The masks have distinct meanings:

```text
input_available_mask
    true for original observations and successfully patched short gaps

target_observed_mask
    true only for original visitor observations
```

- `input_available_mask` controls input eligibility and is exposed to models.
- `target_observed_mask` controls autoencoder reconstruction loss and defines evaluable ground truth.
- Patched or placeholder values never contribute to reconstruction loss, threshold populations or evaluation labels as observations.

## 7. Exact short-gap patching algorithm

Patching is performed independently for each series and true split after restoring every `war_fehlend=True` visitor position to missing.

1. Reindex the series to the complete hourly grid for that split.
2. Find maximal consecutive runs where `target_observed_mask=False`.
3. A run is patchable only when its length is one or two hours and at least one originally observed anchor exists inside the same true split.
4. When both adjacent within-split anchors exist, linearly interpolate the visitor representation between them.
5. At a true split edge, when exactly one within-split anchor exists, carry that anchor backward or forward across the one- or two-hour run.
6. Runs longer than two hours, and runs without a within-split anchor, remain unavailable.
7. Set `input_available_mask=True` only for original observations and successfully patched positions.
8. Supply a finite neutral placeholder to the network for unavailable values while keeping `input_available_mask=False`.

Run detection always uses the original-observation mask, not whether the CSV happens to contain an interpolated value. Patching may not cross the training/validation/test boundaries. July 8 is not a true split boundary, so a one- or two-hour run may be patched across it using test-only anchors.

Interpolation occurs in the final agreed visitor representation. The representation decision in section 8 must therefore be frozen before accepted model training.

## 8. Shared preprocessing and remaining acceptance gate

The following choices are frozen:

- timestamps are stored, split and joined in UTC;
- behavioural hour and weekday features are derived after conversion to `Europe/Berlin`;
- preprocessing artifacts are fitted on training only;
- fitting uses originally observed training visitor values, not stored or regenerated patches;
- the shared layer exposes visitor values, both masks and local calendar features;
- `avgDuration` is not an autoencoder feature;
- the partner decides whether the LSTM consumes any additional exposed field and documents its handling;
- a separate LSTM target transform or scaler is allowed only when the frozen partner specification defines it, fits it on training-only eligible ground truth and records it in `model_config_id` and `run_id`; the shared pipeline may not hardcode it in advance.

One material choice remains open: the final visitor representation and scaling policy. The old design proposed per-series `log1p` plus train-only standardization; the partner snapshot currently applies a pooled `StandardScaler` and also scales `avgDuration`. Neither choice becomes authoritative by accident.

Before the first accepted model training run, the students must record one explicit decision covering:

- raw, `log1p`, Anscombe or another named visitor transform;
- per-series or pooled scaling;
- exact fitting population;
- zero-variance and unseen-series behavior;
- the neutral placeholder after scaling.

The decision must be made without test scores, injected labels or injection performance. Until it is recorded, data-pipeline audits and dry runs are allowed, but their trained weights or metrics are not accepted study results.

## 9. Autoencoder eligibility

These rules apply only to Alper's 24-hour reconstruction model:

- training uses `k=0` after permitted short-gap patching; a training window with any remaining unavailable input hour is excluded;
- validation and primary test scoring use `k=6`, requiring at least 18 of 24 input hours to be available;
- `k=4`, requiring at least 20 of 24 input hours, is reported as a stricter sensitivity analysis;
- masked reconstruction loss uses only originally observed target positions;
- autoencoder eligibility never depends on the existence of an LSTM forecast target.

The partner defines and documents LSTM eligibility. Model-specific scored-hour coverage is always reported.

Two independent read-only audits reproduced the following feasibility counts under the written patching and eligibility rules. They are expected values for the acceptance verifier, not a substitute for an executable version-controlled check:

| Split and rule | Eligible windows | Distinct scored originally observed series-hours |
|---|---:|---:|
| Training, `k=0` | 1,795 | 2,325 |
| Validation, `k=6` | 700 | 1,155 |
| Validation, `k=4` | 700 | 1,155 |
| Continuous test, `k=6` | 1,999 | 2,689 |
| Continuous test, `k=4` | 1,578 | 2,555 |

Under `k=6`, Condition A contains 1,127 scored hours out of 1,127 originally observed hours, and Condition B contains 1,562 out of 2,032, or approximately 76.87%. Under `k=4`, Condition A remains 1,127 out of 1,127 and Condition B contains 1,428 out of 2,032, or approximately 70.28%.

`Kurpark - Eingang Parkstraße` has originally observed training values but no eligible 24-hour `k=0` training window. It remains in the population, but its autoencoder results must be identified as performance on a series unseen during window-level training.

## 10. Canonical score-table schema

Every detector and the mandatory baseline export one row per eligible, originally observed series-hour:

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

Definitions:

- `series_id` is the exact Unicode value from the canonical CSV `name` column. If numeric indices are needed internally, use one versioned mapping artifact and never join on independently factorized integers.
- `model_config_id` identifies the complete frozen hyperparameter and model-specific preprocessing configuration.
- `run_id` identifies one exact `model_config_id`, model seed, canonical/source manifest and accepted environment. It is immutable and globally unique within the project.
- `model_seed` is null only for a deterministic baseline with no fitted stochastic component.
- `evaluation_copy_id` identifies the clean, injected or noise-perturbed data copy and scenario.
- `evaluation_condition` is one of `validation`, `condition_a`, or `condition_b` for the current validation and test-derived scores. Additional values may be introduced for explicit diagnostics.

The unique score key is:

```text
(run_id, evaluation_copy_id, series_id, timestamp_utc)
```

The label key is:

```text
(evaluation_copy_id, series_id, timestamp_utc)
```

The threshold key is:

```text
(run_id, threshold_quantile)
```

Duplicate score or label keys are fatal. Labels are joined only after the evaluation population is frozen and key uniqueness is verified.

For each declared pair of `model_config_id` values, derive structural support once per configuration on the clean copy and freeze their intersection for the same `evaluation_copy_id`, `series_id` and `timestamp_utc`. Every `run_id` belonging to those configurations is evaluated on that same population. Section 13 defines how this support is frozen for derived copies. Report separately:

- each run's scoreable count;
- the common intersection;
- coverage by condition, UTC date, series and the descriptive missingness variables below.

For every validation/test series-hour, derive model-independent missingness descriptors from the fixed trailing 24-hour context ending at the scored timestamp after permitted split-safe patching:

```text
trailing_context_hours
trailing_24h_unavailable_count
trailing_24h_missingness_bucket
```

If fewer than 24 within-split hours exist, use `boundary_lt_24h`. Otherwise bucket the numeric unavailable count as `0`, `1-2`, `3-4`, `5-6`, `7-12` or `13-24`. The continuous test is one true split, so July 8 does not create a boundary bucket. These fields are descriptive and never replace either model's eligibility rule.

Absolute score magnitudes are not compared directly between architectures.

## 11. Validation and thresholds

The same 48-hour validation period is used for:

- early stopping and best-weight restoration;
- reconstruction-loss-based autoencoder engineering selection;
- sparse-lambda comparison;
- calibration of the predeclared empirical score quantiles `0.98` and `0.99`.

For each `run_id`, calculate final validation series-hour scores and both quantiles using the frozen population and preprocessing. Use `quantile(..., method="linear")`. A score is anomalous only when `score > threshold`; a tie is non-anomalous. Apply both thresholds unchanged to both test conditions and every derived test copy. Report the validation-score count, threshold value, quantile method, comparator and number of scores above each threshold. Do not select one quantile after seeing test results.

Validation reconstruction loss is an engineering criterion, not evidence that a configuration is the superior anomaly detector. Report all sparse-lambda candidates. Do not use injected test results to choose architecture, lambda, weights or threshold.

Reusing one short, correlated validation period for weight selection and threshold calibration creates adaptive optimism. This is an accepted dataset-size compromise and a required limitation, not evidence of independent validation.

## 12. Evaluation requirements

The mandatory comparison contains:

- the standard and sparse Conv1D autoencoders;
- the partner-owned LSTM;
- the frozen inexpensive series-specific seasonal/count-residual baseline;
- the analytical positive-prevalence reference for average precision and `0.5` reference for ROC-AUC.

The seasonal baseline is fitted only on originally observed training values in the accepted shared visitor representation. Its expected value is the median by `series_id x Europe/Berlin local hour x weekend flag`, with fallback to the `series_id x local hour` median, then the `series_id` median, then the global originally observed training median. It scores every originally observed validation/test series-hour, uses `n_contributing_windows=1`, has a deterministic `run_id` and null `model_seed`, exports the shared schema and calibrates both validation thresholds under section 11.

Advanced metrics, extra baselines, count-aware variants such as an Anscombe residual, external weather/event triangulation and a 26-series sensitivity are useful improvements rather than universal acceptance gates. External interpretations are reported only where evidence is actually available.

For controlled injections, report:

- `sklearn.metrics.average_precision_score` as the named primary imbalance-aware ranking metric; do not call it an unspecified PR-AUC;
- ROC-AUC because the assignment requires it;
- confusion matrix, precision, recall and F1 at both frozen thresholds;
- the professor-confirmed overlap coefficient or both temporal IoU and Szymkiewicz-Simpson overlap under explicit names;
- paired differences, mean, standard deviation and seed structure;
- counterfactual score lift at injected positions.

Use confusion-matrix label order `[0, 1]` and `zero_division=0` for precision, recall and F1, while separately flagging every zero-denominator case. Report average precision and ROC-AUC as `NA` when their required classes are absent.

Calculate each metric per `run_id` and injection copy. Average model seeds within each copy, then pair detector-family differences only by identical evaluation condition, scenario and injection seed. Event hours and overlapping window contributions are not independent replicates and must not be used as the sample size for uncertainty summaries.

Do not use naive point adjustment. Unknown native anomalies in nominally negative hours, score correlation from overlapping windows and unequal detector information sets remain limitations.

## 13. Injection and July 8 behavior

- Use separate clean-derived injection copies for Conditions A and B.
- An injected event may not cross `2025-07-08 00:00 UTC`.
- A Condition A copy contains Condition A events only; a Condition B copy contains Condition B events only.
- Headline metrics use scored timestamps belonging to that copy's condition.
- Score spillover outside an event but inside the same condition remains a false positive.
- Spillover crossing July 8 is retained in a separate diagnostic table, not silently discarded or counted in the other condition's headline result.
- Window generation remains continuous across July 8.
- The Gaussian measurement-noise sensitivity remains separate from Condition B; missingness robustness and measurement-noise sensitivity are not interchangeable.

For every declared model-configuration pair and condition:

1. determine each `model_config_id`'s structural support on the corresponding clean copy without using anomaly scores, labels or model seeds;
2. freeze the clean common intersection;
3. generate injections only on that frozen support;
4. left-join every injected-copy score onto the frozen support;
5. if any required score is missing or non-finite, mark the affected `run_id`/copy failed and report the coverage loss; do not calculate ranking or threshold metrics after silently dropping the row.

Injected values may not change the evaluated population. Event timestamps use half-open ranges `[start_timestamp_utc, end_timestamp_exclusive)`.

The event table and capacity rule can be implemented before the LSTM is complete, but final clean common-support event placement cannot be frozen until the partner supplies the LSTM specification and structural score coverage. This blocks joint injection evaluation, not Alper's model development after the shared preprocessing gate is closed.

## 14. Current `new-data` implementation status

The partner pipeline in [`new-data/src/windowing.py`](../../new-data/src/windowing.py) successfully loads the current derived feature snapshot and implements the approved training, validation and Condition A date boundaries. The derived file can remain a disposable artifact only if it is regenerated from, or hash/provenance-validated against, the canonical CSV.

Its current outputs are useful audit evidence, not accepted contract counts:

- training windows: 1,709;
- validation windows: 416;
- July 6–8 test windows: 347.

Those counts reflect implementation choices that still conflict with this contract:

1. the test ends at July 8 instead of July 14;
2. autoencoder windows require the LSTM's 25th-hour target;
3. one shared `k=4` rule is applied to both models;
4. all long gaps are median-filled;
5. the two-hour run-length patch rule is not enforced;
6. availability is not an input channel;
7. `avgDuration` is included in the autoencoder input;
8. calendar features are derived in UTC;
9. scaling is pooled and still unresolved under section 8;
10. paths depend on the process working directory;
11. the derived feature CSV can be consumed without regeneration or validation against the canonical CSV;
12. scaling is fitted on flattened eligible windows, so overlapping observations are reweighted and patched or imputed values enter the fit instead of using each originally observed training value once;
13. a separate LSTM target scaler is hardcoded before the partner-owned LSTM specification decides whether it is needed.

A derived feature artifact and a separate LSTM target scaler are not inherently forbidden. They are defects here because their provenance and ownership are not yet governed by the frozen contract.

Preserve working components where tests confirm them, but do not treat these current choices as implicit amendments to the contract.

## 15. Gates before accepted training and evaluation

Accepted model training requires:

1. the section 8 preprocessing decision;
2. a current verifier using `new-data`, all 28 series and the half-open periods above;
3. reproduced continuous-test autoencoder coverage for `k=6` and `k=4`, by condition/date/series/missingness bucket;
4. passing mask, patching, timezone and split-boundary tests;
5. a source/data hash manifest and environment record;
6. bundled partner reapproval of the material shared-rule clarifications in this revision.

Joint comparison and injection additionally require:

7. the partner's LSTM specification and eligibility;
8. validated score, label and threshold key uniqueness;
9. reproduced model-specific and frozen clean common-support counts;
10. a deterministic common-support injection-capacity check;
11. frozen half-open event tables and thresholds;
12. passing tests that injected copies cannot change the evaluated population.

The professor's Transformer wording and intended anomaly-overlap coefficient remain external clarification items. If no overlap clarification is received, report both named range measures without claiming either is uniquely required.

## 16. Required report limitations

The final report must state that:

- approximately 95 training hours do not cover a complete weekly cycle;
- weekend behavior appears mainly in validation and test;
- overlapping windows are correlated examples;
- the split was availability-informed;
- the 48-hour validation period is adaptively reused;
- thresholds assume mostly normal validation data and are not verified false-positive rates;
- direct metrics use a potentially easier common-score intersection;
- Condition B preferentially retains scoreable, better-covered hours;
- `Kurpark - Eingang Parkstraße` has no eligible `k=0` autoencoder training window and is unseen during window-level training;
- the two area-labelled series have unresolved observational semantics;
- synthetic anomalies do not prove accuracy on unknown real anomalies;
- conclusions apply only to this short Bad Nauheim case study, not other cities, seasons or long-term deployment.

## 17. Immediate implementation sequence

1. Record the final visitor transform/scaling decision.
2. Update the verifier and shared preprocessing tests.
3. Extend the test timeline through `2025-07-14 00:00 UTC` without resetting at July 8.
4. Separate shared preparation from model-specific example construction.
5. Implement the versioned `series_id`, score identity, descriptive missingness and metric conventions.
6. Reproduce and record all acceptance counts.
7. Obtain bundled partner reapproval of the revised shared evaluation rules.
8. Capture the accepted environment and source manifest.
9. Begin accepted autoencoder training.
10. Freeze clean common-support injections after the LSTM export contract is available.
