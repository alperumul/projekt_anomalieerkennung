"""
Dieses Modul analysiert zeitliche Muster der Besucherzahlen.

Enthalten sind:
- Besucherwerte nach lokaler Stunde,
- Besucherwerte nach lokalem Wochentag,
- Nullwerte pro Stunde und Wochentag,
- CSV-Export der Musterergebnisse,
- Diagramme für Stunden- und Wochentagsmuster.

Die UTC-Zeitstempel werden dafür nach Europe/Berlin umgerechnet.
"""

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import pandas as pd

from daten_einlesen import lade_daten


OUTPUT_DIR = Path("../plots")
OUTPUT_DIR.mkdir(exist_ok=True)

WOCHENTAGE_DEUTSCH = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
    5: "Samstag",
    6: "Sonntag",
}


def konvertiere_zeitstempel(timestamp_text):
    """
    Wandelt einen UTC-Zeitstempel aus den Rohdaten in ein timezone-aware datetime-Objekt um.
    """
    zeitstempel = datetime.strptime(timestamp_text, "%Y-%m-%dT%H:%M:%S.000Z")
    return zeitstempel.replace(tzinfo=timezone.utc)


def analysiere_stunden_und_wochentage(sensordaten):
    """
    Analysiert Besucherwerte nach lokaler Stunde und lokalem Wochentag.
    """
    print("\n" + "=" * 80)
    print("5. STUNDEN- UND WOCHENTAGSANALYSE")
    print("=" * 80)

    zeitzone_berlin = ZoneInfo("Europe/Berlin")
    besucher_pro_stunde = defaultdict(list)
    besucher_pro_wochentag = defaultdict(list)
    nullwerte_pro_stunde = Counter()
    nullwerte_pro_wochentag = Counter()

    for datensatz in sensordaten:
        besucher = datensatz.get("visitors")
        if besucher is None:
            continue

        zeitstempel_utc = konvertiere_zeitstempel(datensatz["timestamp"])
        zeitstempel_lokal = zeitstempel_utc.astimezone(zeitzone_berlin)

        lokale_stunde = zeitstempel_lokal.hour
        wochentag = WOCHENTAGE_DEUTSCH[zeitstempel_lokal.weekday()]

        besucher_pro_stunde[lokale_stunde].append(besucher)
        besucher_pro_wochentag[wochentag].append(besucher)

        if besucher == 0:
            nullwerte_pro_stunde[lokale_stunde] += 1
            nullwerte_pro_wochentag[wochentag] += 1

    stunden_ergebnisse = []
    print("\nDurchschnittliche Besucherwerte nach lokaler Stunde:")
    for stunde in range(24):
        werte = besucher_pro_stunde[stunde]
        if not werte:
            continue
        print(
            "Stunde:",
            stunde,
            "| Rohdatensätze:",
            len(werte),
            "| Durchschnitt Besucher:",
            round(mean(werte), 2),
            "| Median:",
            median(werte),
            "| Nullwerte:",
            nullwerte_pro_stunde[stunde],
        )
        stunden_ergebnisse.append(
            {
                "stunde": stunde,
                "anzahl": len(werte),
                "mittelwert": mean(werte),
                "median": median(werte),
                "nullwerte": nullwerte_pro_stunde[stunde],
            }
        )

    wochentag_ergebnisse = []
    print("\nDurchschnittliche Besucherwerte nach lokalem Wochentag:")
    reihenfolge_wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

    for wochentag in reihenfolge_wochentage:
        werte = besucher_pro_wochentag[wochentag]
        if not werte:
            continue
        print(
            "Wochentag:",
            wochentag,
            "| Rohdatensätze:",
            len(werte),
            "| Durchschnitt Besucher:",
            round(mean(werte), 2),
            "| Median:",
            median(werte),
            "| Nullwerte:",
            nullwerte_pro_wochentag[wochentag],
        )
        wochentag_ergebnisse.append(
            {
                "wochentag": wochentag,
                "anzahl": len(werte),
                "mittelwert": mean(werte),
                "median": median(werte),
                "nullwerte": nullwerte_pro_wochentag[wochentag],
            }
        )

    return pd.DataFrame(stunden_ergebnisse), pd.DataFrame(wochentag_ergebnisse)


def speichere_csv(df, dateiname):
    pfad = OUTPUT_DIR / dateiname
    df.to_csv(pfad, index=False, encoding="utf-8")
    print("Gespeichert:", pfad)


def speichere_liniendiagramm(df, x, y, dateiname, titel, xlabel, ylabel):
    plt.figure(figsize=(10, 6))
    plt.plot(df[x], df[y], marker="o", color="darkorange")
    plt.title(titel)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    pfad = OUTPUT_DIR / dateiname
    plt.savefig(pfad, dpi=300, bbox_inches="tight")
    plt.close()
    print("Gespeichert:", pfad)


def speichere_balkendiagramm(df, x, y, dateiname, titel, xlabel, ylabel):
    plt.figure(figsize=(11, 6))
    plt.bar(df[x].astype(str), df[y], color="seagreen")
    plt.title(titel)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    pfad = OUTPUT_DIR / dateiname
    plt.savefig(pfad, dpi=300, bbox_inches="tight")
    plt.close()
    print("Gespeichert:", pfad)


if __name__ == "__main__":
    sensordaten = lade_daten()
    stunden_df, wochentage_df = analysiere_stunden_und_wochentage(sensordaten)

    speichere_csv(stunden_df, "eda_stunden.csv")
    speichere_csv(wochentage_df, "eda_wochentage.csv")

    speichere_liniendiagramm(
        stunden_df,
        x="stunde",
        y="mittelwert",
        dateiname="eda_besucher_nach_stunde.png",
        titel="Durchschnittliche Besucherzahl nach lokaler Stunde",
        xlabel="Stunde",
        ylabel="Durchschnittliche Besucherzahl",
    )

    speichere_balkendiagramm(
        wochentage_df,
        x="wochentag",
        y="mittelwert",
        dateiname="eda_besucher_nach_wochentag.png",
        titel="Durchschnittliche Besucherzahl nach Wochentag",
        xlabel="Wochentag",
        ylabel="Durchschnittliche Besucherzahl",
    )