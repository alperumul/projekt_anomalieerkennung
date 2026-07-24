"""
Zentrale Startdatei für die explorative Datenanalyse.

Diese Datei ruft die drei EDA-Module nacheinander auf:
1. Sensoren und Zeit
2. Besucherzahlen und Aufenthaltsdauer
3. Stunden- und Wochentagsmuster

Alle Ergebnisse werden als CSV und PNG im Output-Ordner gespeichert.
"""

import subprocess
import sys


SKRIPTE = [
    "explorative_datenanalyse_sensoren_und zeit.py",
    "explorative_datenanalyse_besucher_und_aufenthaltsdauer.py",
    "explorative_datenanalyse_muster_und_export.py",
]


def starte_eda():
    """
    Führt alle EDA-Skripte nacheinander aus.
    """
    for skript in SKRIPTE:
        print("\n" + "=" * 80)
        print(f"Starte {skript}")
        print("=" * 80)

        ergebnis = subprocess.run([sys.executable, skript])

        if ergebnis.returncode != 0:
            print(f"Fehler in {skript}. Abbruch der EDA-Pipeline.")
            return

    print("\nAlle EDA-Skripte wurden erfolgreich ausgeführt.")


if __name__ == "__main__":
    starte_eda()