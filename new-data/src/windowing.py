"""
Erstellt gemeinsame 24-Stunden-Inputfenster für LSTM und Autoencoder.
Das LSTM verwendet die unmittelbar folgende 25. Stunde als Forecast-Ziel.
Der Autoencoder rekonstruiert dagegen die gemeinsamen 24 Inputstunden.
Damit sind Fensterauswahl, Zeitpunkte, Features und Vorverarbeitung identisch,
während sich die modelltypischen Zielwerte unterscheiden.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

EINGABEDATEI = "../data/bad_nauheim_features.csv"

ANZAHL_ERWARTETE_SENSOREN = 28
FENSTERGROESSE = 24
SCHRITTWEITE = 1
# Maximal vier der 24 Inputstunden dürfen ursprünglich gefehlt haben. Das entspricht 16,7 Prozent des Fensters.
MAX_FEHLENDE_INPUT_STUNDEN = 4
TRAINING_START = pd.Timestamp("2025-06-30 01:00:00", tz="UTC")
TRAINING_ENDE = pd.Timestamp("2025-07-04 00:00:00", tz="UTC")
VALIDIERUNG_START = pd.Timestamp("2025-07-04 00:00:00", tz="UTC")
VALIDIERUNG_ENDE = pd.Timestamp("2025-07-06 00:00:00", tz="UTC")
TEST_START = pd.Timestamp("2025-07-06 00:00:00", tz="UTC")
TEST_ENDE = pd.Timestamp("2025-07-08 00:00:00", tz="UTC")
FEATURE_SPALTEN = ["visitors", "avgDuration", "ist_wochenende", "stunde_sin", "stunde_cos", "wochentag_sin", "wochentag_cos",]
# Nur visitors und avgDuration werden mit StandardScaler skaliert.
NUMERISCHE_FEATURE_INDIZES = [0, 1]
# Nur diese Spalten können nach großen Lücken noch echte NaN-Werte enthalten.
IMPUTATIONS_SPALTEN = ["visitors", "avgDuration"]

def konvertiere_bool_spalte(serie):
    """Konvertiert boolesche Werte robust, auch wenn CSV Strings enthält."""
    if pd.api.types.is_bool_dtype(serie):
        return serie.fillna(False).astype(bool)
    wahr_werte = {"true", "1", "ja", "yes", "wahr"}
    return (serie.fillna(False).astype(str).str.strip().str.lower().isin(wahr_werte))

def lade_daten(dateipfad):
    df = pd.read_csv(dateipfad)
    erforderliche_spalten = ["timestamp", "name", "sensor_id", "war_fehlend", *FEATURE_SPALTEN,]
    fehlende_spalten = [
        spalte
        for spalte in erforderliche_spalten
        if spalte not in df.columns
]

    if fehlende_spalten:
        raise ValueError(f"Folgende erforderliche Spalten fehlen: {fehlende_spalten}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce",)

    if df["timestamp"].isna().any():
        raise ValueError("Der Feature-Datensatz enthält ungültige oder fehlende Zeitstempel.")
    df["war_fehlend"] = konvertiere_bool_spalte(df["war_fehlend"])
    df = df.sort_values(by=["sensor_id", "timestamp"]).reset_index(drop=True)
    return df


def pruefe_eingabedaten(df):
    anzahl_sensoren = df["sensor_id"].nunique()

    if anzahl_sensoren != ANZAHL_ERWARTETE_SENSOREN:
        raise ValueError(
            f"Erwartet wurden {ANZAHL_ERWARTETE_SENSOREN} Sensoren, "
            f"gefunden wurden aber {anzahl_sensoren}."
        )
    doppelte_sensor_zeitpunkte = df.duplicated(subset=["sensor_id", "timestamp"]).sum()

    if doppelte_sensor_zeitpunkte > 0:
        raise ValueError(
            "Im Feature-Datensatz existieren noch "
            f"{doppelte_sensor_zeitpunkte} doppelte "
            "Sensor-Zeitpunkt-Kombinationen."
        )

    print("Windowing-Daten erfolgreich eingelesen.")
    print("Anzahl der Zeilen:", len(df))
    print("Anzahl der Sensoren:", anzahl_sensoren)
    print("Erster Zeitstempel:", df["timestamp"].min())
    print("Letzter Zeitstempel:", df["timestamp"].max())
    print("\nNaN-Werte vor der split-sicheren Auffüllung:")
    print(df[FEATURE_SPALTEN].isna().sum())
    print("Ursprünglich fehlende Zeitpunkte:", int(df["war_fehlend"].sum()))

def waehle_zeitraum(df, start, ende):
    maske = ((df["timestamp"] >= start)& (df["timestamp"] < ende))
    return df.loc[maske].copy()

def teile_nach_festen_zeitraeumen(df):
    df_training = waehle_zeitraum(df, TRAINING_START, TRAINING_ENDE)
    df_validierung = waehle_zeitraum(df, VALIDIERUNG_START, VALIDIERUNG_ENDE)
    df_test = waehle_zeitraum(df, TEST_START, TEST_ENDE)
    pruefe_zeitliche_trennung(df_training, df_validierung, df_test,)
    return df_training, df_validierung, df_test

def pruefe_zeitliche_trennung(df_training, df_validierung, df_test):
    if df_training.empty: raise ValueError("Der Trainingsdatensatz ist leer.")
    if df_validierung.empty: raise ValueError("Der Validierungsdatensatz ist leer.")
    if df_test.empty: raise ValueError("Der Testdatensatz ist leer.")
    if df_training["timestamp"].max() >= VALIDIERUNG_START: raise ValueError("Training und Validierung überschneiden sich.")
    if df_validierung["timestamp"].min() < VALIDIERUNG_START: raise ValueError("Die Validierung beginnt zu früh.")
    if df_validierung["timestamp"].max() >= TEST_START: raise ValueError("Validierung und Test überschneiden sich.")
    if df_test["timestamp"].min() < TEST_START: raise ValueError("Der Testdatensatz beginnt zu früh.")

def ergaenze_zeitfeatures(df):
    """Berechnet Zeitfeatures erneut, falls durch Reindexing Zeilen entstanden."""
    stunde = df["timestamp"].dt.hour
    wochentag = df["timestamp"].dt.dayofweek
    df["ist_wochenende"] = (wochentag >= 5).astype(np.float32)
    df["stunde_sin"] = np.sin(2 * np.pi * stunde / 24).astype(np.float32)
    df["stunde_cos"] = np.cos(2 * np.pi * stunde / 24).astype(np.float32)
    df["wochentag_sin"] = np.sin(2 * np.pi * wochentag / 7).astype(np.float32)
    df["wochentag_cos"] = np.cos(2 * np.pi * wochentag / 7).astype(np.float32)
    return df

def vervollstaendige_stundenraster(df_split, start, ende):
    """
    Erzeugt pro Sensor ein vollständiges Stundenraster innerhalb des Splits.
    Neu eingefügte Stunden werden mit war_fehlend=True markiert. Dadurch können
    große Lücken später anhand der Anzahl fehlender Inputstunden erkannt werden.
    """
    vollstaendiger_index = pd.date_range(start=start,end=ende - pd.Timedelta(hours=1),freq="h",tz="UTC",)
    teile = []
    sensor_stammdaten = (df_split[["sensor_id", "name"]].drop_duplicates(subset=["sensor_id"]).sort_values("sensor_id"))
    for _, stammdaten in sensor_stammdaten.iterrows():
        sensor_id = stammdaten["sensor_id"]
        sensorname = stammdaten["name"]
        sensor_df = (
            df_split.loc[df_split["sensor_id"] == sensor_id]
            .sort_values("timestamp")
            .set_index("timestamp")
            .reindex(vollstaendiger_index)
            .rename_axis("timestamp")
            .reset_index()
        )
        neu_eingefuegt = sensor_df["sensor_id"].isna()
        sensor_df["sensor_id"] = sensor_id
        sensor_df["name"] = sensorname
        sensor_df["war_fehlend"] = konvertiere_bool_spalte(sensor_df["war_fehlend"]) | neu_eingefuegt
        sensor_df = ergaenze_zeitfeatures(sensor_df)
        teile.append(sensor_df)

    if not teile:
        return df_split.copy()
    return (pd.concat(teile, ignore_index=True).sort_values(["sensor_id", "timestamp"]).reset_index(drop=True))

def analysiere_fehlende_stunden_pro_fenster(df_split, datensatz_name):
    anzahl_fehlend_pro_fenster = []
    for _, sensor_df in df_split.groupby("sensor_id"):
        sensor_df = sensor_df.sort_values("timestamp").reset_index(drop=True)
        for start_index in range(0,len(sensor_df) - FENSTERGROESSE,SCHRITTWEITE,):
            ende_index = start_index + FENSTERGROESSE
            fenster = sensor_df.iloc[start_index:ende_index]
            anzahl_fehlend = int(fenster["war_fehlend"].fillna(False).astype(bool).sum())
            anzahl_fehlend_pro_fenster.append(anzahl_fehlend)
    serie = pd.Series(anzahl_fehlend_pro_fenster)
    print("=" * 70)
    print("Fehlende Inputstunden pro Fenster:", datensatz_name)
    print("=" * 70)
    print(serie.describe())
    print("nAnteil Fenster mit höchstens 4 fehlenden Stunden:")
    print((serie <= 4).mean())
    print("Anteil Fenster mit höchstens 6 fehlenden Stunden:")
    print((serie <= 6).mean())
    print("Anteil Fenster mit höchstens 8 fehlenden Stunden:")
    print((serie <= 8).mean())
    print("Anteil Fenster mit höchstens 12 fehlenden Stunden:")
    print((serie <= 12).mean())

def analysiere_datenqualitaet_pro_tag(df):
    """
    Analysiert die Datenqualität für jeden Kalendertag über alle Sensoren.
    Die Analyse nutzt ein vollständiges Stundenraster. Dadurch werden auch
    Stunden berücksichtigt, für die im ursprünglichen Datensatz keine Zeile
    vorhanden war. Solche Stunden sind mit war_fehlend=True markiert.
    """
    analyse_df = df.copy()
    analyse_df["datum"] = analyse_df["timestamp"].dt.date
    tagesstatistik = (analyse_df.groupby("datum", as_index=False).agg(
            anzahl_zeilen=("timestamp", "size"),
            anzahl_sensoren=("sensor_id", "nunique"),
            fehlende_zeitpunkte=("war_fehlend", "sum"),
        )
    )

    tagesstatistik["fehlanteil"] = (tagesstatistik["fehlende_zeitpunkte"] / tagesstatistik["anzahl_zeilen"])
    tagesstatistik["fehlanteil_prozent"] = (tagesstatistik["fehlanteil"] * 100).round(2)

    def bewerte_tag(fehlanteil):
        if fehlanteil <= 0.15: return "gut"
        if fehlanteil <= 0.25: return "mittel"
        return "schlecht"
    tagesstatistik["bewertung"] = (tagesstatistik["fehlanteil"].apply(bewerte_tag) )
    print("=" * 95)
    print("DATENQUALITÄT PRO TAG")
    print("=" * 95)
    print(tagesstatistik[["datum","anzahl_zeilen","anzahl_sensoren","fehlende_zeitpunkte","fehlanteil_prozent","bewertung",]].to_string(index=False))
    return tagesstatistik

def erstelle_vollstaendigen_analyse_datensatz(df):
    """
    Erstellt ein vollständiges Stundenraster über den gesamten Datensatz.
    Diese Kopie wird ausschließlich für die Qualitätsanalyse verwendet.
    Die eigentlichen Trainings-, Validierungs- und Testdaten bleiben davon
    unverändert.
    """
    gesamt_start = df["timestamp"].min().floor("h")
    gesamt_ende = (df["timestamp"].max().floor("h")+ pd.Timedelta(hours=1))
    return vervollstaendige_stundenraster(df, gesamt_start, gesamt_ende,)

def berechne_imputationswerte(df_training):
    """
    Berechnet Ersatzwerte ausschließlich aus dem Trainingssplit.
    Reihenfolge beim späteren Auffüllen:
    1. Median je Sensor und Stunde
    2. Median je Sensor
    3. globaler Median des Trainingssplits
    """
    train = df_training.copy()
    train["stunde"] = train["timestamp"].dt.hour

    statistiken = {}

    for spalte in IMPUTATIONS_SPALTEN:
        statistiken[spalte] = {
            "sensor_stunde": train.groupby(["sensor_id", "stunde"])[spalte].median(),
            "sensor": train.groupby("sensor_id")[spalte].median(),
            "global": train[spalte].median(),
        }

        if pd.isna(statistiken[spalte]["global"]):
            raise ValueError(f"Für {spalte} konnte kein globaler Trainingsmedian berechnet werden.")

    return statistiken

def fuelle_mit_trainingswerten(df_split, statistiken):
    """Füllt verbleibende NaNs ohne Informationen aus Validierung/Test zu nutzen."""
    df = df_split.copy()
    df["stunde"] = df["timestamp"].dt.hour

    for spalte in IMPUTATIONS_SPALTEN:
        fehlt = df[spalte].isna()

        if fehlt.any():
            schluessel = pd.MultiIndex.from_arrays(
                [df.loc[fehlt, "sensor_id"], df.loc[fehlt, "stunde"],],
                names=["sensor_id", "stunde"],
            )
            ersatz_sensor_stunde = statistiken[spalte]["sensor_stunde"].reindex(schluessel).to_numpy()
            df.loc[fehlt, spalte] = ersatz_sensor_stunde
        fehlt = df[spalte].isna()
        if fehlt.any(): df.loc[fehlt, spalte] = (df.loc[fehlt, "sensor_id"].map(statistiken[spalte]["sensor"]).to_numpy())
        fehlt = df[spalte].isna()
        if fehlt.any(): df.loc[fehlt, spalte] = statistiken[spalte]["global"]
    df = df.drop(columns=["stunde"])

    if df[FEATURE_SPALTEN].isna().any().any():
        fehlende = df[FEATURE_SPALTEN].isna().sum()
        raise ValueError("Nach der split-sicheren Auffüllung existieren noch NaNs:\n" f"{fehlende}")
    return df

def erzeuge_metadaten(sensor_id, sensorname, fenster_df, zielzeile, datensatz_name, anzahl_fehlend,):
    return {
        "sensor_id": sensor_id,
        "sensorname": sensorname,
        "fenster_start": fenster_df["timestamp"].iloc[0],
        "fenster_ende": fenster_df["timestamp"].iloc[-1],
        "zielzeitpunkt": zielzeile["timestamp"],
        "anzahl_war_fehlend": int(anzahl_fehlend),
        "anteil_war_fehlend": float(anzahl_fehlend / FENSTERGROESSE),
        "datensatz": datensatz_name,
    }


def erstelle_zeitfenster(df_split, datensatz_name):
    """
    Erstellt gemeinsame Fenster für Forecasting-Modell und Autoencoder.
    Gemeinsame Regel:
    - 24 Inputstunden
    - Stunde 25 ist das Forecasting-Ziel
    - Zielwert muss eine echte Beobachtung sein
    - Maximal MAX_FEHLENDE_INPUT_STUNDEN im Input
    - Interpolierte/aufgefüllte Inputwerte sind erlaubt
    """
    alle_fenster = []
    alle_zielwerte = []
    alle_beobachtungsmasken = []
    alle_metadaten = []
    verworfen_wegen_zu_viel_fehlend = 0
    verworfen_wegen_fehlendem_ziel = 0
    verworfen_wegen_nan = 0
    verworfen_wegen_zu_wenig_daten = 0
    sensor_statistiken = []

    for sensor_id, sensor_df in df_split.groupby("sensor_id"):
        sensor_df = sensor_df.sort_values("timestamp").reset_index(drop=True)
        sensorname = sensor_df["name"].iloc[0]
        anzahl_zeilen = len(sensor_df)
        theoretische_fenster = max(anzahl_zeilen - FENSTERGROESSE, 0,)
        statistik = {
            "sensor_id": sensor_id,
            "sensorname": sensorname,
            "datensatz": datensatz_name,
            "zeilen": anzahl_zeilen,
            "theoretische_fenster": theoretische_fenster,
            "gueltige_fenster": 0,
            "verworfen_zu_viel_fehlend": 0,
            "verworfen_fehlendes_ziel": 0,
            "verworfen_nan": 0,
        }

        if anzahl_zeilen <= FENSTERGROESSE:
            verworfen_wegen_zu_wenig_daten += 1
            sensor_statistiken.append(statistik)
            continue

        for start_index in range(0, anzahl_zeilen - FENSTERGROESSE, SCHRITTWEITE,):
            ende_index = start_index + FENSTERGROESSE
            fenster_df = sensor_df.iloc[start_index:ende_index]
            zielzeile = sensor_df.iloc[ende_index]
            # True = ursprünglich fehlend, auch wenn inzwischen ein Wert steht.
            war_fehlend_input = (fenster_df["war_fehlend"].fillna(False).astype(bool).to_numpy())
            anzahl_fehlend = int(war_fehlend_input.sum())

            if anzahl_fehlend > MAX_FEHLENDE_INPUT_STUNDEN:
                verworfen_wegen_zu_viel_fehlend += 1
                statistik["verworfen_zu_viel_fehlend"] += 1
                continue

            # Stunde 25 darf keine künstlich ersetzte Messung sein.
            if bool(zielzeile["war_fehlend"]):
                verworfen_wegen_fehlendem_ziel += 1
                statistik["verworfen_fehlendes_ziel"] += 1
                continue

            fenster_array = fenster_df[FEATURE_SPALTEN].to_numpy(dtype=np.float32)
            zielwert = np.float32(zielzeile["visitors"])

            # Sicherheitsprüfung: Nach Imputation sollte das nie eintreten.
            if np.isnan(fenster_array).any() or np.isnan(zielwert):
                verworfen_wegen_nan += 1
                statistik["verworfen_nan"] += 1
                continue
            alle_fenster.append(fenster_array)
            alle_zielwerte.append(zielwert)
            # True = echte Beobachtung; False = ursprünglich fehlend.
            # Diese Maske wird beim Autoencoder für die Fehlerberechnung benötigt.
            alle_beobachtungsmasken.append(~war_fehlend_input)
            alle_metadaten.append(
                erzeuge_metadaten(
                    sensor_id=sensor_id,
                    sensorname=sensorname,
                    fenster_df=fenster_df,
                    zielzeile=zielzeile,
                    datensatz_name=datensatz_name,
                    anzahl_fehlend=anzahl_fehlend,
                )
            )
            statistik["gueltige_fenster"] += 1
        sensor_statistiken.append(statistik)

    if alle_fenster:
        X = np.asarray(alle_fenster, dtype=np.float32)
        y = np.asarray(alle_zielwerte, dtype=np.float32)
        beobachtungsmasken = np.asarray(alle_beobachtungsmasken,dtype=bool,)
    else:
        X = np.empty((0, FENSTERGROESSE, len(FEATURE_SPALTEN)),dtype=np.float32,)
        y = np.empty((0,), dtype=np.float32)
        beobachtungsmasken = np.empty((0, FENSTERGROESSE), dtype=bool,)

    return (X, y, beobachtungsmasken, pd.DataFrame(alle_metadaten), pd.DataFrame(sensor_statistiken),
        {
            "verworfen_zu_viel_fehlend": verworfen_wegen_zu_viel_fehlend,
            "verworfen_fehlendes_ziel": verworfen_wegen_fehlendem_ziel,
            "verworfen_nan": verworfen_wegen_nan,
            "sensoren_zu_wenig_daten": verworfen_wegen_zu_wenig_daten,
        },
    )

def normalisiere_daten(X_train, X_validierung, X_test, y_train, y_validierung, y_test,):
    if len(X_train) == 0: raise ValueError("Training enthält keine gültigen Fenster.")
    if len(X_validierung) == 0: raise ValueError("Validierung enthält keine gültigen Fenster.")
    if len(X_test) == 0: raise ValueError("Test enthält keine gültigen Fenster.")
    X_train_skaliert = X_train.copy()
    X_validierung_skaliert = X_validierung.copy()
    X_test_skaliert = X_test.copy()
    feature_scaler = StandardScaler()
    train_numerisch = X_train[:, :, NUMERISCHE_FEATURE_INDIZES].reshape(-1, len(NUMERISCHE_FEATURE_INDIZES),)
    feature_scaler.fit(train_numerisch)
    for original, skaliert in [
        (X_train, X_train_skaliert),
        (X_validierung, X_validierung_skaliert),
        (X_test, X_test_skaliert),
    ]:
        numerisch = original[:, :, NUMERISCHE_FEATURE_INDIZES].reshape(-1,len(NUMERISCHE_FEATURE_INDIZES),)
        numerisch_skaliert = feature_scaler.transform(numerisch)
        skaliert[:, :, NUMERISCHE_FEATURE_INDIZES] = (
            numerisch_skaliert.reshape(original.shape[0],original.shape[1],len(NUMERISCHE_FEATURE_INDIZES), )
        )

    zielwert_scaler = StandardScaler()
    zielwert_scaler.fit(y_train.reshape(-1, 1))
    y_train_skaliert = zielwert_scaler.transform(y_train.reshape(-1, 1)).reshape(-1)
    y_validierung_skaliert = zielwert_scaler.transform(y_validierung.reshape(-1, 1)).reshape(-1)
    y_test_skaliert = zielwert_scaler.transform(y_test.reshape(-1, 1)).reshape(-1)

    return (
        X_train_skaliert.astype(np.float32),
        X_validierung_skaliert.astype(np.float32),
        X_test_skaliert.astype(np.float32),
        y_train_skaliert.astype(np.float32),
        y_validierung_skaliert.astype(np.float32),
        y_test_skaliert.astype(np.float32),
        feature_scaler,
        zielwert_scaler,
    )

def bereite_autoencoder_daten_vor(X_train_skaliert, X_validierung_skaliert, X_test_skaliert,):
    """Autoencoder rekonstruiert dieselben 24 Inputstunden."""
    return (X_train_skaliert.copy(), X_train_skaliert.copy(), X_validierung_skaliert.copy(), X_validierung_skaliert.copy(),
            X_test_skaliert.copy(), X_test_skaliert.copy(),)

def zeige_split_status(name, df):
    print("-" * 70)
    print(name)
    print("-" * 70)
    print("Zeilen:", len(df))
    print("Sensoren:", df["sensor_id"].nunique())
    print("Beginn:", df["timestamp"].min())
    print("Ende:", df["timestamp"].max())
    print("war_fehlend=True:", int(df["war_fehlend"].sum()))
    print("NaNs:")
    print(df[FEATURE_SPALTEN].isna().sum())

def zeige_fenster_status(name, X, y, masken, metadaten, statistik, gruende):
    print("=" * 80)
    print(name)
    print("=" * 80)
    print("X:", X.shape)
    print("y:", y.shape)
    print("Beobachtungsmasken:", masken.shape)
    print("Metadaten:", len(metadaten))
    print("Verwerfungsgründe:", gruende)

    if not statistik.empty:
        print("\nFensterstatistik pro Sensor:")
        print(statistik.to_string(index=False))

    if len(X) > 0:
        print("\nMittlerer Anteil ursprünglich fehlender Inputstunden:",metadaten["anteil_war_fehlend"].mean(),)
        print("Anteil echter Autoencoder-Zielpositionen:", masken.mean(),)

def pruefe_fenstergrenzen(metadaten_train, metadaten_validierung, metadaten_test,):
    pruefungen = [
        (metadaten_train, TRAINING_START, TRAINING_ENDE, "Training"),
        (metadaten_validierung, VALIDIERUNG_START, VALIDIERUNG_ENDE, "Validierung",),
        (metadaten_test, TEST_START, TEST_ENDE, "Test"),
    ]

    for metadaten, start, ende, name in pruefungen:
        if metadaten.empty: continue
        if metadaten["fenster_start"].min() < start: raise ValueError(f"{name}: Ein Fenster beginnt vor der Split-Grenze.")
        if metadaten["zielzeitpunkt"].max() >= ende: raise ValueError(f"{name}: Ein Ziel liegt außerhalb des Splits.")
    print("Prüfung erfolgreich: Kein Fenster überschreitet eine Split-Grenze.")

def hauptprogramm():
    df = lade_daten(EINGABEDATEI)
    pruefe_eingabedaten(df)
    df_analyse = erstelle_vollstaendigen_analyse_datensatz(df)
    tagesstatistik = analysiere_datenqualitaet_pro_tag(df_analyse)
    df_training, df_validierung, df_test = teile_nach_festen_zeitraeumen(df)
    # Vollständige Stundenraster erzeugen. Fehlende Stunden werden markiert,
    # aber noch nicht mit Informationen aus Validierung/Test aufgefüllt.
    df_training = vervollstaendige_stundenraster(df_training, TRAINING_START, TRAINING_ENDE,)
    df_validierung = vervollstaendige_stundenraster(df_validierung, VALIDIERUNG_START, VALIDIERUNG_ENDE,)
    df_test = vervollstaendige_stundenraster(df_test, TEST_START, TEST_ENDE,)
    analysiere_fehlende_stunden_pro_fenster(df_training,"Training",)
    analysiere_fehlende_stunden_pro_fenster(df_validierung,"Validierung",)
    analysiere_fehlende_stunden_pro_fenster(df_test,"Test",)
    # Nur Training bestimmt die Ersatzwerte. Dadurch entsteht kein Leakage.
    imputationswerte = berechne_imputationswerte(df_training)
    df_training = fuelle_mit_trainingswerten(df_training, imputationswerte,)
    df_validierung = fuelle_mit_trainingswerten(df_validierung, imputationswerte,)
    df_test = fuelle_mit_trainingswerten(df_test, imputationswerte,)
    zeige_split_status("TRAINING VOR WINDOWING", df_training)
    zeige_split_status("VALIDIERUNG VOR WINDOWING", df_validierung)
    zeige_split_status("TEST VOR WINDOWING", df_test)
    (X_train, y_train, masken_train, metadaten_train, statistiken_train, gruende_train,) = erstelle_zeitfenster(df_training, "Training")

    (X_validierung,y_validierung,masken_validierung,metadaten_validierung,statistiken_validierung,gruende_validierung,
    ) = erstelle_zeitfenster(df_validierung, "Validierung")

    (X_test, y_test, masken_test, metadaten_test, statistiken_test, gruende_test,) = erstelle_zeitfenster(df_test, "Test")

    pruefe_fenstergrenzen(metadaten_train, metadaten_validierung, metadaten_test,)

    zeige_fenster_status("TRAINING NACH WINDOWING", X_train, y_train, masken_train, metadaten_train, statistiken_train, gruende_train,)
    zeige_fenster_status(
        "VALIDIERUNG NACH WINDOWING",
        X_validierung,
        y_validierung,
        masken_validierung,
        metadaten_validierung,
        statistiken_validierung,
        gruende_validierung,
    )
    zeige_fenster_status("TEST NACH WINDOWING", X_test, y_test, masken_test, metadaten_test, statistiken_test, gruende_test,)

    if (len(X_train) == 0 or len(X_validierung) == 0 or len(X_test) == 0):
        print("=" * 80)
        print("WINDOWING NOCH NICHT MODELLBEREIT")
        print("=" * 80)
        print(
            "Mindestens ein Split enthält keine gültigen Fenster. "
            "Prüfe die oben ausgegebene Datenqualität pro Tag und passe "
            "anschließend nur die chronologischen Split-Grenzen an."
        )

        return {
            "tagesstatistik": tagesstatistik,
            "X_train": X_train,
            "y_train": y_train,
            "X_validierung": X_validierung,
            "y_validierung": y_validierung,
            "X_test": X_test,
            "y_test": y_test,
            "autoencoder_maske_train": masken_train,
            "autoencoder_maske_validierung": masken_validierung,
            "autoencoder_maske_test": masken_test,
            "metadaten_train": metadaten_train,
            "metadaten_validierung": metadaten_validierung,
            "metadaten_test": metadaten_test,
        }

    (
        X_train_skaliert,
        X_validierung_skaliert,
        X_test_skaliert,
        y_train_skaliert,
        y_validierung_skaliert,
        y_test_skaliert,
        feature_scaler,
        zielwert_scaler,
    ) = normalisiere_daten(X_train,X_validierung,X_test,y_train,y_validierung,y_test,)

    (
        X_train_autoencoder,
        y_train_autoencoder,
        X_validierung_autoencoder,
        y_validierung_autoencoder,
        X_test_autoencoder,
        y_test_autoencoder,
    ) = bereite_autoencoder_daten_vor(X_train_skaliert,X_validierung_skaliert,X_test_skaliert,)

    print("=" * 80)
    print("FERTIGE MODELLDATEN")
    print("=" * 80)
    print("Forecasting X_train:", X_train_skaliert.shape)
    print("Forecasting y_train:", y_train_skaliert.shape)
    print("Autoencoder X_train:", X_train_autoencoder.shape)
    print("Autoencoder y_train:", y_train_autoencoder.shape)
    print("Autoencoder-Maske Training:", masken_train.shape)
    print("\nWindowing erfolgreich abgeschlossen.")

    return {
        "tagesstatistik": tagesstatistik,
        "X_train": X_train,
        "y_train": y_train,
        "X_validierung": X_validierung,
        "y_validierung": y_validierung,
        "X_test": X_test,
        "y_test": y_test,
        "X_train_skaliert": X_train_skaliert,
        "y_train_skaliert": y_train_skaliert,
        "X_validierung_skaliert": X_validierung_skaliert,
        "y_validierung_skaliert": y_validierung_skaliert,
        "X_test_skaliert": X_test_skaliert,
        "y_test_skaliert": y_test_skaliert,
        "X_train_autoencoder": X_train_autoencoder,
        "y_train_autoencoder": y_train_autoencoder,
        "X_validierung_autoencoder": X_validierung_autoencoder,
        "y_validierung_autoencoder": y_validierung_autoencoder,
        "X_test_autoencoder": X_test_autoencoder,
        "y_test_autoencoder": y_test_autoencoder,
        "autoencoder_maske_train": masken_train,
        "autoencoder_maske_validierung": masken_validierung,
        "autoencoder_maske_test": masken_test,
        "metadaten_train": metadaten_train,
        "metadaten_validierung": metadaten_validierung,
        "metadaten_test": metadaten_test,
        "feature_scaler": feature_scaler,
        "zielwert_scaler": zielwert_scaler,
        "imputationswerte": imputationswerte,
    }

if __name__ == "__main__":
    ergebnisse = hauptprogramm()