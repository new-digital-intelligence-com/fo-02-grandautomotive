"""Fetches a public web page and keeps only its readable text, for building the knowledge base.

grandautomotive.eu is a Wix site: the text is in the server-rendered HTML, inside the page's <main> (the header and
footer are kept apart, so the menu is not repeated on every page).

Usage: python fetch_page.py <url> [<url> ...]
Each page is printed with a header, and saved as text under research/pages/.
"""
import gzip
import html
import os
import re
import sys
import urllib.parse
import urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
os.makedirs(OUT, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
    "Accept-Encoding": "gzip",
    "Accept-Language": "en,el;q=0.8",
}


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=40) as response:
        raw = response.read()
        if response.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def readable(fragment: str) -> list[str]:
    fragment = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr|span)>", "\n", fragment)
    fragment = re.sub(r"(?i)</t[dh]>", " | ", fragment)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", fragment))
    lines = [re.sub(r"[ \t ​]+", " ", line).strip() for line in text.splitlines()]
    kept: list[str] = []
    for line in lines:
        if len(line) > 1 and (not kept or kept[-1] != line):  # Wix repeats some texts for the mobile layout
            kept.append(line)
    return kept


def main_text(page: str) -> str:
    page = re.sub(r"(?is)<(script|style|noscript|svg|template)[^>]*>.*?</\1>", " ", page)
    main = re.search(r"(?is)<main[^>]*>(.*?)</main>", page)
    footer = re.search(r"(?is)<footer[^>]*>(.*?)</footer>", page)
    body = re.search(r"(?is)<body[^>]*>(.*)</body>", page)
    parts = readable(main.group(1) if main else (body.group(1) if body else page))
    if footer:
        parts += ["", "[footer]"] + readable(footer.group(1))
    return "\n".join(parts)


def links(page: str, url: str) -> list[str]:
    """The page's links to its own site (relative links resolved), to find the next pages to read."""
    site = urllib.parse.urlsplit(url).netloc
    found = {urllib.parse.urljoin(url, href.split("#")[0]) for href in re.findall(r'href="([^"]+)"', page)}
    return sorted(link for link in found if urllib.parse.urlsplit(link).netloc == site
                  and not re.search(r"\.(css|js|png|jpe?g|svg|ico|webp|woff2?)(\?|$)", link))


if __name__ == "__main__":
    for url in sys.argv[1:]:
        try:
            page = fetch(url)
            text = main_text(page)
        except Exception as error:  # noqa: BLE001 - a research helper: report and move on
            print(f"===== {url}\n!! {error}\n")
            continue
        name = re.sub(r"[^A-Za-z0-9]+", "_", url.split("://", 1)[-1]).strip("_")[:120]
        with open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8") as file:
            file.write(url + "\n\n" + text)
        print(f"===== {url} ({len(text)} chars)\n{text[:6000]}\n-- links: {links(page, url)}\n")
