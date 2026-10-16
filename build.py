# Monta la web.
#   python3 build.py              -> index.html (vista local) + docs/ (lo que se publica en barberiasur.es)
#   python3 build.py ruta.html    -> además escribe la versión para el artifact
import re, sys, shutil, pathlib, datetime
root = pathlib.Path(__file__).parent
DOMAIN = "https://barberiasur.es"

def symbol(name):
    s = (root / "assets" / f"{name}.svg").read_text()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    inner = re.search(r'<svg[^>]*>(.*)</svg>', s, re.S).group(1).strip()
    return f'<symbol id="{name}" viewBox="{vb}">{inner}</symbol>'

page = (root / "src" / "page.html").read_text()
page = page.replace("{{SEAL_SYMBOL}}", symbol("seal")).replace("{{HAND_SYMBOL}}", symbol("hand"))
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(page)

head, _, body = page.partition("</style>")

def document(head, body, extra_head=""):
    return ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + extra_head + head + "</style>\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")

(root / "index.html").write_text(document(head, body))

# ---------- Producción ----------
SEO_TITLE = "Barbería Sur · Barbería en Albacete | Cortes, formación y productos"
DESC = ("Barbería Sur, C/ Portugal 3, Albacete. Reserva tu corte en Booksy, aprende el oficio en los "
        "workshops de Isma, mentoría para abrir tu barbería y la línea de productos Sur. 5,0 en Google.")
schema = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"HairSalon","name":"Barbería Sur","url":"%s/",
"image":"%s/productos/kit.jpg","logo":"%s/favicon.svg",
"address":{"@type":"PostalAddress","streetAddress":"Calle Portugal, 3","postalCode":"02002","addressLocality":"Albacete","addressRegion":"Albacete","addressCountry":"ES"},
"geo":{"@type":"GeoCoordinates","latitude":38.9840229,"longitude":-1.8568547},
"openingHoursSpecification":[
{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Wednesday","Thursday","Friday"],"opens":"10:00","closes":"14:30"},
{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Wednesday","Thursday","Friday"],"opens":"15:30","closes":"19:00"},
{"@type":"OpeningHoursSpecification","dayOfWeek":"Tuesday","opens":"10:00","closes":"14:30"},
{"@type":"OpeningHoursSpecification","dayOfWeek":"Tuesday","opens":"15:30","closes":"19:30"}],
"sameAs":["https://www.instagram.com/barberia__sur/","https://barberiasur.booksy.com/"]}
</script>
""" % (DOMAIN, DOMAIN, DOMAIN)
extra = (f'<link rel="canonical" href="{DOMAIN}/">\n'
         '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
         '<meta name="theme-color" content="#16150F">\n'
         '<meta property="og:type" content="website">\n'
         '<meta property="og:site_name" content="Barbería Sur">\n'
         f'<meta property="og:title" content="Barbería Sur · Albacete">\n'
         f'<meta property="og:description" content="{DESC}">\n'
         f'<meta property="og:url" content="{DOMAIN}/">\n'
         f'<meta property="og:image" content="{DOMAIN}/productos/kit.jpg">\n'
         '<meta name="twitter:card" content="summary_large_image">\n' + schema)
prod_head = re.sub(r"<title>.*?</title>", f"<title>{SEO_TITLE}</title>", head, count=1)
prod_head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', prod_head, count=1)
prod_head = prod_head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")

dist = root / "docs"
if dist.exists(): shutil.rmtree(dist)
dist.mkdir()
(dist / "index.html").write_text(document(prod_head, body, extra))
for folder in ("productos", "fotos"):
    src = root / folder
    if src.exists():
        shutil.copytree(src, dist / folder)
shutil.copy(root / "assets" / "favicon.svg", dist / "favicon.svg")
(dist / "CNAME").write_text("barberiasur.es\n")
(dist / ".nojekyll").write_text("")
(dist / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
today = datetime.date.today().isoformat()
(dist / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod></url>\n</urlset>\n')
(dist / "404.html").write_text("""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página no encontrada · Barbería Sur</title><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@400;700&display=swap">
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#16150F;color:#ECE4CF;font-family:"Zilla Slab",Georgia,serif;text-align:center;padding:24px}
img{width:140px;height:140px}h1{font-size:clamp(2.2rem,7vw,4rem);text-transform:uppercase;margin:16px 0 8px;line-height:1}p{color:#B9B29C;font-size:1.15rem}
a{display:inline-block;margin-top:18px;background:#B5321E;color:#ECE4CF;border:2.5px solid #ECE4CF;box-shadow:4px 4px 0 #ECE4CF;padding:.9em 1.4em;font-weight:700;text-transform:uppercase;letter-spacing:.08em;text-decoration:none}</style></head>
<body><main><img src="/favicon.svg" alt=""><h1>Este corte no existe</h1><p>La página que buscas no está aquí.</p><a href="/">Volver a Barbería Sur</a></main></body></html>
""")
print("docs listo:", sorted(p.name for p in dist.iterdir()))
