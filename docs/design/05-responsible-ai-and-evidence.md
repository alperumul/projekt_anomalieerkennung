# 05 - Responsible AI and evidence

[Back to documentation index](../README.md)

## Purpose

This document explains how generative AI assists the project without becoming an unverified source, hidden author or substitute for student understanding.

The goal is not to claim that AI was absent. The goal is to demonstrate that it was used transparently within a human-controlled engineering and research process.

## Permitted roles

Generative AI is used as:

- a structured brainstorming partner;
- a literature-discovery and synthesis assistant;
- an adversarial reviewer of proposed methodology;
- a code and test scaffolding assistant;
- a documentation and language assistant.

It is not treated as:

- an author or accountable decision-maker;
- an unquestioned source of facts or citations;
- a replacement for running and understanding the code;
- authority to alter partner agreements or assignment requirements;
- evidence that a result is scientifically valid.

## Human-controlled workflow

```text
Student question or constraint
    -> AI proposes alternatives and failure modes
    -> students inspect the data and reproduce numerical claims
    -> students check relevant primary sources
    -> students select and explain the decision
    -> implementation is tested against explicit invariants
    -> responsible student reviews and can explain the result
```

Human control does not require per-step permission for routine agent work. Within
an approved task and the frozen contract, an agent may autonomously inspect,
implement, test, document and correct failures end to end. Human approval is
required when a result would change a shared methodological decision, fill an
open partner- or professor-owned choice, or become a submitted scientific claim.
This separates efficient agentic execution from accountability for research
decisions.

This follows the accountability, transparency and responsibility principles described by the European Research Area ([R5](references.md#r5)) and the DFG's requirement that researchers disclose generative-model use while retaining responsibility for good scientific practice ([R6](references.md#r6)).

These sources are general guidance. They do not certify this workflow or override the professor's and university's rules. Before submission, ask which AI uses, tool details and prompt/output records the course specifically requires.

## Examples from this project

These examples show AI contributing to a process rather than delivering an unquestioned final answer:

### Split correction

1. An initial chronological split was proposed.
2. Critical review questioned whether its 24-hour windows survived restored missingness.
3. The version-controlled audit reproduced the counts from the agreed CSV.
4. The validation and test slices were shown to contain no complete 24-hour windows.
5. The revised split was proposed before model training; student approval remains recorded separately.

### Mask correction

1. Historical windowing code defined validity from patched values.
2. Review identified that this treated interpolation like measurement ground truth.
3. The revised contract distinguishes context availability from original observation.
4. The shared contract now contains two masks with separate tests.

### Local-time correction

1. Historical calendar features were calculated directly from UTC timestamps.
2. Domain reasoning identified a mismatch with local pedestrian schedules.
3. A concrete UTC-to-Berlin date-boundary test was specified.
4. UTC remains the split clock, while `Europe/Berlin` defines behavioural features.

### Evaluation correction

1. Stable unlabelled data made conventional F1 evaluation impossible.
2. AI-assisted research identified controlled injection as one possible surrogate.
3. Primary evaluation research was checked in this AI-assisted review and linked for student verification.
4. The revised design proposes hybrid evaluation with limited claims rather than injection-only validation.

These decision chains are stronger evidence of responsible use than a claim that AI "helped with the project."

## Verification rules

- Data-derived numbers come from executable checks, not AI recollection.
- Academic claims used in the report are checked in primary sources.
- Internal research summaries help locate sources but are not final citation authorities.
- AI-generated code must be readable and explainable by its responsible student.
- An AI statement that a claim was “verified” is not human verification; a named student must inspect the cited source or run the linked check and record sign-off.
- Test labels and metrics may not influence model or threshold selection.
- Failed configurations and negative results remain in the experiment record.
- The students remain responsible for every submitted statement, result and line of code.

## Minimal evidence package

To make the process auditable without creating bureaucracy, retain:

- this design documentation and its change history;
- scripts or tests reproducing important dataset counts;
- experiment configurations and seeds;
- a short log of material AI-assisted decisions;
- selected prompt/output excerpts or session exports for decisions where the reasoning cannot be reconstructed from the resulting artifact alone;
- primary papers actually cited in the report;
- records of deviations from the pre-results design.

Complete chat transcripts are not automatically useful evidence. The important record is which substantive suggestion was accepted, how it was checked and what changed.

The record should include the AI tool, access date, task, material output, linked verification artifact, decision owner and status. Protect confidential, personal or partner-owned material; do not publish raw chats merely for completeness.

## What this package can demonstrate

This package can credibly show a transparent process, reproducible checks, critical review, rejected suggestions and student control. It cannot by itself prove that a student understands the work, that a cited claim is correct or that AI-generated code is original and reliable. Those stronger claims require the executable artifacts, source reading, version history, experiment outputs and the student's ability to explain and defend the decisions.

## AI-use and decision log

The entries below are a draft record of material assistance. “Pending student sign-off” is intentional: this review can provide evidence and executable checks, but it cannot honestly certify that either student has personally completed them.

| Date | Tool | Question or task | AI contribution | Verification evidence | Human owner/status | Decision or artifact |
|---|---|---|---|---|---|---|
| 2026-07-22 | Codex | Is the initial split usable? | Challenged the split and proposed survival checks. | The historical [`verify_design_contract.py`](../../scripts/verify_design_contract.py) reproduces the earlier counts. | Superseded by the jointly approved 2026-07-24 structure | Proposed the earlier train-core/train-tail/test design. |
| 2026-07-22 | Codex | Can patched gaps be targets? | Identified that one validity flag could conflate input context with measurement ground truth. | Delivered preprocessing code sets `war_fehlend` before interpolation; contract tests are specified. | Shared rule approved according to Alper; implementation tests pending | Separate input and target masks. |
| 2026-07-22 | Codex | How can unlabelled anomalies be evaluated? | Compared evaluation strategies and criticized injection-only claims. | Assignment plus [R1](references.md#r1), [R2](references.md#r2), [R3](references.md#r3) and [R7](references.md#r7) were checked in this AI-assisted review. | Shared rule approved according to Alper; student source review still required | Hybrid evaluation with limited claims. |
| 2026-07-22 | Codex | Are the design claims adequately grounded? | Audited the documents independently, narrowed overclaims and found common-support, model-ownership, clipped-injection and test-availability issues. | [Design evidence review](../reviews/2026-07-22-design-evidence-review.md) and historical verifier. | Superseded where the 2026-07-24 contract differs | Revised shared interface; LSTM decisions returned to the partner. |
| 2026-07-24 | Codex | Is the implementation handoff authoritative and implementation-ready? | Separated documentation defects from methodological blockers, audited `new-data`, and consolidated authority, patching, validation, score-schema and evaluation rules. | [Consolidated implementation handoff](../handoffs/2026-07-24-implementation-handoff.md), canonical hash and successful partner-pipeline dry run. | Alper confirmed partner approval of the shared structure; preprocessing decision pending | Current shared contract and execution gates. |
| 2026-07-24 | Codex finalization review | Can the consolidated handoff be finalized without ambiguous joins or evaluation populations? | Identified missing run/configuration identity, derived-copy support bias, undefined missingness buckets, an under-specified mandatory baseline and additional qualified implementation conflicts. Reproduced contract feasibility counts and the zero-training-window series. | Revised [consolidated handoff](../handoffs/2026-07-24-implementation-handoff.md), [shared data contract](02-shared-data-contract.md), [evaluation protocol](04-evaluation-and-injection.md) and [checklist](06-checklist-and-limitations.md). | Alper authorized incorporation on 2026-07-24; bundled partner reapproval pending | Immutable run keys, clean-frozen support, exact metric/baseline conventions and explicit acceptance counts. |

Add entries only for assistance that materially changes a scientific or engineering decision. Routine completion and spelling corrections do not need separate entries.

When a student completes a pending item, replace the status with the student's name, date and concrete action, for example “Alper, 2026-07-23 - ran script; matched SHA-256 and counts” or “Partner, 2026-07-23 - read R2 and confirmed the point-adjustment claim.” Do not backfill approval that did not occur.

## Suggested disclosure statement

> Generative AI tools were used to assist literature discovery, compare design alternatives, review methodology, scaffold code and tests, and improve documentation. The project authors verified data-derived claims through executable analyses, checked report citations against primary sources, made all final methodological decisions, reviewed the generated code, and remain fully responsible for the submitted work. AI-generated text and code were not treated as scientific evidence or accepted without human review.

Use this statement only if the described verification has actually been completed. Adapt it to the professor's and university's disclosure policy.

## Preparing to explain the work

Each student should be able to answer:

1. Which part did I personally implement and verify?
2. Which AI suggestion did we reject, and why?
3. Which data-derived fact changed our design?
4. Which paper supports a methodological choice, and what does it not prove?
5. How would I detect leakage or an invalid mask in our implementation?
6. What can our final metrics legitimately claim?

Being able to answer these questions is better evidence of ownership than trying to make an AI-assisted project appear AI-free.
