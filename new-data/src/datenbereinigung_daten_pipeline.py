"""
Zentrale Pipeline zur Datenvorbereitung für die Anomalieerkennung.

Diese Datei steuert den gesamten Vorverarbeitungsablauf:
1. Einlesen und erste Prüfung
2. Analyse und Aggregation von Mehrfachmessungen
3. Vervollständigung der Zeitachse und Interpolation
4. Qualitätsbewertung und Speicherung des bereinigten Datensatzes
"""

from src.datenbereinigung_daten_einlesen_und_pruefen import (
    daten_vorbereiten,
    relevante_spalten_auswaehlen,
    zeitstempel_umwandeln,
    fehlende_werte_pruefen,
    identische_dubletten_pruefen,
)
from src.datenbereinigung_daten_mehrfachmessungen_und_aggregation import (
    mehrfachmessungen_pruefen,
    beispiel_mehrfachmessung_anzeigen,
    mehrfachmessungen_analysieren,
    mehrfachmessungen_aggregieren,
)
from src.datenbereinigung_daten_zeitachse_und_interpolation import (
    fehlende_stunden_analysieren,
    lueckenlaengen_analysieren,
    zeitachsen_vervollstaendigen,
    kurze_luecken_interpolieren,
)
from src.datenbereinigung_daten_qualitaet_und_speichern import (
    datenqualitaet_nach_interpolation_analysieren,
    datenqualitaet_pro_sensor_und_tag_analysieren,
    ungeeignete_sensoren_entfernen,
    bereinigte_daten_speichern,
)


def hauptpipeline():
    df = daten_vorbereiten()
    df = relevante_spalten_auswaehlen(df)
    df = zeitstempel_umwandeln(df)
    df = fehlende_werte_pruefen(df)
    df = identische_dubletten_pruefen(df)

    df, mehrfachmessungen = mehrfachmessungen_pruefen(df)
    beispiel_mehrfachmessung_anzeigen(df, mehrfachmessungen)
    mehrfachmessungen_analyse = mehrfachmessungen_analysieren(df)
    df = mehrfachmessungen_aggregieren(df)

    luecken_df = fehlende_stunden_analysieren(df)
    lueckenlaengen_df = lueckenlaengen_analysieren(df)

    df = zeitachsen_vervollstaendigen(df)
    df = kurze_luecken_interpolieren(df, maximale_luecke=2)

    qualitaet_sensor_tag_df = (
        datenqualitaet_pro_sensor_und_tag_analysieren(df)
    )

    qualitaet_df = datenqualitaet_nach_interpolation_analysieren(
        df,
        ausschlussgrenze_prozent=50,
    )
    df = ungeeignete_sensoren_entfernen(df, qualitaet_df)

    bereinigte_daten_speichern(df)

    return {
        "df_bereinigt": df,
        "mehrfachmessungen_analyse": mehrfachmessungen_analyse,
        "luecken_df": luecken_df,
        "lueckenlaengen_df": lueckenlaengen_df,
        "qualitaet_df": qualitaet_df,
        "qualitaet_sensor_tag_df": qualitaet_sensor_tag_df,

    }


if __name__ == "__main__":
    ergebnisse = hauptpipeline()
    print("\nPipeline erfolgreich abgeschlossen.")
    print("Verfügbare Ergebnisse:", list(ergebnisse.keys()))