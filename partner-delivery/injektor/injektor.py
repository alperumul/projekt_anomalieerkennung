"""
Der Anomalie-Injektor — eigenständiger Auszug zum Nachprüfen.

Das hier ist der **komplette fachliche Kern** der Injektion, aus
`src/anomaly_detection/phase12.py` und `phase13.py` herausgelöst und auf das
reduziert, was die Ereignisse tatsächlich bestimmt. Die Funktionsnamen sind
absichtlich unverändert, damit du Zeile für Zeile gegen das Original vergleichen
kannst.

Was **nicht** drin ist, weil es die Ereignisse nicht beeinflusst: Hash-Pinning,
Lauf-Manifeste, Provenance, Staging, Fortschrittsdateien, die Scoring-Schleife
über die 13 Läufe und die Metrikberechnung.

Abhängigkeiten: `pandas`, `numpy`. Sonst nichts.

Reihenfolge im Modul — sie entspricht dem tatsächlichen Ablauf:

    1. Konstanten und das Szenario-Raster
    2. Skalierung (Statistiken aus dem Training)
    3. Die beiden Kernformeln
    4. Kandidatenpool + Kapazitätsprüfung
    5. Ziehung (gesät, deterministisch)
    6. Ereignisse mit realisierten Stärken
    7. Kopien-Aufzählung
    8. Störung einer Kopie (inkl. Rauschen)
    9. Ereignis-Tabelle und Labels
   10. Loader für die gemeinsame CSV

Hinweis zur Reproduktion: die exakten Ereignisse aus Phase 13 bekommst du damit
**nicht**, weil der Kandidatenpool auf der eingefrorenen gemeinsamen
Auswertungsmenge aufsetzt und die Datei hier nicht dabei liegt. Was du prüfen
kannst, ist die Logik — mit `demo.py` auf synthetischen Daten und mit
`test_injektor.py`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import math

import numpy as np
import pandas as pd


class InjektorFehler(ValueError):
    """Im Original `Phase13ArtifactError` bzw. `Phase12ArtifactError`."""


# ===========================================================================
# 1. Konstanten und das Szenario-Raster
# ===========================================================================

HOUR = pd.Timedelta(hours=1)

TRAINING_START = pd.Timestamp("2025-06-30T01:00:00Z")
TRAINING_END_EXCLUSIVE = pd.Timestamp("2025-07-04T00:00:00Z")
CONTINUOUS_TEST_START = pd.Timestamp("2025-07-06T00:00:00Z")
CONTINUOUS_TEST_END_EXCLUSIVE = pd.Timestamp("2025-07-14T00:00:00Z")

# Der 8. Juli trennt die beiden Conditions. Ereignisse dürfen die Grenze nicht
# überschreiten; die Fensterbildung läuft durchgehend darüber hinweg.
CONDITION_RANGES = {
    "condition_a": (
        pd.Timestamp("2025-07-06T00:00:00Z"),
        pd.Timestamp("2025-07-08T00:00:00Z"),
    ),
    "condition_b": (
        pd.Timestamp("2025-07-08T00:00:00Z"),
        pd.Timestamp("2025-07-14T00:00:00Z"),
    ),
}
CONDITIONS = ("condition_a", "condition_b")
CONDITION_TOKENS = {"condition_a": "ca", "condition_b": "cb"}
ROUTE_TOKENS = {"k=6": "k6", "k=4": "k4"}
ELIGIBILITY_RULES = ("k=6", "k=4")

INPUT_VISITOR_COLUMN = "input_visitor_scaled"
TARGET_VISITOR_COLUMN = "target_visitor_scaled"


@dataclass(frozen=True)
class Scenario:
    """Ein Szenario = Familie + Dauer + Stärke + Richtung."""

    scenario_id: str
    family: str
    duration_hours: int
    requested_magnitude: float | None
    direction: str


# 14 Szenarien, kanonisch sortiert. `level_shift` mit 5 h stand ursprünglich auf
# 8 h; auf der gemeinsamen Auswertungsmenge gibt es in Condition B nicht genug
# platzierbare 8-Stunden-Fenster für die Regel "fünf Ereignisse auf fünf
# verschiedenen Serien". 5 h ist die längste Dauer, die die Regel in beiden
# Conditions unverändert erfüllt.
SCENARIOS = (
    Scenario("level_shift-d4h-m1-neg", "level_shift", 4, 1.0, "-"),
    Scenario("level_shift-d4h-m1-pos", "level_shift", 4, 1.0, "+"),
    Scenario("level_shift-d4h-m2-neg", "level_shift", 4, 2.0, "-"),
    Scenario("level_shift-d4h-m2-pos", "level_shift", 4, 2.0, "+"),
    Scenario("level_shift-d5h-m1-neg", "level_shift", 5, 1.0, "-"),
    Scenario("level_shift-d5h-m1-pos", "level_shift", 5, 1.0, "+"),
    Scenario("level_shift-d5h-m2-neg", "level_shift", 5, 2.0, "-"),
    Scenario("level_shift-d5h-m2-pos", "level_shift", 5, 2.0, "+"),
    Scenario("observed_zero_dropout-d2h-mna-neg", "observed_zero_dropout", 2, None, "-"),
    Scenario("observed_zero_dropout-d4h-mna-neg", "observed_zero_dropout", 4, None, "-"),
    Scenario("point_spike-d1h-m2-neg", "point_spike", 1, 2.0, "-"),
    Scenario("point_spike-d1h-m2-pos", "point_spike", 1, 2.0, "+"),
    Scenario("point_spike-d1h-m4-neg", "point_spike", 1, 4.0, "-"),
    Scenario("point_spike-d1h-m4-pos", "point_spike", 1, 4.0, "+"),
)
SCENARIO_BY_ID = {scenario.scenario_id: scenario for scenario in SCENARIOS}
SCENARIO_COUNT = 14

INJECTION_SEEDS = tuple(range(1, 16))          # 1 … 15
NOISE_SEEDS = tuple(range(101, 106))           # 101 … 105, bewusst anderer Raum
PART_D_INJECTION_SEEDS = (1, 2, 3)             # Teil D ist auf 3 Seeds begrenzt
PART_D_SCENARIO_IDS = (                        # je das mittlere Szenario pro Familie
    "point_spike-d1h-m2-pos",
    "point_spike-d1h-m2-neg",
    "level_shift-d4h-m1-pos",
    "level_shift-d4h-m1-neg",
    "observed_zero_dropout-d2h-mna-neg",
)
NOISE_SCALE = 0.1                              # N(0, 0.1²)

EVENTS_PER_SCENARIO = 5
MAX_DRAWS = 10_000

PART_A_DATA_COPIES = 420       # 14 × 2 × 15
PART_D_DATA_COPIES = 150       # 5 × 2 × 3 × 5
TOTAL_DATA_COPIES = 570
TOTAL_EVALUATION_COPIES = 1_140  # 570 × 2 Zulässigkeitsregeln

# Das Präfix `phase12|` ist historisch und bleibt bewusst stehen: ein stiller
# Wechsel würde jedes einzelne Ereignis verschieben.
PLACEMENT_SEED_MATERIAL = "phase12|{scenario_id}|{condition}|{injection_seed}"
NOISE_SEED_MATERIAL = (
    "phase12|noise|{scenario_id}|{condition}|{injection_seed}|{noise_seed}"
)

DATA_COPY_ID_PART_A = "injected-{scenario_id}-{cond}-s{seed:02d}-v1"
DATA_COPY_ID_PART_D = "noise-{scenario_id}-{cond}-s{seed:02d}-n{noise_seed}-v1"
EVALUATION_COPY_ID_PART_A = "injected-{scenario_id}-{cond}-s{seed:02d}-{route}-v1"
EVALUATION_COPY_ID_PART_D = (
    "noise-{scenario_id}-{cond}-s{seed:02d}-n{noise_seed}-{route}-v1"
)


def condition_of(moment: pd.Timestamp) -> str:
    """Condition einer Teststunde."""
    for condition, (low, high) in CONDITION_RANGES.items():
        if low <= moment < high:
            return condition
    raise InjektorFehler(f"Zeitpunkt liegt außerhalb der Testperiode: {moment!r}")


# ===========================================================================
# 2. Skalierung — Statistiken ausschließlich aus dem Training
# ===========================================================================


def observed_training_median(values: Sequence[float]) -> float:
    """Median der rohen Zählwerte, mit festgelegter Regel bei gerader Anzahl.

    Bei gerader Anzahl das **arithmetische Mittel der beiden mittleren Werte**.
    18 der 28 Serien haben eine gerade Anzahl beobachteter Trainingszeilen, also
    entscheidet diese Regel real mit: nähme man stattdessen den unteren der
    beiden, kämen andere Mediane heraus und die Kandidatenpools der
    Dropout-Szenarien verschöben sich.
    """
    ordered = sorted(values)
    count = len(ordered)
    if count == 0:
        raise InjektorFehler("Trainingsmedian über eine leere Serie")
    middle = count // 2
    if count % 2 == 1:
        return float(ordered[middle])
    return (float(ordered[middle - 1]) + float(ordered[middle])) / 2.0


def fit_visitor_statistics(
    observations: pd.DataFrame,
) -> dict[str, tuple[float, float, float]]:
    """`series_id -> (mean_s, scale_s, floor_s)`, gefittet nur auf dem Training.

    Darstellung: `log1p` der rohen Besucherzahl, dann pro Serie standardisiert.
    `floor_s` ist der skalierte Wert einer rohen Zahl von 0, also die
    Untergrenze, gegen die geklippt wird.

    Aufsummiert mit `math.fsum`, nicht `numpy.mean`. Der Unterschied ist ein ULP
    und überlebt die Serialisierung mit `.17g` — bei zwei Implementierungen, die
    dasselbe reproduzieren sollen, ist das der Unterschied zwischen "gleich" und
    "fast gleich".

    Erwartet die Spalten `series_id`, `timestamp_utc`, `visitors_raw`,
    `originally_observed`.
    """
    training = observations.loc[
        observations["originally_observed"]
        & (observations["timestamp_utc"] >= TRAINING_START)
        & (observations["timestamp_utc"] < TRAINING_END_EXCLUSIVE)
    ]
    statistics: dict[str, tuple[float, float, float]] = {}
    for series_id, group in training.groupby("series_id", sort=True):
        values = [math.log1p(float(value)) for value in group["visitors_raw"]]
        count = len(values)
        mean_s = math.fsum(values) / count
        variance = math.fsum((value - mean_s) ** 2 for value in values) / count
        scale_s = math.sqrt(variance) if variance > 0 else 1.0
        floor_s = (math.log1p(0.0) - mean_s) / scale_s
        statistics[str(series_id)] = (mean_s, scale_s, floor_s)
    return statistics


def scaled_value(raw_visitors: float, statistic: tuple[float, float, float]) -> float:
    """`(log1p(besucher) - mean_s) / scale_s`."""
    mean_s, scale_s, _ = statistic
    return (math.log1p(float(raw_visitors)) - mean_s) / scale_s


def training_medians(observations: pd.DataFrame) -> dict[str, float]:
    """Beobachteter Trainingsmedian der **rohen** Zählwerte je Serie."""
    training = observations.loc[
        observations["originally_observed"]
        & (observations["timestamp_utc"] >= TRAINING_START)
        & (observations["timestamp_utc"] < TRAINING_END_EXCLUSIVE)
    ]
    return {
        str(series_id): observed_training_median(
            [float(value) for value in group["visitors_raw"]]
        )
        for series_id, group in training.groupby("series_id", sort=True)
    }


# ===========================================================================
# 3. Die beiden Kernformeln
# ===========================================================================


def per_hour_realized_change(
    scenario: Scenario, scaled_original: float, floor_s: float
) -> float:
    """Realisierte Änderung **einer** Stunde, in der skalierten Darstellung.

        point_spike / level_shift :  abs( max(floor_s, x ± m) - x )
        observed_zero_dropout     :  abs( floor_s - x )

    Das Klippen ist ausschließlich eine **Untergrenze**. Nach oben gibt es keine
    Grenze. Deshalb kann die realisierte Stärke unter der angeforderten liegen —
    und deshalb führt die Ereignistabelle beide.
    """
    if scenario.family == "observed_zero_dropout":
        return abs(floor_s - scaled_original)
    magnitude = float(scenario.requested_magnitude or 0.0)
    if scenario.direction == "+":
        return abs(max(floor_s, scaled_original + magnitude) - scaled_original)
    return abs(max(floor_s, scaled_original - magnitude) - scaled_original)


def injected_scaled_value(
    scenario: Scenario, scaled_original: float, floor_s: float
) -> float:
    """Der Wert, der tatsächlich in die Kopie geschrieben wird.

    Beim Dropout wird die rohe Zahl auf 0 gesetzt; deren skalierter Wert ist
    exakt `floor_s`.
    """
    if scenario.family == "observed_zero_dropout":
        return floor_s
    magnitude = float(scenario.requested_magnitude or 0.0)
    if scenario.direction == "+":
        return max(floor_s, scaled_original + magnitude)
    return max(floor_s, scaled_original - magnitude)


# ===========================================================================
# 4. Kandidatenpool und Kapazitätsprüfung
# ===========================================================================


def build_candidate_pool(
    scenario: Scenario,
    condition: str,
    *,
    scaled: Mapping[tuple[str, pd.Timestamp], float],
    raw: Mapping[tuple[str, pd.Timestamp], float],
    statistics: Mapping[str, tuple[float, float, float]],
    medians: Mapping[str, float],
    population: frozenset[tuple[str, pd.Timestamp]],
) -> tuple[tuple[str, pd.Timestamp], ...]:
    """Alle zulässigen `(series_id, start)`-Paare — die vier Kriterien.

    Zulässig **genau dann, wenn alle vier** gelten:

    1. alle D Stunden liegen im halboffenen Zeitfenster der Condition. Das
       erzwingt gleichzeitig "nur Test" und "kein Ereignis über den 8. Juli";
    2. alle D Stunden liegen in der eingefrorenen Auswertungsmenge. Kein
       gelabeltes Ereignis darf außerhalb der Menge liegen, auf der gemessen wird;
    3. die **mittlere** absolute realisierte Änderung über die D Stunden ist nach
       dem Klippen echt größer als 0;
    4. nur beim Dropout: die mittlere **rohe** Besucherzahl der Spanne ist
       mindestens so hoch wie der Trainingsmedian dieser Serie.

    Sortiert aufsteigend nach `(series_id, start)`; `series_id` als Python-`str`,
    also Unicode-Codepoint-Reihenfolge auf dem exakten CSV-Namen, **ohne**
    Normalisierung. Diese sortierte Liste ist das gesamte Ziehungsuniversum.

    Kriterium 3 nimmt bewusst den **Mittelwert**, nicht den Wert je Stunde: eine
    Pro-Stunde-Lesart ändert bei 5 der 14 Szenarien den Pool.
    """
    low, high = CONDITION_RANGES[condition]
    duration = scenario.duration_hours
    eligible: list[tuple[str, pd.Timestamp]] = []
    for series_id, start in sorted(population, key=lambda item: (item[0], item[1])):
        hours = [start + index * HOUR for index in range(duration)]
        if hours[0] < low or hours[-1] >= high:
            continue
        if any((series_id, hour) not in population for hour in hours):
            continue
        _, _, floor_s = statistics[series_id]
        originals = [scaled[(series_id, hour)] for hour in hours]
        # Kriterium 4 vor Kriterium 3, weil billiger.
        if scenario.family == "observed_zero_dropout":
            span_mean = math.fsum(
                float(raw[(series_id, hour)]) for hour in hours
            ) / duration
            if span_mean < medians[series_id]:
                continue
        per_hour = [
            per_hour_realized_change(scenario, value, floor_s) for value in originals
        ]
        if math.fsum(per_hour) / duration <= 0.0:
            continue
        eligible.append((series_id, start))
    return tuple(eligible)


def capacity_check(
    candidates: Sequence[tuple[str, pd.Timestamp]],
) -> tuple[int, int, int]:
    """`(K, angefordert, realisiert)` — **vor** jeder Ziehung, ohne Modellausgabe.

    K ist die Anzahl verschiedener Serien im Pool. Das Protokoll erlaubt weniger
    als fünf Ereignisse nur, wenn genau diese Prüfung beweist, dass fünf
    unmöglich sind. Auf der echten Menge greift der Zweig nirgends — er ist
    implementiert und getestet, darf im Lauf aber nicht ausgeführt werden.
    """
    distinct = len({series_id for series_id, _ in candidates})
    if distinct >= EVENTS_PER_SCENARIO:
        return distinct, EVENTS_PER_SCENARIO, EVENTS_PER_SCENARIO
    return distinct, EVENTS_PER_SCENARIO, distinct


def contiguity_curve(
    population: Sequence[tuple[str, pd.Timestamp]],
    durations: Sequence[int] = (1, 2, 4, 5, 6, 7, 8),
) -> dict[tuple[str, int], tuple[int, int]]:
    """Rein strukturelle Platzierbarkeit je Condition und Dauer.

    Ohne Verkehrsregel, ohne Null-Änderungs-Filter — nur: wie viele
    D-stündige, lückenlos in der Auswertungsmenge liegende Fenster gibt es?
    Das ist die Grundlage der Dauer-Entscheidung (siehe `SCENARIOS`).
    """
    frozen = frozenset(population)
    ordered = sorted(population, key=lambda item: (item[0], item[1]))
    curve: dict[tuple[str, int], tuple[int, int]] = {}
    for condition in CONDITIONS:
        low, high = CONDITION_RANGES[condition]
        for duration in durations:
            pool = []
            for series_id, start in ordered:
                hours = [start + index * HOUR for index in range(duration)]
                if hours[0] < low or hours[-1] >= high:
                    continue
                if any((series_id, hour) not in frozen for hour in hours):
                    continue
                pool.append((series_id, start))
            curve[(condition, duration)] = (
                len(pool),
                len({series_id for series_id, _ in pool}),
            )
    return curve


# ===========================================================================
# 5. Ziehung — gesät und deterministisch
# ===========================================================================


def placement_seed_int(scenario_id: str, condition: str, injection_seed: int) -> int:
    """Seed-Integer aus dem Materialstring.

    `condition` ist das **volle** Token (`condition_a`), nie `ca`.
    `injection_seed` ist eine **ungepolsterte** Dezimalzahl — `1`, nie `01`.
    """
    if condition not in CONDITION_RANGES:
        raise InjektorFehler(f"Seed-Material braucht das volle Token: {condition!r}")
    material = PLACEMENT_SEED_MATERIAL.format(
        scenario_id=scenario_id, condition=condition, injection_seed=injection_seed
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def noise_seed_int(
    scenario_id: str, condition: str, injection_seed: int, noise_seed: int
) -> int:
    """Wie oben, für den Rauschstrom — eigener Materialstring, eigener Raum."""
    if condition not in CONDITION_RANGES:
        raise InjektorFehler(f"Seed-Material braucht das volle Token: {condition!r}")
    material = NOISE_SEED_MATERIAL.format(
        scenario_id=scenario_id,
        condition=condition,
        injection_seed=injection_seed,
        noise_seed=noise_seed,
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _no_overlap(
    series_id: str,
    start: pd.Timestamp,
    duration: int,
    selected: Sequence[tuple[str, pd.Timestamp, int, int]],
    scenario_duration: int,
) -> bool:
    """Überlappung gilt nur **innerhalb derselben Serie**.

    Zwei Ereignisse überlappen genau dann, wenn sie dieselbe `series_id` haben
    **und** sich ihre halboffenen Stundenbereiche schneiden. Eine reine
    Zeitraum-Lesart wäre falsch — sie würde auf gültigen Ereignismengen anschlagen.
    """
    low = start
    high = start + duration * HOUR
    for other_series, other_start, _, _ in selected:
        if other_series != series_id:
            continue
        other_low = other_start
        other_high = other_start + scenario_duration * HOUR
        if low < other_high and other_low < high:
            return False
    return True


def place_events(
    candidates: Sequence[tuple[str, pd.Timestamp]],
    scenario: Scenario,
    condition: str,
    injection_seed: int,
) -> tuple[tuple[str, pd.Timestamp, int, int], ...]:
    """Sequentielles Rejection-Sampling. Vier Details bestimmen das Ergebnis:

    1. gezogen wird in **jeder** Iteration aus der **vollen** Kandidatenliste,
       nicht aus einer auf unbenutzte Serien vorgefilterten. Beides ergibt
       dieselbe Verteilung, aber einen anderen Verbrauch an Zufallszahlen und
       damit eine andere Ereignismenge;
    2. `rng.integers(0, N)` ist **ein** gleichverteilter Index — kein
       `rng.choice`, kein Shuffle, keine Permutation;
    3. die Verschiedene-Serien-Bedingung wirkt als Verwerfen **nach** der
       Ziehung, nicht als Vorfilter;
    4. der Generator ist `PCG64`, gesät wie in `placement_seed_int`.

    Bewusste Konsequenz: gleichverteilt gezogen wird über **Kandidaten**, nicht
    über **Serien**. Eine Serie mit mehr zulässigen Startpositionen bekommt mit
    höherer Wahrscheinlichkeit ein Ereignis. Die Alternative ("erst fünf Serien,
    dann je eine Startstunde") wäre ebenso protokollkonform, hätte aber eine
    andere Randverteilung.

    Rückgabe in **Ziehungsreihenfolge**: `(series_id, start, index, draws)`.
    """
    count = len(candidates)
    if count == 0:
        raise InjektorFehler(
            f"Leerer Kandidatenpool für {scenario.scenario_id}/{condition}"
        )
    distinct_series = len({series_id for series_id, _ in candidates})
    seed_value = placement_seed_int(scenario.scenario_id, condition, injection_seed)
    rng = np.random.Generator(np.random.PCG64(seed_value))
    target = min(EVENTS_PER_SCENARIO, distinct_series)

    selected: list[tuple[str, pd.Timestamp, int, int]] = []
    used_series: set[str] = set()
    draws = 0
    while len(selected) < target and draws < MAX_DRAWS:
        index = int(rng.integers(0, count))
        draws += 1
        series_id, start = candidates[index]
        if series_id in used_series:
            continue                      # verwerfen, neu ziehen
        if not _no_overlap(
            series_id, start, scenario.duration_hours, selected,
            scenario.duration_hours,
        ):
            # Unter der Per-Serie-Definition folgt Nichtüberlappung bereits aus
            # verschiedenen Serien. Wenn das hier greift, ist es ein Defekt.
            raise InjektorFehler(
                "no_overlap hat ausgelöst — verschiedene Serien implizierten "
                "keine Nichtüberlappung; das ist ein Implementierungsfehler"
            )
        selected.append((series_id, start, index, draws))
        used_series.add(series_id)

    if len(selected) < target:
        raise InjektorFehler(
            f"Ziehung erschöpfte {MAX_DRAWS} Versuche mit {len(selected)} "
            f"Ereignissen bei {distinct_series} verschiedenen Serien im Pool"
        )
    return tuple(selected)


# ===========================================================================
# 6. Ereignisse mit realisierten Stärken
# ===========================================================================


@dataclass(frozen=True)
class PlacedEvent:
    series_id: str
    start: pd.Timestamp
    duration_hours: int
    candidate_index: int
    draws_consumed: int
    selection_order: int
    realized_min: float
    realized_mean: float
    realized_max: float

    @property
    def end_exclusive(self) -> pd.Timestamp:
        return self.start + self.duration_hours * HOUR

    @property
    def hours(self) -> tuple[pd.Timestamp, ...]:
        return tuple(self.start + i * HOUR for i in range(self.duration_hours))


def realized_magnitudes(
    scenario: Scenario,
    series_id: str,
    start: pd.Timestamp,
    *,
    scaled: Mapping[tuple[str, pd.Timestamp], float],
    statistics: Mapping[str, tuple[float, float, float]],
) -> tuple[float, float, float]:
    """`(min, mean, max)` der realisierten Änderung.

    Der Mittelwert ist `math.fsum(werte) / D`, **nicht** `numpy.mean`. Die beiden
    unterscheiden sich bei einzelnen Ereignissen um ein ULP, und der Unterschied
    überlebt die Serialisierung mit `.17g`.

    Ein Ereignis mit realisiertem Mittelwert 0 ist ungültig und bricht ab — es
    wäre eine Anomalie, die nichts verändert, aber als positiv gelabelt wird.
    """
    _, _, floor_s = statistics[series_id]
    duration = scenario.duration_hours
    per_hour = [
        per_hour_realized_change(
            scenario, scaled[(series_id, start + index * HOUR)], floor_s
        )
        for index in range(duration)
    ]
    mean_value = math.fsum(per_hour) / duration
    if mean_value <= 0.0:
        raise InjektorFehler(
            f"Ereignis ohne realisierte Änderung: {series_id!r} um {start!r}"
        )
    return min(per_hour), mean_value, max(per_hour)


def build_events(
    copy: "CopySpec",
    candidates: Sequence[tuple[str, pd.Timestamp]],
    *,
    scaled: Mapping[tuple[str, pd.Timestamp], float],
    statistics: Mapping[str, tuple[float, float, float]],
    population: frozenset[tuple[str, pd.Timestamp]] | None = None,
) -> tuple[PlacedEvent, ...]:
    """Platziert und bewertet die fünf Ereignisse einer Kopie.

    Ausgabe sortiert nach `(series_id, start)`; die Ziehungsreihenfolge bleibt in
    `selection_order` / `draws_consumed` erhalten.
    """
    scenario = copy.scenario
    selected = place_events(candidates, scenario, copy.condition, copy.injection_seed)
    events: list[PlacedEvent] = []
    for order, (series_id, start, index, draws) in enumerate(selected, start=1):
        low, mean, high = realized_magnitudes(
            scenario, series_id, start, scaled=scaled, statistics=statistics
        )
        end_exclusive = start + scenario.duration_hours * HOUR
        low_bound, high_bound = CONDITION_RANGES[copy.condition]
        if start < low_bound or end_exclusive > high_bound:
            raise InjektorFehler(
                f"Ereignis {series_id!r} um {start!r} verlässt {copy.condition}"
            )
        hours = tuple(
            start + offset * HOUR for offset in range(scenario.duration_hours)
        )
        if population is not None:
            outside = [hour for hour in hours if (series_id, hour) not in population]
            if outside:
                raise InjektorFehler(
                    f"Ereignis {series_id!r} um {start!r} legt {len(outside)} "
                    "gelabelte Stunden außerhalb der Auswertungsmenge ab"
                )
        events.append(
            PlacedEvent(
                series_id=series_id,
                start=start,
                duration_hours=scenario.duration_hours,
                candidate_index=index,
                draws_consumed=draws,
                selection_order=order,
                realized_min=low,
                realized_mean=mean,
                realized_max=high,
            )
        )
    events.sort(key=lambda event: (event.series_id, event.start))
    if len({event.series_id for event in events}) != len(events):
        raise InjektorFehler("Platzierte Ereignisse nutzen nicht verschiedene Serien")
    if len(events) != EVENTS_PER_SCENARIO:
        raise InjektorFehler(
            f"Kopie {copy.data_copy_id} hat {len(events)} Ereignisse, nicht "
            f"{EVENTS_PER_SCENARIO}"
        )
    return tuple(events)


# ===========================================================================
# 7. Kopien-Aufzählung
# ===========================================================================


@dataclass(frozen=True)
class CopySpec:
    """Eine Datenkopie. Teil A/C wenn `noise_seed is None`, sonst Teil D."""

    scenario_id: str
    condition: str
    injection_seed: int
    noise_seed: int | None

    @property
    def scenario(self) -> Scenario:
        return SCENARIO_BY_ID[self.scenario_id]

    @property
    def is_part_d(self) -> bool:
        return self.noise_seed is not None

    @property
    def data_copy_id(self) -> str:
        token = CONDITION_TOKENS[self.condition]
        if self.noise_seed is None:
            return DATA_COPY_ID_PART_A.format(
                scenario_id=self.scenario_id, cond=token, seed=self.injection_seed
            )
        return DATA_COPY_ID_PART_D.format(
            scenario_id=self.scenario_id,
            cond=token,
            seed=self.injection_seed,
            noise_seed=self.noise_seed,
        )

    def evaluation_copy_id(self, eligibility_rule: str) -> str:
        """Regel-spezifische ID — das Token steht **vor** dem `-v1`.

        Beide Zulässigkeitsregeln bewerten dieselbe Datenkopie. Ohne dieses
        Token würde der Score-Schlüssel
        `(run_id, evaluation_copy_id, series_id, timestamp_utc)` kollidieren,
        und doppelte Schlüssel sind ein Abbruchgrund.
        """
        token = CONDITION_TOKENS[self.condition]
        route = ROUTE_TOKENS[eligibility_rule]
        if self.noise_seed is None:
            return EVALUATION_COPY_ID_PART_A.format(
                scenario_id=self.scenario_id, cond=token,
                seed=self.injection_seed, route=route,
            )
        return EVALUATION_COPY_ID_PART_D.format(
            scenario_id=self.scenario_id, cond=token, seed=self.injection_seed,
            noise_seed=self.noise_seed, route=route,
        )

    @property
    def corresponding_part_a(self) -> "CopySpec":
        """Die rauschfreie Kopie, aus der Teil D Ereignisse und Labels übernimmt."""
        if self.noise_seed is None:
            raise InjektorFehler("Teil-A-Kopien haben kein Gegenstück")
        return CopySpec(self.scenario_id, self.condition, self.injection_seed, None)


def enumerate_data_copies() -> tuple[CopySpec, ...]:
    """Alle 570 Datenkopien: 420 Teil A/C + 150 Teil D."""
    copies: list[CopySpec] = []
    for scenario in SCENARIOS:
        for condition in CONDITIONS:
            for seed in INJECTION_SEEDS:
                copies.append(CopySpec(scenario.scenario_id, condition, seed, None))
    if len(copies) != PART_A_DATA_COPIES:
        raise InjektorFehler(f"Teil A hat {len(copies)} Kopien, nicht {PART_A_DATA_COPIES}")
    for scenario_id in PART_D_SCENARIO_IDS:
        for condition in CONDITIONS:
            for seed in PART_D_INJECTION_SEEDS:
                for noise in NOISE_SEEDS:
                    copies.append(CopySpec(scenario_id, condition, seed, noise))
    if len(copies) != TOTAL_DATA_COPIES:
        raise InjektorFehler(f"Insgesamt {len(copies)} Kopien, nicht {TOTAL_DATA_COPIES}")
    if len({copy.data_copy_id for copy in copies}) != TOTAL_DATA_COPIES:
        raise InjektorFehler("Doppelte data_copy_id in der Aufzählung")
    identifiers = {
        copy.evaluation_copy_id(rule) for copy in copies for rule in ELIGIBILITY_RULES
    }
    if len(identifiers) != TOTAL_EVALUATION_COPIES:
        raise InjektorFehler(
            f"{len(identifiers)} Auswertungs-IDs, nicht {TOTAL_EVALUATION_COPIES}"
        )
    return tuple(copies)


# ===========================================================================
# 8. Störung einer Kopie
# ===========================================================================


def noise_targets(
    event_hours: frozenset[tuple[str, pd.Timestamp]],
    observed_grid: Sequence[tuple[str, pd.Timestamp]],
) -> tuple[tuple[str, pd.Timestamp], ...]:
    """Der Störbereich für Teil D: das **ganze beobachtete Testgitter**, minus
    der Ereignisstunden dieser Kopie.

    Ausdrücklich **nicht** nur die Auswertungsmenge. Fenster laufen durchgehend,
    also fließen auch beobachtete, aber nicht ausgewertete Positionen in Fenster
    ein, deren Score auf einer ausgewerteten Position landet. Blieben sie sauber,
    hinge die Störung, die eine ausgewertete Position abbekommt, von ihrem
    Abstand zum Rand der Auswertungsmenge ab.

    Auswertungsmenge = Label- und Metrikbereich. Beobachtetes Gitter = Störbereich.
    """
    targets = [key for key in observed_grid if key not in event_hours]
    targets.sort(key=lambda item: (item[0], item[1]))
    return tuple(targets)


def noise_deltas(
    scenario: Scenario,
    condition: str,
    injection_seed: int,
    noise_seed: int,
    target_count: int,
) -> np.ndarray:
    """**Ein einziger** `size=N`-Zug. Nie stückweise, nie pro Serie.

    `Generator.normal` ist präfixstabil in `size`: eine Implementierung, die die
    falsche Zielmenge rauscht, reproduziert die ersten Werte exakt und ordnet
    trotzdem jeden einzelnen falsch zu. Deshalb wird `N` selbst geprüft, nicht
    nur die Werte.
    """
    seed_value = noise_seed_int(
        scenario.scenario_id, condition, injection_seed, noise_seed
    )
    generator = np.random.Generator(np.random.PCG64(seed_value))
    return generator.normal(loc=0.0, scale=NOISE_SCALE, size=target_count)


def apply_copy_perturbation(
    test_frame: pd.DataFrame,
    copy: CopySpec,
    events: Sequence[PlacedEvent],
    *,
    statistics: Mapping[str, tuple[float, float, float]],
    observed_grid: Sequence[tuple[str, pd.Timestamp]],
) -> pd.DataFrame:
    """Baut die gestörte Testperiode einer Kopie.

    Verändert werden ausschließlich `input_visitor_scaled` und
    `target_visitor_scaled` an **original beobachteten** Positionen.

    Unverändert bleiben:

    * beide Masken — sie werden nach dem Schreiben gegen das Original geprüft.
      Die Masken bestimmen die Fensterzulässigkeit und damit die eingefrorene
      Auswertungsmenge; dürfte eine Injektion sie ändern, könnte sie ihre eigene
      Auswertungsgrundlage verschieben;
    * die kurzen interpolierten Lücken. Sie werden einmal aus den sauberen Daten
      berechnet und sind in jeder Kopie identisch. Würden sie pro Kopie neu
      berechnet, könnte ein Ereignis benachbarte *ergänzte* Werte mitverändern —
      und die sind als negativ gelabelt;
    * Training und Validierung. Injiziert wird nur in die Testperiode.
    """
    result = test_frame.copy()
    position = {
        (str(series_id), moment): index
        for index, (series_id, moment) in enumerate(
            zip(result["series_id"], result["timestamp_utc"], strict=True)
        )
    }
    observed = result["target_observed_mask"].to_numpy(copy=True)
    available = result["input_available_mask"].to_numpy(copy=True)
    inputs = result[INPUT_VISITOR_COLUMN].to_numpy(dtype="float64", copy=True)
    targets = result[TARGET_VISITOR_COLUMN].to_numpy(dtype="float64", copy=True)

    scenario = copy.scenario
    event_hours: set[tuple[str, pd.Timestamp]] = set()
    for event in events:
        _, _, floor_s = statistics[event.series_id]
        for hour in event.hours:
            key = (event.series_id, hour)
            index = position.get(key)
            if index is None or not observed[index]:
                raise InjektorFehler(
                    f"Ereignisstunde ist keine beobachtete Position: {key!r}"
                )
            injected = injected_scaled_value(scenario, targets[index], floor_s)
            inputs[index] = injected
            targets[index] = injected
            event_hours.add(key)

    if len(event_hours) != EVENTS_PER_SCENARIO * scenario.duration_hours:
        raise InjektorFehler(
            f"{len(event_hours)} Ereignisstunden statt "
            f"{EVENTS_PER_SCENARIO * scenario.duration_hours}"
        )

    if copy.is_part_d:
        target_list = noise_targets(frozenset(event_hours), observed_grid)
        deltas = noise_deltas(
            scenario, copy.condition, copy.injection_seed,
            int(copy.noise_seed), len(target_list),
        )
        for offset, key in enumerate(target_list):
            index = position.get(key)
            if index is None or not observed[index]:
                raise InjektorFehler(
                    f"Rauschziel ist keine beobachtete Position: {key!r}"
                )
            _, _, floor_s = statistics[key[0]]
            perturbed = max(floor_s, targets[index] + float(deltas[offset]))
            inputs[index] = perturbed
            targets[index] = perturbed

    result[INPUT_VISITOR_COLUMN] = inputs
    result[TARGET_VISITOR_COLUMN] = targets
    if not np.array_equal(result["target_observed_mask"].to_numpy(), observed):
        raise InjektorFehler("Störung hat target_observed_mask verändert")
    if not np.array_equal(result["input_available_mask"].to_numpy(), available):
        raise InjektorFehler("Störung hat input_available_mask verändert")
    return result


# ===========================================================================
# 9. Ereignis-Tabelle und Labels
# ===========================================================================

EVENT_TABLE_COLUMNS = (
    "series_id",
    "start_timestamp_utc",
    "end_timestamp_exclusive",
    "anomaly_type",
    "requested_magnitude",
    "realized_magnitude_min",
    "realized_magnitude_mean",
    "realized_magnitude_max",
    "duration_hours",
    "direction",
    "injection_seed",
    "evaluation_copy_id",
    "evaluation_condition",
)

LABEL_COLUMNS = ("evaluation_copy_id", "series_id", "timestamp_utc", "label")


def event_table_rows(
    copy: CopySpec, events: Sequence[PlacedEvent]
) -> list[dict[str, object]]:
    """Die 13-spaltige Ereignistabelle.

    Zeitbereiche sind **halboffen**: `[start, end_exclusive)`. Die Differenz muss
    `duration_hours` sein und der Bereich genau so viele Stundenpositionen
    enthalten.
    """
    scenario = copy.scenario
    return [
        {
            "series_id": event.series_id,
            "start_timestamp_utc": event.start,
            "end_timestamp_exclusive": event.end_exclusive,
            "anomaly_type": scenario.family,
            "requested_magnitude": (
                "NA" if scenario.requested_magnitude is None
                else float(scenario.requested_magnitude)
            ),
            "realized_magnitude_min": event.realized_min,
            "realized_magnitude_mean": event.realized_mean,
            "realized_magnitude_max": event.realized_max,
            "duration_hours": scenario.duration_hours,
            "direction": scenario.direction,
            "injection_seed": copy.injection_seed,
            "evaluation_copy_id": copy.data_copy_id,
            "evaluation_condition": copy.condition,
        }
        for event in events
    ]


def label_rows(
    copy: CopySpec,
    events: Sequence[PlacedEvent],
    population: Sequence[tuple[str, pd.Timestamp]],
) -> list[dict[str, object]]:
    """Labels auf der eingefrorenen Auswertungsmenge.

    Jede Ereignisstunde **auf der Serie des Ereignisses** ist positiv. Jede
    andere Stunde der Menge ist negativ — mit der ausdrücklichen Einschränkung,
    dass unbekannte echte Anomalien damit als negativ gezählt werden.
    """
    positive = {(event.series_id, hour) for event in events for hour in event.hours}
    rows = [
        {
            "evaluation_copy_id": copy.data_copy_id,
            "series_id": series_id,
            "timestamp_utc": moment,
            "label": 1 if (series_id, moment) in positive else 0,
        }
        for series_id, moment in population
    ]
    expected_positive = EVENTS_PER_SCENARIO * copy.scenario.duration_hours
    observed_positive = sum(1 for row in rows if row["label"] == 1)
    if observed_positive != expected_positive:
        raise InjektorFehler(
            f"{observed_positive} positive Labels statt 5 × "
            f"{copy.scenario.duration_hours} = {expected_positive}"
        )
    return rows


# ===========================================================================
# 10. Loader
# ===========================================================================


def load_shared_bundle(path: str) -> pd.DataFrame:
    """Liest `gemeinsame_stundendaten.csv` — die Datei, die du schon hast."""
    frame = pd.read_csv(path)
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True)
    frame["series_id"] = frame["series_id"].astype("string").astype(object)
    for column in ("input_available_mask", "target_observed_mask"):
        if frame[column].dtype != bool:
            frame[column] = frame[column].map(
                {True: True, False: False, "True": True, "False": False}
            ).astype(bool)
    return frame


def continuous_test_frame(prepared: pd.DataFrame) -> pd.DataFrame:
    """Nur die durchgehende Testperiode, kanonisch sortiert."""
    frame = prepared.loc[prepared["true_split"] == "continuous_test"].copy()
    return frame.sort_values(["series_id", "timestamp_utc"]).reset_index(drop=True)


def load_canonical_observations(path: str) -> pd.DataFrame:
    """Liest die vier Spalten der kanonischen CSV.

    Eine Position ist **original beobachtet** genau dann, wenn `war_fehlend`
    falsch ist **und** `visitors` eine nicht-leere Zahl ist. Ergänzte,
    interpolierte und regenerierte Positionen sind es nie.
    """
    frame = pd.read_csv(path, usecols=["name", "timestamp", "visitors", "war_fehlend"])
    frame["series_id"] = frame["name"].astype("string").astype(object)
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp"], utc=True)
    missing = frame["war_fehlend"]
    if missing.dtype != bool:
        missing = missing.map(
            {True: True, False: False, "True": True, "False": False}
        ).astype(bool)
    visitors = pd.to_numeric(frame["visitors"], errors="coerce")
    frame["visitors_raw"] = visitors
    frame["originally_observed"] = (~missing) & visitors.notna()
    return frame[
        ["series_id", "timestamp_utc", "visitors_raw", "originally_observed"]
    ].copy()
