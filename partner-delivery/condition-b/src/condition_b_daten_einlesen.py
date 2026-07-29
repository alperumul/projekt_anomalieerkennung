"""Liest und validiert die öffentlichen Condition-B-Tabellen.

Dieses Modul liest ausschließlich die exportierten CSV-Dateien. Es
führt keine Vorverarbeitung, Interpolation, Skalierungsanpassung,
Fensterbildung oder Modellentscheidung aus.
"""

from __future__ import annotations

import math
from pathlib import Path
import re

import pandas as pd

DATENVERZEICHNIS = Path(__file__).resolve().parents[1] / "data"
STUNDENDATEN_DATEI = DATENVERZEICHNIS / "condition_b_stundendaten.csv"
BEDINGUNGEN_DATEI = (
    DATENVERZEICHNIS / "condition_a_b_verfuegbarkeit.csv"
)
TAGES_DATEI = (
    DATENVERZEICHNIS / "condition_b_verfuegbarkeit_pro_tag.csv"
)
SERIEN_DATEI = (
    DATENVERZEICHNIS / "condition_b_verfuegbarkeit_pro_serie.csv"
)

STUNDENDATEN_SPALTEN = (
    "series_id",
    "timestamp_utc",
    "true_split",
    "evaluation_condition",
    "visitors_source_stored",
    "visitors_original_observed",
    "avgDuration_source_stored",
    "war_fehlend",
    "target_observed_mask",
    "input_available_mask",
    "input_was_patched",
    "input_visitor_scaled",
    "local_hour",
    "local_weekday",
    "local_hour_sin",
    "local_hour_cos",
    "local_weekday_sin",
    "local_weekday_cos",
)
VERFUEGBARKEITS_SPALTEN = (
    "evaluation_condition",
    "grid_rows",
    "series_count",
    "timestamp_count",
    "originally_observed_count",
    "originally_missing_count",
    "original_observation_rate",
    "patched_input_count",
    "input_available_count",
    "input_available_rate",
    "unavailable_input_count",
)
TAGES_SPALTEN = ("utc_date", *VERFUEGBARKEITS_SPALTEN[1:])
SERIEN_SPALTEN = (
    "series_id",
    "grid_rows",
    "originally_observed_count",
    "originally_missing_count",
    "original_observation_rate",
    "patched_input_count",
    "input_available_count",
    "input_available_rate",
    "unavailable_input_count",
    "longest_originally_missing_run_hours",
    "longest_unavailable_input_run_hours",
)
BOOLEAN_SPALTEN = (
    "war_fehlend",
    "target_observed_mask",
    "input_available_mask",
    "input_was_patched",
)
PFLICHT_ZAHLEN = (
    "input_visitor_scaled",
    "local_hour_sin",
    "local_hour_cos",
    "local_weekday_sin",
    "local_weekday_cos",
)
OPTIONALE_ZAHLEN = (
    "visitors_source_stored",
    "visitors_original_observed",
    "avgDuration_source_stored",
)
ZEITMUSTER = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:00:00Z")
DATUMSMUSTER = re.compile(r"\d{4}-\d{2}-\d{2}")
ERWARTETE_BEDINGUNGEN = {
    "condition_a": {
        "grid_rows": 1344,
        "series_count": 28,
        "timestamp_count": 48,
        "originally_observed_count": 1127,
        "originally_missing_count": 217,
        "patched_input_count": 133,
        "input_available_count": 1260,
        "unavailable_input_count": 84,
    },
    "condition_b": {
        "grid_rows": 4032,
        "series_count": 28,
        "timestamp_count": 144,
        "originally_observed_count": 2032,
        "originally_missing_count": 2000,
        "patched_input_count": 322,
        "input_available_count": 2354,
        "unavailable_input_count": 1678,
    },
}
ERWARTETE_TAGESWERTE = {
    "2025-07-08": 318,
    "2025-07-09": 368,
    "2025-07-10": 442,
    "2025-07-11": 306,
    "2025-07-12": 435,
    "2025-07-13": 163,
}


def _lese_roh(pfad: str | Path) -> pd.DataFrame:
    """Liest eine CSV-Datei strikt als UTF-8-Zeichenketten."""

    try:
        return pd.read_csv(
            pfad,
            dtype="string",
            keep_default_na=False,
            encoding="utf-8",
            encoding_errors="strict",
        )
    except (OSError, UnicodeError, pd.errors.ParserError) as fehler:
        raise ValueError(
            f"CSV-Datei kann nicht als striktes UTF-8 gelesen werden: {fehler}"
        ) from fehler


def _pruefe_spalten(
    df: pd.DataFrame,
    erwartet: tuple[str, ...],
    tabellenname: str,
) -> None:
    """Prüft das vollständige öffentliche Schema in fester Reihenfolge."""

    vorhanden = tuple(df.columns)
    if vorhanden != erwartet:
        raise ValueError(
            f"{tabellenname}: ungültiges Schema "
            f"(erwartet={erwartet!r}, vorhanden={vorhanden!r})"
        )


def _parse_boolean(werte: pd.Series, spalte: str) -> pd.Series:
    """Akzeptiert ausschließlich die expliziten Werte true und false."""

    if not werte.isin(("true", "false")).all():
        raise ValueError(
            f"{spalte}: nur kleingeschriebenes true/false ist zulässig"
        )
    return werte.map({"true": True, "false": False}).astype(bool)


def _parse_zahl(
    werte: pd.Series,
    spalte: str,
    *,
    optional: bool = False,
) -> pd.Series:
    """Parst endliche Zahlen und lässt nur explizit optionale Felder leer."""

    if not optional and werte.eq("").any():
        raise ValueError(f"{spalte}: Pflichtwert fehlt")
    eingabe = werte.mask(werte == "", pd.NA) if optional else werte
    try:
        zahlen = pd.to_numeric(eingabe, errors="raise")
    except (TypeError, ValueError) as fehler:
        raise ValueError(f"{spalte}: ungültige Zahl: {fehler}") from fehler
    if not zahlen.dropna().map(
        lambda wert: math.isfinite(float(wert))
    ).all():
        raise ValueError(f"{spalte}: Wert muss endlich sein")
    return zahlen


def _parse_ganzzahl(werte: pd.Series, spalte: str) -> pd.Series:
    """Parst nichtnegative Ganzzahlen."""

    zahlen = _parse_zahl(werte, spalte)
    if not zahlen.map(
        lambda wert: float(wert).is_integer() and int(wert) >= 0
    ).all():
        raise ValueError(f"{spalte}: nichtnegative Ganzzahl erwartet")
    return zahlen.astype("int64")


def _pruefe_rechnung(df: pd.DataFrame, tabellenname: str) -> None:
    """Prüft Summen und Raten der Verfügbarkeitstabellen."""

    if not df["originally_observed_count"].add(
        df["originally_missing_count"]
    ).equals(df["grid_rows"]):
        raise ValueError(
            f"{tabellenname}: Originalbeobachtungen stimmen nicht"
        )
    if not df["input_available_count"].add(
        df["unavailable_input_count"]
    ).equals(df["grid_rows"]):
        raise ValueError(
            f"{tabellenname}: Eingabeverfügbarkeit stimmt nicht"
        )
    erwartete_originalrate = (
        df["originally_observed_count"] / df["grid_rows"]
    )
    erwartete_eingaberate = (
        df["input_available_count"] / df["grid_rows"]
    )
    if not (
        (df["original_observation_rate"] - erwartete_originalrate)
        .abs()
        .le(1e-15)
        .all()
        and (df["input_available_rate"] - erwartete_eingaberate)
        .abs()
        .le(1e-15)
        .all()
    ):
        raise ValueError(f"{tabellenname}: Rate stimmt nicht mit Zählung")


def lade_condition_b_stundendaten(
    pfad: str | Path = STUNDENDATEN_DATEI,
) -> pd.DataFrame:
    """Liest und validiert alle 4.032 Condition-B-Serien-Stunden."""

    df = _lese_roh(pfad)
    _pruefe_spalten(df, STUNDENDATEN_SPALTEN, "Stundendaten")
    if not df["timestamp_utc"].str.fullmatch(ZEITMUSTER.pattern).all():
        raise ValueError(
            "timestamp_utc: YYYY-MM-DDTHH:00:00Z in UTC erwartet"
        )
    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        format="%Y-%m-%dT%H:%M:%SZ",
        errors="raise",
        utc=True,
    )
    for spalte in BOOLEAN_SPALTEN:
        df[spalte] = _parse_boolean(df[spalte], spalte)
    for spalte in PFLICHT_ZAHLEN:
        df[spalte] = _parse_zahl(df[spalte], spalte)
    for spalte in OPTIONALE_ZAHLEN:
        df[spalte] = _parse_zahl(df[spalte], spalte, optional=True)
    for spalte, maximum in (("local_hour", 23), ("local_weekday", 6)):
        df[spalte] = _parse_ganzzahl(df[spalte], spalte)
        if not df[spalte].le(maximum).all():
            raise ValueError(f"{spalte}: Wert außerhalb des Bereichs")

    if len(df) != 4032:
        raise ValueError(
            f"Stundendaten: 4.032 Zeilen erwartet, {len(df)} gefunden"
        )
    if df.duplicated(["series_id", "timestamp_utc"]).any():
        raise ValueError("Stundendaten: doppelte Serien-Stunden")
    sortiert = df.sort_values(
        ["series_id", "timestamp_utc"]
    ).reset_index(drop=True)
    if not df[["series_id", "timestamp_utc"]].equals(
        sortiert[["series_id", "timestamp_utc"]]
    ):
        raise ValueError("Stundendaten: Reihenfolge ist nicht deterministisch")
    if df["series_id"].nunique() != 28:
        raise ValueError("Stundendaten: genau 28 Zeitreihen erwartet")
    if df["timestamp_utc"].nunique() != 144:
        raise ValueError("Stundendaten: genau 144 UTC-Stunden erwartet")
    if df["timestamp_utc"].min() != pd.Timestamp(
        "2025-07-08T00:00:00Z"
    ) or df["timestamp_utc"].max() != pd.Timestamp(
        "2025-07-13T23:00:00Z"
    ):
        raise ValueError("Stundendaten: Condition-B-Grenzen verändert")
    if not df["true_split"].eq("continuous_test").all():
        raise ValueError(
            "Stundendaten: true_split muss continuous_test bleiben"
        )
    if not df["evaluation_condition"].eq("condition_b").all():
        raise ValueError(
            "Stundendaten: evaluation_condition muss condition_b bleiben"
        )
    erwartet_beobachtet = (
        ~df["war_fehlend"] & df["visitors_source_stored"].notna()
    )
    if not df["target_observed_mask"].equals(erwartet_beobachtet):
        raise ValueError(
            "target_observed_mask widerspricht der Quellbedeutung"
        )
    erwartet_gepatcht = (
        df["input_available_mask"] & ~df["target_observed_mask"]
    )
    if not df["input_was_patched"].equals(erwartet_gepatcht):
        raise ValueError("input_was_patched widerspricht den Masken")
    if not df.loc[
        ~df["input_available_mask"], "input_visitor_scaled"
    ].eq(0.0).all():
        raise ValueError("Nicht verfügbare Eingaben benötigen Platzhalter 0.0")
    if not df.loc[
        ~df["target_observed_mask"], "visitors_original_observed"
    ].isna().all():
        raise ValueError(
            "Fehlende Originalbeobachtung enthält einen Zielwert"
        )
    if int(df["target_observed_mask"].sum()) != 2032:
        raise ValueError("Stundendaten: Originalbeobachtungszahl verändert")
    if int(df["input_was_patched"].sum()) != 322:
        raise ValueError("Stundendaten: Patchzahl verändert")
    if int((~df["input_available_mask"]).sum()) != 1678:
        raise ValueError("Stundendaten: Eingabeausfallzahl verändert")
    return df


def _lade_zusammenfassung(
    pfad: str | Path,
    spalten: tuple[str, ...],
    tabellenname: str,
) -> pd.DataFrame:
    """Liest eine Verfügbarkeitstabelle mit strikten Zahltypen."""

    df = _lese_roh(pfad)
    _pruefe_spalten(df, spalten, tabellenname)
    zaehlspalten = (
        "grid_rows",
        "series_count",
        "timestamp_count",
        "originally_observed_count",
        "originally_missing_count",
        "patched_input_count",
        "input_available_count",
        "unavailable_input_count",
        "longest_originally_missing_run_hours",
        "longest_unavailable_input_run_hours",
    )
    for spalte in zaehlspalten:
        if spalte in df:
            df[spalte] = _parse_ganzzahl(df[spalte], spalte)
    for spalte in (
        "original_observation_rate",
        "input_available_rate",
    ):
        df[spalte] = _parse_zahl(df[spalte], spalte).astype(float)
    _pruefe_rechnung(df, tabellenname)
    return df


def lade_condition_a_b_verfuegbarkeit(
    pfad: str | Path = BEDINGUNGEN_DATEI,
) -> pd.DataFrame:
    """Liest den getrennten Vergleich von Bedingung A und B."""

    df = _lade_zusammenfassung(
        pfad,
        VERFUEGBARKEITS_SPALTEN,
        "Bedingungsverfügbarkeit",
    )
    if df["evaluation_condition"].tolist() != [
        "condition_a",
        "condition_b",
    ]:
        raise ValueError("Bedingungsverfügbarkeit: Reihenfolge verändert")
    for zeile in df.to_dict("records"):
        erwartet = ERWARTETE_BEDINGUNGEN[zeile["evaluation_condition"]]
        for spalte, wert in erwartet.items():
            if int(zeile[spalte]) != wert:
                raise ValueError(
                    f"Bedingungsverfügbarkeit: {spalte} verändert"
                )
    return df


def lade_condition_b_verfuegbarkeit_pro_tag(
    pfad: str | Path = TAGES_DATEI,
) -> pd.DataFrame:
    """Liest die Condition-B-Verfügbarkeit nach UTC-Datum."""

    df = _lade_zusammenfassung(
        pfad,
        TAGES_SPALTEN,
        "Tagesverfügbarkeit",
    )
    if not df["utc_date"].str.fullmatch(DATUMSMUSTER.pattern).all():
        raise ValueError("utc_date: YYYY-MM-DD erwartet")
    if df["utc_date"].tolist() != list(ERWARTETE_TAGESWERTE):
        raise ValueError("Tagesverfügbarkeit: UTC-Datumsfolge verändert")
    if not df["grid_rows"].eq(672).all():
        raise ValueError("Tagesverfügbarkeit: 672 Serien-Stunden erwartet")
    gefunden = dict(
        zip(
            df["utc_date"],
            df["originally_observed_count"].astype(int),
            strict=True,
        )
    )
    if gefunden != ERWARTETE_TAGESWERTE:
        raise ValueError("Tagesverfügbarkeit: Tageszählung verändert")
    return df


def lade_condition_b_verfuegbarkeit_pro_serie(
    pfad: str | Path = SERIEN_DATEI,
) -> pd.DataFrame:
    """Liest die Condition-B-Verfügbarkeit je Zeitreihe."""

    df = _lade_zusammenfassung(
        pfad,
        SERIEN_SPALTEN,
        "Serienverfügbarkeit",
    )
    if len(df) != 28 or df["series_id"].nunique() != 28:
        raise ValueError("Serienverfügbarkeit: 28 Zeitreihen erwartet")
    if df["series_id"].tolist() != sorted(df["series_id"].tolist()):
        raise ValueError("Serienverfügbarkeit: Reihenfolge verändert")
    if not df["grid_rows"].eq(144).all():
        raise ValueError("Serienverfügbarkeit: 144 Stunden je Serie erwartet")
    if int(df["originally_observed_count"].sum()) != 2032:
        raise ValueError("Serienverfügbarkeit: Beobachtungen stimmen nicht")
    if int(df["patched_input_count"].sum()) != 322:
        raise ValueError("Serienverfügbarkeit: Patchzahl stimmt nicht")
    if int(df["unavailable_input_count"].sum()) != 1678:
        raise ValueError("Serienverfügbarkeit: Ausfallzahl stimmt nicht")
    return df


def lade_alle_tabellen(
    datenverzeichnis: str | Path = DATENVERZEICHNIS,
) -> dict[str, pd.DataFrame]:
    """Liest alle vier öffentlichen Tabellen aus einem Verzeichnis."""

    wurzel = Path(datenverzeichnis)
    return {
        "stundendaten": lade_condition_b_stundendaten(
            wurzel / "condition_b_stundendaten.csv"
        ),
        "bedingungen": lade_condition_a_b_verfuegbarkeit(
            wurzel / "condition_a_b_verfuegbarkeit.csv"
        ),
        "tage": lade_condition_b_verfuegbarkeit_pro_tag(
            wurzel / "condition_b_verfuegbarkeit_pro_tag.csv"
        ),
        "serien": lade_condition_b_verfuegbarkeit_pro_serie(
            wurzel / "condition_b_verfuegbarkeit_pro_serie.csv"
        ),
    }


def hauptprogramm() -> dict[str, pd.DataFrame]:
    """Liest alle Tabellen und gibt eine knappe Verfügbarkeitsübersicht aus."""

    print("\n" + "=" * 80)
    print("CONDITION-B-DATEN EINLESEN UND PRÜFEN")
    print("=" * 80)
    tabellen = lade_alle_tabellen()
    stundendaten = tabellen["stundendaten"]
    print(
        "Geladen:",
        f"{len(stundendaten)} Serien-Stunden,",
        f"{stundendaten['series_id'].nunique()} Zeitreihen,",
        f"{stundendaten['timestamp_utc'].nunique()} UTC-Stunden",
    )
    print(
        "Hinweis: Die Masken bestimmen Beobachtung und "
        "Eingabeverfügbarkeit; nicht der Zahlenwert 0.0."
    )
    print("Condition-B-Daten erfolgreich geprüft.")
    return tabellen


if __name__ == "__main__":
    hauptprogramm()
