"""Abruf der Rohdaten: städtische OParl-API (Primärquelle) und OParl-Lite (Sitzungen, TOPs)."""
import concurrent.futures as cf
import json
from datetime import datetime, timezone

from . import config
from .net import get_json, post_form, post_graphql


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


def fetch_meetings():
    """Sitzungen (auch künftige) und Wahlperioden aus der städtischen OParl-API."""
    meetings = _oparl_list(f"{config.OPARL_BODY}/meetings")
    keep = ("id", "name", "meetingState", "cancelled", "start", "end", "organization", "web")
    # Tagesordnung (web) und Einladung erscheinen etwa zwei Wochen vor der Sitzung
    config.MEETINGS.write_text(json.dumps(
        [{**{k: m.get(k) for k in keep}, "invitation": (m.get("invitation") or {}).get("accessUrl"),
          "agenda_items": len(m.get("agendaItem") or [])} for m in meetings], ensure_ascii=False))
    terms = _oparl_list(f"{config.OPARL_BODY}/legislativeTerms", size=10)
    config.LEGISLATIVE_TERMS.write_text(json.dumps(terms, ensure_ascii=False))
    _stamp("meetings")
    print(f"{len(meetings)} Sitzungen, {len(terms)} Wahlperioden")


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


OVERPASS_QUERY = '[out:json][timeout:90];way["highway"]["name"]({s},{w},{n},{e});out tags geom;'


def _overpass(query):
    for url in config.OVERPASS:
        try:
            return post_form(url, {"data": query}, tries=3)
        except Exception as exc:  # nächster Server
            print(f"  {url}: {exc}", flush=True)
    raise RuntimeError("Kein Overpass-Server erreichbar.")


def _tile_ways(s, w, n, e, depth=0):
    """Ways einer Kachel (zwischengespeichert); schlägt der Abruf fehl, wird die Kachel
    geviertelt. Liefert (Ways, fehlende Kacheln)."""
    cache = config.OSM_TILES / f"{s}_{w}_{n}_{e}.json"
    if cache.exists():
        return json.loads(cache.read_text()), []
    try:
        elements = _overpass(OVERPASS_QUERY.format(s=s, w=w, n=n, e=e))["elements"]
    except RuntimeError:
        if depth >= 2:
            return [], [(s, w, n, e)]
        ms, mw = round((s + n) / 2, 4), round((w + e) / 2, 4)
        ways, missing = [], []
        for q in ((s, w, ms, mw), (s, mw, ms, e), (ms, w, n, mw), (ms, mw, n, e)):
            got, miss = _tile_ways(*q, depth + 1)
            ways += got
            missing += miss
        return ways, missing
    config.OSM_TILES.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(elements, ensure_ascii=False))
    return elements, []


def fetch_streets(step=0.05):
    """Benannte Straßen (OSM-Ways mit `highway` und `name`) im Stadtgebiet, in Kacheln.
    Nicht abrufbare Kacheln werden übersprungen und in der Ausgabe als `missing_tiles`
    vermerkt; ein erneuter Aufruf holt nur diese nach."""
    south, west, north, east = config.BONN_BBOX
    tiles = [(round(s, 2), round(w, 2), round(min(s + step, north), 2), round(min(w + step, east), 2))
             for s in _frange(south, north, step) for w in _frange(west, east, step)]
    ways, missing = {}, []
    for i, tile in enumerate(tiles, 1):
        elements, miss = _tile_ways(*tile)
        missing += miss
        for el in elements:
            if el.get("geometry"):
                ways[el["id"]] = {"id": el["id"], "name": el["tags"]["name"],
                                  "highway": el["tags"].get("highway"),
                                  "coords": [[p["lon"], p["lat"]] for p in el["geometry"]]}
        print(f"Kachel {i}/{len(tiles)}: {len(ways)} Ways, {len(miss)} Teilkacheln fehlen", flush=True)
    config.OSM_STREETS.write_text(json.dumps(
        {"ways": list(ways.values()), "missing_tiles": missing}, ensure_ascii=False))
    _stamp("osm_streets")
    print(f"{len(ways)} Ways → {config.OSM_STREETS}; fehlende Teilkacheln: {len(missing)}")


def _frange(start, stop, step):
    x = start
    while x < stop - 1e-9:
        yield x
        x += step


def fetch_all():
    fetch_papers()
    fetch_organizations()
    fetch_consultations_lite()
    fetch_meetings()
    fetch_streets()
