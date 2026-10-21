"""Aufruf: python -m pipeline {fetch|fetch-papers|fetch-organizations|fetch-lite|fetch-meetings|fetch-plans|fetch-housenumbers|fetch-texts|fetch-streets|gazetteer|build|export|check|verify|package|seo|baustellen|kandidaten|baustellen-seite|kurzfassungen|stufe-c|soll|all}"""
import sys

from . import baustellen, build, check, export, fetch, geocode, kandidaten, kurzfassung, seo, soll, stufe_c, verify

STEPS = {
    "fetch": fetch.fetch_all,
    "fetch-papers": fetch.fetch_papers,
    "fetch-organizations": fetch.fetch_organizations,
    "fetch-lite": fetch.fetch_consultations_lite,
    "fetch-meetings": fetch.fetch_meetings,
    "fetch-plans": fetch.fetch_plans,
    "fetch-housenumbers": fetch.fetch_housenumbers,
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
    "kandidaten": kandidaten.write,  # Kandidaten Beschluss ↔ Baustelle (Audit, Stichprobe)
    "baustellen-seite": kandidaten.write_site,
    "kurzfassungen": kurzfassung.erzeugen,  # Kurzfassungen mit Mistral (Secret MISTRAL_API_KEY), Branch kurzfassungen
    "stufe-c": stufe_c.schritt,  # Stufe C (Sprachmodell, nach build, vor export): Anfragen, Gegenprüfung, Audit
    "soll": soll.write,  # Soll-Modell der Prozessebene: Verfahren je Vorgang, Abgleich mit den Beratungen (Audit)  # Baustellen und mögliche Umsetzungen (hoch) für die Seite
}


def main(argv):
    if len(argv) != 1 or argv[0] not in (*STEPS, "all"):
        raise SystemExit(__doc__)
    for step in (["fetch", "build", "export", "check", "verify", "package"] if argv[0] == "all" else argv):
        print(f"== {step}", flush=True)
        STEPS[step]()


main(sys.argv[1:])
