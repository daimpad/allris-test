"""Aufruf: python -m pipeline {fetch|fetch-papers|fetch-organizations|fetch-lite|fetch-meetings|fetch-plans|fetch-streets|gazetteer|build|export|check|verify|package|all}"""
import sys

from . import build, check, export, fetch, geocode, verify

STEPS = {
    "fetch": fetch.fetch_all,
    "fetch-papers": fetch.fetch_papers,
    "fetch-organizations": fetch.fetch_organizations,
    "fetch-lite": fetch.fetch_consultations_lite,
    "fetch-meetings": fetch.fetch_meetings,
    "fetch-plans": fetch.fetch_plans,
    "fetch-streets": fetch.fetch_streets,
    "gazetteer": geocode.write_gazetteer,
    "build": build.build,
    "export": export.export,
    "check": check.check,
    "verify": verify.verify,
    "package": verify.package,
}


def main(argv):
    if len(argv) != 1 or argv[0] not in (*STEPS, "all"):
        raise SystemExit(__doc__)
    for step in (["fetch", "build", "export", "check", "verify", "package"] if argv[0] == "all" else argv):
        print(f"== {step}", flush=True)
        STEPS[step]()


main(sys.argv[1:])
