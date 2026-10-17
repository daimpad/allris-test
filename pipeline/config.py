"""Pfade, Quellen und Lizenzen der Pipeline."""
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
STAND = RAW / "STAND.json"
ORTSTEILE = GEO / "ortsteile_bonn.geojson"
DB = BUILD / "allris.sqlite"

OPARL_BODY = "https://www.bonn.sitzung-online.de/oparl/bodies/1"
LITE_GRAPHQL = "https://oparl.bonn.machdenstaat.de/graphql"
USER_AGENT = "allris-bonn-pipeline (https://github.com/daimpad/allris-test)"

# Quelle je Datensatz; wird in die Datenbank und in jeden Export übernommen.
SOURCES = {
    "oparl-bonn": {
        "url": OPARL_BODY,
        "license": "CC0 1.0 (Stadt Bonn, Datensatz „Ratsinformationssystem OParl-API“)",
    },
    "oparl-lite": {
        "url": LITE_GRAPHQL,
        "license": "CC BY-NC 4.0 (OParl-Lite Bonn, machdenstaat)",
    },
    "geo-bonn": {
        "url": "https://opendata.bonn.de/dataset/flächen-der-ortsteile",
        "license": "CC0 1.0 (Stadt Bonn)",
    },
}

PILOT_ORTSTEIL = "Endenich"
