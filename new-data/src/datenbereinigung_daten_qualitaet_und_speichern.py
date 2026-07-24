"""
Dieses Modul bewertet die Datenqualität nach der Interpolation,
entfernt Sensoren mit zu hohem Fehlanteil und speichert den
bereinigten Datensatz als CSV-Datei.
"""
import pandas as pd


def datenqualitaet_pro_sensor_und_tag_analysieren(df):
    print("\n" + "=" * 100)
    print("14. DATENQUALITÄT PRO SENSOR UND TAG")
    print("=" * 100)

    analyse_df = df.copy()
    analyse_df["datum"] = analyse_df["timestamp"].dt.date

    gesamt_start = analyse_df["timestamp"].min()
    gesamt_ende = analyse_df["timestamp"].max()

    ergebnisse = []

    for (sensorname, datum), sensor_tag_df in analyse_df.groupby(
        ["name", "datum"]
    ):
        tagesbeginn = pd.Timestamp(datum, tz="UTC")
        tagesende = tagesbeginn + pd.Timedelta(days=1)

        gueltiger_start = max(tagesbeginn, gesamt_start)
        gueltiges_ende = min(
            tagesende,
            gesamt_ende + pd.Timedelta(hours=1),
        )

        erwartete_stunden = int(
            (gueltiges_ende - gueltiger_start).total_seconds() / 3600
        )

        vorhandene_stunden = int(
            (~sensor_tag_df["war_fehlend"]).sum()
        )

        fehlende_stunden = int(
            sensor_tag_df["war_fehlend"].sum()
        )

        fehlanteil_prozent = (
            fehlende_stunden / erwartete_stunden * 100
            if erwartete_stunden > 0
            else 0
        )

        if fehlanteil_prozent <= 15:
            bewertung = "gut"
        elif fehlanteil_prozent <= 25:
            bewertung = "mittel"
        else:
            bewertung = "schlecht"

        ergebnisse.append(
            {
                "sensorname": sensorname,
                "datum": datum,
                "erwartete_stunden": erwartete_stunden,
                "vorhandene_stunden": vorhandene_stunden,
                "fehlende_stunden": fehlende_stunden,
                "fehlanteil_prozent": round(fehlanteil_prozent, 2),
                "bewertung": bewertung,
            }
        )

    qualitaet_sensor_tag_df = pd.DataFrame(ergebnisse)

    qualitaet_sensor_tag_df = qualitaet_sensor_tag_df.sort_values(
        by=["datum", "fehlanteil_prozent", "sensorname"],
        ascending=[True, False, True],
    ).reset_index(drop=True)

    print(
        qualitaet_sensor_tag_df.to_string(
            index=False,
            formatters={
                "fehlanteil_prozent": lambda wert: f"{wert:.2f}"
            },
        )
    )

    return qualitaet_sensor_tag_df


def datenqualitaet_nach_interpolation_analysieren(df, ausschlussgrenze_prozent=50):
    print("\n" + "=" * 70)
    print("15. DATENQUALITÄT NACH DER INTERPOLATION")
    print("=" * 70)

    ergebnisse = []

    for sensorname, sensor_df in df.groupby("name"):
        anzahl_gesamt = len(sensor_df)
        anzahl_fehlend = sensor_df["visitors"].isna().sum()
        anzahl_urspruenglich_fehlend = sensor_df["war_fehlend"].sum()
        anzahl_interpoliert = (sensor_df["war_fehlend"] & sensor_df["visitors"].notna()).sum()
        anzahl_echte_messungen = (~sensor_df["war_fehlend"]).sum()
        anteil_fehlend_prozent = anzahl_fehlend / anzahl_gesamt * 100
        empfehlung = "ausschließen" if anteil_fehlend_prozent > ausschlussgrenze_prozent else "behalten"

        ergebnisse.append(
            {
                "name": sensorname,
                "gesamt_stunden": anzahl_gesamt,
                "echte_messungen": anzahl_echte_messungen,
                "urspruenglich_fehlend": anzahl_urspruenglich_fehlend,
                "interpolierte_werte": anzahl_interpoliert,
                "verbleibend_fehlend": anzahl_fehlend,
                "anteil_fehlend_prozent": anteil_fehlend_prozent,
                "empfehlung": empfehlung,
            }
        )

    qualitaet_df = pd.DataFrame(ergebnisse).sort_values(
        by="anteil_fehlend_prozent", ascending=False
    ).reset_index(drop=True)

    print(qualitaet_df.to_string(index=False, formatters={"anteil_fehlend_prozent": lambda wert: f"{wert:.2f}"}))
    return qualitaet_df


def ungeeignete_sensoren_entfernen(df, qualitaet_df):
    print("\n" + "=" * 70)
    print("16. UNGEEIGNETE SENSOREN ENTFERNEN")
    print("=" * 70)

    auszuschliessende_sensoren = qualitaet_df.loc[
        qualitaet_df["empfehlung"] == "ausschließen", "name"
    ].tolist()

    if len(auszuschliessende_sensoren) == 0:
        print("Keine Sensoren auszuschließen.")
        return df

    print("Auszuschließende Sensoren:")
    for sensorname in auszuschliessende_sensoren:
        print(sensorname)

    df_bereinigt = df[~df["name"].isin(auszuschliessende_sensoren)].copy()

    print("Anzahl Sensoren vorher:", df["name"].nunique())
    print("Anzahl Sensoren nachher:", df_bereinigt["name"].nunique())
    print("Anzahl Zeilen vorher:", len(df))
    print("Anzahl Zeilen nachher:", len(df_bereinigt))
    print("Entfernte Zeilen:", len(df) - len(df_bereinigt))
    print("Verbleibende fehlende visitors-Werte:", df_bereinigt["visitors"].isna().sum())
    print("Verbleibende fehlende avgDuration-Werte:", df_bereinigt["avgDuration"].isna().sum())

    return df_bereinigt


def bereinigte_daten_speichern(df, dateipfad="../data/bad_nauheim_bereinigt.csv"):
    print("\n" + "=" * 70)
    print("17. BEREINIGTE DATEN SPEICHERN")
    print("=" * 70)

    df = df.sort_values(by=["name", "timestamp"]).reset_index(drop=True)
    df.to_csv(dateipfad, index=False, encoding="utf-8")

    print("Datei wurde gespeichert unter:", dateipfad)
    print("Anzahl gespeicherter Zeilen:", len(df))
    print("Anzahl gespeicherter Sensoren:", df["name"].nunique())
    print("Gespeicherte Spalten:", df.columns.tolist())


if __name__ == "__main__":
    print("Dieses Modul wird aus der Pipeline aufgerufen.")