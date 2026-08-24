from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import run_topup

base = run_topup.base
wallet = run_topup.run_wallet
pricing = wallet.run_pricing
LOGO_PATH = '/brand-logo.svg'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
LOGO_FILE = Path(__file__).resolve().parent / 'static' / 'wbu-logo-v13.svg'
_original_page = base.page
_original_home = base.home

# What Bout Us Collection 01 — expands the live virtual wardrobe while preserving wallet purchasing/equip behavior.
COLLECTION_CLOTHING = [
    ('Classic Hoodie','classic-hoodie',False,475),('Fitted T-Shirt','fitted-tshirt',False,225),('Denim Jacket','denim-jacket',False,725),
    ('Dark Denim Jeans','dark-denim-jeans',False,500),('Business Blazer','business-blazer',False,850),('Cocktail Dress','cocktail-dress',False,900),
    ('Date Night Dress','date-night-dress',False,1100),('Athletic Set','athletic-set',False,650),('Satin Lounge Set','satin-lounge-set',False,600),
    ('Premium Evening Gown','premium-evening-gown',True,9000),('Premium Tailored Suit','premium-tailored-suit',True,11000),
    ('Premium Leather Outfit','premium-leather-outfit',True,12500),('Premium Silk Lingerie Set','premium-silk-lingerie',True,9500),
    ('Premium Men’s Lounge Set','premium-mens-lounge',True,6500)
]
COLLECTION_ACCESSORIES = [
    ('Fashion Earrings','fashion-earrings',False,450),('Hoop Earrings','hoop-earrings',False,425),('Classic Watch','classic-watch',False,950),
    ('Leather Strap Watch','leather-watch',False,1100),('Pendant Necklace','pendant-necklace',False,700),('Cuff Bracelet','cuff-bracelet',False,550),
    ('Fashion Ring','fashion-ring',False,500),('Baseball Cap','baseball-cap',False,300),('Beanie','beanie',False,275),('Handbag','handbag',False,850),
    ('Premium Luxury Handbag','premium-luxury-handbag',True,9500),('Premium Diamond Bracelet','premium-diamond-bracelet',True,16000),
    ('Premium Diamond Necklace','premium-diamond-necklace',True,22000),('Premium Luxury Watch','premium-luxury-watch',True,20000)
]
COLLECTION_SHOES = [
    ('High-Top Sneakers','high-top-sneakers',False,750),('Running Sneakers','running-sneakers',False,700),('Classic Heels','classic-heels',False,850),
    ('Ankle Boots','ankle-boots',False,900),('Work Boots','work-boots',False,950),('Loafers','loafers',False,800),
    ('Premium Designer Heels','premium-designer-heels',True,6500),('Premium Work Boots','premium-work-boots',True,7000)
]
for label,key,premium,price in COLLECTION_CLOTHING:
    if key not in wallet.ITEMS:
        pricing.CLOTHING.append((label,key,premium)); wallet.ITEMS[key]=(label,'clothing',price,premium)
for label,key,premium,price in COLLECTION_ACCESSORIES:
    if key not in wallet.ITEMS:
        pricing.ACCESSORIES.append((label,key,premium)); wallet.ITEMS[key]=(label,'accessories',price,premium)
for label,key,premium,price in COLLECTION_SHOES:
    if key not in wallet.ITEMS:
        pricing.SHOES.append((label,key,premium)); wallet.ITEMS[key]=(label,'shoes',price,premium)


def branded_nav():
    return ('<div class="nav"><div class="shell navin"><a class="brand" href="/"><img src="'+LOGO_PATH+'?v=15" alt="What Bout Us™ AI Companions" style="width:150px;height:58px;object-fit:contain;display:block"></a><div class="links"><a href="/#companions">Companions</a><a href="/clothing">Clothing</a><a href="/accessories">Accessories</a><a href="/shoes">Shoes</a><a href="/account">Account</a></div></div></div>')


def branded_footer():
    return ('<div class="fine"><img src="'+LOGO_PATH+'?v=15" alt="What Bout Us™ AI Companions" style="display:block;width:240px;max-width:70vw;height:auto;margin:0 auto 14px">© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>')


def branded_page(title, body):
    html = _original_page(title, body)
    image = PUBLIC_URL + LOGO_PATH + '?v=15'
    meta = ('<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences."><meta property="og:type" content="website"><meta property="og:site_name" content="What Bout Us™"><meta property="og:title" content="What Bout Us™ — AI Companions"><meta property="og:description" content="Someone to talk to. Someone who remembers."><meta property="og:url" content="'+PUBLIC_URL+'/"><meta property="og:image" content="'+image+'"><meta property="og:image:type" content="image/svg+xml"><meta property="og:image:alt" content="What Bout Us™ AI Companions official logo"><link rel="icon" type="image/svg+xml" href="'+LOGO_PATH+'?v=15"><style>@media(max-width:600px){.nav .shell{padding-top:6px!important;padding-bottom:6px!important}.nav .brand img{width:132px!important;height:50px!important}main.shell>div:first-child{margin-top:8px!important;margin-bottom:2px!important;padding-left:8px!important;padding-right:8px!important}main.shell>div:first-child img{width:min(620px,92vw)!important;max-height:310px!important;object-fit:contain!important}}</style>')
    return html.replace('</head>', meta + '</head>', 1)


def branded_home():
    html = _original_home()
    hero_logo = '<div style="max-width:980px;margin:12px auto 2px;padding:0 14px;text-align:center"><img src="'+LOGO_PATH+'?v=15" alt="What Bout Us™ AI Companions" style="width:min(650px,92vw);height:auto;display:block;margin:auto"></div>'
    collection = '''<section style="max-width:980px;margin:22px auto;padding:0 18px"><div class="card" style="padding:22px"><div class="grad">WHAT BOUT US™ COLLECTION 01</div><h2>Clothing, Shoes &amp; Accessories</h2><p class="sub">Shop virtual looks for your companion. Choose standard styles or unlock premium fashion with an eligible plan. Every purchase uses your virtual style wallet and can be equipped to the companion you choose.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="/clothing">Shop Clothing</a><a class="btn alt" href="/shoes">Shop Shoes</a><a class="btn alt" href="/accessories">Shop Accessories</a></div></div></section>'''
    marker = '<main class="shell">'
    if marker in html:
        html = html.replace(marker, marker + hero_logo + collection, 1)
    return html

base.nav = branded_nav
base.footer = branded_footer
base.page = branded_page
base.home = branded_home

class BrandedHandler(run_topup.TopupHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in (LOGO_PATH, '/brand-logo', '/brand-logo.jpg', '/brand-logo.png', '/favicon.ico'):
            try:
                data = LOGO_FILE.read_bytes()
                if b'<svg' not in data[:500]: raise ValueError('logo is not valid SVG')
            except Exception as exc:
                print('LOGO_ERROR', repr(exc), flush=True); self.send_error(500, 'Logo asset unavailable'); return
            self.send_response(200); self.send_header('Content-Type', 'image/svg+xml; charset=utf-8'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store, max-age=0'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), BrandedHandler).serve_forever()
