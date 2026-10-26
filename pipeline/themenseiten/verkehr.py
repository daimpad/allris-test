"""Themenseite „Verkehr und Mobilität“ (thema/verkehr-und-mobilitaet/), ENTWURF: noch nicht in ALLE, erscheint
erst nach Prüfung des Prüfbogens im Gespräch. Phase 0 und Entscheidungen: verkehr/phase0/BERICHT.md.

Grundlage ist die abgeleitete Themenzuordnung „Verkehr und Mobilität“ (topics.py: Amt 61-3 Stadtverkehr und 66,
Ausschuss für Mobilität und Verkehr, Stichwörter). Stränge nach Wörtern im Titel, die Sperrung der Nordbrücke als
ganzes Verfahren; alle übrigen Vorlagen des Themas nach Stadtbezirk. Keine Bewertung, keine Beträge, keine Zitate."""
import re
from datetime import date

from ..dossier import Regel, Thema
from . import haushalt

# Vergabe der Grünpflege an Straßen („Verkehrsgrün“) gehört nicht zum Thema (Phase 0: 7 Vorlagen)
AUSSCHLUSS = re.compile(r"Verkehrsgrün|Straßenbegleitgrün|Landschaftsgärtnerische Pflege|Verkehrssicherung und "
                        r"Unterhalt", re.I)
NORDBRUECKE = re.compile(r"Nordbrücke", re.I)  # auch „Nordbrückensperrung“, „Nordbrücken-Sperrung“
BUS_BAHN = re.compile(r"ÖPNV|ÖSPV|Nahverkehr|\bBus(?!iness)|Busse|Haltestelle|Stadtbahn|Straßenbahn|Seilbahn|S-Bahn|"
                      r"Regionalbahn|Bahnhof|Schienen|Fahrplan|\bTakt|\bLinie|\bSB ?\d|Ticket|Rufbus|On-Demand|"
                      r"Stadtwerke|SWB", re.I)
# Parken vor Rad und Fuß (Gehwegparken), aber nicht Fahrradparken
PARKEN = re.compile(r"(?<!fahrrad)(?<!rad)park(?:en|platz|plätz|raum|haus|häus|gebühr|schein|verbot|druck|situation|"
                    r"möglichkeit|zone)|Bewohnerpark|Anwohnerpark|Halteverbot|Stellpl(?:atz|ätz)|Ladezone|Lieferzone",
                    re.I)
RAD_FUSS = re.compile(r"\bRad(?:verkehr|weg|fahr|streifen|schnell|spur|station|abstell|bügel|route|netz|parken|achse|"
                      r"pendler|wege)|Fahrrad|Lastenrad|Fußverkehr|Fußgänger|Fußweg|Gehweg|Zebrastreifen|Querung|"
                      r"Bürgersteig|Gehsteig|E-Scooter|Scooter", re.I)
MOBIL = ("Ausschuss für Mobilität und Verkehr",)

THEMA = Thema(
    key="verkehr",
    pfad="thema/verkehr-und-mobilitaet/",
    titel="Verkehr und Mobilität",
    lead="Welche Vorlagen und Verfahren betreffen Verkehr und Mobilität in Bonn, darunter die Sperrung der "
         "Nordbrücke? Diese Seite ordnet Vorlagen aus dem Ratsinformationssystem seit Beginn der Wahlperiode "
         "({seit}) und zeigt, wann und wo darüber beraten wird.",
    seo_text="Verkehr und Mobilität in Bonn: {n} Vorlagen aus dem Ratsinformationssystem zur Sperrung der "
             "Nordbrücke, zu Bus und Bahn, Rad- und Fußverkehr und Parken, mit den nächsten Sitzungen.",
    seit="2025-11-01",  # Beginn der 12. Wahlperiode (legislative_terms)
    straenge=[
        ("nordbruecke", "Sperrung der Nordbrücke",
         "Vorlagen, deren Titel die Nordbrücke nennt, und ganze Verfahren, deren Stammvorlage sie nennt (auch "
         "außerhalb der Themenzuordnung)"),
        ("bus_bahn", "Bus und Bahn",
         "Thema Verkehr und Mobilität, und der Titel nennt ÖPNV, Nahverkehr, Bus, Haltestelle, Stadtbahn, Seilbahn, "
         "Bahnhof, Fahrplan, Takt, Linie, Ticket o. Ä."),
        ("parken", "Parken",
         "Thema Verkehr und Mobilität, und der Titel nennt Parken, Parkplätze, Parkraum, Parkgebühren, "
         "Bewohnerparken, Halteverbot, Stellplätze o. Ä. (nicht Fahrradparken)"),
        ("rad_fuss", "Rad- und Fußverkehr",
         "Thema Verkehr und Mobilität, und der Titel nennt Radverkehr, Radwege, Fahrrad, Fußverkehr, Gehwege, "
         "Zebrastreifen, Querungen, E-Scooter o. Ä."),
        ("weitere", "Weitere Vorlagen zu Verkehr und Mobilität",
         "Thema Verkehr und Mobilität ohne die Merkmale der anderen Stränge; nach Stadtbezirk"),
    ],
    regeln=[
        # ganzes Verfahren nur, wenn die Stammvorlage die Nordbrücke nennt (sonst zöge ein Änderungsantrag zum
        # Nahverkehrsplan das ganze Verfahren mit); einzelne Vorlagen über den Titel
        Regel("nordbruecke", verfahren_titel=NORDBRUECKE, nur_stammvorlage=True),
        Regel("nordbruecke", titel=NORDBRUECKE),
        Regel("bus_bahn", thema="verkehr", titel=BUS_BAHN),
        Regel("parken", thema="verkehr", titel=PARKEN),
        Regel("rad_fuss", thema="verkehr", titel=RAD_FUSS),
        Regel("weitere", thema="verkehr"),
    ],
    ausschluss=AUSSCHLUSS,
    nach_bezirk=frozenset({"weitere"}),  # vollständig, je Stadtbezirk eingeklappt (Entscheidung 26.10.2026)
    punkt_straenge=("nordbruecke", "bus_bahn", "parken", "rad_fuss", "weitere"),
    # Punkte im Bild nur mit Beratung in Rat, Hauptausschuss oder Mobilitätsausschuss (Entscheidung 26.10.2026)
    punkt_gremien=("Rat", "Hauptausschuss") + MOBIL,
    bahnen=[haushalt.BAHN, ("bv", "Bezirksvertretungen"), ("mobil", "Mobilitätsausschuss"),
            ("fach", "andere Ausschüsse"), ("finanz", "Finanzausschuss"), ("rat", "Hauptausschuss, Rat")],
    bahn_gremien={"mobil": MOBIL},
    sitzungen=MOBIL + ("Ausschuss für Finanzen, Beteiligungen und Vergabe", "Hauptausschuss", "Rat"),
    sitzungen_je_gremium=2,
    achse=(date(2025, 11, 1), date(2027, 4, 1), date(2026, 9, 1), 0.42),
    # Haushalt 2027/2028 laut Terminplan in 261064 (themenseiten/haushalt.py; Entscheidung 26.10.2026)
    terminplan=haushalt.TERMINPLAN,
    phasen=haushalt.phasen("mobil"),
    phasen_text=haushalt.TEXT,
    fenster_text=haushalt.FENSTER,
    schritte_titel=haushalt.TITEL,
    schritte=haushalt.schritte("für Verkehr der Ausschuss für Mobilität und Verkehr"),
    hinweis="Zuordnung zu den Strängen abgeleitet (feste Regeln aus der Themenzuordnung und Wörtern im Titel, je "
            "Vorlage mit Grund); Schritte des Haushalts aus Drucksache 261064 zusammengefasst, keine Zitate",
    bild_titel="Zeitleiste: Verkehr und Mobilität in Rat, Hauptausschuss und Mobilitätsausschuss",
    feed_text="zu Verkehr und Mobilität",
    pruefung_text="Die Zuordnung ist noch nicht von Hand geprüft.",
    nicht_gezeigt=[
        "<strong>Beträge:</strong> Kosten von Maßnahmen stehen in den Dokumenten der Vorlagen und im Haushaltsplan "
        "der Stadt, nicht in den Daten des Ratsinformationssystems. Die Seite übernimmt keine Beträge.",
        "<strong>Örtliche Vorgänge</strong> stehen nach Stadtbezirk, ohne Hausnummern; einzelne Straßen und Orte "
        "zeigt die Karte.",
        "<strong>Nichtöffentliche Beratungen</strong> und Vorlagen außerhalb der Themenzuordnung fehlen, außer zur "
        "Nordbrücke.",
    ],
    # Prüfbogen (einmalig): je Strang einige zugeordnete Vorlagen, dazu eine Gegenprobe nicht zugeordneter
    # Vorlagen mit Verkehrsbezug im Titel
    stichprobe_je_strang={"nordbruecke": 4, "bus_bahn": 5, "parken": 5, "rad_fuss": 5, "weitere": 5},
    stichprobe_ohne=6,
    kandidat=re.compile(r"Verkehr|Mobilität|Straße|Radweg|Fahrrad|Gehweg|\bBus|Bahn|Haltestelle|Parken|Parkpl|Ampel|"
                        r"Kreuzung|Tempo", re.I),
)
