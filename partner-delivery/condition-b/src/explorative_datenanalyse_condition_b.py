"""Erstellt vier beschreibende Verfügbarkeitsplots für Condition B.

Die Funktionen verwenden ausschließlich bereits validierte öffentliche
Tabellen. Sie zeigen keine Modellwerte, Scores, Schwellen oder
Anomalieergebnisse.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PLOTVERZEICHNIS = Path(__file__).resolve().parents[1] / "plots"


def _speichere_abbildung(
    abbildung: plt.Figure,
    pfad: str | Path,
) -> Path:
    """Speichert eine Abbildung deterministisch und schließt sie."""

    ziel = Path(pfad)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    try:
        abbildung.tight_layout()
        abbildung.savefig(
            ziel,
            dpi=300,
            bbox_inches="tight",
            format="png",
            metadata={"Software": "Matplotlib 3.11.1"},
        )
    finally:
        plt.close(abbildung)
    print("Gespeichert:", ziel)
    return ziel


def erstelle_condition_a_b_verfuegbarkeit(
    bedingungen_df: pd.DataFrame,
    pfad: str | Path = (
        PLOTVERZEICHNIS / "condition_a_b_verfuegbarkeit.png"
    ),
) -> Path:
    """Vergleicht Originalbeobachtung und Eingabeverfügbarkeit."""

    beschriftungen = ["Bedingung A\n6.–7. Juli", "Bedingung B\n8.–13. Juli"]
    positionen = np.arange(len(bedingungen_df))
    breite = 0.34
    abbildung, achse = plt.subplots(figsize=(10, 6))
    achse.bar(
        positionen - breite / 2,
        bedingungen_df["original_observation_rate"] * 100,
        breite,
        label="Ursprünglich beobachtet",
        color="steelblue",
    )
    achse.bar(
        positionen + breite / 2,
        bedingungen_df["input_available_rate"] * 100,
        breite,
        label="Als Eingabe verfügbar",
        color="darkorange",
    )
    achse.set_title(
        "Datenverfügbarkeit im kontinuierlichen Test\n"
        "Bedingung A und B als getrennte Berichtsbedingungen"
    )
    achse.set_xlabel("Berichtsbedingung")
    achse.set_ylabel("Anteil der Serien-Stunden (%)")
    achse.set_xticks(positionen, beschriftungen)
    achse.set_ylim(0, 100)
    achse.grid(axis="y", alpha=0.3)
    achse.legend()
    return _speichere_abbildung(abbildung, pfad)


def erstelle_condition_b_verfuegbarkeit_pro_tag(
    tage_df: pd.DataFrame,
    pfad: str | Path = (
        PLOTVERZEICHNIS / "condition_b_verfuegbarkeit_pro_tag.png"
    ),
) -> Path:
    """Zeigt beide Verfügbarkeitsraten je UTC-Datum."""

    beschriftungen = tage_df["utc_date"].str.slice(5).str.replace("-", ".")
    abbildung, achse = plt.subplots(figsize=(11, 6))
    achse.plot(
        beschriftungen,
        tage_df["original_observation_rate"] * 100,
        marker="o",
        linewidth=2,
        label="Ursprünglich beobachtet",
        color="steelblue",
    )
    achse.plot(
        beschriftungen,
        tage_df["input_available_rate"] * 100,
        marker="o",
        linewidth=2,
        label="Als Eingabe verfügbar",
        color="darkorange",
    )
    achse.set_title("Condition B: Datenverfügbarkeit je UTC-Datum")
    achse.set_xlabel("UTC-Datum im Juli 2025")
    achse.set_ylabel("Anteil der Serien-Stunden (%)")
    achse.set_ylim(0, 100)
    achse.grid(alpha=0.3)
    achse.legend()
    return _speichere_abbildung(abbildung, pfad)


def erstelle_fehlende_stunden_pro_serie(
    serien_df: pd.DataFrame,
    pfad: str | Path = (
        PLOTVERZEICHNIS
        / "condition_b_fehlende_stunden_pro_serie.png"
    ),
) -> Path:
    """Zeigt ursprüngliche Lücken und verbleibende Eingabeausfälle."""

    positionen = np.arange(len(serien_df))
    breite = 0.38
    abbildung, achse = plt.subplots(figsize=(12, 6))
    achse.bar(
        positionen - breite / 2,
        serien_df["originally_missing_count"],
        breite,
        label="Ursprünglich fehlende Stunden",
        color="cornflowerblue",
    )
    achse.bar(
        positionen + breite / 2,
        serien_df["unavailable_input_count"],
        breite,
        label="Weiterhin nicht als Eingabe verfügbar",
        color="darkorange",
    )
    achse.set_title("Condition B: Fehlende Stunden je Zeitreihe")
    achse.set_xlabel("Zeitreihe")
    achse.set_ylabel("Stunden")
    achse.set_xticks(
        positionen,
        serien_df["series_id"],
        rotation=45,
        ha="right",
    )
    achse.grid(axis="y", alpha=0.3)
    achse.legend()
    return _speichere_abbildung(abbildung, pfad)


def erstelle_groesste_luecke_pro_serie(
    serien_df: pd.DataFrame,
    pfad: str | Path = (
        PLOTVERZEICHNIS
        / "condition_b_groesste_luecke_pro_serie.png"
    ),
) -> Path:
    """Vergleicht längste Original- und Eingabeverfügbarkeitslücken."""

    positionen = np.arange(len(serien_df))
    breite = 0.38
    abbildung, achse = plt.subplots(figsize=(12, 6))
    achse.bar(
        positionen - breite / 2,
        serien_df["longest_originally_missing_run_hours"],
        breite,
        label="Längste Folge ursprünglich fehlend",
        color="steelblue",
    )
    achse.bar(
        positionen + breite / 2,
        serien_df["longest_unavailable_input_run_hours"],
        breite,
        label="Längste Folge als Eingabe nicht verfügbar",
        color="seagreen",
    )
    achse.set_title(
        "Condition B: Größte Lücke je Zeitreihe\n"
        "Originalbeobachtung und verbleibende Eingabeverfügbarkeit"
    )
    achse.set_xlabel("Zeitreihe")
    achse.set_ylabel("Aufeinanderfolgende Stunden")
    achse.set_xticks(
        positionen,
        serien_df["series_id"],
        rotation=45,
        ha="right",
    )
    achse.grid(axis="y", alpha=0.3)
    achse.legend()
    return _speichere_abbildung(abbildung, pfad)


def erstelle_alle_verfuegbarkeitsplots(
    tabellen: dict[str, pd.DataFrame],
    plotverzeichnis: str | Path = PLOTVERZEICHNIS,
) -> dict[str, Path]:
    """Erstellt die vier festgelegten Verfügbarkeitsplots."""

    wurzel = Path(plotverzeichnis)
    return {
        "condition_a_b": erstelle_condition_a_b_verfuegbarkeit(
            tabellen["bedingungen"],
            wurzel / "condition_a_b_verfuegbarkeit.png",
        ),
        "condition_b_pro_tag": (
            erstelle_condition_b_verfuegbarkeit_pro_tag(
                tabellen["tage"],
                wurzel / "condition_b_verfuegbarkeit_pro_tag.png",
            )
        ),
        "fehlende_stunden_pro_serie": (
            erstelle_fehlende_stunden_pro_serie(
                tabellen["serien"],
                wurzel
                / "condition_b_fehlende_stunden_pro_serie.png",
            )
        ),
        "groesste_luecke_pro_serie": (
            erstelle_groesste_luecke_pro_serie(
                tabellen["serien"],
                wurzel
                / "condition_b_groesste_luecke_pro_serie.png",
            )
        ),
    }
