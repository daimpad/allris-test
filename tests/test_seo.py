import json
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from pipeline import seo

SITE = Path(__file__).resolve().parent.parent / "site"


class Head(HTMLParser):
    """Sammelt meta-, link- und JSON-LD-Angaben aus dem Kopf von index.html."""

    def __init__(self):
        super().__init__()
        self.meta, self.links, self.ld, self._ld = {}, [], [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            self.meta[a.get("name") or a.get("property") or a.get("http-equiv")] = a.get("content")
        if tag == "link":
            self.links.append(a)
        self._ld = tag == "script" and a.get("type") == "application/ld+json"

    def handle_data(self, data):
        if self._ld and data.strip():
            self.ld.append(data)

    def handle_endtag(self, tag):
        self._ld = False


def head(text):
    h = Head()
    h.feed(text)
    return h


class Auffindbarkeit(unittest.TestCase):
    def test_kopf_vollstaendig(self):
        h = head((SITE / "index.html").read_text(encoding="utf-8"))
        for key in ("description", "robots", "theme-color", "og:title", "og:description", "og:url", "og:image",
                    "og:image:alt", "twitter:card", "author"):
            self.assertTrue(h.meta.get(key), key)
        self.assertLessEqual(len(h.meta["description"]), 170)
        rels = {link["rel"] for link in h.links}
        self.assertTrue({"canonical", "icon", "apple-touch-icon", "manifest"} <= rels)
        data = json.loads(h.ld[0])
        self.assertEqual({x["@type"] for x in data["@graph"]}, {"WebSite", "WebApplication"})

    def test_dateien_vorhanden(self):
        h = head((SITE / "index.html").read_text(encoding="utf-8"))
        local = [link["href"] for link in h.links if link["rel"] in ("icon", "apple-touch-icon", "manifest")]
        local.append(h.meta["og:image"].removeprefix(seo.DEFAULT_URL))
        manifest = json.loads((SITE / "site.webmanifest").read_text(encoding="utf-8"))
        local += [i["src"] for i in manifest["icons"]]
        for path in local:
            self.assertTrue((SITE / path).is_file(), path)

    def test_adressen_robots_sitemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            for name in seo.PAGES:
                shutil.copy(SITE / name, site / name)
            seo.write(site, "https://ris-bonn.example/")
            for name in seo.PAGES:
                text = (site / name).read_text(encoding="utf-8")
                self.assertNotIn(seo.DEFAULT_URL, text, name)
                self.assertIn("https://ris-bonn.example/", text)
            h = head((site / "index.html").read_text(encoding="utf-8"))
            self.assertEqual(next(x["href"] for x in h.links if x["rel"] == "canonical"), "https://ris-bonn.example/")
            json.loads(h.ld[0])  # bleibt gültiges JSON
            robots = (site / "robots.txt").read_text(encoding="utf-8")
            self.assertIn("Sitemap: https://ris-bonn.example/sitemap.xml", robots)
            urls = [e.text for e in ET.parse(site / "sitemap.xml").getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
            self.assertEqual(urls, ["https://ris-bonn.example/", "https://ris-bonn.example/datenschutz.html"])
            self.assertIsNone(re.search(r"lastmod", (site / "sitemap.xml").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
