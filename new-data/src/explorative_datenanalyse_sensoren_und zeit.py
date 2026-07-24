"""
Dieses Modul analysiert die Sensorstruktur und die zeitliche Verteilung der Rohdaten.

Enthalten sind:
- Anzahl der Sensoren und Rohdatensätze,
- Rohdaten pro Sensor,
- zeitliche Ausdehnung der Daten,
- Mehrfachmessungen pro Sensor und Zeitstempel,
- fehlende Stunden im globalen Beobachtungszeitraum,
- größte interne Zeitlücken pro Sensor.

Die Ergebnisse werden als CSV und PNG im Output-Ordner gespeichert.
"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from daten_einlesen import lade_daten


OUTPUT_DIR = Path("../plots")
OUTPUT_DIR.mkdir(exist_ok=True)


def konvertiere_zeitstempel(timestamp_text):
    """
    Wandelt einen UTC-Zeitstempel aus den Rohdaten in ein timezone-aware datetime-Objekt um.
    """
    zeitstempel = datetime.strptime(timestamp_text, "%Y-%m-%dT%H:%M:%S.000Z")
    return zeitstempel.replace(tzinfo=timezone.utc)


def analysiere_sensoren(sensordaten):
    """
    Zählt die Rohdatensätze pro Sensor.
    """
    sensornamen = [datensatz["name"] for datensatz in sensordaten]
    counter = Counter(sensornamen)

    df = pd.DataFrame(
        {
            "sensor": list(counter.keys()),
            "rohdaten": list(counter.values()),
        }
    ).sort_values(by="sensor").reset_index(drop=True)

    print("\n" + "=" * 80)
    print("1. SENSORANALYSE")
    print("=" * 80)
    print("Gesamtzahl der Rohdatensätze:", len(sensordaten))
    print("Anzahl verschiedener Sensoren:", len(df))
    print(df.to_string(index=False))

    return df


def analysiere_zeit(sensordaten):
    """
    Analysiert die zeitliche Struktur aller Sensoren.

    Für jeden Sensor werden Rohdaten, eindeutige Zeitstempel,
    Mehrfachmessungen, fehlende Stunden und die größte interne Lücke bestimmt.
    """
    print("\n" + "=" * 80)
    print("2. ZEITANALYSE ALLER SENSOREN")
    print("=" * 80)

    zeitstempel_pro_sensor = defaultdict(list)
    alle_zeitstempel = []

    for datensatz in sensordaten:
        sensorname = datensatz["name"]
        zeitstempel = konvertiere_zeitstempel(datensatz["timestamp"])
        zeitstempel_pro_sensor[sensorname].append(zeitstempel)
        alle_zeitstempel.append(zeitstempel)

    globaler_start = min(alle_zeitstempel)
    globales_ende = max(alle_zeitstempel)

    erwartete_globale_zeitstempel = set()
    aktueller = globaler_start
    while aktueller <= globales_ende:
        erwartete_globale_zeitstempel.add(aktueller)
        aktueller += timedelta(hours=1)

    ergebnisse = []

    for sensorname in sorted(zeitstempel_pro_sensor):
        zeitpunkte = sorted(zeitstempel_pro_sensor[sensorname])
        rohdaten = len(zeitpunkte)
        eindeutige = sorted(set(zeitpunkte))

        if not eindeutige:
            continue

        mehrfachmessungen = rohdaten - len(eindeutige)
        fehlende_stunden = len(erwartete_globale_zeitstempel - set(eindeutige))

        groesste_luecke = timedelta(0)
        for i in range(1, len(eindeutige)):
            abstand = eindeutige[i] - eindeutige[i - 1]
            if abstand > groesste_luecke:
                groesste_luecke = abstand

        ergebnisse.append(
            {
                "sensor": sensorname,
                "rohdaten": rohdaten,
                "zeitpunkte": len(eindeutige),
                "mehrfachmessungen": mehrfachmessungen,
                "fehlende_stunden": fehlende_stunden,
                "groesste_luecke_stunden": groesste_luecke.total_seconds() / 3600,
                "erste_messung": eindeutige[0],
                "letzte_messung": eindeutige[-1],
            }
        )

    df = pd.DataFrame(ergebnisse).sort_values(
        by=["fehlende_stunden", "mehrfachmessungen", "rohdaten"],
        ascending=False,
    ).reset_index(drop=True)

    print("Globaler Beginn der Rohdaten:", globaler_start)
    print("Globales Ende der Rohdaten:", globales_ende)
    print("\nDetaillierte Zeitanalyse:")
    print(
        df[
            [
                "sensor",
                "rohdaten",
                "zeitpunkte",
                "mehrfachmessungen",
                "fehlende_stunden",
                "groesste_luecke_stunden",
                "erste_messung",
                "letzte_messung",
            ]
        ].to_string(index=False)
    )

    return df


def speichere_csv(df, dateiname):
    pfad = OUTPUT_DIR / dateiname
    df.to_csv(pfad, index=False, encoding="utf-8")
    print("Gespeichert:", pfad)


def speichere_balkendiagramm(df, x, y, dateiname, titel, xlabel, ylabel):
    plt.figure(figsize=(12, 6))
    plt.bar(df[x].astype(str), df[y], color="steelblue")
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
    sensoren_df = analysiere_sensoren(sensordaten)
    zeit_df = analysiere_zeit(sensordaten)

    speichere_csv(sensoren_df, "eda_sensoren.csv")
    speichere_csv(zeit_df, "eda_zeit.csv")

    speichere_balkendiagramm(
        sensoren_df,
        x="sensor",
        y="rohdaten",
        dateiname="eda_rohdaten_pro_sensor.png",
        titel="Rohdatensätze pro Sensor",
        xlabel="Sensor",
        ylabel="Rohdatensätze",
    )

    speichere_balkendiagramm(
        zeit_df,
        x="sensor",
        y="fehlende_stunden",
        dateiname="eda_fehlende_stunden_pro_sensor.png",
        titel="Fehlende Stunden pro Sensor",
        xlabel="Sensor",
        ylabel="Fehlende Stunden",
    )

    speichere_balkendiagramm(
        zeit_df,
        x="sensor",
        y="groesste_luecke_stunden",
        dateiname="eda_groesste_luecke_pro_sensor.png",
        titel="Größte interne Zeitlücke pro Sensor",
        xlabel="Sensor",
        ylabel="Stunden",
    )