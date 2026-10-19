"""Phase 0 Soll-Modell: zustaendigkeitsordnung.json (bonn-entscheidet) gegen die Seite der Stadt Bonn abgleichen.
Aufruf: python soll/phase0/scripts/zusto_abgleich.py <bonn-entscheidet> <zusto.txt (Text der Seite)>"""
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "out"
ART = {"Anhörung", "Empfehlung", "Entscheidung", "Mitteilung", "Genehmigung", "Vorberatung", "Kenntnisnahme"}
norm = lambda s: re.sub(r"\s+", " ", s or "").strip().rstrip(".")


def parse(text):
    """Ausschuss (römische Ziffer) → {Nr: (Art, Inhalt)} aus dem Seitentext (Zeilen Nr / Art / Inhalt …).
    Mehrzeilige Inhalte (Aufzählungen) werden bis zur nächsten Nummer zusammengefügt; „Mitteilungen“ = Mitteilung."""
    out, cur = {}, None
    lines = [l.strip() for l in text.splitlines()]
    starts = []
    for i, l in enumerate(lines):
        m = re.match(r"^([IVX]+)\. (.+)$", l)
        if m:
            cur = m.group(1)
            out[cur] = {}
            starts.append(i)
            continue
        art = lines[i + 1].rstrip("en") if i + 1 < len(lines) and lines[i + 1].rstrip("en") in ART else (
            lines[i + 1] if i + 1 < len(lines) and lines[i + 1] in ART else None)
        if cur and art and re.fullmatch(r"\d+\.[a-z0-9]+", l):
            j, body = i + 2, []
            while j < len(lines) and not re.fullmatch(r"\d+\.[a-z0-9]+", lines[j]) and not re.match(r"^[IVX]+\. ", lines[j]) \
                    and not lines[j].startswith("Merken"):
                body.append(lines[j])
                j += 1
            out[cur][l] = (art, " ".join(body))
            starts.append(i)
    return out


def main(be, page):
    z = json.loads((Path(be) / "data" / "zustaendigkeitsordnung.json").read_text(encoding="utf-8"))
    site = parse(Path(page).read_text(encoding="utf-8"))
    rows, stats = [], {"json": 0, "seite": sum(len(v) for v in site.values()), "gleich": 0, "art_abweichend": 0,
                       "inhalt_abweichend": 0, "fehlt_auf_seite": 0}
    for a in z["ausschuesse"]:
        s = site.get(a["nr"], {})
        for r in a["rechte"]:
            stats["json"] += 1
            got = s.get(r["nr"])
            if not got:
                stats["fehlt_auf_seite"] += 1
                rows.append((a["nr"], r["nr"], "fehlt auf Seite", r["inhalt"][:120]))
            elif got[0] != r["art"]:
                stats["art_abweichend"] += 1
                rows.append((a["nr"], r["nr"], f"Art {r['art']} ≠ {got[0]}", r["inhalt"][:120]))
            elif norm(got[1]) != norm(r["inhalt"]):
                stats["inhalt_abweichend"] += 1
                rows.append((a["nr"], r["nr"], "Inhalt abweichend", f"{r['inhalt'][:80]} | {got[1][:80]}"))
            else:
                stats["gleich"] += 1
    json_keys = {(a["nr"], r["nr"]) for a in z["ausschuesse"] for r in a["rechte"]}
    for k, v in site.items():
        for nr in v:
            if (k, nr) not in json_keys:
                rows.append((k, nr, "nur auf Seite", v[nr][1][:120]))
    stats["nur_auf_seite"] = sum(1 for r in rows if r[2] == "nur auf Seite")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "zusto_abgleich.tsv").write_text("ausschuss\tnr\tbefund\tinhalt\n" + "".join("\t".join(r) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    for r in rows[:15]:
        print(r)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
