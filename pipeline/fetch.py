"""Abruf der Rohdaten: städtische OParl-API (Primärquelle) und OParl-Lite (Sitzungen, TOPs)."""
import concurrent.futures as cf
import json
from datetime import datetime, timezone

from . import config
from .net import get_json, post_graphql


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _stamp(key):
    stand = json.loads(config.STAND.read_text()) if config.STAND.exists() else {}
    stand[key] = _now()
    config.STAND.write_text(json.dumps(stand, ensure_ascii=False, indent=1) + "\n")


def _oparl_list(url, size=100, workers=6):
    first = get_json(f"{url}?page=1&size={size}")
    pages = first["pagination"]["totalPages"]
    print(f"{url}: {first['pagination']['totalElements']} Objekte, {pages} Seiten", flush=True)
    results = {1: first["data"]}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        fetch = lambda p: (p, get_json(f"{url}?page={p}&size={size}")["data"])
        for p, data in ex.map(fetch, range(2, pages + 1)):
            results[p] = data
    return [item for p in sorted(results) for item in results[p]]


def fetch_papers():
    papers = _oparl_list(f"{config.OPARL_BODY}/papers")
    with open(config.PAPERS, "w", encoding="utf-8") as f:
        for p in papers:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    _stamp("papers")
    print(f"{len(papers)} Vorlagen → {config.PAPERS}")


def fetch_organizations():
    orgs = _oparl_list(f"{config.OPARL_BODY}/organizations")
    config.ORGANIZATIONS.write_text(json.dumps(orgs, ensure_ascii=False))
    vb = [o for o in orgs if o.get("organizationType") == "Verwaltungsbereich"]
    config.VERWALTUNGSBEREICHE.write_text(json.dumps(vb, ensure_ascii=False))
    _stamp("organizations")
    print(f"{len(orgs)} Organisationen, davon {len(vb)} Verwaltungsbereiche")


CONSULTATION_QUERY = """
query($limit: Int!, $offset: Int!) {
  consultations(limit: $limit, offset: $offset, orderBy: {field: URI, direction: ASC}) {
    totalCount
    items {
      uri
      meeting { uri name startDate cancelled }
      agendaItem { uri number name result public }
    }
  }
}"""


def fetch_consultations_lite(page=100, workers=2):
    """Beratungen mit Sitzung und Tagesordnungspunkt; Verknüpfung über die OParl-URI."""
    run = lambda off: post_graphql(
        config.LITE_GRAPHQL, CONSULTATION_QUERY, {"limit": page, "offset": off}
    )["consultations"]
    first = run(0)
    total = first["totalCount"]
    print(f"OParl-Lite: {total} Beratungen", flush=True)
    items = {0: first["items"]}
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for off, res in ex.map(lambda o: (o, run(o)), range(page, total, page)):
            items[off] = res["items"]
    seen = set()
    with open(config.CONSULTATIONS_LITE, "w", encoding="utf-8") as f:
        for off in sorted(items):
            for c in items[off]:
                if c["uri"] in seen:
                    continue
                seen.add(c["uri"])
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
    _stamp("consultations_lite")
    print(f"{len(seen)} Beratungen → {config.CONSULTATIONS_LITE}")


def fetch_all():
    fetch_papers()
    fetch_organizations()
    fetch_consultations_lite()
