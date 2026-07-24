import json


def lade_daten(dateipfad="../data/bad_nauheim.json"):
    """
    Lädt die Rohdaten aus der JSON-Datei und gibt die Liste unter 'sensordata' zurück.
    """
    with open(dateipfad, "r", encoding="utf-8") as datei:
        daten = json.load(datei)

    if "sensordata" not in daten:
        raise KeyError("Der Schlüssel 'sensordata' wurde nicht gefunden.")

    return daten["sensordata"]


if __name__ == "__main__":
    sensordaten = lade_daten()

    print("Datentyp:", type(sensordaten))
    print("Anzahl Datensätze:", len(sensordaten))

    if sensordaten:
        print("Schlüssel des ersten Datensatzes:", list(sensordaten[0].keys()))
        print("Erster Datensatz:", sensordaten[0])

    for datensatz in sensordaten:
        if (datensatz["name"] == "Karlstraße 15"
            and datensatz["timestamp"].startswith("2025-06-30")
        ):
            print(datensatz)
