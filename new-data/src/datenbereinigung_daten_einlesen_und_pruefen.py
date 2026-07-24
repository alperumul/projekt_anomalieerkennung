"""
Dieses Modul lädt die Rohdaten, erstellt einen DataFrame,
wählt die relevanten Spalten aus, wandelt Zeitstempel um
und prüft fehlende Werte sowie identische Dubletten.
"""

import pandas as pd
from daten_einlesen import lade_daten

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

RELEVANTE_SPALTEN = [
    "name",
    "timestamp",
    "visitors",
    "avgDuration",
    "locationId",
    "lat",
    "lon",
]


def daten_vorbereiten():
    sensordaten = lade_daten()
    df = pd.DataFrame(sensordaten)
    print("=" * 70)
    print("1. DATEN EINLESEN")
    print("=" * 70)
    print("Anzahl der Rohdatensätze:", len(df))
    print("Anzahl der Spalten:", len(df.columns))
    print("Vorhandene Spalten:", df.columns.tolist())
    return df


def relevante_spalten_auswaehlen(df):
    print("\n" + "=" * 70)
    print("2. RELEVANTE SPALTEN AUSWÄHLEN")
    print("=" * 70)
    df = df[RELEVANTE_SPALTEN].copy()
    print("Ausgewählte Spalten:", df.columns.tolist())
    print("Erste fünf Zeilen:")
    print(df.head())
    return df


def zeitstempel_umwandeln(df):
    print("\n" + "=" * 70)
    print("3. ZEITSTEMPEL UMWANDELN")
    print("=" * 70)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    print("Ungültige oder fehlende Zeitstempel:", df["timestamp"].isna().sum())
    print("Datentyp der Zeitstempel:", df["timestamp"].dtype)
    print("Frühester Zeitstempel:", df["timestamp"].min())
    print("Spätester Zeitstempel:", df["timestamp"].max())
    return df


def fehlende_werte_pruefen(df):
    print("\n" + "=" * 70)
    print("4. FEHLENDE WERTE PRÜFEN")
    print("=" * 70)
    print("Fehlende Werte pro Spalte:")
    print(df.isna().sum())
    return df


def identische_dubletten_pruefen(df):
    print("\n" + "=" * 70)
    print("5. IDENTISCHE DUBLETTEN PRÜFEN")
    print("=" * 70)
    identische_dubletten = df.duplicated()
    anzahl = identische_dubletten.sum()
    print("Anzahl vollständig identischer Zeilen:", anzahl)
    if anzahl > 0:
        print("Beispiele vollständig identischer Zeilen:")
        print(df[identische_dubletten].head(10))
    else:
        print("Es wurden keine vollständig identischen Zeilen gefunden.")
    return df


if __name__ == "__main__":
    df = daten_vorbereiten()
    df = relevante_spalten_auswaehlen(df)
    df = zeitstempel_umwandeln(df)
    df = fehlende_werte_pruefen(df)
    df = identische_dubletten_pruefen(df)