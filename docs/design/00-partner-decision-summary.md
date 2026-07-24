# Partner approval summary

**Current status:** Alper confirmed on 2026-07-24 that his partner approved the earlier shared structure. Alper subsequently authorized the material evaluation clarifications summarized below; one bundled partner reapproval of the revised rules remains pending. The approval/reapproval message or meeting record should be linked when available. The visitor transform/scaling choice in item 4 remains a separate pre-training decision.

The [consolidated implementation handoff](../handoffs/2026-07-24-implementation-handoff.md) is the normative shared contract. This page is its concise human-facing summary and cannot override it.

1. **Data and provenance:** Use [`new-data/data/bad_nauheim_bereinigt.csv`](../../new-data/data/bad_nauheim_bereinigt.csv) as the source of truth, with SHA-256 `af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`.

2. **Population and identity:** Retain all 28 temporal series. Use the exact canonical `name` as `series_id`; numeric indices require one versioned mapping and are never independent join identifiers. Disclose the unresolved semantics of `Innenstadt` and `Kurpark`; do not claim that all series are point sensors.

3. **Missingness and patching:** Treat every `war_fehlend=True` visitor value as originally missing. Patch only one- or two-hour runs within one true split, using within-split interpolation or a single split-edge anchor. Longer or unanchored runs remain unavailable. Patched values may be inputs but never ground truth.

4. **Preprocessing:** Fit preprocessing artifacts on originally observed training values only. Derive behavioural calendar features in `Europe/Berlin` while storing and splitting in UTC. Supply separate input-availability and target-observation masks. The exact visitor transform, scaling scope and neutral placeholder must be recorded before accepted model training; test or injection results may not decide them.

5. **UTC periods:** Training is `2025-06-30 01:00`–`2025-07-04 00:00`; validation is `2025-07-04 00:00`–`2025-07-06 00:00`; one continuous test timeline is `2025-07-06 00:00`–`2025-07-14 00:00`. Condition A ends and Condition B begins at `2025-07-08 00:00`. July 8 is a reporting boundary, not a new split.

6. **Ownership:** Alper owns every autoencoder-specific choice. The partner owns every LSTM-specific choice, including context, target, consumed features, architecture, loss, eligibility, aggregation and score formula.

7. **Run identity and fair support:** Each score belongs to an immutable `run_id` and `model_config_id`, with unique score, label and threshold keys defined in the handoff. Freeze each declared model-configuration pair's common structural support on the clean copy before injection. All seeds use that population. Left-join derived-copy scores onto it; a missing or non-finite score fails the run/copy and may not be silently dropped.

8. **Validation and thresholds:** Validation reconstruction loss is an engineering selection criterion, not proof of anomaly-detection superiority. For each `run_id`, freeze the `0.98` and `0.99` empirical validation-score quantiles using linear interpolation; classify only `score > threshold` as anomalous. Apply both thresholds unchanged to every test condition and derived copy. Declare the adaptive reuse of the 48-hour validation period.

9. **Controlled tests:** Give both models identical test-only anomaly copies on frozen clean common support. Use half-open event ranges and do not place an event across July 8. Keep Condition A and B copies separate, and keep Gaussian measurement-noise sensitivity separate from missingness robustness. Never train on injected anomalies.

10. **Evaluation and claims:** Use average precision, ROC-AUC, the threshold metrics and the agreed range measures without point adjustment. Use the analytical positive-prevalence AP reference and `0.5` ROC-AUC reference. Include the fully frozen seasonal/count-residual baseline. Summarize seeds using the hierarchy in the handoff rather than treating event hours as independent. Synthetic tests measure response to predefined changes, not proven accuracy on unknown real anomalies; unverified real findings are anomaly candidates.

11. **Descriptive missingness:** Store the numeric unavailable-hour count and predeclared bucket from one fixed trailing 24-hour context after patching. This model-independent description does not replace either model's eligibility rule.

Not claimed by the earlier approval or this reapproval request:

- any LSTM-specific formulation;
- a claim that the two area-labelled series have verified identical semantics;
- a claim that reconstruction-loss selection identifies the best anomaly detector;
- a claim that advanced survey recommendations are automatically binding;
- a claim that either overlap formula is definitely the professor's intended coefficient.

Any material change to these shared items requires both students' approval and a dated decision record.

## Bundled reapproval requested

The partner is asked to approve the following material clarifications as one bundle:

1. exact `series_id`, `model_config_id`, `run_id`, score, label and threshold identities;
2. model-configuration support frozen on clean copies before injection, with no silent dropping of failed derived-copy scores;
3. the numeric and bucketed fixed trailing-24-hour missingness description;
4. the fully specified seasonal-median baseline and analytical AP/ROC references;
5. average precision, quantile, comparator, absent-class, zero-division and seed-aggregation conventions;
6. half-open event ranges and the reproduced feasibility/unseen-series disclosure.

Record the partner's name, date and approval evidence here or link the dated decision record before accepted training.
