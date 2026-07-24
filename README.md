# Bad Nauheim anomaly-detection study

This repository is the implementation workspace for the Bad Nauheim
pedestrian-count anomaly-detection case study.

The project compares Alper's standard and sparse Conv1D reconstruction
autoencoders with a separately specified partner-owned LSTM detector under one
shared data and evaluation contract.

## Current status

Implementation may begin, but accepted model training remains gated by:

- the final shared visitor transform/scaling decision;
- bundled partner reapproval of the revised shared evaluation rules;
- the current executable acceptance verifier and required tests; and
- accepted source, data, dependency, and environment manifests.

Start with the
[consolidated implementation handoff](docs/handoffs/2026-07-24-implementation-handoff.md)
and the [documentation index](docs/README.md).

The canonical dataset is
`new-data/data/bad_nauheim_bereinigt.csv`, SHA-256
`af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`.

## Repository boundaries

`new-data/src/` is the partner pipeline snapshot used as audit input. It is not
automatically compliant with the current contract.

The local `diğer/` predecessor and `CLAUDE.md` contain stale information and are
excluded from this repository.
