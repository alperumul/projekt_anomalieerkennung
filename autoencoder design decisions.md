# Historical design decisions — superseded

> **Do not implement from this file.** Its 26-series population, excluded area
> labels, date split, preprocessing recommendation, and other “locked” decisions
> were replaced by the 2026-07-24 contract. Use
> [`docs/handoffs/2026-07-24-implementation-handoff.md`](docs/handoffs/2026-07-24-implementation-handoff.md)
> and [`docs/design/`](docs/design). This note remains only as historical evidence.

• Data contract #1 is now locked. The remaining nine decisions should be finalized in this order because each one depends on the previous decisions.

  ## 1. Data contract — locked

  - Source: bad_nauheim_bereinigt.csv
  - Remove Innenstadt and Kurpark
  - Final population: 26 point sensors
  - Primary variable: visitors
  - Restore every war_fehlend=True position to missing
  - Observation mask: ~war_fehlend
  - Derive calendar features using Europe/Berlin local time

  ## 2. Chronological split

  Decide the exact training, validation and test intervals.

  Recommended:

  Training:   2025-06-30 01:00 – 2025-07-07 23:00 UTC
  Validation: 2025-07-08 00:00 – 2025-07-10 23:00 UTC
  Test:       2025-07-11 00:00 – 2025-07-13 23:00 UTC

  No window may cross a split boundary.

  ## 3. Numerical preprocessing

  Decide exactly how visitors enters the network.

  Recommended:

  1. Restore original missing positions.
  2. Apply log1p.
  3. Calculate mean and standard deviation separately for each sensor using observed training values only.
  4. Standardize validation and test with those training statistics.
  5. Fill missing normalized inputs with 0.
  6. Preserve the observation mask as a separate channel.

  No preprocessing statistics may be learned from validation or test.

  ## 4. Window and input representation

  Decide what one training example contains.

  Recommended:

  One sensor
  24 consecutive hours
  Stride = 1 hour

  Input channels:

  normalized visitors
  observation mask
  hour_sin
  hour_cos
  is_weekend

  Input shape:

  (batch, 24, 5)

  Reconstruction target:

  (batch, 24, 1)

  Only the visitor sequence is reconstructed.

  ## 5. Conv1D architecture

  Freeze the encoder, bottleneck and decoder design.

  Recommended:

  Encoder:
  Conv1D(16, kernel=3)
  MaxPooling1D(2)
  Conv1D(8, kernel=3)
  MaxPooling1D(2)
  Flatten
  Dense bottleneck

  Decoder:
  Dense + reshape
  UpSampling1D(2)
  Conv1D(8, kernel=3)
  UpSampling1D(2)
  Conv1D(16, kernel=3)
  Conv1D(1, kernel=3, linear output)

  Restrictions:

  - No encoder-decoder skip connections.
  - No large dense layers.
  - No batch normalization initially.
  - Optional dropout limited to approximately 0.1.

  ## 6. Standard versus sparse variant

  Define the difference between the two autoencoders.

  Standard:

  λ = 0

  Sparse:

  loss = reconstruction loss + λ × mean(abs(latent activations))

  Candidate sparsity values:

  λ ∈ {10⁻⁵, 10⁻⁴}

  The architecture, data, initialization protocol and training settings must otherwise be identical. Sparsity is a controlled ablation, not an unrelated model.

  ## 7. Loss and training protocol

  Recommended reconstruction loss:

  masked Huber loss

  Only originally observed target positions contribute:

  masked_loss =
      sum(observation_mask × Huber(target, reconstruction))
      / sum(observation_mask)

  Recommended training defaults:

  Optimizer: Adam
  Learning rate: 0.001
  Batch size: 32 or 64
  Maximum epochs: 200
  Early-stopping patience: 15
  Restore best validation weights: yes
  Weight decay: approximately 10⁻⁵
  Random seeds: 3

  Training windows may be shuffled after the chronological split.

  ## 8. Anomaly score and overlap aggregation

  For each eligible reconstructed value:

  raw anomaly score =
      abs(observed scaled value − reconstructed scaled value)

  Because each sensor-hour can appear in multiple overlapping windows:

  final sensor-hour score =
      mean of all reconstruction errors for that sensor-hour

  Record the number of contributing windows, particularly near split boundaries.

  Originally missing values receive no evaluation score.

  ## 9. Threshold policy

  Recommended primary threshold:

  1. Calculate aggregated validation scores.
  2. Pool standardized scores across the 26 sensors.
  3. Select a predeclared validation quantile, such as the 99th percentile.
  4. Apply the threshold unchanged to the test set.

  Do not tune the threshold against test labels.

  Because validation data are only assumed normal, call this a validation exceedance threshold, not a verified false-positive threshold.

  ## 10. Hyperparameter selection and final reporting

  Use a narrow search:

  Latent dimension: 8 or 16
  Reconstruction loss: Huber or MAE
  Sparsity λ: 0, 10⁻⁵ or 10⁻⁴
  Optional dropout: 0 or 0.1

  Recommended order:

  1. Select latent dimension and reconstruction loss for the standard model.
  2. Freeze the selected architecture.
  3. Compare λ=0, 10⁻⁵ and 10⁻⁴.
  4. Retrain the selected standard and sparse variants with three seeds.
  5. Compare them with the LSTM using identical test anomalies and metrics.

  The final reported set becomes:

  LSTM forecaster
  Standard Conv1D autoencoder
  Sparse Conv1D autoencoder

  The next decision to lock should be #2: the exact chronological split, because preprocessing and window counts depend on it.
