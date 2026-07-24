"""
Dieses Modul analysiert Mehrfachmessungen pro Sensor und Zeitstempel,
zeigt ein Beispiel einer Mehrfachmessung an, untersucht die Spannweite
der Messwerte und aggregiert anschließend zu einer stündlichen Messung.
"""

import pandas as pd


def mehrfachmessungen_pruefen(df):
    print("\n" + "=" * 70)
    print("6. MEHRFACHMESSUNGEN PRÜFEN")
    print("=" * 70)

    anzahl_messungen = (
        df.groupby(["name", "timestamp"])
        .size()
        .reset_index(name="anzahl_messungen")
    )

    mehrfachmessungen = anzahl_messungen[
        anzahl_messungen["anzahl_messungen"] > 1
    ].copy()

    print("Anzahl Sensor-Zeitpunkt-Kombinationen mit mehreren Messungen:", len(mehrfachmessungen))

    if len(mehrfachmessungen) > 0:
        print("Erste zehn Mehrfachmessungen:")
        print(mehrfachmessungen.head(10))
        print("Verteilung der Messungsanzahl:")
        print(mehrfachmessungen["anzahl_messungen"].value_counts().sort_index())

    return df, mehrfachmessungen


def beispiel_mehrfachmessung_anzeigen(df, mehrfachmessungen):
    print("\n" + "=" * 70)
    print("7. BEISPIEL EINER MEHRFACHMESSUNG")
    print("=" * 70)

    if mehrfachmessungen.empty:
        print("Es existieren keine Mehrfachmessungen.")
        return

    beispiele_karlstrasse = mehrfachmessungen[
        mehrfachmessungen["name"] == "Karlstraße 15"
    ]

    if not beispiele_karlstrasse.empty:
        beispiel = beispiele_karlstrasse.iloc[0]
    else:
        beispiel = mehrfachmessungen.iloc[0]

    sensorname = beispiel["name"]
    zeitpunkt = beispiel["timestamp"]

    passende_zeilen = df[
        (df["name"] == sensorname) & (df["timestamp"] == zeitpunkt)
    ]

    print("Sensor:")
    print(sensorname)
    print("Zeitstempel:")
    print(zeitpunkt)
    print("Gefundene Zeilen:")
    print(
        passende_zeilen[
            ["name", "timestamp", "visitors", "avgDuration", "locationId", "lat", "lon"]
        ].to_string(index=False)
    )


def mehrfachmessungen_analysieren(df):
    print("\n" + "=" * 70)
    print("8. MEHRFACHMESSUNGEN ANALYSIEREN")
    print("=" * 70)

    analyse = (
        df.groupby(["name", "timestamp"])
        .agg(
            anzahl_messungen=("visitors", "size"),
            visitors_min=("visitors", "min"),
            visitors_max=("visitors", "max"),
            visitors_mittelwert=("visitors", "mean"),
            visitors_summe=("visitors", "sum"),
            duration_min=("avgDuration", "min"),
            duration_max=("avgDuration", "max"),
            duration_mittelwert=("avgDuration", "mean"),
        )
        .reset_index()
    )

    mehrfachmessungen = analyse[analyse["anzahl_messungen"] > 1].copy()
    mehrfachmessungen["visitors_spannweite"] = (
        mehrfachmessungen["visitors_max"] - mehrfachmessungen["visitors_min"]
    )
    mehrfachmessungen["duration_spannweite"] = (
        mehrfachmessungen["duration_max"] - mehrfachmessungen["duration_min"]
    )

    print("Erste zehn analysierte Mehrfachmessungen:")
    print(
        mehrfachmessungen[
            [
                "name",
                "timestamp",
                "anzahl_messungen",
                "visitors_min",
                "visitors_max",
                "visitors_mittelwert",
                "visitors_summe",
                "visitors_spannweite",
            ]
        ].head(10).to_string(index=False)
    )

    print("Statistik der Besucher-Spannweite:")
    print(mehrfachmessungen["visitors_spannweite"].describe())

    print("Statistik der Aufenthaltsdauer-Spannweite:")
    print(mehrfachmessungen["duration_spannweite"].describe())

    return mehrfachmessungen


def mehrfachmessungen_aggregieren(df):
    print("\n" + "=" * 70)
    print("9. MEHRFACHMESSUNGEN AGGREGIEREN")
    print("=" * 70)

    anzahl_vorher = len(df)

    df_aggregiert = (
        df.groupby(["name", "timestamp"], as_index=False)
        .agg(
            visitors=("visitors", "median"),
            avgDuration=("avgDuration", "median"),
            locationId=("locationId", "first"),
            lat=("lat", "first"),
            lon=("lon", "first"),
        )
    )

    print("Anzahl Zeilen vor der Aggregation:", anzahl_vorher)
    print("Anzahl Zeilen nach der Aggregation:", len(df_aggregiert))
    print("Zusammengefasste Zeilen:", anzahl_vorher - len(df_aggregiert))
    print("Erste fünf aggregierte Zeilen:")
    print(df_aggregiert.head().to_string(index=False))

    return df_aggregiert


if __name__ == "__main__":
    print("Dieses Modul wird aus der Pipeline aufgerufen.")
