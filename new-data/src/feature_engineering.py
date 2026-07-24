import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

EINGABEDATEI = "../data/bad_nauheim_bereinigt.csv"
AUSGABEDATEI = "../data/bad_nauheim_features.csv"

ANZAHL_ERWARTETE_SENSOREN = 28

df = pd.read_csv(EINGABEDATEI)

ERFORDERLICHE_EINGABESPALTEN = [
    "timestamp",
    "name",
    "visitors",
    "avgDuration",
    "war_fehlend",
    "lat",
    "lon",
]

fehlende_spalten = [
    spalte
    for spalte in ERFORDERLICHE_EINGABESPALTEN
    if spalte not in df.columns
]

if fehlende_spalten:
    raise ValueError(
        f"Folgende erforderliche Spalten fehlen: {fehlende_spalten}"
    )

if df["war_fehlend"].dtype != bool:
    df["war_fehlend"] = (
        df["war_fehlend"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False,
        })
    )

if df["war_fehlend"].isna().any():
    raise ValueError(
        "Die Spalte 'war_fehlend' enthält ungültige Werte."
    )

df["war_fehlend"] = df["war_fehlend"].astype(bool)

# Prüfen, ob die bereinigte Datei wirklich 28 Sensoren enthält
anzahl_sensoren = df["name"].nunique()

if anzahl_sensoren != ANZAHL_ERWARTETE_SENSOREN:
    raise ValueError(
        f"Erwartet wurden {ANZAHL_ERWARTETE_SENSOREN} Sensoren, "
        f"gefunden wurden aber {anzahl_sensoren}."
    )

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

if df["timestamp"].isna().any():
    raise ValueError(
        "Die Eingabedatei enthält ungültige oder fehlende Zeitstempel."
    )

df["stunde"] = df["timestamp"].dt.hour
df["wochentag"] = df["timestamp"].dt.weekday
df["ist_wochenende"] = (df["wochentag"] >= 5).astype(int)

df["stunde_sin"] = np.sin(2 * np.pi * df["stunde"] / 24)
df["stunde_cos"] = np.cos(2 * np.pi * df["stunde"] / 24)

df["wochentag_sin"] = np.sin(2 * np.pi * df["wochentag"] / 7)
df["wochentag_cos"] = np.cos(2 * np.pi * df["wochentag"] / 7)

df["sensor_id"] = pd.factorize(df["name"], sort=True)[0]

ERFORDERLICHE_MODELLSPALTEN = [
    "timestamp",
    "name",
    "sensor_id",
    "visitors",
    "avgDuration",
    "war_fehlend",
    "stunde_sin",
    "stunde_cos",
    "wochentag_sin",
    "wochentag_cos",
]

fehlende_modellspalten = [
    spalte
    for spalte in ERFORDERLICHE_MODELLSPALTEN
    if spalte not in df.columns
]

if fehlende_modellspalten:
    raise ValueError(
        f"Folgende Modellspalten fehlen: {fehlende_modellspalten}"
    )

df = df.drop(columns=["locationId"], errors="ignore")

df = df.sort_values(by=["sensor_id", "timestamp"]).reset_index(drop=True)

print("Fehlende Werte pro Spalte:")
print(df.isna().sum())

print()
print("Anzahl ursprünglich fehlender Werte:")
print(df["war_fehlend"].sum())

print()
print("Davon weiterhin fehlende Besucherwerte:")
print(df["visitors"].isna().sum())

fehlende_modellwerte = df[["visitors", "avgDuration"]].isna().any(axis=1).sum()

print()
print("Zeilen mit fehlenden Modellwerten:", fehlende_modellwerte)
print(
    "Diese Zeilen bleiben erhalten. "
    "Die fehlenden Modellwerte werden später im Windowing "
    "mit Trainingsstatistiken aufgefüllt. "
    "Fenster mit zu vielen ursprünglich fehlenden Stunden "
    "werden verworfen."
)

# Sensoren mit fehlenden Koordinaten
sensor_coords = (
    df.groupby("name")[["lat", "lon"]]
    .agg(lambda s: s.isna().all())
    .reset_index()
)

ohne_koordinaten = sensor_coords[
    sensor_coords["lat"] & sensor_coords["lon"]
]["name"].tolist()

print("\nSensoren ohne lat/lon:", ohne_koordinaten)
print("Anzahl:", len(ohne_koordinaten))


df.to_csv(AUSGABEDATEI, index=False, encoding="utf-8")

print()
print("Feature Engineering erfolgreich abgeschlossen.")
print("Anzahl der Zeilen:", len(df))
print("Anzahl der Sensoren:", df["sensor_id"].nunique())
print("Gespeicherte Datei:", AUSGABEDATEI)
print("Spalten:", df.columns.tolist())

print("\nZuordnung der Sensoren:")
print(df[["name", "sensor_id"]].drop_duplicates().sort_values("sensor_id").to_string(index=False))

print("\nErste 5 Zeilen")
print(df.head().to_string())