# 06 — Checklist and limitations

[Back to documentation index](../README.md)

This checklist implements the gates in the [consolidated implementation handoff](../handoffs/2026-07-24-implementation-handoff.md). It cannot create or override shared decisions.

## Before accepted model training

- [x] Alper recorded that the partner approved the earlier shared structure.
- [x] Alper authorized incorporation of the finalization-review clarifications.
- [ ] The partner gives one bundled reapproval for the revised shared evaluation rules.
- [ ] The approval/reapproval message or meeting record is linked if available.
- [x] The canonical source is `new-data/data/bad_nauheim_bereinigt.csv`.
- [x] The canonical SHA-256 is `af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`.
- [ ] A current verifier reproduces 9,380 rows, 28 series, 335 timestamps, 2,626 originally missing positions and 790 stored values at missing positions.
- [ ] The verifier reproduces 1,795 training `k=0`, 700 validation `k=6`/`k=4`, 1,999 test `k=6` and 1,578 test `k=4` windows plus the written distinct-score counts.
- [ ] The exact visitor transform, scaling scope, fitting population, zero-variance behavior and neutral placeholder are frozen in a dated decision.
- [ ] `series_id` is the exact canonical `name`; any numeric mapping is versioned and shared.
- [ ] Derived feature artifacts are regenerated or provenance/hash-validated against the canonical CSV.
- [ ] `Europe/Berlin` calendar-feature tests pass.
- [ ] One- and two-hour interior and split-edge patch tests pass.
- [ ] Long and unanchored gaps remain unavailable.
- [ ] No patch or window crosses a training/validation/test boundary.
- [ ] Windowing remains continuous across the July 8 reporting boundary.
- [ ] Patched values never contribute to loss, thresholds or evaluation ground truth.
- [ ] Autoencoder `k=0`, primary `k=6` and sensitivity `k=4` counts reproduce on the current population.
- [ ] The numeric trailing-24-hour unavailable count and exact descriptive bucket reproduce by condition, UTC date and series.
- [ ] `Kurpark - Eingang Parkstraße` is recorded as having zero eligible `k=0` training windows.
- [ ] The source/data hash manifest and environment manifest are saved.

Pipeline audits, dry runs and rejected experiments may occur before these boxes pass, but their weights and metrics are not accepted study results.

## Before accepting an autoencoder run

- [ ] `model_config_id`, `run_id`, configuration, source manifest, environment and model seed are saved.
- [ ] Scaling statistics use each originally observed training value once; flattened overlapping windows and patched/imputed values do not enter the fit.
- [ ] Training eligibility is `k=0`; validation/test primary eligibility is `k=6`.
- [ ] Autoencoder examples do not depend on the LSTM's target or eligibility.
- [ ] Early stopping uses validation and restores best weights.
- [ ] Validation reconstruction loss is described only as an engineering selection criterion.
- [ ] The run produces finite scores for every eligible original target.
- [ ] Overlap contributions are recorded in `n_contributing_windows`.
- [ ] Sparse models log activation diagnostics.
- [ ] All lambda candidates and failed runs are retained with reasons.

## Before joint injection and final comparison

- [ ] The partner supplies the frozen LSTM context, target, features, loss, score, aggregation and eligibility specification.
- [ ] Any separate LSTM target scaler is partner-specified, training-only and encoded in model/run identity.
- [ ] Every detector and the baseline export the canonical score schema including `model_config_id`, `run_id`, `series_id` and `evaluation_condition`.
- [ ] Score, label and threshold keys are unique and validated before joins.
- [ ] Clean structural support and its model-configuration-pair intersection are frozen without labels, anomaly-score magnitudes or model seeds.
- [ ] Derived-copy scores are left-joined to frozen support; missing/non-finite required scores fail the run/copy instead of being dropped.
- [ ] Run-specific and common-support coverage is reported by condition/date/series and numeric/bucketed trailing missingness.
- [ ] Injection capacity is checked before inspecting model performance.
- [ ] Both models receive identical event tables.
- [ ] Event ranges use `[start_timestamp_utc, end_timestamp_exclusive)`, match `duration_hours` and do not cross July 8.
- [ ] Condition A and Condition B use separate clean-derived injection copies.
- [ ] Cross-condition score spillover is retained as a diagnostic.
- [ ] Thresholds are the frozen validation quantiles `0.98` and `0.99`.
- [ ] Thresholds use linear quantiles, `score > threshold`, explicit tie behavior and remain unchanged across test copies.
- [ ] The fully specified seasonal/count-residual baseline participates in the score schema and threshold convention.
- [ ] Analytical positive prevalence for AP and `0.5` for ROC-AUC are reported; no random simulation is required.
- [ ] Average precision, ROC-AUC, confusion matrices, zero-division behavior, range overlap and paired score lift follow the written definitions.
- [ ] AP/ROC-AUC are `NA` when required classes are absent; confusion matrices use label order `[0, 1]`.
- [ ] Metrics are calculated per run/copy, seeds are averaged within copy, and family differences are paired by identical scenario and injection seed.
- [ ] Gaussian measurement-noise sensitivity remains separate from Condition B missingness analysis.

## Before submission or presentation

- [ ] The report calls the comparison one between detector families or principles, not an isolated architecture effect.
- [ ] Results distinguish the autoencoder's retrospective reconstruction from the LSTM's documented information set.
- [ ] Synthetic results are not called real-world anomaly accuracy.
- [ ] Unverified real-data detections are called anomaly candidates.
- [ ] Per-series behavior is shown alongside pooled metrics.
- [ ] `Innenstadt` and `Kurpark` semantics are disclosed.
- [ ] Negative and inconvenient findings are retained.
- [ ] Every report citation is checked against the primary source.
- [ ] Both students can explain the shared data and evaluation path and their own model.
- [ ] AI use is disclosed under the applicable university policy.
- [ ] Material deviations are dated, justified and identified as pre- or post-test.

## Required report limitations

1. Approximately 95 training hours do not cover a complete weekly cycle.
2. Weekend behavior first appears mainly in validation and test.
3. Overlapping windows are correlated and do not create independent information.
4. The periods were chosen after inspecting future availability and window survival.
5. The same 48 validation hours affect restored weights, engineering selection and threshold calibration, creating adaptive optimism.
6. Reconstruction-loss selection does not establish anomaly-detection superiority.
7. Validation is only assumed mostly normal; empirical quantiles are not verified false-positive rates.
8. Synthetic anomalies cover only predefined families and do not validate all real anomalies.
9. Unknown native anomalies are counted as negatives in synthetic binary metrics.
10. Similar count deviations can represent events, closures or sensor faults.
11. Direct metrics use a common-score intersection that may favor better-covered hours.
12. Condition B score coverage is selected by model eligibility under severe missingness.
13. Pooled thresholds may affect series differently.
14. The meanings of `Innenstadt` and `Kurpark` remain unresolved.
15. One Gaussian-noise sensitivity does not represent all sensor noise.
16. Results apply only to this short Bad Nauheim period, not other cities, seasons or deployment conditions.
17. Average precision depends on anomaly prevalence; scenario comparisons require positive fractions and the analytical prevalence reference.
18. `Kurpark - Eingang Parkstraße` is unseen during autoencoder window-level training because it has no eligible `k=0` training window.

## Stop conditions

Pause and fix the contract or implementation if:

- canonical hashes or verified counts change unexpectedly;
- two active documents specify different periods, population or preprocessing;
- a patched value reaches loss or evaluation as ground truth;
- a preprocessing artifact includes validation or test;
- a patch or window crosses a true split boundary;
- windowing resets at July 8;
- autoencoder eligibility depends on an LSTM target;
- independently factorized numeric series identifiers are used for joins;
- a score, label or threshold key is duplicated;
- direct metrics use different or derived-copy-selected series-hour populations;
- an injected/noise copy changes the frozen evaluated population;
- a missing or non-finite required derived-copy score is silently dropped;
- test or injection results influence a predeclared decision;
- two models receive different injected event tables;
- an event uses an inclusive end, crosses July 8 or has zero realized change;
- the declared injection capacity cannot be supplied;
- an all-masked loss batch occurs.
