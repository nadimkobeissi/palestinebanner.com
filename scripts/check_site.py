#!/usr/bin/env python3
"""Check static SEO metadata, discovery files, assets, and banner consistency."""

import datetime
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import sys
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://palestinebanner.com"
PAGES = {"index.html": ORIGIN + "/", "click/index.html": ORIGIN + "/click/"}
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.metadata = {}
        self.links = {}
        self.title = ""
        self.jsonld = []
        self.capture = None
        self.feed(content)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.tags.append((tag, attrs))
        if tag == "meta":
            name = attrs.get("name", attrs.get("property"))
            if name:
                check(name not in self.metadata, f"Duplicate metadata: {name}")
                self.metadata[name] = attrs.get("content", "")
        if tag == "link":
            for rel in attrs.get("rel", "").split():
                self.links.setdefault(rel, []).append(attrs)
        if tag == "title":
            self.capture = "title"
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.capture = "jsonld"
            self.jsonld.append("")

    def handle_data(self, data):
        if self.capture == "title":
            self.title += data
        elif self.capture == "jsonld":
            self.jsonld[-1] += data

    def handle_endtag(self, tag):
        if tag in ("title", "script"):
            self.capture = None


def local_path(url, base=ORIGIN + "/"):
    parsed = urlsplit(urljoin(base, url))
    if parsed.netloc != "palestinebanner.com":
        return None
    path = ROOT / unquote(parsed.path).lstrip("/")
    if path.is_dir():
        path /= "index.html"
    check(path.is_file(), f"Missing local URL: {parsed.path}")
    return path


def png_size(path):
    if not path or not path.is_file():
        return None
    data = path.read_bytes()
    check(data[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG: {path.name}")
    return struct.unpack(">II", data[16:24]) if len(data) >= 24 else None


titles = set()
descriptions = set()
for filename, canonical in PAGES.items():
    content = (ROOT / filename).read_text()
    page = Page(content)
    prefix = filename + ": "
    titles.add(page.title)
    descriptions.add(page.metadata.get("description"))
    check(10 <= len(page.title) <= 65, prefix + "check title length")
    check(80 <= len(page.metadata.get("description", "")) <= 180, prefix + "check description length")
    check(sum(tag == "h1" for tag, _ in page.tags) == 1, prefix + "expected one H1")
    check(any(tag == "html" and attrs.get("lang") == "en" for tag, attrs in page.tags), prefix + "missing page language")
    check(page.metadata.get("author") == "Nadim Kobeissi", prefix + "missing author")
    robots = page.metadata.get("robots", "")
    check("noindex" not in robots and "index" in robots and "max-image-preview:large" in robots, prefix + "unexpected indexing policy")
    check([link.get("href") for link in page.links.get("canonical", [])] == [canonical], prefix + "canonical mismatch")
    for name in ("og:title", "og:description", "og:type", "og:site_name", "og:locale", "og:url", "og:image", "og:image:alt", "twitter:title", "twitter:description", "twitter:image", "twitter:image:alt"):
        check(bool(page.metadata.get(name)), prefix + "missing " + name)
    check(page.metadata.get("og:title") == page.title == page.metadata.get("twitter:title"), prefix + "inconsistent titles")
    check(page.metadata.get("og:url") == canonical, prefix + "Open Graph URL mismatch")
    check(page.metadata.get("twitter:card") == "summary_large_image", prefix + "missing large card")
    check(page.metadata.get("og:image") == page.metadata.get("twitter:image"), prefix + "social image mismatch")
    image = local_path(page.metadata.get("og:image", ""))
    check(png_size(image) == (1200, 630), prefix + "social image must be 1200 × 630")
    check(page.metadata.get("og:image:width") == "1200" and page.metadata.get("og:image:height") == "630", prefix + "social image dimensions mismatch")
    check(bool(page.links.get("alternate")) and bool(page.links.get("describedby")), prefix + "missing machine-readable discovery links")
    check(len(page.jsonld) == 1, prefix + "expected one JSON-LD graph")
    for raw in page.jsonld:
        try:
            structured = json.loads(raw)
        except json.JSONDecodeError as error:
            errors.append(prefix + str(error))
            continue
        check(structured.get("@context") == "https://schema.org", prefix + "incorrect JSON-LD context")
        graph = structured.get("@graph", [])
        nodes = {node.get("@id"): node for node in graph}
        check(len(nodes) == len(graph), prefix + "duplicate or missing graph IDs")
        check(any(node.get("@type") == "WebSite" and node.get("name") == "Palestine Banner" for node in graph), prefix + "missing site identity")
        webpages = [node for node in graph if node.get("@type") in ("WebPage", "CollectionPage")]
        check(len(webpages) == 1 and webpages[0].get("url") == canonical, prefix + "structured page URL mismatch")

        def inspect(value):
            if isinstance(value, list):
                for item in value:
                    inspect(item)
            elif isinstance(value, dict):
                if set(value) == {"@id"}:
                    check(value["@id"] in nodes, prefix + "unresolved graph reference " + value["@id"])
                for item in value.values():
                    inspect(item)

        inspect(graph)
        if filename.startswith("click/"):
            lists = [node for node in graph if node.get("@type") == "ItemList"]
            check(len(lists) == 1 and lists[0].get("numberOfItems") == 3, prefix + "donation list mismatch")
            if lists:
                for item in lists[0]["itemListElement"]:
                    check(item["url"] in content, prefix + "donation schema does not match visible links")
    # All internal links and assets must resolve to files, including absolute metadata URLs.
    for tag, attributes in page.tags:
        for attribute in ("href", "src"):
            if attributes.get(attribute):
                local_path(attributes[attribute], canonical)

check(len(titles) == len(PAGES), "Page titles must be distinct")
check(len(descriptions) == len(PAGES), "Page descriptions must be distinct")

namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
sitemap = ET.parse(ROOT / "sitemap.xml")
locations = [node.text for node in sitemap.findall("s:url/s:loc", namespace)]
check(set(locations) == set(PAGES.values()) and len(locations) == len(PAGES), "Sitemap must contain exactly the canonical HTML pages")
for node in sitemap.findall("s:url", namespace):
    modified = node.find("s:lastmod", namespace)
    try:
        date = datetime.date.fromisoformat(modified.text)
        check(date <= datetime.date.today(), "Sitemap lastmod must not be in the future")
    except (AttributeError, TypeError, ValueError):
        errors.append("Missing or invalid sitemap lastmod")

robots = RobotFileParser()
robots.parse((ROOT / "robots.txt").read_text().splitlines())
check(ORIGIN + "/sitemap.xml" in (robots.site_maps() or []), "robots.txt must advertise the sitemap")
for path in ("/", "/click/", "/assets/social-home.png", "/assets/social-donations.png", "/llms.txt", "/index.md", "/click/index.md"):
    check(robots.can_fetch("*", ORIGIN + path), "Crawling blocked: " + path)

for filename in ("llms.txt", "llms-full.txt", "index.md", "click/index.md"):
    text = (ROOT / filename).read_text()
    check(text.startswith("# "), filename + ": missing Markdown title")
    for url in re.findall(r"\]\((https://[^)]+)\)", text):
        local_path(url)

snippet = (ROOT / "downloads/banner.html").read_text().strip()
homepage = (ROOT / "index.html").read_text()
textarea = re.search(r'<textarea\b[^>]*id="embed-code"[^>]*>(.*?)</textarea>', homepage, re.S)
check(textarea and html.unescape(textarea.group(1)).strip() == snippet, "Copied HTML and download differ")
check(snippet in homepage, "Rendered banner and download differ")
check(snippet in (ROOT / "index.md").read_text() and snippet in (ROOT / "llms-full.txt").read_text(), "Markdown banner is out of sync")

manifest = json.loads((ROOT / "site.webmanifest").read_text())
for icon in manifest["icons"]:
    size = tuple(map(int, icon["sizes"].split("x")))
    check(png_size(local_path(icon["src"])) == size, "Manifest icon dimensions mismatch")
check(png_size(ROOT / "assets/favicon-96.png") == (96, 96), "Search favicon must be square")
check(png_size(ROOT / "assets/apple-touch-icon.png") == (180, 180), "Apple touch icon dimensions mismatch")
check((ROOT / "CNAME").read_text().strip() == "palestinebanner.com", "Unexpected custom domain")
check((ROOT / ".nojekyll").exists(), "Missing .nojekyll; Markdown exports may be transformed")
error_page = Page((ROOT / "404.html").read_text())
check("noindex" in error_page.metadata.get("robots", ""), "404 page must be noindex")

if errors:
    print("Site checks failed:", *["- " + error for error in errors], sep="\n")
    sys.exit(1)
print("Passed: metadata, JSON-LD consistency, sitemap, crawlability, local links, social images, icons, Markdown exports, and banner consistency.")
