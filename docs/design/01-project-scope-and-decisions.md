# 01 - Project scope and decisions

[Back to documentation index](../README.md)

## Purpose

This file defines what the project is trying to answer and why its major design choices are reasonable for a two-person student project. Implementation details belong in the linked specialist documents.

## Research question

Can two different deep-learning principles identify unusual behaviour in the Bad Nauheim pedestrian-count data, and how do their results differ under the same evaluation rules?

The compared model families are:

- **Conv1D reconstruction:** reconstruct a 24-hour window and use reconstruction error as the anomaly score.
- **Partner-owned LSTM detector:** the partner defines its representation, context, target, loss and anomaly score in a separate specification. This document does not freeze those choices.

The project is a context-bound case study covering approximately two weeks. It cannot establish that either architecture is universally superior.

## Team boundary

- Alper owns the standard and sparse Conv1D autoencoders.
- His project partner owns the LSTM model and every decision about its formulation.
- Both students must jointly approve the material shared items summarized in the [partner decision summary](00-partner-decision-summary.md). The earlier shared structure was approved according to Alper; the finalization-review clarifications remain pending one bundled partner reapproval. The [consolidated implementation handoff](../handoffs/2026-07-24-implementation-handoff.md) is the normative record. The detailed data and evaluation documents implement it and cannot introduce a new material obligation without joint reapproval.

This division permits independent model development without allowing preprocessing or metric differences to make the comparison unfair.

## Meaning of the comparison

The autoencoder is retrospective because a tested value is part of the reconstructed window and overlapping windows can include later context. The partner must document what information the LSTM detector receives and whether it is causal or retrospective.

Identical source data, anomaly events and metric definitions control the experiment, but they do not automatically make the architectures' information sets or score coverage identical. The final comparison must describe those differences after the partner-owned specification is complete.

## Assignment fit

The assignment requires:

- comparison of at least two deep-learning architectures;
- justified preprocessing, representation and architecture choices;
- systematic optimization and training-stability measures;
- reproducible confusion matrices, precision, recall, F1, ROC-AUC and an anomaly-overlap coefficient;
- comparison of accuracy, noise robustness and generalization;
- interpretable results and reproducible experiments.

The LSTM and autoencoder satisfy the explicit two-architecture minimum. However, the brief lists a Transformer as "expected for best performance." Before implementation is frozen, the team should ask the professor whether that wording is an aspiration or an additional expectation.

The brief also requires a coefficient for anomaly overlap without naming its formula. The team must confirm whether the professor expects temporal IoU, the Szymkiewicz-Simpson overlap coefficient or another range metric. Until then, temporal IoU is a clearly defined project proposal, not an interpretation attributed to the assignment or to [R3](references.md#r3).

## What counts as evidence

The design deliberately distinguishes assignment requirements, reproducible facts from this dataset, external research and predeclared project choices. The [references and evidence file](references.md#evidence-categories) defines these categories. Exact parameters are not made scientific merely by attaching a citation: they remain hypotheses or conventions to test unless a source and the local data support a stronger claim.

## Evidence-to-decision trail

| Question | Evidence | Decision |
|---|---|---|
| Which source is authoritative? | Team agreement plus the delivered preprocessing output | Use the agreed CSV; Parquet may only be a disposable cache. This is a provenance decision. |
| Which periods are feasible for 24-hour windows? | Availability and window-survival audits performed before model training | Use training through July 3, validation on July 4–5 and one continuous July 6–13 test with two reporting conditions. This is an availability-informed project choice. |
| Can interpolation become ground truth? | `war_fehlend` is set before interpolation in the delivered preprocessing code | No; use separate input-availability and target-observation masks. |
| Which clock describes pedestrian behaviour? | The data location and domain reasoning; [R4](references.md#r4) only supports the relevance of diurnal and weekday context | Split in UTC but calculate calendar features in `Europe/Berlin`. |
| How can label-dependent metrics be calculated without verified labels? | Assignment requirements; [R1](references.md#r1) studies injection performance as one imperfect label-free surrogate | Use controlled synthetic injection as one evaluation component, with explicitly limited claims. |
| Can injected results prove real-world accuracy? | Construct-validity limits; [R1](references.md#r1) does not establish that equivalence | No; combine injection with untouched-test analysis and qualify claims. |
| How should anomaly ranges be scored? | The assignment requires an unspecified overlap coefficient; [R3](references.md#r3) supports range-aware evaluation generally | Propose temporal IoU, report point metrics separately and confirm the required formula with the professor. |
| Why use this exact 24-hour, `k`, threshold and injection configuration? | Data feasibility, team scope and pre-results sensitivity plans | Treat the values as predeclared project choices, not literature-derived optima. Reconstruction-loss selection is an engineering criterion, not evidence of anomaly-detection superiority. |

## Deliberate first-version exclusions

- Transformer, subject to professor confirmation;
- Isolation Forest unless time remains;
- 168-hour windows;
- `avgDuration` as an autoencoder feature;
- area-aggregate modelling;
- phase-shift or learned anomaly injection;
- production serving and monitoring infrastructure.

These are scope decisions, not claims that the excluded methods have no scientific value.

## Rejected alternatives

| Alternative | Why it was rejected |
|---|---|
| Import a complete earlier experimental framework | Too much code and process for the revised division of work; it also contains assumptions superseded by this contract. |
| Build independent preprocessing for each model | Model effects would be mixed with preprocessing effects. |
| Reset a separate test split at Jul 8 | It destroys usable context at the reporting boundary; July 8 instead separates two reporting conditions within one continuous test timeline. |
| Treat existing interpolations as observations | Input context would incorrectly become target ground truth. |
| Calculate calendar features in UTC | Local pedestrian schedules are shifted by two hours during this dataset. |
| Maintain a second authoritative Parquet dataset | It creates provenance ambiguity without a benefit at this scale. |
| Avoid injection entirely | The assignment's label-dependent metrics could not be calculated objectively. |
| Use injection as the only evidence | Synthetic events do not validate accuracy on all real anomalies. |
| Inject only very large spikes | The benchmark would become trivial and favour amplitude detectors. |
| Tune thresholds on injected test labels | That is test leakage and oracle thresholding. |

## Documents that implement this scope

- [Shared data contract](02-shared-data-contract.md)
- [Conv1D autoencoder specification](03-conv1d-autoencoder.md)
- [Evaluation and injection protocol](04-evaluation-and-injection.md)
- [Responsible AI and evidence process](05-responsible-ai-and-evidence.md)
