import base64
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import run_topup

base = run_topup.base
LOGO_PATH = '/brand-logo.jpg'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
LOGO_FILE = Path(__file__).resolve().parent / 'static' / 'wbu-logo.b64'
_original_nav = base.nav
_original_footer = base.footer
_original_page = base.page
_original_home = base.home


def branded_nav():
    return ('<div class="nav"><div class="shell navin"><a class="brand" href="/">'
            '<img src="'+LOGO_PATH+'?v=9" alt="What Bout Us™ AI Companions" style="width:72px;height:72px;object-fit:contain;border-radius:12px">'
            '</a><div class="links"><a href="/#companions">Companions</a><a href="/#plans">Plans</a><a href="/account">Account</a><a href="/simone">Talk to Simone</a></div></div></div>')


def branded_footer():
    return ('<div class="fine"><img src="'+LOGO_PATH+'?v=9" alt="What Bout Us™ AI Companions" style="display:block;width:180px;max-width:55vw;height:auto;margin:0 auto 16px;border-radius:14px">© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>')


def branded_page(title, body):
    html = _original_page(title, body)
    image = PUBLIC_URL + LOGO_PATH + '?v=9'
    meta = ('<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences.">'
            '<meta property="og:type" content="website"><meta property="og:site_name" content="What Bout Us™">'
            '<meta property="og:title" content="What Bout Us™ — AI Companions"><meta property="og:description" content="Someone to talk to. Someone who remembers.">'
            '<meta property="og:url" content="'+PUBLIC_URL+'/"><meta property="og:image" content="'+image+'"><meta property="og:image:secure_url" content="'+image+'">'
            '<meta property="og:image:type" content="image/jpeg"><meta property="og:image:alt" content="What Bout Us™ AI Companions official logo">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="'+image+'">'
            '<link rel="icon" type="image/jpeg" href="'+LOGO_PATH+'?v=9"><link rel="apple-touch-icon" href="'+LOGO_PATH+'?v=9">')
    return html.replace('</head>', meta + '</head>', 1)


def branded_home():
    html = _original_home()
    hero_logo = '<div style="max-width:1180px;margin:18px auto -8px;padding:0 18px;text-align:center"><img src="'+LOGO_PATH+'?v=9" alt="What Bout Us™ AI Companions" style="width:min(420px,86vw);height:auto;border-radius:22px;display:block;margin:auto"></div>'
    marker = '<main class="shell">'
    if marker in html:
        html = html.replace(marker, marker + hero_logo, 1)
    return html

base.nav = branded_nav
base.footer = branded_footer
base.page = branded_page
base.home = branded_home


def logo_bytes():
    raw = ''.join(LOGO_FILE.read_text(encoding='ascii').split())
    data = base64.b64decode(raw, validate=True)
    if not (data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9')):
        raise ValueError('Decoded logo is not a complete JPEG')
    return data


class BrandedHandler(run_topup.TopupHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in (LOGO_PATH, '/brand-logo', '/brand-logo.png', '/static/wbu-official-logo.webp', '/favicon.ico', '/apple-touch-icon.png'):
            try:
                data = logo_bytes()
            except Exception as exc:
                print('LOGO_ERROR', repr(exc), flush=True)
                self.send_error(500, 'Logo asset unavailable')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', 'no-store, max-age=0')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), BrandedHandler).serve_forever()
