"""Aufruf: python -m pipeline {fetch|fetch-papers|fetch-organizations|fetch-lite|fetch-meetings|fetch-plans|fetch-housenumbers|fetch-objects|fetch-texts|fetch-streets|gazetteer|build|export|check|verify|package|seo|baustellen|anliegen|anliegen-seite|kandidaten|baustellen-seite|kurzfassungen|stufe-c|soll|kontext-ausschnitte|fetch-haltestellen|kontext|kultur-stichprobe|verkehr-stichprobe|schule-stichprobe|wohnen-stichprobe|klima-stichprobe|all}"""
import sys

from . import anliegen, baustellen, build, check, dossier, export, fetch, geocode, kandidaten, kontext, kurzfassung, seo, soll, stufe_c, verify
from .themenseiten import klima, kultur, schule, verkehr, wohnen

STEPS = {
    "fetch": fetch.fetch_all,
    "fetch-papers": fetch.fetch_papers,
    "fetch-organizations": fetch.fetch_organizations,
    "fetch-lite": fetch.fetch_consultations_lite,
    "fetch-meetings": fetch.fetch_meetings,
    "fetch-plans": fetch.fetch_plans,
    "fetch-housenumbers": fetch.fetch_housenumbers,
    "fetch-objects": fetch.fetch_objects,
    "fetch-texts": fetch.fetch_texts,
    "fetch-streets": fetch.fetch_streets,
    "gazetteer": geocode.write_gazetteer,
    "build": build.build,
    "export": export.export,
    "check": check.check,
    "verify": verify.verify,
    "package": verify.package,
    "seo": seo.write,  # nach dem Zusammenstellen der Seite in _site
    "baustellen": baustellen.archive,  # Archiv der Baustellen (eigener Workflow, Branch archiv)
    "anliegen": anliegen.archive,  # Archiv des Mängelmelders (Workflow baustellen.yml, Branch archiv, Ordner anliegen)
    "anliegen-seite": anliegen.seite,  # Zahlen je Ortsteil für den Steckbrief (nach dem Auschecken des Archivs)
    "kandidaten": kandidaten.write,  # Kandidaten Beschluss ↔ Baustelle (Audit, Stichprobe)
    "baustellen-seite": kandidaten.write_site,
    "kurzfassungen": kurzfassung.erzeugen,  # Kurzfassungen mit Mistral (Secret MISTRAL_API_KEY), Branch kurzfassungen
    "stufe-c": stufe_c.schritt,  # Stufe C (Sprachmodell, nach build, vor export): Anfragen, Gegenprüfung, Audit
    "kontext-ausschnitte": kontext.ausschnitte,  # einmalig: Ausschnitte für Bonn (Zensus, Bodenrichtwerte, Klima, ...)
    "fetch-haltestellen": kontext.fetch_haltestellen,  # monatlich: Haltestellen (VRS-GTFS)
    "kontext": kontext.write,  # Kontextdaten je Ortsteil (nach export)
    "kultur-stichprobe": lambda: dossier.stichprobe(kultur.THEMA),  # einmalig: Prüfbogen zur Themenseite (nach export)
    "verkehr-stichprobe": lambda: dossier.stichprobe(verkehr.THEMA),  # einmalig: Prüfbogen (Entwurf, aus der Datenbank)
    "schule-stichprobe": lambda: dossier.stichprobe(schule.THEMA),  # einmalig: Prüfbogen (Entwurf, aus der Datenbank)
    "wohnen-stichprobe": lambda: dossier.stichprobe(wohnen.THEMA),  # einmalig: Prüfbogen (Entwurf, aus der Datenbank)
    "klima-stichprobe": lambda: dossier.stichprobe(klima.THEMA),  # einmalig: Prüfbogen (Entwurf, aus der Datenbank)
    "soll": soll.write,  # Soll-Modell der Prozessebene: Verfahren je Vorgang, Abgleich mit den Beratungen (Audit)  # Baustellen und mögliche Umsetzungen (hoch) für die Seite
}


def main(argv):
    if len(argv) != 1 or argv[0] not in (*STEPS, "all"):
        raise SystemExit(__doc__)
    for step in (["fetch", "build", "export", "kontext", "check", "verify", "package"] if argv[0] == "all" else argv):
        print(f"== {step}", flush=True)
        STEPS[step]()


main(sys.argv[1:])
