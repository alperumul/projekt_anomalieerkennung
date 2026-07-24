"""
Dieses Modul analysiert die numerischen Hauptvariablen der Rohdaten.

Enthalten sind:
- Besucherzahlen,
- durchschnittliche Aufenthaltsdauer,
- fehlende Werte,
- negative Werte,
- Nullwerte,
- Minimum, Maximum, Mittelwert, Median, Standardabweichung,
- Quartile und statistische Ausreißer.

Die Ergebnisse werden als CSV und PNG im Output-Ordner gespeichert.
"""

from pathlib import Path
from statistics import mean, median, stdev, quantiles

import matplotlib.pyplot as plt
import pandas as pd

from daten_einlesen import lade_daten


OUTPUT_DIR = Path("../plots")
OUTPUT_DIR.mkdir(exist_ok=True)


def sichere_statistik(werte):
    """
    Berechnet Kennzahlen für numerische Werte.
    """
    if not werte:
        return None

    werte = sorted(werte)
    ergebnis = {
        "anzahl": len(werte),
        "minimum": min(werte),
        "maximum": max(werte),
        "mittelwert": mean(werte),
        "median": median(werte),
        "standardabweichung": stdev(werte) if len(werte) >= 2 else None,
        "q1": None,
        "q3": None,
        "iqr": None,
        "untere_grenze": None,
        "obere_grenze": None,
        "ausreisser_anzahl": 0,
    }

    if len(werte) >= 4:
        q1, _, q3 = quantiles(werte, n=4, method="inclusive")
        iqr = q3 - q1
        untere_grenze = q1 - 1.5 * iqr
        obere_grenze = q3 + 1.5 * iqr
        ausreisser = [w for w in werte if w < untere_grenze or w > obere_grenze]

        ergebnis.update(
            {
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "untere_grenze": untere_grenze,
                "obere_grenze": obere_grenze,
                "ausreisser_anzahl": len(ausreisser),
            }
        )

    return ergebnis


def analysiere_numerisches_merkmalsfeld(sensordaten, spaltenname, titel):
    """
    Analysiert ein numerisches Feld der Rohdaten.
    """
    print("\n" + "=" * 80)
    print(titel)
    print("=" * 80)

    werte = []
    fehlende_werte = 0
    negative_werte = 0
    nullwerte = 0

    for datensatz in sensordaten:
        wert = datensatz.get(spaltenname)
        if wert is None:
            fehlende_werte += 1
            continue
        werte.append(wert)
        if wert < 0:
            negative_werte += 1
        if wert == 0:
            nullwerte += 1

    stats = sichere_statistik(werte)

    print("Anzahl gültiger Werte:", 0 if stats is None else stats["anzahl"])
    print("Fehlende Werte:", fehlende_werte)
    print("Negative Werte:", negative_werte)
    print("Nullwerte:", nullwerte)

    if stats is None:
        return pd.DataFrame()

    print("Minimum:", stats["minimum"])
    print("Maximum:", stats["maximum"])
    print("Mittelwert:", round(stats["mittelwert"], 2))
    print("Median:", stats["median"])
    print(
        "Standardabweichung:",
        None if stats["standardabweichung"] is None else round(stats["standardabweichung"], 2),
    )

    if stats["q1"] is not None:
        print("1. Quartil:", stats["q1"])
        print("3. Quartil:", stats["q3"])
        print("IQR:", stats["iqr"])
        print("Untere Ausreißergrenze:", stats["untere_grenze"])
        print("Obere Ausreißergrenze:", stats["obere_grenze"])
        print("Anzahl statistischer Ausreißer:", stats["ausreisser_anzahl"])

    return pd.DataFrame(
        [
            {
                "merkmal": spaltenname,
                "anzahl_gueltig": stats["anzahl"],
                "fehlende_werte": fehlende_werte,
                "negative_werte": negative_werte,
                "nullwerte": nullwerte,
                "minimum": stats["minimum"],
                "maximum": stats["maximum"],
                "mittelwert": stats["mittelwert"],
                "median": stats["median"],
                "standardabweichung": stats["standardabweichung"],
                "q1": stats["q1"],
                "q3": stats["q3"],
                "iqr": stats["iqr"],
                "ausreisser_anzahl": stats["ausreisser_anzahl"],
            }
        ]
    )


def speichere_csv(df, dateiname):
    pfad = OUTPUT_DIR / dateiname
    df.to_csv(pfad, index=False, encoding="utf-8")
    print("Gespeichert:", pfad)


def speichere_histogramm(werte, spalte, dateiname, titel, xlabel):
    plt.figure(figsize=(10, 6))
    plt.hist(werte, bins=40, color="cornflowerblue", edgecolor="black")
    plt.title(titel)
    plt.xlabel(xlabel)
    plt.ylabel("Häufigkeit")
    plt.tight_layout()
    pfad = OUTPUT_DIR / dateiname
    plt.savefig(pfad, dpi=300, bbox_inches="tight")
    plt.close()
    print("Gespeichert:", pfad)


def speichere_boxplot(werte, dateiname, titel, ylabel):
    plt.figure(figsize=(8, 5))
    plt.boxplot(werte, orientation="vertical")
    plt.title(titel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    pfad = OUTPUT_DIR / dateiname
    plt.savefig(pfad, dpi=300, bbox_inches="tight")
    plt.close()
    print("Gespeichert:", pfad)


if __name__ == "__main__":
    sensordaten = lade_daten()

    visitor_df = analysiere_numerisches_merkmalsfeld(
        sensordaten,
        "visitors",
        "3. ANALYSE DER BESUCHERZAHLEN",
    )

    duration_df = analysiere_numerisches_merkmalsfeld(
        sensordaten,
        "avgDuration",
        "4. ANALYSE DER AUFENTHALTSDAUER",
    )

    speichere_csv(visitor_df, "eda_visitors.csv")
    speichere_csv(duration_df, "eda_avgDuration.csv")

    roh_df = pd.DataFrame(sensordaten)

    visitors = roh_df["visitors"].dropna().tolist()
    durations = roh_df["avgDuration"].dropna().tolist()

    speichere_histogramm(
        visitors,
        "visitors",
        "eda_visitors_histogramm.png",
        "Verteilung der Besucherzahlen",
        "Besucherzahlen",
    )

    speichere_boxplot(
        visitors,
        "eda_visitors_boxplot.png",
        "Boxplot der Besucherzahlen",
        "Besucherzahlen",
    )

    speichere_histogramm(
        durations,
        "avgDuration",
        "eda_avgDuration_histogramm.png",
        "Verteilung der Aufenthaltsdauer",
        "Aufenthaltsdauer",
    )

    speichere_boxplot(
        durations,
        "eda_avgDuration_boxplot.png",
        "Boxplot der Aufenthaltsdauer",
        "Aufenthaltsdauer",
    )