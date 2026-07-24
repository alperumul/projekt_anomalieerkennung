# References and evidence sources

[Back to documentation index](../README.md)

## Evidence categories

The project uses four different kinds of support. They should not be presented as interchangeable:

1. **Assignment requirements** state what the project must deliver.
2. **Project evidence** establishes facts about this particular CSV through inspectable code and output.
3. **External research** supports general methodological or domain claims, within the limits stated below.
4. **Predeclared project choices** are reasoned conventions to be tested, not facts supposedly dictated by a paper.

The exact split timestamps, autoencoder 24-hour footprint, autoencoder completeness values `k=0`, `k=6` and `k=4`, two-hour patch limit, network widths, autoencoder hyperparameter grid, shared threshold quantiles, injection magnitudes, event counts and random seeds are category 4. Their defensibility comes from being explicit, leak-safe, feasible on the audited data and fixed before model results are inspected. No cited paper is claimed to prove that those exact values are optimal, and none of these records prescribes the partner's LSTM design.

## Peer-reviewed research

The bibliographic metadata and the claim summaries below were checked against the publisher or conference pages on 2026-07-22.

### R1

Goswami, M., Challu, C., Callot, L., Minorics, L., & Kan, A. (2023). *Unsupervised Model Selection for Time-Series Anomaly Detection*. ICLR 2023. [OpenReview paper](https://openreview.net/pdf?id=gOZ_pKANaPW).

**Supports:** anomaly labels are often scarce, and performance on injected synthetic anomalies is one of several imperfect surrogate signals studied for label-free model selection.

**Does not support:** treating injected anomalies as verified real anomalies, using injection as the only evidence, or claiming that this project's chosen perturbations have external validity.

### R2

Kim, S., Choi, K., Choi, H.-S., Lee, B., & Yoon, S. (2022). *Towards a Rigorous Evaluation of Time-Series Anomaly Detection*. *Proceedings of the AAAI Conference on Artificial Intelligence, 36*(7), 7194-7201. [DOI](https://doi.org/10.1609/aaai.v36i7.20680).

**Supports:** naive point adjustment can substantially overestimate time-series anomaly-detection performance and can produce misleading method rankings.

**Does not support:** any particular threshold, anomaly-injection family or overlap formula used by this project.

### R3

Tatbul, N., Lee, T. J., Zdonik, S., Alam, M., & Gottschlich, J. (2018). *Precision and Recall for Time Series*. *Advances in Neural Information Processing Systems, 31*. [NeurIPS paper](https://papers.neurips.cc/paper_files/paper/2018/hash/8f468c873a32bb0619eaeb2050ba45d1-Abstract.html).

**Supports:** interval anomalies should be evaluated as temporal ranges and may require range-aware metrics rather than only independent point classification.

**Does not support:** the project's exact temporal-IoU formula. Temporal IoU is a project-defined interpretation of the assignment's unspecified “overlap coefficient” and must be confirmed with the professor.

### R4

Dobler, G., Vani, J., & Dam, T. T. L. (2021). *Patterns of Urban Foot Traffic Dynamics*. *Computers, Environment and Urban Systems, 89*, 101674. [DOI](https://doi.org/10.1016/j.compenvurbsys.2021.101674).

**Supports:** urban foot traffic can exhibit repeatable time-of-day patterns and differences between weekdays, weekends and holidays.

**Does not support:** assuming that New York patterns transfer unchanged to Bad Nauheim, or proving that this project's six feature channels are optimal. The `Europe/Berlin` conversion follows from the local meaning of calendar time; the paper only supports modelling temporal context.

### R7

Saito, T., & Rehmsmeier, M. (2015). *The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets*. *PLOS ONE, 10*(3), e0118432. [DOI](https://doi.org/10.1371/journal.pone.0118432).

**Supports:** precision-recall analysis is more informative than ROC analysis in strongly imbalanced binary evaluation, which is typical when injected anomaly hours are rare; the PR baseline depends on positive prevalence, and interpolation requires care.

**Does not support:** omitting ROC-AUC, which remains an explicit assignment requirement, or uniquely requiring scikit-learn average precision. The project names `average_precision_score` as its reproducible primary convention.

## Research-integrity and AI-use guidance

These are official governance sources, not peer-reviewed anomaly-detection research.

### R5

European Commission, Directorate-General for Research and Innovation. (2026). *Living Guidelines on the Responsible Use of Generative AI in Research* (3rd ed.). [Official guidelines](https://research-and-innovation.ec.europa.eu/document/download/2b6cf7e5-36ac-41cb-aab5-0d32050143dc_en?filename=ec_rtd_ai-guidelines.pdf).

**Supports:** human accountability, critical verification of AI output, transparent disclosure of substantial use, attention to reproducibility, and protection of confidential or personal information.

**Status:** non-binding general guidance; the university's and professor's rules take precedence.

### R6

Deutsche Forschungsgemeinschaft. (2023). *Statement by the Executive Committee of the Deutsche Forschungsgemeinschaft on the Influence of Generative Models of Text and Image Creation on Science and the Humanities and on the DFG's Funding Activities*. [Official DFG statement](https://www.dfg.de/resource/blob/389608/ai-230921-statement-executive-committee.pdf).

**Supports:** transparent disclosure of the purpose and extent of generative-model use and continued human responsibility for content and research integrity.

**Status:** DFG guidance, not a substitute for the applicable course or university policy.

## Project evidence

- [`Projektbeschreibung.pdf`](../../Projektbeschreibung.pdf) - official assignment brief; visually and textually checked against the requirement summary on 2026-07-22.
- [`bad_nauheim_bereinigt.csv`](../../new-data/data/bad_nauheim_bereinigt.csv) - canonical source table, SHA-256 `af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`.
- [`datenbereinigung_daten_zeitachse_und_interpolation.py`](../../new-data/src/datenbereinigung_daten_zeitachse_und_interpolation.py) - establishes how `war_fehlend` is recorded around the delivered interpolation step.
- [`datenbereinigung_daten_qualitaet_und_speichern.py`](../../new-data/src/datenbereinigung_daten_qualitaet_und_speichern.py) - documents the upstream sensor-quality and storage logic used to produce the delivered CSV.
- [`windowing.py`](../../new-data/src/windowing.py) - partner preprocessing/windowing snapshot used for the 2026-07-24 dry-run audit; it is not itself the normative shared contract.
- [`2026-07-24-new-data.sha256`](../provenance/2026-07-24-new-data.sha256) - complete SHA-256 manifest of the inspected `new-data` snapshot.
- [`verify_design_contract.py`](../../scripts/verify_design_contract.py) - historical verifier for the superseded 26-series design; it must be replaced or extended for current acceptance counts.
- [`autoencoder design decisions.md`](../../autoencoder%20design%20decisions.md) - version-controlled design history, not an academic source.

## Citation verification rule

Before a source appears in the final report:

1. open the publisher, proceedings or official issuing-body source;
2. identify the exact claim it supports and what it does not support;
3. prefer the original paper over an AI summary or internal note;
4. ensure the project does not state a stronger or more local conclusion than the source;
5. record the final citation in the team's reference manager or report bibliography; and
6. have a student, not only an AI tool, sign off that the source was read and understood.
