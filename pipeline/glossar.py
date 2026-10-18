"""Glossar für Seite und Ratsassistent (data/export/glossar.json, eine Quelle für beide).

- ergebnisse: Ergebnistexte und Rollen der Beratung, wie sie wörtlich in den Quellen stehen
- hinweise: Erläuterungen zu Prozessschritten (Schlüssel `note` in den Exporten, process.NOTES)
- schritte, evidenz, staende: Bezeichnungen der Prozessebene (process.py)
- themen: Bezeichnungen der abgeleiteten Themen (topics.py)
- begriffe: allgemeine Begriffe mit Fundstelle (Gemeindeordnung NRW bzw. Datenfeld); allgemeine
  Erklärungen, keine Rechtsberatung"""
from . import process as proc, topics

ERGEBNISSE = {
    "ungeändert beschlossen": "Das Gremium hat dem Vorschlag in der vorgelegten Fassung zugestimmt.",
    "geändert beschlossen": "Das Gremium hat zugestimmt, aber mit Änderungen, etwa aus Änderungsanträgen.",
    "zur Kenntnis genommen": "Das Gremium wurde informiert; über einen Beschluss wurde nicht abgestimmt.",
    "abgelehnt": "Die Mehrheit des Gremiums hat dagegen gestimmt.",
    "vertagt": "Die Beratung wurde auf eine spätere Sitzung verschoben.",
    "zurückgezogen": "Die Einreichenden haben die Vorlage zurückgenommen.",
    "verwiesen": "Die Vorlage wurde zur Beratung an ein anderes Gremium weitergegeben.",
    "nicht abgestimmt": "In dieser Sitzung fand keine Abstimmung statt.",
    "ohne Votum": "Das Gremium hat keine Empfehlung abgegeben.",
    "erledigt durch Stellungnahme der Verwaltung": "Der Antrag gilt als erledigt, weil die Verwaltung schriftlich "
                                                   "Stellung genommen hat.",
    "bei Anerkennung der Tagesordnung nicht aufgenommen oder vertagt": "Der Punkt wurde zu Beginn der Sitzung von der "
                                                                       "Tagesordnung genommen oder verschoben.",
    "mit Protokollnotiz": "Zusätzlich wurde eine Anmerkung ins Protokoll aufgenommen.",
    "mit Maßgabe": "Der Beschluss gilt mit einer zusätzlichen Bedingung oder Vorgabe.",
    "Entscheidung": "Dieses Gremium entscheidet abschließend.",
    "Empfehlung": "Das Gremium berät vor und gibt eine Empfehlung an das entscheidende Gremium.",
    "Anhörung": "Das Gremium wird angehört; seine Stellungnahme ist nicht bindend.",
    "Kenntnisnahme": "Das Gremium wird informiert.",
}

SCHRITTE = {
    "initiierung": "Initiierung", "vorbereitung": "Vorbereitung", "veroeffentlichung": "Datum der Vorlage",
    "beratung": "Beratung", "entscheidung": "Entscheidung", "folgevorlage": "Folgevorlage", "vollzug": "Vollzug",
}

EVIDENZ = {  # Wortlaut wie in der Legende der Seite
    "belegt": "Als Datenobjekt in der Quelle vorhanden.",
    "abgeleitet": "Aus Quelldaten erschlossen (z. B. Verknüpfung mit OParl-Lite, Titelmuster).",
    "nicht_öffentlich": "Findet regelmäßig statt, ist von außen aber nicht einsehbar.",
    "unklar": "Ob und wann der Schritt stattfindet, lässt sich aus öffentlichen Quellen nicht bestimmen.",
    "soll": "Nach Regelwerk zu erwarten, aber nicht dokumentiert (noch nicht modelliert).",
}

STAENDE = {
    "entschieden": "Eine entscheidende Beratung hat ein abschließendes Ergebnis.",
    "beraten, ohne Entscheidung": "Alle Beratungen sind abgeschlossen, keine davon war entscheidend "
                                  "(z. B. Mitteilungen, die zur Kenntnis genommen wurden).",
    "in Beratung": "Mindestens eine Beratung hat ein Ergebnis, andere stehen aus oder wurden vertagt.",
    "offen": "Noch keine Beratung mit Ergebnis.",
    "ohne Beratungsfolge": "Für die Vorlage ist keine Beratung in einem Gremium erfasst.",
}

DATENFELD = "Ratsinformationssystem der Stadt Bonn (OParl-API)"
ALLGEMEIN = "allgemeine Erklärung"
BEGRIFFE = [
    ("Vorlage", "Schriftstück, über das Rat, Bezirksvertretungen oder Ausschüsse beraten, etwa ein Antrag, eine "
                "Beschlussvorlage oder ein Bürgerantrag.", DATENFELD + ", Objekt „Paper“"),
    ("Drucksachennummer", "Kennung einer Vorlage, z. B. 261798. Zusätze wie „-01“ kennzeichnen zugehörige "
                          "Folgevorlagen.", DATENFELD + ", Feld „reference“"),
    ("Beschlussvorlage", "Vorlage der Verwaltung mit einem Beschlussvorschlag, über den ein Gremium entscheidet.",
     ALLGEMEIN),
    ("Mitteilungsvorlage", "Vorlage, mit der die Verwaltung ein Gremium informiert; ein Beschluss ist nicht vorgesehen.",
     ALLGEMEIN),
    ("Antrag", "Vorlage einer Fraktion, Gruppe oder eines Mitglieds, mit der ein Gremium um einen Beschluss gebeten "
               "wird.", ALLGEMEIN),
    ("Änderungsantrag", "Antrag, der eine andere Vorlage oder einen anderen Antrag ändern will.", ALLGEMEIN),
    ("Stellungnahme der Verwaltung", "Schriftliche Antwort der Verwaltung, meist auf einen Antrag oder eine Anfrage.",
     ALLGEMEIN),
    ("Anfrage", "Fragen einer Fraktion oder eines Mitglieds an die Verwaltung (Kleine oder Große Anfrage); die "
                "Verwaltung antwortet schriftlich oder in der Sitzung.", ALLGEMEIN),
    ("Anregungen und Beschwerden (Bürgerantrag)", "Jede Person kann sich schriftlich mit Anregungen oder Beschwerden "
     "in Angelegenheiten der Gemeinde an den Rat oder die Bezirksvertretung wenden.", "§ 24 GO NRW"),
    ("Einwohnerfragestunde", "Zeit in einer Sitzung, in der Einwohnerinnen und Einwohner Fragen stellen können; "
                             "Einzelheiten regelt die Geschäftsordnung.", "Geschäftsordnung des Rates der Stadt Bonn"),
    ("Rat", "Gewählte Vertretung der Bürgerinnen und Bürger; er ist für alle Angelegenheiten der Gemeinde zuständig, "
            "soweit nichts anderes bestimmt ist.", "§ 41 GO NRW"),
    ("Bezirksvertretung", "Gewählte Vertretung eines Stadtbezirks in kreisfreien Städten; Bonn hat vier "
     "(Bonn, Bad Godesberg, Beuel, Hardtberg). Sie entscheidet über Angelegenheiten, deren Bedeutung nicht "
     "wesentlich über den Stadtbezirk hinausgeht.", "§§ 36, 37 GO NRW"),
    ("Ausschuss", "Vom Rat gebildetes Gremium, das Beschlüsse vorbereitet oder in übertragenen Angelegenheiten "
                  "selbst entscheidet.", "§§ 41, 57 GO NRW"),
    ("Hauptausschuss", "Pflichtausschuss des Rates; er stimmt die Arbeit der Ausschüsse ab und kann in dringenden "
                       "Fällen anstelle des Rates entscheiden.", "§§ 59, 60 GO NRW"),
    ("Dringlichkeitsentscheidung", "Entscheidung in dringenden Fällen ohne Sitzung des zuständigen Gremiums; sie wird "
     "dem Gremium nachträglich zur Genehmigung vorgelegt.", "§ 60 GO NRW (Rat), § 36 GO NRW (Bezirksvertretung)"),
    ("Fraktion", "Zusammenschluss von Mitgliedern des Rates oder einer Bezirksvertretung.", "§ 56 GO NRW"),
    ("Öffentlichkeit von Sitzungen", "Sitzungen des Rates sind grundsätzlich öffentlich; für einzelne Angelegenheiten "
     "kann die Öffentlichkeit ausgeschlossen werden. Inhalte nichtöffentlicher Beratungen sind nicht einsehbar.",
     "§ 48 GO NRW"),
    ("Federführendes Amt", "Amt der Verwaltung, das eine Vorlage verantwortet.", DATENFELD + ", Feld „underDirectionOf“"),
    ("Beratungsfolge", "Reihenfolge der Gremien, die eine Vorlage beraten, jeweils mit Rolle (Entscheidung, Empfehlung, "
                       "Anhörung, Kenntnisnahme).", DATENFELD + ", Objekt „Consultation“"),
    ("Tagesordnungspunkt", "Punkt der Tagesordnung einer Sitzung; über ihn wird beraten und gegebenenfalls "
                           "abgestimmt. Das Ergebnis stammt aus OParl-Lite.", DATENFELD + ", Objekt „AgendaItem“"),
]


def glossar():
    return {
        "meta": {"note": "Allgemeine Erklärungen ohne Rechtsberatung; Fundstelle je Begriff. Ergebnistexte erscheinen "
                         "wörtlich wie in den Quellen."},
        "ergebnisse": ERGEBNISSE,
        "hinweise": proc.NOTES,
        "schritte": SCHRITTE,
        "evidenz": EVIDENZ,
        "staende": STAENDE,
        "themen": dict(topics.THEMES),
        "begriffe": [{"begriff": b, "erklaerung": e, "fundstelle": f} for b, e, f in BEGRIFFE],
    }
