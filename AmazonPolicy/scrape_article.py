#!/usr/bin/env python3
"""Scrape Amazon FBA fee article."""

import sys
import requests
from bs4 import BeautifulSoup

URL = "https://www.efulfillmentservice.com/2026/04/amazon-2026-fba-fee-changes-what-sellers-need-to-know/"

try:
    resp = requests.get(URL, timeout=15)
    resp.raise_for_status()
except requests.RequestException as e:
    print(f"Fetch error: {e}", file=sys.stderr)
    sys.exit(1)

soup = BeautifulSoup(resp.text, "html.parser")

# Remove nav, header, footer, script, style
for tag in soup.find_all(["nav", "header", "footer", "script", "style", "aside"]):
    tag.decompose()

# Try article content
article = soup.find("article") or soup.find("main") or soup

# Extract headings + paragraphs
print(f"# {soup.title.string or 'Article'}\n")
for elem in article.find_all(["h1","h2","h3","h4","p","li","blockquote"]):
    text = elem.get_text(strip=True)
    if not text:
        continue
    if elem.name in ["h1","h2","h3","h4"]:
        level = "#" * (int(elem.name[1]) + 1)
        print(f"\n{level} {text}\n")
    elif elem.name == "li":
        print(f"- {text}")
    elif elem.name == "blockquote":
        print(f"> {text}")
    else:
        print(text)
    print()
