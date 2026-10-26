"""Themenseite „Kultur und Haushalt“ (thema/kultur-und-haushalt/): Vorlagen und Verfahren, die mit dem Haushalt
und der Kulturförderung zusammenhängen. Anlass und Prüfung: kultur/phase0/BERICHT.md, kultur/PRUEFUNG.md.

Die Zuordnung der Vorlagen zu den Strängen ist abgeleitet: feste Regeln aus Amt, Gremium, Titel und
Drucksachennummer (REGELN), je Vorlage mit Grund. Keine Bewertung, keine Beträge, keine Zitate aus den
Dokumenten; der Weg des Haushalts ist aus Mitteilungsvorlage 261064 zusammengefasst."""
import re
from datetime import date

from ..dossier import Regel, Thema, Zustaendig

BUEHNEN = "260127"     # Stammnummer „Zukunft der Bonner Bühnen“
HAUSHALT = re.compile(r"Haushaltssatzung|Haushaltssperre|haushaltswirtschaftlich|Haushaltskonsolidierung|Konsolidierung|"
                      r"Haushaltssicherung|Eckwert|Haushaltsplan|Doppelhaushalt|Nachtragshaushalt", re.I)
FINANZEN = re.compile(r"Förder|Zuschuss|Zuschüsse|Einspar|Kürzung|Gebühr|Entgelt|Wirtschaftsplan|Festbetrag|"
                      r"Gleichbehandlung|Haushalt|Finanz|Drittmittel|Budget|Kosten|Controlling", re.I)
# Prüfung im Gespräch 25.10.2026 (kultur/PRUEFUNG.md): ein Titeltreffer zieht das ganze Verfahren (Stammnummer) mit
BUEHNEN_TITEL = re.compile(r"Bühnen|Theaterliegenschaft|Schauspiel", re.I)  # „Schauspiel“ seit 25.10.2026
KULTURFEST = re.compile(r"Kulturfest|Kultur- und Begegnungsfest", re.I)
KULTUR = Zustaendig(
    aemter=("41 ", "42 ", "45 ", "46 ", "48 "),  # Kulturamt, Stadtbibliothek, Kunstmuseum, Theater, Beethovenorchester
    # Stabsstelle Beethovenhalle (Prüfung 25.10.2026) nur mit „Beethovenhalle“ im Titel: sie betreut auch den
    # Finanzausschuss (Sitzungstermine, nichtöffentliche Tagesordnungen) und das World Conference Center
    stellen_mit_titel={"II-1 Stabsstelle Konferenzzentrum/Beethovenhalle": re.compile(r"Beethovenhalle")},
    gremien=("Kulturausschuss", "Kulturkommission"))

THEMA = Thema(
    key="kultur",
    pfad="thema/kultur-und-haushalt/",
    titel="Kultur und Haushalt",
    lead="Welche Vorlagen und Verfahren hängen mit dem Haushalt der Stadt Bonn und der Kulturförderung zusammen? "
         "Diese Seite ordnet Vorlagen aus dem Ratsinformationssystem seit Beginn der Wahlperiode ({seit}) und zeigt, "
         "wann und wo darüber beraten wird.",
    seo_text="Haushalt 2027/2028 und Kulturförderung in Bonn: {n} Vorlagen aus dem Ratsinformationssystem "
             "in vier Strängen, der Weg des Haushalts und die nächsten Sitzungen.",
    seit="2025-11-01",  # Beginn der 12. Wahlperiode (legislative_terms)
    straenge=[
        ("haushalt", "Haushalt und Konsolidierung",
         "Titel nennt Haushaltssatzung, Haushaltssperre, haushaltswirtschaftliche Lage, Konsolidierung, Eckwerte o. Ä."),
        ("buehnen", "Zukunft der Bonner Bühnen",
         f"Drucksache {BUEHNEN} und ihre Folgevorlagen sowie Verfahren, in denen ein Titel „Bühnen“, "
         "„Theaterliegenschaften“ oder „Schauspiel“ nennt"),
        ("kultur_finanzen", "Kulturförderung, Zuschüsse, Gebühren",
         "Kulturamt, Stadtbibliothek, Kunstmuseum, Theater, Beethovenorchester oder Stabsstelle Beethovenhalle "
         "(nur mit „Beethovenhalle“ im Titel) federführend oder Beratung im Kulturausschuss bzw. in der Kulturkommission, und der Titel nennt Förderung, "
         "Zuschüsse, Einsparung, Gebühren, Entgelte, Wirtschaftsplan, Finanzierung, Controlling o. Ä.; dazu Verfahren, "
         "in denen ein Titel ein Kulturfest nennt"),
        ("kultur_weitere", "Weitere Vorlagen aus Kulturamt und Kulturausschuss",
         "wie zuvor, ohne Bezug zu Geld im Titel"),
    ],
    regeln=[
        Regel("buehnen", stammnummer=BUEHNEN),
        Regel("buehnen", verfahren_titel=BUEHNEN_TITEL),
        Regel("kultur_finanzen", verfahren_titel=KULTURFEST),
        Regel("haushalt", titel=HAUSHALT),
        Regel("kultur_finanzen", zustaendig=KULTUR, titel=FINANZEN, sonst="kultur_weitere"),
    ],
    eingeklappt={"kultur_weitere"},  # vollständig, auf der Seite eingeklappt (Entscheidung 25.10.2026)
    punkt_straenge=("haushalt", "buehnen", "kultur_finanzen"),
    # Prozessbild: Bahnen von oben nach unten (Schlüssel, Beschriftung) und die Gremien eigener Bahnen
    bahnen=[("plan", "Haushalt 2027/2028"), ("bv", "Bezirksvertretungen"), ("kultur", "Kulturausschuss"),
            ("fach", "andere Ausschüsse"), ("finanz", "Finanzausschuss"), ("rat", "Hauptausschuss, Rat")],
    bahn_gremien={"kultur": KULTUR.gremien},
    sitzungen=("Kulturausschuss", "Kulturkommission", "Ausschuss für Finanzen, Beteiligungen und Vergabe",
               "Hauptausschuss", "Rat"),
    sitzungen_je_gremium=2,  # Bezirksvertretungen: je eine (Haushaltsberatung und Einwohnerfragestunde, GeschO § 26)
    # Zeitachse: der Rückblick gestaucht, die Monate der Haushaltsberatung breiter
    achse=(date(2025, 11, 1), date(2027, 4, 1), date(2026, 9, 1), 0.42),
    # Phasen des Haushalts 2027/2028 laut Terminplan in 261064 (geplant, abgeleitet): oben der Ablauf im Ganzen,
    # darunter die Gremien, in denen beraten wird (Bahn, von, bis, Beschriftung, nicht öffentlich)
    terminplan="261064",
    phasen=[("plan", "2026-02-27", "2026-09-30", "Aufstellung in der Verwaltung", True),
            ("plan", "2026-10-01", "2026-11-30", "Einbringung, Beratung", False),
            ("plan", "2026-12-01", "2026-12-31", "Beschluss", False),
            ("plan", "2027-01-01", "2027-03-31", "Genehmigung", False),
            ("bv", "2026-10-01", "2026-11-30", "Beratung des Haushalts", False),
            ("kultur", "2026-10-01", "2026-11-30", "Beratung des Haushalts", False),
            ("fach", "2026-10-01", "2026-11-30", "Beratung des Haushalts", False),
            ("finanz", "2026-11-01", "2026-11-30", "Vorberatung für den Rat", False),
            ("rat", "2026-10-01", "2026-11-15", "Einbringung des Entwurfs", False),
            ("rat", "2026-12-01", "2026-12-31", "Beschluss der Haushaltssatzung", False)],
    phasen_text="Der Haushalt 2027/2028 wird laut Terminplan von Oktober bis Dezember 2026 beraten und im Dezember "
                "im Rat beschlossen.",
    fenster_text="Zeitraum der Haushaltsberatung",
    # Weg des Haushalts 2027/2028: zusammengefasst aus Mitteilungsvorlage 261064 und ihrer Anlage (Terminplan),
    # selbst formuliert, ohne Zitate (Rahmen der Stadt Bonn vom 19.10.2026)
    schritte_titel="So entsteht der Haushalt 2027/2028",
    schritte=[
        ("Aufstellung in der Verwaltung", "Frühjahr und Sommer 2026",
         "Die Ämter melden ihren Bedarf im Rahmen von Eckwerten je Amt und Dezernat; Mehrbedarf ist innerhalb des "
         "Dezernats auszugleichen. Der Verwaltungsvorstand bespricht Härtefälle. Dieser Teil ist nicht öffentlich."),
        ("Einbringung des Entwurfs", "Herbst 2026",
         "Die Verwaltung legt dem Rat den Entwurf des Haushaltsplans vor; die Mitglieder der Ausschüsse erhalten die Unterlagen."),
        ("Beratung in den Fachausschüssen und Bezirksvertretungen", "Oktober und November 2026",
         "Jedes Fachgremium berät den Entwurf einmal, für die Kultur der Kulturausschuss. Fraktionen können "
         "Änderungsanträge stellen."),
        ("Ausschuss für Finanzen, Beteiligungen und Vergabe", "November 2026",
         "Er tagt nach den Fachgremien und bereitet den Beschluss des Rates vor."),
        ("Beschluss im Rat", "Dezember 2026",
         "Etwa zwei Wochen nach dem Finanzausschuss beschließt der Rat die Haushaltssatzung."),
        ("Kommunalaufsicht", "Anfang 2027",
         "Die Satzung geht an die Bezirksregierung Köln; die Genehmigung erwartet die Verwaltung im ersten Quartal 2027."),
    ],
    # Vergleich: Zahl der Vorlagen im Verfahren zur Haushaltssatzung 2025/2026
    vergleich="240986",
    vergleich_text="Zum Vergleich: Zum Doppelhaushalt 2025/2026 ({ref}) gehören im Ratsinformationssystem "
                   "{n} Vorlagen, vor allem Änderungsanträge und Stellungnahmen der Verwaltung.",
    hinweis="Zuordnung zu den Strängen abgeleitet (feste Regeln, je Vorlage mit Grund); Schritte des Haushalts aus "
            "Drucksache 261064 zusammengefasst, keine Zitate",
    bild_titel="Zeitleiste: Haushalt und Kultur in Rat, Ausschüssen und Bezirksvertretungen",
    feed_text="zu Haushalt und Kultur",
    pruefung_text="Eine Stichprobe von 30 Vorlagen wurde am 25.10.2026 von Hand geprüft (keine unpassend), danach "
                  "wurden die Regeln ergänzt.",
    nicht_gezeigt=[
        "<strong>Beträge:</strong> Zahlen je Einrichtung stehen in den Dokumenten der Vorlagen und im Haushaltsplan "
        "der Stadt (Produktbereich 1.04 Kultur und Wissenschaft, auf bonn.de), nicht in den Daten des "
        "Ratsinformationssystems. Die Seite übernimmt keine Beträge.",
        "<strong>Vorbereitung in der Verwaltung:</strong> Eckwerte, Aufgabenkritik und Beratungen des "
        "Verwaltungsvorstands sind nicht öffentlich.",
        "<strong>Nichtöffentliche Beratungen</strong> und Vorlagen, deren Titel keines der Merkmale nennt, fehlen.",
    ],
    # Prüfbogen (einmalig): je Strang einige zugeordnete Vorlagen, dazu eine Gegenprobe nicht zugeordneter
    # Vorlagen mit Kulturbezug im Titel; Sportplätze und Straßennamen nicht
    stichprobe_je_strang={"haushalt": 4, "buehnen": 4, "kultur_finanzen": 7, "kultur_weitere": 7},
    stichprobe_ohne=8,
    kandidat=re.compile(r"Kultur|Theater|Museum|Bibliothek|Oper\b|Musik(?!erviertel)|Kunst(?!rasen)|Beethoven|Bühne|"
                        r"Festival|Konzert|Orchester", re.I),
)
