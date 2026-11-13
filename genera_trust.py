import hashlib
import json
import re
import urllib.request
from html import escape

FEED_URL = "https://www.brunorachiele.it/feeds/posts/default?alt=json&max-results=100"
TEMPLATE_FILE = "trust_template.html"

def clean_html(raw_html):
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def calcola_hash_articolo(canonical_url):
    return hashlib.sha256(canonical_url.strip().encode("utf-8")).hexdigest()

def main():
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    entries = data.get("feed", {}).get("entry", [])
    indice_articoli = []

    for entry in entries:
        title = entry.get("title", {}).get("$t", "Senza titolo")
        published = entry.get("published", {}).get("$t", "")
        updated = entry.get("updated", {}).get("$t", published)
        content_raw = entry.get("content", {}).get("$t", "") or entry.get("summary", {}).get("$t", "")
        
        canonical_url = ""
        for link in entry.get("link", []):
            if link.get("rel") == "alternate":
                canonical_url = link.get("href", "")
                break

        if not canonical_url:
            continue

        canonical_url = canonical_url.replace("http://", "https://")
        doc_hash = calcola_hash_articolo(canonical_url)
        descrizione = clean_html(content_raw)[:240] + "..."

        html_scheda = (
            template
            .replace("{{ TITLE }}", escape(title))
            .replace("{{ HASH }}", doc_hash)
            .replace("{{ CANONICAL_URL }}", escape(canonical_url))
            .replace("{{ DATE_PUBLISHED }}", escape(published))
            .replace("{{ DATE_MODIFIED }}", escape(updated))
            .replace("{{ DESCRIPTION }}", escape(descrizione))
        )

        filename = f"{doc_hash}.html"
        with open(filename, "w", encoding="utf-8") as out:
            out.write(html_scheda)

        indice_articoli.append({
            "title": title,
            "hash": doc_hash,
            "date": published[:10],
            "url": canonical_url
        })

    # Genera le card HTML per la index
    righe_html = ""
    for item in indice_articoli:
        righe_html += f"""
        <article class="trust-item" data-search="{escape(item['title'].lower())} {item['hash']}">
          <div class="trust-item-top">
            <span class="trust-pill">✓ Verificato • {escape(item['date'])}</span>
            <span class="trust-hash" title="{item['hash']}">SHA-256: {item['hash'][:16]}…</span>
          </div>
          <h2 class="trust-item-title">
            <a href="{item['hash']}.html">{escape(item['title'])}</a>
          </h2>
          <div class="trust-item-actions">
            <a href="{item['hash']}.html" class="link-cert">Apri certificato →</a>
            <a href="{escape(item['url'])}" target="_blank" rel="noopener" class="link-orig">Articolo originale ↗</a>
          </div>
        </article>
        """

    totale = len(indice_articoli)

    index_html = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Notizie pubblicate | brunorachiele.it</title>
  <meta name="robots" content="noindex, nofollow">
  <link rel="icon" href="https://static.brunorachiele.it/logo.png">
  <style>
    :root {{
      --primary: #0f294a;
      --primary
