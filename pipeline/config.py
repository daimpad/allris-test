"""Pfade, Quellen und Lizenzen der Pipeline."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
GEO = ROOT / "data" / "geo"
BUILD = ROOT / "data" / "build"
EXPORT = ROOT / "data" / "export"

PAPERS = RAW / "papers.jsonl"
ORGANIZATIONS = RAW / "organizations.json"
VERWALTUNGSBEREICHE = RAW / "verwaltungsbereiche.json"
CONSULTATIONS_LITE = RAW / "consultations_lite.jsonl"
MEETINGS = RAW / "meetings.json"
LEGISLATIVE_TERMS = RAW / "legislative_terms.json"
OSM_STREETS = RAW / "osm_streets.json"
OSM_TILES = RAW / "osm_tiles"
STAND = RAW / "STAND.json"
ORTSTEILE = GEO / "ortsteile_bonn.geojson"
STADTBEZIRKE = GEO / "stadtbezirke_bonn.geojson"
# Straßenverzeichnis (Name → Lagen je Ortsteil), abgeleitet aus OSM; im Repository, damit die
# Aktualisierung ohne Overpass auskommt. Neu erzeugen mit `python -m pipeline gazetteer`.
STRASSEN = GEO / "strassen_bonn.json"
BPLAN = GEO / "bebauungsplaene_bonn.geojson"
BPLAN_URL = "https://stadtplan.bonn.de/geojson?Thema=20074"
DB = BUILD / "allris.sqlite"

OPARL_BODY = "https://www.bonn.sitzung-online.de/oparl/bodies/1"
LITE_GRAPHQL = "https://oparl.bonn.machdenstaat.de/graphql"
OVERPASS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]
# Umgebendes Rechteck der 51 Ortsteile (Süd, West, Nord, Ost), für den Kachelabruf gerundet
BONN_BBOX = (50.63, 7.02, 50.78, 7.22)
USER_AGENT = "allris-bonn-pipeline (https://github.com/daimpad/allris-test)"

# Quelle je Datensatz; wird in die Datenbank und in jeden Export übernommen.
SOURCES = {
    "oparl-bonn": {
        "url": OPARL_BODY,
        "license": "CC0 1.0 (Stadt Bonn, Datensatz „Ratsinformationssystem OParl-API“)",
    },
    "oparl-lite": {
        "url": LITE_GRAPHQL,
        "license": "CC BY 4.0 (OParl-Lite Bonn, machdenstaat)",
    },
    "osm": {
        "url": "https://www.openstreetmap.org (Overpass API)",
        "license": "ODbL 1.0, © OpenStreetMap-Mitwirkende",
    },
    "geo-bonn": {
        "url": "https://opendata.bonn.de/dataset/flächen-der-ortsteile",
        "license": "CC0 1.0 (Stadt Bonn)",
    },
    "bplan-bonn": {
        "url": "https://opendata.bonn.de/dataset/lage-der-bebauungspläne",
        "license": "CC0 1.0 (Stadt Bonn, Datensatz „Lage der Bebauungspläne“)",
    },
}

PILOT_ORTSTEIL = "Endenich"

# Öffentliche Adresse der Seite (für absolute Links in Feeds, Kalender und DCAT-Beschreibung)
SITE_URL = os.environ.get("SITE_URL", "https://ris-bonn.datenatlas.de/")
