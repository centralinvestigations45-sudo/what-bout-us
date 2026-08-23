import base64
import os
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_topup

base = run_topup.base
LOGO_PATH = '/brand-logo.png'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
_original_nav = base.nav
_original_footer = base.footer
_original_page = base.page
_original_home = base.home

# Known-good 1x1 PNG fallback. The configured official logo is used only when it
# decodes to a browser-safe PNG/JPEG/GIF/WebP payload.
FALLBACK_PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=')


def branded_nav():
    return ('<div class="nav"><div class="shell navin">'
            '<a class="brand" href="/" style="display:flex;align-items:center;gap:10px">'
            '<img src="'+LOGO_PATH+'?v=7" alt="What Bout Us™ AI Companions" '
            'style="width:72px;height:72px;object-fit:contain;border-radius:12px">'
            '</a><div class="links"><a href="/#companions">Companions</a>'
            '<a href="/#plans">Plans</a><a href="/account">Account</a>'
            '<a href="/simone">Talk to Simone</a></div></div></div>')


def branded_footer():
    return ('<div class="fine">'
            '<img src="'+LOGO_PATH+'?v=7" alt="What Bout Us™ AI Companions" '
            'style="display:block;width:180px;max-width:55vw;height:auto;margin:0 auto 16px;border-radius:14px">'
            '© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>')


def branded_page(title, body):
    html = _original_page(title, body)
    meta = ('<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences.">'
            '<meta property="og:type" content="website">'
            '<meta property="og:site_name" content="What Bout Us™">'
            '<meta property="og:title" content="What Bout Us™ — AI Companions">'
            '<meta property="og:description" content="Someone to talk to. Someone who remembers.">'
            '<meta property="og:url" content="'+PUBLIC_URL+'/">'
            '<meta property="og:image" content="'+PUBLIC_URL+LOGO_PATH+'?v=7">'
            '<meta property="og:image:secure_url" content="'+PUBLIC_URL+LOGO_PATH+'?v=7">'
            '<meta property="og:image:alt" content="What Bout Us™ AI Companions official logo">'
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="What Bout Us™ — AI Companions">'
            '<meta name="twitter:description" content="Someone to talk to. Someone who remembers.">'
            '<meta name="twitter:image" content="'+PUBLIC_URL+LOGO_PATH+'?v=7">'
            '<link rel="icon" type="image/png" href="'+LOGO_PATH+'?v=7">'
            '<link rel="apple-touch-icon" href="'+LOGO_PATH+'?v=7">')
    return html.replace('</head>', meta + '</head>', 1)


def branded_home():
    html = _original_home()
    hero_logo = ('<div style="max-width:1180px;margin:18px auto -8px;padding:0 18px;text-align:center">'
                 '<img src="'+LOGO_PATH+'?v=7" alt="What Bout Us™ AI Companions" '
                 'style="width:min(260px,68vw);height:auto;border-radius:22px">'
                 '</div>')
    marker = '<main class="shell">'
    if marker in html:
        html = html.replace(marker, marker + hero_logo, 1)
    return html

base.nav = branded_nav
base.footer = branded_footer
base.page = branded_page
base.home = branded_home


def _logo_bytes_and_type():
    raw = os.environ.get('WBU_LOGO_B64', '').strip()
    if raw:
        if raw.startswith('data:') and ',' in raw:
            raw = raw.split(',', 1)[1]
        raw = ''.join(raw.split())
        try:
            data = base64.b64decode(raw, validate=False)
        except Exception:
            try:
                data = base64.urlsafe_b64decode(raw + ('=' * (-len(raw) % 4)))
            except Exception:
                data = b''
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            return data, 'image/png'
        if data.startswith(b'\xff\xd8\xff'):
            return data, 'image/jpeg'
        if data.startswith((b'GIF87a', b'GIF89a')):
            return data, 'image/gif'
        if data[:4] == b'RIFF' and len(data) >= 12 and data[8:12] == b'WEBP':
            return data, 'image/webp'
    return FALLBACK_PNG, 'image/png'


class BrandedHandler(run_topup.TopupHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in (LOGO_PATH, '/brand-logo', '/static/wbu-official-logo.webp', '/favicon.ico', '/apple-touch-icon.png'):
            data, mime = _logo_bytes_and_type()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', 'no-cache, max-age=0, must-revalidate')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), BrandedHandler).serve_forever()
