# 03 - Conv1D autoencoder

[Back to documentation index](../README.md)

## Purpose and ownership

This is the authoritative specification for Alper's model family only. It defines one standard autoencoder and sparse variants as a controlled ablation. It may not override the shared decisions in the [consolidated implementation handoff](../handoffs/2026-07-24-implementation-handoff.md). Shared preprocessing is detailed in the [data contract](02-shared-data-contract.md).

## Training example

One example contains one retained temporal series and 24 consecutive hours:

```text
Input shape:  (batch, 24, 6)
Target shape: (batch, 24, 1)
Stride:       1 hour
```

The six input channels, in canonical order, are:

```text
scaled visitor representation
input_available_mask
local_hour_sin
local_hour_cos
local_weekday_sin
local_weekday_cos
```

`target_observed_mask` is supplied separately as loss/evaluation metadata and is never an autoencoder input. Only the final scaled visitor representation is reconstructed.

Missing or patched target positions must contain a finite placeholder such as zero before elementwise loss is calculated. They are then excluded using `target_observed_mask`. Computing a loss against `NaN` and multiplying by zero afterwards is forbidden because `0 * NaN` remains `NaN`.

## Frozen architecture family

All convolutions use `padding="same"`.

```text
Encoder
    Conv1D(16, kernel_size=3, activation="relu")
    MaxPooling1D(pool_size=2)                 # 24 -> 12
    Conv1D(8, kernel_size=3, activation="relu")
    MaxPooling1D(pool_size=2)                 # 12 -> 6
    Dropout(p)                                # p in {0.0, 0.1}
    Flatten()                                 # 6 x 8 = 48
    Dense(latent_dim, activation="relu")

Decoder
    Dense(6 * 8, activation="relu")
    Reshape((6, 8))
    UpSampling1D(size=2)                      # 6 -> 12
    Conv1D(8, kernel_size=3, activation="relu")
    UpSampling1D(size=2)                      # 12 -> 24
    Conv1D(16, kernel_size=3, activation="relu")
    Conv1D(1, kernel_size=3, activation="linear")
```

Restrictions:

- no encoder-decoder skip connections;
- no batch normalization in the first implementation;
- no additional large dense layers;
- identical architecture for standard and sparse variants.

This design is intentionally small. The dataset does not justify a much larger network, and model complexity would make the student comparison harder to explain.

The exact filter counts, kernel size, bottleneck sizes and dropout values are a constrained project search space, not values established as optimal by an external paper. Their justification is proportionality to the audited sample size, the assignment's requirement for systematic optimization and the pre-results selection protocol below. The seasonal baseline in [04 - Evaluation and injection](04-evaluation-and-injection.md) is needed to test whether this added complexity is useful at all.

## Standard and sparse variants

The ReLU bottleneck is identical in every variant:

```text
total_loss = masked_reconstruction_loss
           + lambda * mean(abs(latent_activation))
```

Candidates:

```text
lambda in {0, 1e-5, 1e-4}
```

- `lambda=0` is the standard autoencoder.
- Positive values are sparse controlled ablations.
- Sparse strength may not be selected using injected test labels.

Log these sparsity diagnostics:

- reconstruction-loss term;
- unweighted and weighted sparsity term;
- mean absolute latent activation;
- fraction of activations below a predeclared near-zero tolerance;
- decoder weight norm, which can expose latent-shrink/decoder-growth compensation.

A model is not described as meaningfully sparse merely because its loss contains a penalty. Its activations must demonstrate the effect.

## Masked reconstruction loss

Huber with `delta=1.0` and MAE are candidates:

```text
masked_loss = sum(target_observed_mask * elementwise_loss(target, reconstruction))
            / max(sum(target_observed_mask), 1)
```

The implementation must fail loudly if an entire batch contains no observed targets. Silently returning a zero loss would hide an invalid training batch.

## Narrow selection protocol

First compare standard models across:

```text
latent_dim          in {8, 16}
reconstruction_loss in {Huber, MAE}
dropout             in {0.0, 0.1}
```

This yields eight configurations. Run each with three model seeds and select using mean masked validation reconstruction loss only. This is a predeclared engineering selection criterion; it is not evidence that the selected configuration is the superior anomaly detector. Do not inspect test scores or injected test labels during selection.

After that:

1. freeze the selected architecture;
2. compare `lambda=0`, `1e-5` and `1e-4`;
3. use matched initial weights and initial batch order for a given seed;
4. report all lambda candidates rather than declaring a sparse winner from the reused validation period or hiding an inconvenient result.

Normal reconstruction loss can favour a model that also reconstructs anomalies well. This limitation is one reason injected results are not used to retroactively choose the architecture.

## Training defaults

```text
Optimizer:               AdamW
Learning rate:           0.001
Weight decay:            1e-5
Batch size:              64
Maximum epochs:          200
Early-stopping patience: 15
Restore best weights:    yes
Model seeds:             [0, 1, 2]
```

Training windows may be shuffled inside the training split after split-safe construction. No row may move between chronological splits.

Training uses only complete 24-hour input windows after permitted short-gap patching (`k=0`). Validation and primary test scoring use `k=6`; `k=4` is the stricter sensitivity analysis. These eligibility rules are independent of the LSTM target or eligibility.

These defaults are starting values to be logged and evaluated, not research findings. If a default changes because training is unstable, record the reason and whether the change occurred before or after test inspection.

## Required outputs

Each run must save:

- `model_config_id`, `run_id`, complete configuration and random seed;
- accepted source/data manifest and environment identity included by `run_id`;
- best epoch and training/validation loss history;
- selected weights or a reproducible model artifact;
- sparsity diagnostics where applicable;
- final score table using the schema in [04 - Evaluation and injection](04-evaluation-and-injection.md);
- enough metadata to reproduce the run from the agreed CSV.

## Acceptance tests

- Model input and output lengths are both 24.
- A batch containing masked targets produces a finite loss.
- Changing only a masked target value does not change the loss.
- An all-masked batch raises an error.
- Standard and sparse variants have identical trainable architecture.
- Matched seeds produce identical initial standard/sparse weights.
- No validation or test value influences scaler fitting.
- Validation influences early stopping, best-weight restoration, reconstruction-loss engineering selection and threshold calibration only through the declared roles.
- Test scores and injected labels do not influence model, lambda, weights or thresholds.

The reuse of the same 48 validation hours for restored-weight selection and threshold calibration creates adaptive optimism. The report must describe this as an accepted dataset-size compromise.
