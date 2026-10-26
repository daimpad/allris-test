"""Beschreibungen der Themenseiten (thema/<name>/): je Thema eine Datei mit Regeln, Bahnen und Texten.
Daten, Seite, Prozessbild, Kalender, Feed und Bild zum Teilen erzeugen pipeline/dossier.py und
pipeline/prozessbild.py für alle Themen gleich. Ein neues Thema erscheint erst nach Prüfung von Hand
(Phase 0, Regelentwurf, Prüfbogen; Vorgehen wie kultur/)."""
from . import kultur, verkehr

ALLE = [kultur.THEMA]
ENTWUERFE = [verkehr.THEMA]  # nur Prüfbogen (python -m pipeline verkehr-stichprobe), keine Seite, kein Export
