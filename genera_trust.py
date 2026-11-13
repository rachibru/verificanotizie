import hashlib
import json
import os
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
    # Impronta SHA-256 deterministica legata all'URL canonico del post
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

        # Normalizza in https
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

    # Genera la homepage index.html con il registro pubblico
    righe_html = ""
    for item in indice_articoli:
        righe_html += f"""
        <li style="padding: 14px 0; border-bottom: 1px solid #dce3ec;">
          <div style="font-size: 0.8rem; color: #5a6778;">{escape(item['date'])} • SHA-256: <code>{item['hash'][:16]}...</code></div>
          <a href="{item['hash']}.html" style="font-weight: 600; color: #0f294a; text-decoration: none; font-size: 1.02rem;">{escape(item['title'])}</a>
        </li>
        """

    index_html = f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Registro Pubblico di Tracciabilità | BrunoRachiele.it</title>
  <link rel="icon" href="https://www.brunorachiele.it/favicon.ico">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f7fa; color: #1c2430; margin: 0; padding: 24px 16px;">
  <div style="max-width: 820px; margin: 0 auto; background: #fff; border: 1px solid #dce3ec; border-radius: 12px; padding: 28px;">
    <h1 style="color: #0f294a; margin-top: 0;">Registro di Tracciabilità Editoriale — BrunoRachiele.it</h1>
    <p style="color: #5a6778;">Elenco pubblico dei contenuti verificati con impronta crittografica SHA-256 e conformità agli standard di trasparenza giornalistica.</p>
    <ul style="list-style: none; padding: 0; margin: 20px 0 0 0;">
      {righe_html}
    </ul>
  </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as idx:
        idx.write(index_html)

    print(f"Generate {len(indice_articoli)} schede di certificazione.")

if __name__ == "__main__":
    main()
