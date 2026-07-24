# Pre-implementation environment audit

**Captured:** 2026-07-24

**Purpose:** record the environment used to run the partner preprocessing/windowing snapshot before accepted model training.

## Interpreter and packages observed

```text
Python       3.14.2
NumPy        2.4.1
pandas       3.0.0
scikit-learn 1.8.0
```

Interpreter used:

```text
C:\Users\alper\AppData\Local\Python\bin\python.exe
```

The command `python windowing.py`, executed with `new-data/src` as the working directory, successfully loaded the canonical snapshot and produced the dry-run counts recorded in the consolidated handoff.

## Scope and limitations

This is a preliminary audit, not the accepted experiment environment:

- no dependency lockfile currently exists;
- neural-network framework versions were not needed or captured for the preprocessing dry run;
- the current script uses working-directory-relative paths;
- an accepted run must save a fresh interpreter/package manifest, model-framework versions, source/data hashes and run configuration.

When the implementation dependencies stabilize, create a reproducible lock or pinned requirements file. Do not infer the accepted model environment from this preliminary record.
