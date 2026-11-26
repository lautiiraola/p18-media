#!/usr/bin/env python3
"""Lee los feeds RSS/Atom de las fuentes de noticias P18 y deja sólo lo de los últimos N días.
Uso: python3 rss.py [--dias 7] [--salida candidatas_rss.json]
Sin librerías externas. Imprime cuántas notas trajo cada feed y guarda [{fuente, titulo, link, fecha, resumen}]."""
import argparse, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "The Verge (IA)": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "TechCrunch (IA)": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "Wired (IA)": "https://www.wired.com/feed/tag/ai/latest/rss",
    "Xataka": "https://feeds.weblogssl.com/xataka2",
}


GENERALES = {"Xataka"}  # feeds que mezclan temas: sólo pasa lo de IA
IA = re.compile(r"\b(IA|inteligencia artificial|ChatGPT|OpenAI|Gemini|Claude|Anthropic|Copilot|Llama|Grok|Mistral|"
                r"DeepSeek|modelo de lenguaje|algoritmo|chatbot|agente|robot|NVIDIA|Midjourney|Sora)\b", re.I)


def fecha(txt):
    if not txt:
        return None
    txt = txt.strip()
    try:
        d = parsedate_to_datetime(txt)
    except Exception:
        try:
            d = datetime.fromisoformat(txt.replace("Z", "+00:00"))
        except Exception:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def limpio(t, n=280):
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", t).strip()[:n]


def leer(nombre, url, desde):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh) P18-noticias"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raiz = ET.fromstring(r.read())
    out = []
    for it in raiz.iter():
        tag = it.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        g = {c.tag.split("}")[-1]: c for c in it}
        titulo = (g.get("title").text if g.get("title") is not None else "") or ""
        link = ""
        if g.get("link") is not None:
            link = g["link"].text or g["link"].get("href") or ""
        f = None
        for k in ("pubDate", "published", "updated", "date"):
            if g.get(k) is not None:
                f = fecha(g[k].text)
                if f:
                    break
        if not f or f < desde:
            continue
        res = g.get("description") if g.get("description") is not None else g.get("summary")
        if nombre in GENERALES and not IA.search(titulo + " " + (res.text if res is not None and res.text else "")):
            continue
        out.append({"fuente": nombre, "titulo": limpio(titulo, 200), "link": link.strip(),
                    "fecha": f.date().isoformat(), "resumen": limpio(res.text if res is not None else "")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--salida", default="candidatas_rss.json")
    a = ap.parse_args()
    desde = datetime.now(timezone.utc) - timedelta(days=a.dias)
    todo = []
    for n, u in FEEDS.items():
        try:
            items = leer(n, u, desde)
            print(f"{n}: {len(items)}")
            todo += items
        except Exception as e:
            print(f"{n}: error ({str(e)[:80]})", file=sys.stderr)
    todo.sort(key=lambda x: x["fecha"], reverse=True)
    json.dump(todo, open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Total: {len(todo)} → {a.salida}")


if __name__ == "__main__":
    main()
