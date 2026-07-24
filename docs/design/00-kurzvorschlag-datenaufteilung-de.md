# Vorschlag zur zeitlichen Datenaufteilung

> **Nicht normativ:** Diese deutschsprachige Kurzfassung erklärt nur die zeitliche Aufteilung. Der [konsolidierte Implementierungs-Handoff](../handoffs/2026-07-24-implementation-handoff.md) ist verbindlich und hat bei Abweichungen Vorrang.

| Phase | Zeitraum (UTC) |
|---|---|
| Training | 30.06.2025, 01:00 – 04.07.2025, 00:00 |
| Validierung | 04.07.2025, 00:00 – 06.07.2025, 00:00 |
| Primärer Test | 06.07.2025, 00:00 – 08.07.2025, 00:00 |
| Sekundärer Missingness-Test | 08.07.2025, 00:00 – 14.07.2025, 00:00 |

## Begründung

Die Datenqualität verschlechtert sich ab dem 08.07. deutlich. Deshalb sollte dieser Zeitraum nicht der einzige reguläre Test sein.

Den Zeitraum vollständig zu verwerfen wäre bei unserem kleinen Datensatz aber ebenfalls problematisch. Vom 10.07. bis 13.07. bleiben noch ausreichend ursprünglich beobachtete und bewertbare Sensorstunden erhalten. Deshalb trennen wir die Auswertung:

- Der Zeitraum vom 06.07. bis 07.07. ist der primäre Test für den normalen Modellvergleich.
- Der Zeitraum vom 08.07. bis 13.07. wird separat als Missingness-Test verwendet. Er zeigt, wie stabil die Modelle bei stark unvollständigen Eingaben bleiben und bei welcher Datenverfügbarkeit sie keine zuverlässigen Scores mehr liefern.
- Beide Zeiträume werden als eine fortlaufende Testzeitachse verarbeitet. Am 08.07. wird die Fensterbildung nicht neu gestartet; nur die spätere Berichterstattung wird getrennt.
- Die Ergebnisse beider Testzeiträume werden getrennt berichtet und nicht zu einer gemeinsamen Kennzahl vermischt.

## Darstellung in der Arbeit

Der Zeitraum ab dem 08.07. wird nicht als qualitativ gleichwertiger Testdatensatz behandelt, aber auch nicht verworfen. Der besser abgedeckte Zeitraum vom 06.07. bis 07.07. dient als primäre Modellbewertung. Die späteren Tage bilden eine zusätzliche Robustheitsanalyse gegenüber fehlenden Messwerten. Dadurch verhindern wir, dass die Hauptbewertung überwiegend durch Messausfälle bestimmt wird, und nutzen gleichzeitig die noch vorhandenen Beobachtungen für eine getrennte, klar begrenzte Fragestellung.
