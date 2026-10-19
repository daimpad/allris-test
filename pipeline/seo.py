"""Auffindbarkeit der Seite: robots.txt, sitemap.xml und absolute Adressen (canonical, Open Graph,
strukturierte Daten, Fehlerseite) für die öffentliche Adresse SITE_URL.

Die Quelldateien in site/ enthalten die Adresse von GitHub Pages; dieser Schritt ersetzt sie in der
zusammengestellten Seite (_site), damit ein Wechsel auf die eigene Domain nur SITE_URL braucht.
Ohne Zeitstempel (kein lastmod), damit sich der Branch deploy nur bei Inhaltsänderungen ändert."""
from pathlib import Path
from xml.sax.saxutils import escape

from . import config

DEFAULT_URL = "https://daimpad.github.io/allris-test/"
PAGES = ("index.html", "404.html")


def robots(site_url):
    return f"User-agent: *\nAllow: /\n\nSitemap: {site_url}sitemap.xml\n"


def sitemap(site_url):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"  <url><loc>{escape(site_url)}</loc><changefreq>daily</changefreq></url>\n"
            "</urlset>\n")


def write(site=Path("_site"), site_url=None):
    site_url = site_url or config.SITE_URL
    if not site_url.endswith("/"):
        site_url += "/"
    for name in PAGES:
        page = site / name
        if page.exists():
            page.write_text(page.read_text(encoding="utf-8").replace(DEFAULT_URL, site_url), encoding="utf-8")
    (site / "robots.txt").write_text(robots(site_url), encoding="utf-8")
    (site / "sitemap.xml").write_text(sitemap(site_url), encoding="utf-8")
    print(f"robots.txt, sitemap.xml und Adressen für {site_url}")
