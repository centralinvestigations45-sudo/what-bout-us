from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import run_topup

base = run_topup.base
LOGO_PATH = '/brand-logo.svg'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
LOGO_FILE = Path(__file__).resolve().parent / 'static' / 'wbu-logo-v13.svg'
_original_page = base.page
_original_home = base.home


def branded_nav():
    return ('<div class="nav"><div class="shell navin"><a class="brand" href="/">'
            '<img src="'+LOGO_PATH+'?v=13" alt="What Bout Us™ AI Companions" style="width:170px;height:72px;object-fit:contain">'
            '</a><div class="links"><a href="/#companions">Companions</a><a href="/#plans">Plans</a><a href="/account">Account</a><a href="/simone">Talk to Simone</a></div></div></div>')


def branded_footer():
    return ('<div class="fine"><img src="'+LOGO_PATH+'?v=13" alt="What Bout Us™ AI Companions" style="display:block;width:260px;max-width:75vw;height:auto;margin:0 auto 16px">© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>')


def branded_page(title, body):
    html = _original_page(title, body)
    image = PUBLIC_URL + LOGO_PATH + '?v=13'
    meta = ('<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences.">'
            '<meta property="og:type" content="website"><meta property="og:site_name" content="What Bout Us™">'
            '<meta property="og:title" content="What Bout Us™ — AI Companions"><meta property="og:description" content="Someone to talk to. Someone who remembers.">'
            '<meta property="og:url" content="'+PUBLIC_URL+'/"><meta property="og:image" content="'+image+'"><meta property="og:image:type" content="image/svg+xml">'
            '<meta property="og:image:alt" content="What Bout Us™ AI Companions official logo">'
            '<link rel="icon" type="image/svg+xml" href="'+LOGO_PATH+'?v=13">')
    return html.replace('</head>', meta + '</head>', 1)


def branded_home():
    html = _original_home()
    hero_logo = '<div style="max-width:1180px;margin:18px auto -8px;padding:0 18px;text-align:center"><img src="'+LOGO_PATH+'?v=13" alt="What Bout Us™ AI Companions" style="width:min(760px,96vw);height:auto;display:block;margin:auto"></div>'
    marker = '<main class="shell">'
    if marker in html:
        html = html.replace(marker, marker + hero_logo, 1)
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
                if b'<svg' not in data[:500]:
                    raise ValueError('v13 logo is not valid SVG')
            except Exception as exc:
                print('LOGO_ERROR', repr(exc), flush=True)
                self.send_error(500, 'Logo asset unavailable')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', 'no-store, max-age=0')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), BrandedHandler).serve_forever()
