# Historical design note — superseded

> **Do not use this file as current implementation authority.** It records an
> earlier autoencoder discussion and contains superseded population and design
> assumptions. The current authority is
> [`docs/handoffs/2026-07-24-implementation-handoff.md`](docs/handoffs/2026-07-24-implementation-handoff.md),
> followed by [`docs/design/`](docs/design). Retain this file only as decision
> history.

 ## Verdict on the lean design

  The proposed design is appropriate:

  > LSTM forecasting versus a small retrospective Conv1D autoencoder, evaluated through the same anomaly-injection and scoring pipeline.

  The difference between the models is clear:

  - The LSTM learns to predict the next visitor count from past observations.
  - The autoencoder learns to compress and reconstruct normal 24-hour patterns.
  - The LSTM uses prediction error.
  - The autoencoder uses reconstruction error.
  - The LSTM is causal; the autoencoder is retrospective.

  That is a legitimate comparison. You only need to explain that the two models use different anomaly-detection principles.

  ## Why a Conv1D autoencoder fits this dataset

  A Conv1D autoencoder is not guaranteed to be the best-performing model, but it offers the best balance of suitability, simplicity and defensibility here.

  ### 1. It understands local temporal structure

  Pedestrian traffic usually changes gradually:

  night → morning increase → daytime activity → evening decrease

  A one-dimensional convolution looks at neighbouring hours and learns local patterns such as:

  - morning increases;
  - evening decreases;
  - short peaks;
  - quiet nighttime periods;
  - unusual transitions between consecutive hours.

  A dense autoencoder sees 24 unrelated numbers unless it learns these relationships from scratch. Conv1D builds temporal locality directly into the architecture.

  ### 2. It shares parameters across time

  The same convolutional filter is applied throughout the 24-hour window. A filter that recognizes a sudden increase can recognize it at multiple positions.

  This requires fewer parameters than giving every hour a separate set of connections, which is important because the dataset contains only 335 hours per sensor.

  ### 3. It is smaller and easier to train than recurrent alternatives

  An LSTM or GRU autoencoder would also model sequences, but it would:

  - contain more parameters;
  - take longer to train;
  - be more sensitive to optimization choices;
  - overlap methodologically with your partner’s LSTM.

  Conv1D gives you a clearer architectural contrast while remaining a time-series model.

  ### 4. It produces an error for every hour

  The decoder reconstructs the complete 24-hour visitor sequence. You can therefore calculate:

  error(sensor, hour) = |observed visitor count - reconstructed visitor count|

  For timestamps appearing in multiple overlapping windows, average their reconstruction errors to produce one final score per sensor-hour.

  ### 5. It is explainable

  You can show:

  - original and reconstructed visitor curves;
  - reconstruction errors over time;
  - the anomaly threshold;
  - highlighted anomalous hours;
  - examples where the autoencoder succeeds or fails.

  That directly supports the brief’s requirement to avoid a pure black-box presentation.

  ## Recommended concrete architecture

  Keep it small. For example:

  Input: 24 hours × input channels

  Encoder:
  Conv1D: 16 filters, kernel size 3
  MaxPool: 24 → 12
  Conv1D: 8 filters, kernel size 3
  MaxPool: 12 → 6
  Dense bottleneck: 8 or 16 units

  Decoder:
  Dense + reshape
  Upsampling: 6 → 12
  Conv1D: 8 filters
  Upsampling: 12 → 24
  Conv1D: 16 filters
  Output Conv1D: 1 reconstructed visitor value per hour

  Use no skip connections. Skip connections could allow the network to copy the input too easily, reducing reconstruction error even for anomalies.

  The input channels can be:

  scaled visitor value
  original-observation mask
  hour_sin
  hour_cos

  Calendar features are known context, but the decoder should reconstruct only the visitor channel—not the masks or calendar features.

  I would leave sensor embeddings out of the first implementation. Per-sensor scaling already removes major level differences. Add a small embedding later only if the pooled model performs noticeably
  differently across sensors.

  ## A slightly better refinement: denoising Conv1D autoencoder

  The most useful alternative is not a completely different architecture. It is a light denoising version of the same Conv1D autoencoder.

  During training, slightly corrupt some observed inputs:

  - add small Gaussian noise to normalized visitor values; or
  - temporarily hide approximately 5% of observed input positions.

  The target remains the original uncorrupted visitor window.

  This discourages the network from learning a simple identity function and makes it learn the underlying daily shape. It may also improve the required noise robustness.

  Keep this modest. Start with the normal Conv1D autoencoder. If it reconstructs injected anomalies too accurately, enable light denoising as a regularization option—not as a third model.

  ## Realistic alternatives

   Alternative                Advantages                             Why I would not choose it first
  ━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Dense autoencoder          Easiest implementation; very small     Does not encode temporal locality
  ─────────────────────────  ─────────────────────────────────────  ──────────────────────────────────────────────────────────────
   LSTM/GRU autoencoder       Strong sequence modelling              Too similar to partner’s LSTM and more complex
  ─────────────────────────  ─────────────────────────────────────  ──────────────────────────────────────────────────────────────
   TCN autoencoder            Larger temporal receptive field        Dilations/residual blocks are unnecessary for only 24 hours
  ─────────────────────────  ─────────────────────────────────────  ──────────────────────────────────────────────────────────────
   Variational autoencoder    Probabilistic latent representation    More difficult loss tuning and often blurrier reconstruction
  ─────────────────────────  ─────────────────────────────────────  ──────────────────────────────────────────────────────────────
   Transformer autoencoder    Flexible long-range attention          Too data-hungry and unnecessary for 24-hour sequences

  A dense autoencoder is the strongest simple alternative. It could potentially perform equally well because the window contains only 24 values. However, the Conv1D model has the better theoretical
  justification for hourly time-series data.

  ## Keep the experiment manageable

  Use one primary configuration:

  - 26 point sensors;
  - 24-hour windows;
  - visitors only;
  - train-only per-sensor scaling;
  - masked MAE or Huber loss;
  - latent size 8 or 16;
  - early stopping;
  - one score per sensor-hour.

  Perform a narrow search of perhaps 6-8 configurations—not dozens. Compare latent size, loss and one or two filter sizes.

  Use exactly the same:

  - source table and sensor list;
  - chronological train/validation/test intervals;
  - anomaly timestamps and anomaly magnitudes;
  - original-observation masks;
  - evaluation code;
  - test population.

  One important leakage detail: interpolation and scaling must not use information across the chronological split boundaries.

  ## Final recommendation

  Use a small retrospective Conv1D reconstruction autoencoder. If needed, improve it with light denoising regularization without turning it into another model.

  It is the best practical choice because it:

  - satisfies the autoencoder requirement;
  - contrasts clearly with LSTM forecasting;
  - suits short hourly windows;
  - has relatively few parameters;
  - supports understandable reconstruction plots;
  - is realistic for a student project.

  Do not claim beforehand that it is objectively the best-performing architecture. Say that it is the most appropriate candidate given the limited dataset, and let the quantitative comparison determine whether
  it actually outperforms the LSTM.


› Can you expand on the alternative auto encoder models A critical aspect of this project is to be able to defend our selections so if I don't understand our other options I won't be able to defend this


• The strongest way to defend the Conv1D autoencoder is not to claim that it is universally superior. The defensible claim is:

  > Given 24-hour windows, limited training history, one primary measurement variable, and an existing LSTM comparison model, a small Conv1D autoencoder provides the most appropriate balance between temporal
  > modelling, model capacity, methodological distinction and implementation complexity.

  Here are the realistic alternatives and why you would or would not select them.

  ## 1. Dense feed-forward autoencoder

  A dense autoencoder flattens the 24-hour window:

  [hour 1, hour 2, ..., hour 24]
                ↓
          Dense encoder
                ↓
           latent vector
                ↓
          Dense decoder
                ↓
  reconstructed 24-hour window

  An example might be:

  24 → 16 → 8 → 16 → 24

  If masks and calendar features are included, the flattened input becomes larger.

  Advantages:

  - Simplest autoencoder to implement and explain.
  - Very fast to train.
  - Can have extremely few parameters.
  - A reasonable option for such short windows.
  - Provides a clear reconstruction error.

  Disadvantages:

  - It has no built-in understanding that hour 10 is adjacent to hours 9 and 11.
  - Every input position has separate weights.
  - Patterns learned at one position do not automatically transfer to another position.
  - Sliding windows can begin at different hours, making position-specific learning less natural.
  - It may learn a general compressed lookup table rather than reusable temporal patterns.

  Important nuance: a compact dense autoencoder may actually have fewer parameters than a Conv1D model. Therefore, you should not defend Conv1D by simply saying “it always has fewer parameters.” Its real
  advantage is its temporal inductive bias and weight sharing.

  Verdict: the strongest simple alternative. If implementation time were the overriding concern, a dense autoencoder would be acceptable. Conv1D is better justified for sliding time-series windows.

  ## 2. Standard Conv1D autoencoder

  A Conv1D model moves small filters across the time axis:

  ... 08:00, 09:00, 10:00 ...
             └───────┘
          local filter

  A kernel of size 3 examines three neighbouring hours at a time. It can learn features such as:

  - sudden increases;
  - sudden drops;
  - gradual trends;
  - short peaks;
  - flatline behaviour;
  - transitions between active and quiet periods.

  The same filter is applied throughout the window. A learned “sudden increase” detector can therefore operate at several positions.

  Advantages:

  - Directly models local temporal relationships.
  - Shares learned filters across time.
  - Well suited to sliding windows.
  - Trains faster and more easily than recurrent models.
  - Produces a reconstruction for each hour.
  - Clearly different from the partner’s recurrent LSTM.
  - Easier to visualize and explain than Transformer attention.

  Disadvantages:

  - A small convolution mainly captures local patterns.
  - It may miss relationships between distant parts of the day.
  - If it has too much capacity or skip connections, it may copy anomalies.
  - Convolution alone does not know that 08:00 and 20:00 have different meanings.

  The pooling layers and bottleneck allow the model to summarize the complete 24-hour window, while hour_sin and hour_cos provide absolute time information.

  Verdict: the recommended primary architecture.

  ## 3. Denoising autoencoder

  “Denoising” is not a separate temporal architecture. A dense, Conv1D or LSTM autoencoder can all be trained as denoising autoencoders.

  During training, the input is slightly corrupted:

  original window → add small noise or hide a few values → autoencoder
                                                         ↓
                                               reconstruct original

  For example:

  - Add weak Gaussian noise to observed normalized values.
  - Temporarily hide 5% of observed input values.
  - Keep the original uncorrupted values as reconstruction targets.

  Advantages:

  - Reduces the danger of learning an identity function.
  - Encourages learning the underlying normal shape.
  - Can improve robustness to measurement noise.
  - Fits the project’s noise-robustness requirement.
  - Adds little architectural complexity.

  Disadvantages:

  - Noise magnitude becomes another hyperparameter.
  - Excessive corruption can destroy real temporal information.
  - Artificial corruption must be kept separate from genuine missingness.
  - The model might become insensitive to small real anomalies if trained with excessive noise.

  You would need three concepts:

  original observation mask
  natural missingness mask
  artificial training-corruption mask

  At inference, you normally provide the uncorrupted available input and calculate reconstruction error.

  Verdict: a valuable refinement of the Conv1D autoencoder. Start with an ordinary Conv1D model and add mild denoising only as a regularization experiment.

  ## 4. Sparse autoencoder

  A sparse autoencoder adds a penalty that encourages only a small number of latent units to be active.

  The idea is that normal pedestrian behaviour might be represented through a few patterns:

  night pattern
  morning pattern
  daytime pattern
  weekend pattern

  Advantages:

  - Can create a more structured latent representation.
  - Reduces the likelihood of unrestricted copying.
  - Potentially easier to interpret.
  - May help when normal behaviour consists of a small number of modes.

  Disadvantages:

  - Requires choosing a sparsity penalty.
  - Too much sparsity causes underfitting.
  - Sparse activations do not necessarily correspond to meaningful patterns.
  - Adds optimization complexity without addressing temporal structure itself.

  A sparse dense autoencoder still does not understand adjacency. A sparse Conv1D autoencoder is possible, but it introduces another experimental dimension.

  Verdict: theoretically reasonable but unnecessary for this student project. A compact bottleneck and regularization already provide much of the desired capacity control.

  ## 5. LSTM or GRU autoencoder

  An LSTM autoencoder reads the window sequentially, compresses it into a hidden representation, and then reconstructs the sequence.

  Advantages:

  - Naturally designed for ordered sequences.
  - Can model long-range dependencies.
  - Can remember earlier values while processing later ones.
  - Widely used for time-series anomaly detection.

  Disadvantages:

  - More difficult and slower to train.
  - Usually has more optimization sensitivity.
  - Unnecessary recurrence for a sequence of only 24 hours.
  - Methodologically close to your partner’s LSTM.
  - Makes the comparison look more like “LSTM forecasting versus another LSTM.”
  - Harder to explain exactly what temporal patterns were learned.

  It would still be a valid reconstruction-based comparison because the objective differs, but the architectural diversity would be weaker.

  Verdict: a good general anomaly-detection model, but not the best project choice because the partner already uses LSTM and the sequences are short.

  ## 6. TCN autoencoder

  A Temporal Convolutional Network uses dilated convolutions:

  ordinary convolution: neighbouring hours
  dilation 2:           every second hour
  dilation 4:           every fourth hour

  This gives a large receptive field without recurrence.

  Advantages:

  - Captures longer temporal relationships.
  - Trains in parallel.
  - Often more stable than recurrent networks.
  - Could connect morning and evening patterns efficiently.

  Disadvantages:

  - More architectural decisions: dilation factors, residual blocks and receptive field.
  - Residual or skip connections can make reconstruction too easy.
  - A sophisticated TCN is unnecessary for a 24-hour sequence.
  - Harder to justify its added complexity with only two weeks of data.

  A simple Conv1D autoencoder with two convolution/pooling stages already sees progressively larger parts of the 24-hour window. It provides some of the TCN benefits without the additional machinery.

  Verdict: potentially strong, but excessive for the current sequence length and project scope.

  ## 7. Variational autoencoder

  A Variational Autoencoder, or VAE, learns a probability distribution in its latent space rather than one deterministic latent vector.

  Instead of encoding a window as:

  z = [0.2, -0.7, 1.1]

  it learns means and variances and samples from them.

  Advantages:

  - Produces a structured probabilistic latent space.
  - Can potentially identify observations in low-probability regions.
  - Offers more than raw reconstruction error.
  - Has a strong theoretical foundation.

  Disadvantages:

  - Requires balancing reconstruction loss against KL-divergence.
  - Can suffer from posterior collapse.
  - Reconstructions are often smoother and less precise.
  - A very flexible probability distribution can sometimes represent anomalies too well.
  - More difficult to explain and tune.
  - Limited data make learned uncertainty less trustworthy.

  Verdict: academically interesting, but its additional probability machinery is not justified by this dataset. A deterministic reconstruction error is easier to defend and evaluate.

  ## 8. Transformer autoencoder

  A Transformer uses attention to relate every hour to every other hour.

  Advantages:

  - Can model global relationships directly.
  - Does not need recurrence.
  - Flexible and powerful on large datasets.
  - Can potentially learn relationships between distant time positions.

  Disadvantages:

  - The window contains only 24 positions, so long-range attention offers limited benefit.
  - The dataset has only 335 timestamps per sensor.
  - Attention models have additional parameters and design choices.
  - Greater risk of overfitting.
  - Harder to interpret reliably with limited data.
  - “Attention weights” are not automatically explanations.
  - Considerably more work for uncertain improvement.

  Verdict: inappropriate as the primary autoencoder here. It could be an exploratory third model only after the two-model comparison is complete.

  ## Sensor-wise versus multivariate autoencoders

  This is a separate decision from the architecture.

  ### Sensor-wise pooled model

  one sensor × 24 hours

  Windows from all 26 point sensors are pooled during training.

  Advantages:

  - More training windows.
  - Smaller input.
  - Easier per-sensor anomaly localization.
  - Fewer parameters.
  - Natural comparison with a pooled LSTM.

  Disadvantages:

  - Cannot detect that one sensor disagrees with neighbouring sensors.
  - Assumes sensors share some normal temporal patterns.
  - Synchronized sensors do not provide fully independent samples.

  This remains the recommended representation.

  ### Joint multivariate model

  24 hours × 26 sensors

  Advantages:

  - Can learn correlations between sensors.
  - Can detect city-wide and spatially inconsistent behaviour.
  - Useful for collective anomalies.

  Disadvantages:

  - Only about 312 possible sliding positions in the full timeline.
  - Much larger input.
  - High overfitting risk.
  - Missingness becomes more complicated.
  - Sensor ordering has no natural spatial meaning for convolution.

  Verdict: potentially useful in a larger dataset, but not suitable as the main model here.

  ## Why Conv1D wins the design decision

  The choice can be summarized like this:

   Criterion                        Dense AE    Conv1D AE     LSTM AE        VAE    Transformer AE
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━  ━━━━━━━━━━━  ━━━━━━━━━━  ━━━━━━━━━  ━━━━━━━━━━━━━━━━
   Suitable for short sequences         Good    Excellent        Good       Good              Weak
  ──────────────────────────────  ───────────  ───────────  ──────────  ─────────  ────────────────
   Models temporal locality               No          Yes         Yes    Depends               Yes
  ──────────────────────────────  ───────────  ───────────  ──────────  ─────────  ────────────────
   Small-data suitability          Excellent         Good    Moderate       Weak              Weak
  ──────────────────────────────  ───────────  ───────────  ──────────  ─────────  ────────────────
   Easy to train                   Excellent    Excellent    Moderate       Weak              Weak
  ──────────────────────────────  ───────────  ───────────  ──────────  ─────────  ────────────────
   Distinct from partner’s LSTM          Yes          Yes        Weak        Yes               Yes
  ──────────────────────────────  ───────────  ───────────  ──────────  ─────────  ────────────────
   Easy to explain                 Excellent         Good    Moderate       Weak              Weak
  ──────────────────────────────  ───────────  ───────────  ──────────  ─────────  ────────────────
   Project complexity               Very low          Low      Medium       High              High

  Conv1D does not dominate every category. Dense AE is simpler, and LSTM AE can model sequence dependencies more explicitly. Conv1D wins because it achieves the best overall compromise.

  ## A concise defence you can use

  > We selected a sensor-wise Conv1D autoencoder because the inputs are short hourly sequences with strong local temporal relationships. One-dimensional convolution provides an appropriate temporal inductive
  > bias by applying shared filters across neighbouring hours. Compared with a dense autoencoder, it explicitly models temporal locality; compared with an LSTM autoencoder, it is smaller, easier to optimize
  > and more methodologically distinct from the LSTM forecasting model already included in the comparison. More complex alternatives such as variational, TCN and Transformer autoencoders introduce additional
  > parameters and tuning requirements that are difficult to justify with only two weeks of observations. The model is deliberately kept small and uses a compressed bottleneck without skip connections to
  > prevent trivial input copying.

  The most defensible final choice is therefore:

  > A small sensor-wise Conv1D reconstruction autoencoder, optionally trained with mild denoising regularization.

  That is not claimed to be universally best. It is the model whose assumptions most closely match your data and project constraints.
