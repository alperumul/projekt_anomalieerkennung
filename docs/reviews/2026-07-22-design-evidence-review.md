# Independent design and evidence review - 2026-07-22

[Back to documentation index](../README.md)

**Reviewer:** Codex, acting as an AI-assisted independent reviewer

**Scope:** `docs/design/01` through `06`, `references.md`, the assignment brief, delivered preprocessing code and agreed CSV

**Historical status:** superseded where the jointly approved 2026-07-24 consolidated contract differs

**Review timing:** pre-implementation and pre-results

## Overall verdict

The revised design is a credible pre-results agreement for a small student case study. Its six external research citations were real and correctly identified, and a seventh source was added for the PR-AUC claim. The dataset and window numbers reproduce exactly from the agreed CSV.

The design is not a literature-derived recipe, and it should not be presented as one. Its strongest parts are the explicit leakage controls, separation of input availability from observed ground truth, limited synthetic-evaluation claims, baseline, and stated limitations. Its weakest parts before this review were over-attribution of exact metric choices to broad research papers, intrusion into partner-owned model decisions, unequal evaluation populations, local-only provenance references and AI-log entries that sounded human-verified without named human sign-off. Those issues were corrected in the documents.

Four decisions still require people rather than more AI text:

1. The professor must clarify whether a Transformer is expected in addition to the explicit minimum of two architectures.
2. The professor should clarify which overlap coefficient is intended; otherwise the report should name and show both proposed formulas.
3. The partner must provide and approve the LSTM specification. Both students need only approve the shared score interface and common scored-hour intersection used for direct comparisons.
4. Both students must check the applicable university/course AI policy and complete the pending source and contract sign-offs.
5. The data owner, preprocessing partner or professor should confirm whether `Innenstadt` and `Kurpark` are actually area-level series; otherwise their exclusion must remain labeled as a scope choice based on names and missing coordinates.

## Review method

- Read all seven requested Markdown documents and their internal links.
- Rendered and inspected both pages of `Projektbeschreibung.pdf`, then compared every summarized requirement against the source.
- Checked R1-R4 and R7 against conference, journal or publisher records and checked R5-R6 against the issuing institutions' documents.
- Inspected how the delivered preprocessing pipeline creates `war_fehlend` and excludes poor-quality sensors.
- Independently reconstructed the shared-contract availability rules and then added [`verify_design_contract.py`](../../scripts/verify_design_contract.py) as a permanent audit.
- Searched retained documentation for machine-local paths and references to the local historical folder.

## Reproducible data result

The audit passed against:

```text
Historical external snapshot, no longer present in the workspace
SHA-256: 2e97d94f86a264b1cba5d76b2b933c559c6e80224ee770b7a1fa61b6e7edd887
```

It reproduced:

- 9,380 source rows, 28 sensors and 335 timestamps;
- 8,710 rows and 26 retained named-location series after removing two provisionally classified area-level series;
- 2,456 originally missing retained sensor-hours and 745 stored interpolations restored to missing;
- the rejected split's coverage, complete-window and minimum-observation figures; and
- every `k=0`, `k=6` and `k=4` autoencoder reconstruction and distinct scored-hour count in the contract.

This establishes consistency with this exact CSV and algorithm. It does not independently validate the upstream sensor readings, aggregation semantics, the provisional area-level interpretation of `Innenstadt` and `Kurpark`, or whether `war_fehlend` was correctly generated from the original provider data.

## Findings and dispositions

### High - direct model metrics did not guarantee the same evaluated population

The autoencoder yields 1,158 distinct scored test hours under `k=6`; the partner model's score coverage is unknown until its design is frozen and implemented. “Same preprocessing” does not by itself make head-to-head PR-AUC, F1 or ROC-AUC comparable. The evaluation contract therefore requires direct metrics on the finite-score intersection and separate reporting of architecture-specific coverage.

**Disposition:** corrected in `04-evaluation-and-injection.md` and the checklist.

### High - shared documents froze a partner-owned LSTM decision

The earlier contract prescribed 23 context hours followed by a 24th-hour target and published counts derived from that assumption. Alper does not own the LSTM design, so this was not merely an ambiguity: it crossed the stated responsibility boundary and risked presenting an AI-inherited assumption as a team decision.

**Disposition:** all LSTM-specific context, target, score, aggregation and eligibility decisions and derived counts were removed from the shared/autoencoder specifications. The partner supplies a separate model specification; the shared documents constrain only source data, split safety, mask semantics, score-table interoperability, common events and comparison metrics.

### High - the assignment's “overlap coefficient” was treated as temporal IoU without authority

Tatbul et al. establishes the need for range-aware evaluation but does not prescribe temporal IoU. The assignment names an overlap coefficient without a formula, and “overlap coefficient” can also refer to the Szymkiewicz-Simpson measure.

**Disposition:** temporal IoU is now explicitly a project proposal. Ask the professor; if unresolved, report both formulas under unambiguous names.

### High - AI-log wording overstated human verification

The earlier log stated that counts and primary papers had been checked, but it did not name a student or link a verification artifact. An AI-generated sentence that “human verification” occurred is not evidence that it occurred.

**Disposition:** entries now link evidence and remain “pending student sign-off.” Never backfill approval.

### Medium - synthetic-injection support was too broadly worded

Goswami et al. studies injected-anomaly performance as one of multiple imperfect surrogates for unsupervised model selection. It does not prove that this project's anomaly families represent real Bad Nauheim anomalies. The hybrid evaluation is defensible only as a controlled reaction benchmark with untouched-test exploration and limited claims.

**Disposition:** citation scope narrowed in the project scope, evaluation contract and reference notes.

### Medium - exact parameter choices looked more research-grounded than they are

No source establishes that 24 hours, a two-hour patch, `k=6`, 0.98/0.99 quantiles, the selected layer widths, 15 injection seeds or Gaussian noise with standard deviation 0.1 are optimal here. They are reasonable, auditable choices for scope and feasibility, but results and sensitivity checks must carry their justification.

**Disposition:** evidence categories and explicit “project choice” statements added throughout.

### Medium - event provenance was insufficient for multiple copies

`injection_seed` alone cannot distinguish anomaly type, magnitude and duration copies. A single realized magnitude also loses information when clipping changes different hours by different amounts.

**Disposition:** `evaluation_copy_id` and `noise_seed` were added to score provenance; event tables now retain minimum, mean and maximum realized normalized changes and define inclusive intervals.

### Medium - clipping could create a labelled event with little or no perturbation

Downward point and level shifts are clipped at the raw-count zero floor. At a low original count, the realized change can be far below the requested standardized offset; at zero it can be unchanged. Treating such a position as a full requested-severity anomaly would corrupt the label semantics.

**Disposition:** zero-mean-change candidates are invalid, direction is an explicit scenario factor, and results retain requested and realized severity. Capacity must be checked before model results.

### Medium - future availability informed the held-out design

The revised split and completeness policy were chosen after inspecting missingness and window survival in candidate future periods. This is not anomaly-label or score leakage and was necessary to avoid an empty evaluation, but the test period was not blind with respect to its availability structure.

**Disposition:** added as a mandatory limitation; it must not be described as a completely untouched design process.

### Medium - PR-AUC differs with scenario prevalence

Longer injected ranges create a larger positive fraction than point anomalies, changing the random PR-AUC baseline. Raw PR-AUC across such scenarios is not a pure measure of anomaly-type difficulty.

**Disposition:** compare architectures within the same scenario and report each copy's positive fraction and random baseline.

### Medium - PR-AUC's stated priority lacked a direct citation

The decision was methodologically sound for rare positives, but the bibliography did not support the imbalance claim.

**Disposition:** Saito and Rehmsmeier (2015) added as R7. ROC-AUC remains because the assignment explicitly requires it.

### Low - local historical references were not portable

The rejected-alternative text and project-evidence list referred to a local folder that will not exist for the partner, professor or GitHub reader.

**Disposition:** retained documents contain no such dependency, and the local folder is excluded in `.gitignore`. The folder itself was not deleted.

## Document-by-document assessment

### 01 - Project scope and decisions

The assignment summary is accurate. The limitation to a context-bound case study is appropriate. The Transformer and overlap-coefficient ambiguities are now visible instead of silently resolved. The evidence trail is credible after separating reproducible facts, research support and project conventions.

### 02 - Shared data contract

The numerical claims reproduce. The split and dual masks are defensible anti-leakage measures. The revised gap-patch semantics remove autoencoder implementation ambiguity without prescribing the partner model. The exact autoencoder preprocessing and completeness settings remain choices to evaluate, not universal facts.

### 03 - Conv1D autoencoder

The architecture is small and internally coherent, the masked loss handles `NaN` correctly, and the sparse comparison is a controlled ablation. The layer widths, optimizer settings and lambda grid are not justified by literature as optimal; the document now says so. Train-tail reuse for selection, early stopping and calibration remains a small-data compromise that must stay in the limitations.

### 04 - Evaluation and injection

The hybrid design is substantially more honest than injection-only evaluation. Common support, direction, realized severity, event provenance and label semantics are now explicit. Remaining limitations are external validity, unknown native anomalies counted as negatives, contextual score spillover, availability-informed split design and the professor's undefined overlap formula.

### 05 - Responsible AI and evidence

The proposed approach is viable if it records decisions and verification rather than trying to impress with transcript volume. Its evidentiary value comes from links to source checks, code, tests, diffs, failed attempts and named student acceptance. It is not a substitute for understanding or authorship responsibility.

### 06 - Checklist and limitations

The checklist now captures the main stop conditions and unresolved approvals. It should be used as a gate, not merely included in the repository and ignored.

### References

All seven external entries are genuine. R1-R4 and R7 are peer-reviewed research; R5-R6 are official guidance and are labeled accordingly. Each entry now states both the supported claim and the inference it cannot justify.

## Student acceptance record

Complete this section after both students have performed the checks themselves:

- [ ] Alper ran `python scripts/verify_design_contract.py` and matched the recorded CSV hash and counts.
- [ ] Partner inspected the shared data audit and accepted only the shared population, masks, split and interoperability rules.
- [ ] Alper opened and checked every source used for his model and evaluation claims.
- [ ] Partner documented and checked the sources and decisions used for the partner-owned LSTM model.
- [ ] Both students approved the common-support comparison rule.
- [ ] Professor guidance on Transformer and overlap metric was recorded, or the stated fallback was accepted.
- [ ] Applicable AI-disclosure rules were checked and the final disclosure was adapted.

Names, dates and any disagreement should be recorded in the decision log rather than replacing this review with a cleaner retrospective story.
