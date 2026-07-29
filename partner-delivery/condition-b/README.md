# Condition B – Daten- und Verfügbarkeitspaket

Dieses Paket enthält die sechs Tage von **Condition B**:
`2025-07-08 00:00 UTC` bis ausschließlich `2025-07-14 00:00 UTC`.
Condition B ist kein eigener Datensatz und kein neuer Split. Sie ist die
Berichtsbedingung mit starker Fehlwertbelastung innerhalb des einen
kontinuierlichen, zurückgehaltenen Tests vom 6. bis 14. Juli 2025.
Der 8. Juli setzt weder Vorverarbeitung noch Patch-Verlauf oder eine
spätere Fensterhistorie zurück.

Die kanonische Quelle im Projekt lautet
`new-data/data/bad_nauheim_bereinigt.csv`, SHA-256
`af807e38e63a253eea4a3639649c67744b0a34b839b80ee7c6682a55ea62991f`. Das Paket enthält alle **4.032** Condition-B-Zeilen:
28 Zeitreihen × 144 UTC-Stunden. Es filtert weder mit der
Autoencoder-Regel `k=6`/`k=4` noch mit einer erfundenen LSTM-Regel.

## Verfügbarkeitszahlen

| Größe | Bedingung A | Bedingung B |
|---|---:|---:|
| Serien-Stunden | 1.344 | 4.032 |
| Zeitreihen | 28 | 28 |
| UTC-Stunden | 48 | 144 |
| Ursprünglich beobachtet | 1.127 | 2.032 |
| Ursprünglich fehlend | 217 | 2.000 |
| Für Eingabekontext gepatcht | 133 | 322 |
| Als Eingabe verfügbar | 1.260 | 2.354 |
| Als Eingabe nicht verfügbar | 84 | 1.678 |

Ursprünglich beobachtete Serien-Stunden in Condition B nach UTC-Datum:
8. Juli 318, 9. Juli 368, 10. Juli 442, 11. Juli 306,
12. Juli 435 und 13. Juli 163; jede Tageszeile umfasst 672
Serien-Stunden.

## Bedeutungen der Werte und Masken

- `visitors_source_stored` bewahrt den in der Quell-CSV gespeicherten
  Wert. Bei `war_fehlend=true` kann dies eine dort gespeicherte
  Interpolation sein; sie ist keine Messung und keine Ground Truth.
- `visitors_original_observed` enthält nur eine ursprüngliche Messung,
  wenn `target_observed_mask=true`; sonst bleibt das Feld leer.
- `input_was_patched=true` bedeutet, dass die gemeinsame, bereits
  geprüfte Vorbereitung eine zulässige ein- oder zweistündige Lücke nur
  für den Eingabekontext geschlossen hat. Ein Patch wird nie zum Ziel.
- `input_available_mask=false` kennzeichnet eine weiterhin nicht
  verfügbare Eingabe. Der Wert `0.0` in `input_visitor_scaled` ist dort
  nur ein endlicher, maskierter Platzhalter. Die Verfügbarkeit darf
  niemals aus diesem Zahlenwert abgeleitet werden.
- `avgDuration_source_stored` ist eine unveränderte, informative
  Quellspalte. Ob und wie sie später für ein LSTM genutzt wird, bleibt
  ausschließlich Afnans Entscheidung.

Die beiden area-bezeichneten Reihen `Innenstadt` und `Kurpark` bleiben
enthalten; ihre genaue Beobachtungsbedeutung ist ungeklärt. Deshalb
spricht dieses Paket von 28 Zeitreihen bzw. Serien und nicht von 28
Punktsensoren.

## Dateien

`data/condition_b_stundendaten.csv` enthält die vollständige
Serien-Stunden-Tabelle. Die drei weiteren CSV-Dateien beschreiben
Bedingung A/B, UTC-Tage und einzelne Serien. Die vier PNG-Dateien zeigen
ausschließlich ursprüngliche Beobachtungs- und Eingabeverfügbarkeit.
`manifest.json` enthält Quell-, Versions- und Datei-Hashes.

Die portablen Module unter `src/` lesen nur diese exportierten
CSV-Dateien. Sie führen keine Interpolation, Statistik-Anpassung,
Skalierung, Fensterbildung, Modellierung oder Bewertung aus.

## Daten prüfen und Plots neu erzeugen

Die Skripte lösen Daten- und Ausgabepfade relativ zu ihrer eigenen Datei
auf. Deshalb funktionieren sie unabhängig vom aktuellen
Arbeitsverzeichnis. Ersetze `<PAKETPFAD>` durch den absoluten Pfad zu
diesem `condition-b`-Ordner:

```text
python -B "<PAKETPFAD>/src/condition_b_daten_einlesen.py"
python -B "<PAKETPFAD>/src/explorative_datenanalyse_condition_b_pipeline.py"
```

Erforderlich sind Python 3.12, pandas 3.0.0 und für die Plots die
autorisierte Abhängigkeit `matplotlib==3.11.1`. Die Pipeline
nutzt ein nicht-interaktives Backend, zeigt kein Fenster an und
überschreibt nur die vier benannten PNG-Dateien im eigenen Paket.

## Wissenschaftliche Grenze

Condition B ist zurückgehaltenes Testmaterial. Die gezeigte
Fehlwertstruktur darf nicht zur Auswahl oder Abstimmung eines LSTM
verwendet werden. Jede Einsicht in Condition B vor dem Einfrieren der
LSTM-Spezifikation muss ehrlich offengelegt werden. Das Paket lässt
Afnan ihre eigene LSTM-Eignung, Eingaben, Ziele, Fenster, Skalierung,
Architektur, Verlustfunktion und Score-Definition festlegen.

Condition B beschreibt Verhalten unter starker Fehlwertbelastung und
Abdeckungsverlust. Sie misst keine Robustheit gegenüber realem
Sensorrauschen. Dieses Paket enthält keine Modellresultate,
Anomalie-Scores, Schwellen, Labels oder Leistungsbehauptungen und wählt
kein LSTM-Design aus.
