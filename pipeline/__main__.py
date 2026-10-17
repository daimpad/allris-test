"""Aufruf: python -m pipeline {fetch|fetch-papers|fetch-organizations|fetch-lite|build|export|check|all}"""
import sys

from . import build, check, export, fetch

STEPS = {
    "fetch": fetch.fetch_all,
    "fetch-papers": fetch.fetch_papers,
    "fetch-organizations": fetch.fetch_organizations,
    "fetch-lite": fetch.fetch_consultations_lite,
    "build": build.build,
    "export": export.export,
    "check": check.check,
}


def main(argv):
    if len(argv) != 1 or argv[0] not in (*STEPS, "all"):
        raise SystemExit(__doc__)
    for step in (["fetch", "build", "export", "check"] if argv[0] == "all" else argv):
        print(f"== {step}", flush=True)
        STEPS[step]()


main(sys.argv[1:])
