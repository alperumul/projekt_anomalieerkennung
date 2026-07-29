"""Führt das Einlesen und die Condition-B-Verfügbarkeitsplots aus."""

from __future__ import annotations

from pathlib import Path

from condition_b_daten_einlesen import lade_alle_tabellen
from explorative_datenanalyse_condition_b import (
    erstelle_alle_verfuegbarkeitsplots,
)

PAKETVERZEICHNIS = Path(__file__).resolve().parents[1]
DATENVERZEICHNIS = PAKETVERZEICHNIS / "data"
PLOTVERZEICHNIS = PAKETVERZEICHNIS / "plots"


def starte_eda() -> dict[str, object]:
    """Liest die öffentlichen Tabellen und erzeugt vier PNG-Dateien."""

    print("\n" + "=" * 80)
    print("1. CONDITION-B-TABELLEN EINLESEN UND PRÜFEN")
    print("=" * 80)
    tabellen = lade_alle_tabellen(DATENVERZEICHNIS)
    print(
        "Geprüft:",
        f"{len(tabellen['stundendaten'])} Serien-Stunden,",
        "28 Zeitreihen und 144 UTC-Stunden.",
    )

    print("\n" + "=" * 80)
    print("2. BESCHREIBENDE VERFÜGBARKEITSPLOTS ERSTELLEN")
    print("=" * 80)
    plots = erstelle_alle_verfuegbarkeitsplots(
        tabellen,
        PLOTVERZEICHNIS,
    )

    print("\n" + "=" * 80)
    print("CONDITION-B-EDA ERFOLGREICH ABGESCHLOSSEN")
    print("=" * 80)
    print(
        "Die Plots beschreiben nur Datenverfügbarkeit und treffen "
        "keine LSTM- oder Modellentscheidung."
    )
    return {"tabellen": tabellen, "plots": plots}


def hauptpipeline() -> dict[str, object]:
    """Startet die sichtbare, dateirelative EDA-Pipeline."""

    return starte_eda()


if __name__ == "__main__":
    hauptpipeline()
