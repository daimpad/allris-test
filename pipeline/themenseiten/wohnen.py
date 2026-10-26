"""Themenseite „Wohnen und Bauen“ (thema/wohnen-und-bauen/), ENTWURF: noch nicht in ALLE, erscheint erst nach
Prüfung des Prüfbogens im Gespräch. Phase 0 und Entscheidungen: wohnen/phase0/BERICHT.md.

Eigene Regeln statt der Themenzuordnung „Bauen“ (dort stehen auch Schulen, Bühnen und Sporthallen des
Gebäudemanagements; Wohnen liegt oft beim Thema Soziales): Wörter im Titel für Bauleitplanung, „Bau-Turbo“,
Wohnraum und Denkmalschutz, übrige Vorlagen aus Stadtplanungsamt, Bodenmanagement, Bauordnungsamt und
Planungsausschuss nach Stadtbezirk (Entscheidung 26.10.2026). Keine Bewertung, keine Beträge, keine Zitate."""
import re
from datetime import date

from ..dossier import Regel, Thema, Zustaendig
from . import haushalt

PLANUNG = "Ausschuss für Planen, Bauen und Denkmalschutz"
SOZIAL = "Ausschuss für Soziales, Migration, Gesundheit, Wohnen und Senioren"
# „Bau-Turbo“ (§ 246e BauGB, Zustimmung nach § 36a) und Beschleunigung der Bauleitplanung; vor Bebauungsplänen
TURBO = re.compile(r"Bau-?Turbo|§ ?36a|§ ?246e|Planungsturbo|Verfahrensbeschleunigung", re.I)
PLAN = re.compile(r"Bebauungsplan|Flächennutzungsplan|Veränderungssperre|Bauleitplan|vorhabenbezogene", re.I)
# Wohnraum einschließlich Wohnungslosigkeit (Entscheidung 26.10.2026); nicht „Miet…“ allein (Fahrradmietsystem,
# Anmietung), nicht „Wohngebiet“ (Tempo 30 u. Ä.)
WOHNRAUM = re.compile(r"Wohnungsbau|Wohnraum|geförderte[nmrs]? Wohn|Sozialwohnung|bezahlbare[nmrs]? Wohn|VEBOWAG|"
                      r"Vereinigte Bonner Wohnungs|Wohnungsbaugenossenschaft|wohnbaulich|Wohnungsmarkt|Mietspiegel|"
                      r"Mietpreis|Mietwohn|Leerstand|Zweckentfremd|Wohnungslos|Obdachlos|Housing First|Wohnungsnot|"
                      r"Wohnbau|Wohnquartier|Wohnungen|Wohnheim|Handlungskonzept Wohnen|Wohnen in Bonn", re.I)
DENKMAL = re.compile(r"(?<!Bauen und )Denkmal", re.I)  # nicht der Name des Planungsausschusses
# Sammellisten nichtöffentlicher Punkte, Formalien; „Miet…“ ohne Wohnbezug; Gebäude der Stadt, die auf der
# Kulturseite stehen (Bühnen, Beethovenhalle)
AUSSCHLUSS = re.compile(r"Tagesordnungspunkte in nichtöffentlicher Sitzung|Bestellung der Schriftführung|"
                        r"Sitzungstermine|Fahrradmiet|Anmietung|Mietzuschuss|mietzinsfrei|Wohnmobil|Bonner Bühnen|"
                        r"Theaterliegenschaft|Beethovenhalle", re.I)
# Stadtplanungsamt (ohne Abteilung Stadtverkehr, siehe ohne_thema), Bodenmanagement, Bauordnungsamt, Planungsausschuss
BAUEN = Zustaendig(aemter=("61 ", "62 ", "63 "), gremien=(PLANUNG,))

THEMA = Thema(
    key="wohnen",
    pfad="thema/wohnen-und-bauen/",
    titel="Wohnen und Bauen",
    lead="Welche Vorlagen und Verfahren betreffen Wohnen und Bauen in Bonn – Bebauungspläne, Wohnraum, den "
         "„Bau-Turbo“ und Denkmalschutz? Diese Seite ordnet Vorlagen aus dem Ratsinformationssystem seit Beginn der "
         "Wahlperiode ({seit}) und zeigt, wann und wo darüber beraten wird. Gebäude der Stadt wie Schulen und "
         "Bühnen gehören nicht dazu.",
    seo_text="Wohnen und Bauen in Bonn: {n} Vorlagen aus dem Ratsinformationssystem zu Bebauungsplänen, Wohnraum, "
             "„Bau-Turbo“ und Denkmalschutz, mit den nächsten Sitzungen.",
    seit="2025-11-01",  # Beginn der 12. Wahlperiode (legislative_terms)
    straenge=[
        ("turbo", "„Bau-Turbo“ und schnellere Planung",
         "Titel nennt den „Bau-Turbo“, § 36a oder § 246e BauGB, den „Planungsturbo“ oder eine Verfahrensbeschleunigung"),
        ("bebauungsplan", "Bebauungspläne",
         "Titel nennt einen Bebauungsplan, den Flächennutzungsplan, eine Veränderungssperre oder die Bauleitplanung"),
        ("wohnraum", "Wohnraum",
         "Titel nennt Wohnungsbau, Wohnraum, geförderte oder bezahlbare Wohnungen, die VEBOWAG, Mietspiegel, "
         "Leerstand, Zweckentfremdung, das Handlungskonzept Wohnen oder Wohnungslosigkeit (auch Housing First)"),
        ("denkmal", "Denkmalschutz",
         "Titel nennt Denkmalschutz, ein Denkmal oder eine Denkmalbereichssatzung (nicht Verkehr)"),
        ("weitere", "Weitere Vorlagen zu Planen und Bauen",
         "Stadtplanungsamt (ohne Verkehr), Bodenmanagement oder Bauordnungsamt federführend oder Beratung im "
         "Ausschuss für Planen, Bauen und Denkmalschutz, ohne die Merkmale der anderen Stränge; nach Stadtbezirk"),
    ],
    regeln=[
        Regel("turbo", titel=TURBO),
        Regel("bebauungsplan", titel=PLAN),
        Regel("wohnraum", titel=WOHNRAUM),
        Regel("denkmal", titel=DENKMAL, ohne_thema="verkehr"),  # nicht Tempo 30 an einem Denkmal
        Regel("weitere", zustaendig=BAUEN, ohne_thema="verkehr"),
    ],
    ausschluss=AUSSCHLUSS,
    nach_bezirk=frozenset({"weitere"}),  # je Stadtbezirk eingeklappt (Entscheidung 26.10.2026)
    punkt_straenge=("turbo", "bebauungsplan", "wohnraum", "denkmal", "weitere"),
    # Punkte im Bild nur mit Beratung in Rat, Hauptausschuss, Planungsausschuss oder Sozialausschuss (Wohnen)
    punkt_gremien=("Rat", "Hauptausschuss", PLANUNG, SOZIAL),
    bahnen=[haushalt.BAHN, ("bv", "Bezirksvertretungen"), ("planung", "Planungsausschuss"),
            ("fach", "andere Ausschüsse"), ("finanz", "Finanzausschuss"), ("rat", "Hauptausschuss, Rat")],
    bahn_gremien={"planung": (PLANUNG,)},
    sitzungen=(PLANUNG, SOZIAL, "Ausschuss für Finanzen, Beteiligungen und Vergabe", "Hauptausschuss", "Rat"),
    sitzungen_je_gremium=2,
    achse=(date(2025, 11, 1), date(2027, 4, 1), date(2026, 9, 1), 0.42),
    # Haushalt 2027/2028 laut Terminplan in 261064 (themenseiten/haushalt.py)
    terminplan=haushalt.TERMINPLAN,
    phasen=haushalt.phasen("planung"),
    phasen_text=haushalt.TEXT,
    fenster_text=haushalt.FENSTER,
    schritte_titel=haushalt.TITEL,
    schritte=haushalt.schritte("für Planen und Bauen der Ausschuss für Planen, Bauen und Denkmalschutz"),
    hinweis="Zuordnung zu den Strängen abgeleitet (feste Regeln aus Amt, Gremium und Wörtern im Titel, je Vorlage "
            "mit Grund); Schritte des Haushalts aus Drucksache 261064 zusammengefasst, keine Zitate",
    bild_titel="Zeitleiste: Wohnen und Bauen in Rat, Hauptausschuss, Planungs- und Sozialausschuss",
    feed_text="zu Wohnen und Bauen",
    pruefung_text="Die Zuordnung ist noch nicht von Hand geprüft.",
    nicht_gezeigt=[
        "<strong>Beträge und Mieten:</strong> Kosten, Fördersummen und Mietpreise stehen in den Dokumenten der "
        "Vorlagen, nicht in den Daten des Ratsinformationssystems. Die Seite übernimmt keine Beträge.",
        "<strong>Bebauungspläne auf der Karte:</strong> Geltungsbereich und Planchronik rechtskräftiger Pläne zeigt "
        "die Ebene „Bebauungspläne“ der <a href=\"../../?plaene=1\">Karte</a>.",
        "<strong>Gebäude der Stadt</strong> (Schulen, Bühnen, Sporthallen) und Vorlagen zum Verkehr stehen auf den "
        "jeweiligen Themenseiten. Nichtöffentliche Beratungen fehlen.",
    ],
    # Prüfbogen (einmalig): je Strang einige zugeordnete Vorlagen, dazu eine Gegenprobe nicht zugeordneter
    # Vorlagen mit Bezug zu Wohnen oder Bauen im Titel
    stichprobe_je_strang={"turbo": 5, "bebauungsplan": 5, "wohnraum": 5, "denkmal": 5, "weitere": 5},
    stichprobe_ohne=5,
    kandidat=re.compile(r"Wohn|Bauvor|Bauantrag|Baugenehmigung|Grundstück|Quartier|Städtebau|Stadtentwicklung|"
                        r"Rahmenplan|Nachverdichtung|Baulücke|Erhaltungssatzung|Gestaltungssatzung|Neubaugebiet", re.I),
)
