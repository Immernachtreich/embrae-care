"""Shared source -> Shopify mappings for the build tools (links and the soup parser)."""
import re
from pathlib import Path
from bs4 import BeautifulSoup, Comment

root = Path(__file__).resolve().parent.parent
PRODUCTS = {"reset-cleanser", "urban-defense-serum", "climate-adapt-moisturizer", "daily-shield-sunscreen",
            "daily-urban-defense-routine"}
# Journal articles are the pages that use the article CSS group.
_first = (root / "source/css/shared-12p-01.css").read_text().split("\n", 1)[0]
ARTICLE_PAGES = {x.replace(".html", "").strip() for x in _first.replace("/* used by:", "").replace("*/", "").split(",")}


def parse(html):
    """Parse a page with its HTML comments removed (bs4 would otherwise print their text without <!-- -->)."""
    soup = BeautifulSoup(html, "lxml")
    for c in soup.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()
    return soup


def link(h):
    """Map a source href to a Shopify URL."""
    if not h or h.startswith(("#", "http", "mailto:", "tel:")):
        return h
    m = re.match(r"^([a-z0-9-]+)\.html(#.*)?$", h)
    if not m:
        return h
    page, frag = m.group(1), m.group(2) or ""
    if page == "index":
        url = "/"
    elif page in PRODUCTS:
        url = f"/products/{page}"
    elif page == "journal":
        url = "/blogs/journal"
    elif page == "coming-soon":
        url = "/policies/refund-policy"
    elif page in ARTICLE_PAGES:
        url = f"/blogs/journal/{page}"
    else:
        url = f"/pages/{page}"
    return url + frag
