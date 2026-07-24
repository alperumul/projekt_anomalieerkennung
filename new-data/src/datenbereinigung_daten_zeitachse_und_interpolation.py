"""
Dieses Modul analysiert fehlende Stunden und interne Lücken,
vervollständigt anschließend die stündliche Zeitachse pro Sensor
und interpoliert nur kurze interne Lücken.
"""

import pandas as pd


def fehlende_stunden_analysieren(df):
    print("\n" + "=" * 70)
    print("10. FEHLENDE STUNDEN ANALYSIEREN")
    print("=" * 70)

    startzeit = df["timestamp"].min()
    endzeit = df["timestamp"].max()

    vollstaendige_zeitachse = pd.date_range(start=startzeit, end=endzeit, freq="h")
    anzahl_erwartete_stunden = len(vollstaendige_zeitachse)

    ergebnisse = []

    for sensorname, sensor_df in df.groupby("name"):
        vorhandene_zeitstempel = pd.DatetimeIndex(sensor_df["timestamp"].unique())
        fehlende_zeitstempel = vollstaendige_zeitachse.difference(vorhandene_zeitstempel)

        ergebnisse.append(
            {
                "name": sensorname,
                "erwartete_stunden": anzahl_erwartete_stunden,
                "vorhandene_stunden": len(vorhandene_zeitstempel),
                "fehlende_stunden": len(fehlende_zeitstempel),
                "anteil_fehlend_prozent": len(fehlende_zeitstempel) / anzahl_erwartete_stunden * 100,
                "erste_messung": sensor_df["timestamp"].min(),
                "letzte_messung": sensor_df["timestamp"].max(),
            }
        )

    luecken_df = pd.DataFrame(ergebnisse).sort_values(
        by="fehlende_stunden", ascending=False
    ).reset_index(drop=True)

    print(luecken_df.to_string(index=False, formatters={"anteil_fehlend_prozent": lambda wert: f"{wert:.2f}"}))
    return luecken_df


def lueckenlaengen_analysieren(df):
    print("\n" + "=" * 70)
    print("11. INTERNE LÜCKENLÄNGEN ANALYSIEREN")
    print("=" * 70)

    alle_luecken = []

    for sensorname, sensor_df in df.groupby("name"):
        vorhandene_zeiten = (
            sensor_df["timestamp"]
            .drop_duplicates()
            .sort_values()
            .reset_index(drop=True)
        )

        if len(vorhandene_zeiten) < 2:
            continue

        for i in range(1, len(vorhandene_zeiten)):
            vorheriger_zeitpunkt = vorhandene_zeiten.iloc[i - 1]
            aktueller_zeitpunkt = vorhandene_zeiten.iloc[i]
            anzahl_fehlende_stunden = int(
                (aktueller_zeitpunkt - vorheriger_zeitpunkt).total_seconds() / 3600 - 1
            )

            if anzahl_fehlende_stunden > 0:
                alle_luecken.append(
                    {
                        "name": sensorname,
                        "luecke_nach": vorheriger_zeitpunkt,
                        "luecke_vor": aktueller_zeitpunkt,
                        "lueckenlaenge_stunden": anzahl_fehlende_stunden,
                    }
                )

    lueckenlaengen_df = pd.DataFrame(alle_luecken)

    if lueckenlaengen_df.empty:
        print("Es wurden keine internen Lücken gefunden.")
        return lueckenlaengen_df

    print("Anzahl interner Lücken:", len(lueckenlaengen_df))
    print(lueckenlaengen_df["lueckenlaenge_stunden"].value_counts().sort_index().to_string())
    print(lueckenlaengen_df["lueckenlaenge_stunden"].describe())
    print(lueckenlaengen_df.sort_values(by="lueckenlaenge_stunden", ascending=False).head(10).to_string(index=False))

    return lueckenlaengen_df


def zeitachsen_vervollstaendigen(df):
    print("\n" + "=" * 70)
    print("12. ZEITACHSEN VERVOLLSTÄNDIGEN")
    print("=" * 70)

    startzeit = df["timestamp"].min()
    endzeit = df["timestamp"].max()
    vollstaendige_zeitachse = pd.date_range(start=startzeit, end=endzeit, freq="h")

    sensor_daten = []

    for sensorname, sensor_df in df.groupby("name"):
        sensor_df = sensor_df.sort_values(by="timestamp").copy()
        sensor_df = sensor_df.set_index("timestamp")
        sensor_df = sensor_df.reindex(vollstaendige_zeitachse)
        sensor_df.index.name = "timestamp"
        sensor_df["name"] = sensorname

        for col in ["locationId", "lat", "lon"]:
            sensor_df[col] = sensor_df[col].ffill().bfill()

        sensor_df = sensor_df.reset_index()
        sensor_daten.append(sensor_df)

    df_vollstaendig = pd.concat(sensor_daten, ignore_index=True)

    df_vollstaendig["war_fehlend"] = (df_vollstaendig["visitors"].isna())

    print("Anzahl Zeilen vor der Vervollständigung:", len(df))
    print("Anzahl Zeilen nach der Vervollständigung:", len(df_vollstaendig))
    print("Fehlende Besucherwerte nach der Vervollständigung:", df_vollstaendig["visitors"].isna().sum())
    print("Fehlende Aufenthaltsdauer-Werte:", df_vollstaendig["avgDuration"].isna().sum())

    print(
        "Zeilen mit vorhandenen visitors, aber fehlender avgDuration:",
        (
                df_vollstaendig["visitors"].notna()
                & df_vollstaendig["avgDuration"].isna()
        ).sum()
    )

    return df_vollstaendig


def kurze_luecken_interpolieren(df, maximale_luecke=2):
    print("\n" + "=" * 70)
    print("13. KURZE LÜCKEN INTERPOLIEREN")
    print("=" * 70)

    df = df.sort_values(by=["name", "timestamp"]).copy()
    interpolierte_sensoren = []

    for sensorname, sensor_df in df.groupby("name", sort=False):
        sensor_df = sensor_df.copy()
        fehlend = sensor_df["visitors"].isna()
        gruppennummer = fehlend.ne(fehlend.shift()).cumsum()
        gruppengroesse = sensor_df.groupby(gruppennummer)["visitors"].transform("size")

        wert_vorher_vorhanden = sensor_df["visitors"].notna().shift(1).fillna(False)
        wert_nachher_vorhanden = sensor_df["visitors"].notna().shift(-1).fillna(False)

        interne_gruppe = (
            wert_vorher_vorhanden.groupby(gruppennummer).transform("any")
            & wert_nachher_vorhanden.groupby(gruppennummer).transform("any")
        )

        kurze_interne_luecke = fehlend & (gruppengroesse <= maximale_luecke) & interne_gruppe

        visitors_interpoliert = sensor_df["visitors"].interpolate(method="linear", limit_area="inside")
        duration_interpoliert = sensor_df["avgDuration"].interpolate(method="linear", limit_area="inside")

        sensor_df.loc[kurze_interne_luecke, "visitors"] = visitors_interpoliert.loc[kurze_interne_luecke]
        sensor_df.loc[kurze_interne_luecke, "avgDuration"] = duration_interpoliert.loc[kurze_interne_luecke]

        interpolierte_sensoren.append(sensor_df)

    df = pd.concat(interpolierte_sensoren, ignore_index=True)

    print("Fehlende visitors nach der Interpolation:", df["visitors"].isna().sum())
    print("Fehlende avgDuration nach der Interpolation:", df["avgDuration"].isna().sum())

    return df


if __name__ == "__main__":
    print("Dieses Modul wird aus der Pipeline aufgerufen.")