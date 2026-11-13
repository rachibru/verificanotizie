import hashlib
import json
import re
import urllib.request
from html import escape

FEED_URL = "https://www.brunorachiele.it/feeds/posts/default?alt=json&max-results=100"
TEMPLATE_FILE = "trust_template.html"

INDEX_TEMPLATE = """<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Registro Tracciabilità Pubblicazioni | brunorachiele.it</title>
  <meta name="robots" content="noindex, nofollow">
  <link rel="icon" href="https://static.brunorachiele.it/logo.png">
  <style>
    :root {
      --primary: #0f294a;
      --accent: #0d7a3e;
      --accent-bg: #eaf6ef;
      --border: #dce3ec;
      --bg: #f3f6fa;
      --text: #1c2430;
      --muted: #5a6778;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
    }
    .topbar {
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      padding: 14px 20px;
    }
    .topbar-inner {
      max-width: 880px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: var(--primary);
      font-weight: 800;
      font-size: 1.05rem;
    }
    .brand img {
      width: 28px;
      height: 28px;
      border-radius: 6px;
    }
    .back-site {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--primary);
      text-decoration: none;
      padding: 6px 14px;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: #f8fafc;
    }
    .back-site:hover { background: #eef3f9; }
    .hero {
      background: linear-gradient(135deg, #0f294a 0%, #193e6b 100%);
      color: #ffffff;
      padding: 36px 20px 44px;
    }
    .hero-inner {
      max-width: 880px;
      margin: 0 auto;
    }
    .hero-badge {
      display: inline-block;
      background: rgba(255, 255, 255, 0.14);
      border: 1px solid rgba(255, 255, 255, 0.25);
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.03em;
      margin-bottom: 12px;
    }
    .hero h1 {
      margin: 0 0 10px 0;
      font-size: 1.75rem;
      line-height: 1.25;
    }
    .hero p {
      margin: 0;
      color: #d6e2f0;
      font-size: 0.98rem;
      max-width: 680px;
    }
    .container {
      max-width: 880px;
      margin: -24px auto 48px;
      padding: 0 16px;
    }
    .toolbar {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      box-shadow: 0 4px 14px rgba(15, 41, 74, 0.06);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
      margin-bottom: 20px;
    }
    .counter {
      font-size: 0.9rem;
      color: var(--muted);
    }
    .counter strong {
      color: var(--primary);
      font-size: 1.05rem;
    }
    .search-input {
      flex: 1;
      min-width: 240px;
      max-width: 380px;
      padding: 9px 14px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 0.9rem;
      outline: none;
    }
    .search-input:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(15, 41, 74, 0.08);
    }
    .list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .trust-item {
      background: #ffffff;
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 10px;
      padding: 16px 20px;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .trust-item:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(15, 41, 74, 0.06);
    }
    .trust-item-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }
    .trust-pill {
      background: var(--accent-bg);
      color: var(--accent);
      border: 1px solid #b7e2c9;
      font-size: 0.76rem;
      font-weight: 700;
      padding: 2px 10px;
      border-radius: 999px;
    }
    .trust-hash {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.78rem;
      color: var(--muted);
      background: #f1f5f9;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .trust-item-title {
      margin: 0 0 10px 0;
      font-size: 1.08rem;
      line-height: 1.35;
    }
    .trust-item-title a {
      color: var(--primary);
      text-decoration: none;
    }
    .trust-item-title a:hover {
      text-decoration: underline;
    }
    .trust-item-actions {
      display: flex;
      gap: 16px;
      font-size: 0.84rem;
      font-weight: 600;
    }
    .link-cert {
      color: var(--accent);
      text-decoration: none;
    }
    .link-orig {
      color: var(--muted);
      text-decoration: none;
    }
    .link-cert:hover, .link-orig:hover { text-decoration: underline; }
    footer {
      max-width: 880px;
      margin: 0 auto 40px;
      padding: 0 16px;
      text-align: center;
      font-size: 0.82rem;
      color: var(--muted);
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <a href="https://trust.brunorachiele.it/" class="brand">
        <img src="https://static.brunorachiele.it/trust.png" alt="Trust Logo" onerror="this.src='https://static.brunorachiele.it/logo.png'">
        <span>TRUST • brunorachiele.it</span>
      </a>
      <a href="https://www.brunorachiele.it" class="back-site">← Torna su brunorachiele.it</a>
    </div>
  </header>

  <section class="hero">
    <div class="hero-inner">
      <span class="hero-badge">STANDARD TRASPARENZA EDITORIALE • SHA-256</span>
      <h1>Registro Tracciabilità Pubblicazioni</h1>
      <p>Archivio crittografico dei contenuti originali pubblicati da brunorachiele.it. Ogni scheda attesta data, provenienza e integrità digitale dell'articolo.</p>
    </div>
  </section>

  <main class="container">
    <div class="toolbar">
      <div class="counter">Contenuti certificati in archivio: <strong>{{ TOTALE }}</strong></div>
      <input type="search" id="trustSearch" class="search-input" placeholder="Cerca per titolo o impronta SHA-256...">
    </div>

    <div class="list" id="trustList">
      {{ RIGHE_HTML }}
    </div>
  </main>

  <footer>
    Sistema di verifica e integrità editoriale di <strong>brunorachiele.it</strong> • Impronte generate automaticamente dal feed ufficiale dell'editore.
  </footer>

  <script>
    document.getElementById('trustSearch').addEventListener('input', function(e) {
      var q = e.target.value.toLowerCase().trim();
      var items = document.querySelectorAll('.trust-item');
      items.forEach(function(el) {
        var text = el.getAttribute('data-search') || '';
        el.style.display = text.indexOf(q) !== -1 ? 'block' : 'none';
      });
    });
  </script>
</body>
</html>"""


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

    righe_html = ""
    for item in indice_articoli:
        righe_html += (
            '<article class="trust-item" data-search="' + escape(item["title"].lower()) + " " + item["hash"] + '">'
            '<div class="trust-item-top">'
            '<span class="trust-pill">✓ Verificato • ' + escape(item["date"]) + '</span>'
            '<span class="trust-hash" title="' + item["hash"] + '">SHA-256: ' + item["hash"][:16] + '…</span>'
            '</div>'
            '<h2 class="trust-item-title"><a href="' + item["hash"] + '.html">' + escape(item["title"]) + '</a></h2>'
            '<div class="trust-item-actions">'
            '<a href="' + item["hash"] + '.html" class="link-cert">Apri certificato →</a>'
            '<a href="' + escape(item["url"]) + '" target="_blank" rel="noopener" class="link-orig">Articolo originale ↗</a>'
            '</div>'
            '</article>\n'
        )

    index_html = (
        INDEX_TEMPLATE
        .replace("{{ TOTALE }}", str(len(indice_articoli)))
        .replace("{{ RIGHE_HTML }}", righe_html)
    )

    with open("index.html", "w", encoding="utf-8") as idx:
        idx.write(index_html)

    print(f"Generate {len(indice_articoli)} schede di certificazione.")


if __name__ == "__main__":
    main()
