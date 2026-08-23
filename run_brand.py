import base64
import os
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_topup

base = run_topup.base
LOGO_PATH = '/brand-logo'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
_original_nav = base.nav
_original_footer = base.footer
_original_page = base.page
_original_home = base.home


def branded_nav():
    return ('<div class="nav"><div class="shell navin">'
            '<a class="brand" href="/" style="display:flex;align-items:center;gap:10px">'
            '<img src="'+LOGO_PATH+'?v=5" alt="What Bout Us™ AI Companions" '
            'style="width:72px;height:72px;object-fit:contain;border-radius:12px;image-rendering:auto;filter:drop-shadow(0 0 8px rgba(236,80,255,.35))">'
            '</a><div class="links"><a href="/#companions">Companions</a>'
            '<a href="/#plans">Plans</a><a href="/account">Account</a>'
            '<a href="/simone">Talk to Simone</a></div></div></div>')


def branded_footer():
    return ('<div class="fine">'
            '<img src="'+LOGO_PATH+'?v=5" alt="What Bout Us™ AI Companions" '
            'style="display:block;width:180px;max-width:55vw;height:auto;margin:0 auto 16px;border-radius:14px;image-rendering:auto;filter:drop-shadow(0 0 12px rgba(236,80,255,.28))">'
            '© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>')


def branded_page(title, body):
    html = _original_page(title, body)
    meta = ('<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences.">'
            '<meta property="og:type" content="website">'
            '<meta property="og:site_name" content="What Bout Us™">'
            '<meta property="og:title" content="What Bout Us™ — AI Companions">'
            '<meta property="og:description" content="Someone to talk to. Someone who remembers.">'
            '<meta property="og:url" content="'+PUBLIC_URL+'/">'
            '<meta property="og:image" content="'+PUBLIC_URL+LOGO_PATH+'?v=5">'
            '<meta property="og:image:secure_url" content="'+PUBLIC_URL+LOGO_PATH+'?v=5">'
            '<meta property="og:image:alt" content="What Bout Us™ AI Companions official logo">'
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="What Bout Us™ — AI Companions">'
            '<meta name="twitter:description" content="Someone to talk to. Someone who remembers.">'
            '<meta name="twitter:image" content="'+PUBLIC_URL+LOGO_PATH+'?v=5">'
            '<link rel="icon" href="'+LOGO_PATH+'?v=5">'
            '<link rel="apple-touch-icon" href="'+LOGO_PATH+'?v=5">')
    return html.replace('</head>', meta + '</head>', 1)


def branded_home():
    html = _original_home()
    hero_logo = ('<div style="max-width:1180px;margin:18px auto -8px;padding:0 18px;text-align:center">'
                 '<img src="'+LOGO_PATH+'?v=5" alt="What Bout Us™ AI Companions" '
                 'style="width:min(260px,68vw);height:auto;border-radius:22px;image-rendering:auto;filter:drop-shadow(0 0 20px rgba(236,80,255,.32))">'
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
    if not raw:
        raise ValueError('missing logo data')
    if raw.startswith('data:') and ',' in raw:
        raw = raw.split(',', 1)[1]
    raw = ''.join(raw.split())
    try:
        data = base64.b64decode(raw, validate=False)
    except Exception:
        data = base64.urlsafe_b64decode(raw + ('=' * (-len(raw) % 4)))
    if not data:
        raise ValueError('missing logo data')
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        mime = 'image/png'
    elif data.startswith(b'\xff\xd8\xff'):
        mime = 'image/jpeg'
    elif data.startswith((b'GIF87a', b'GIF89a')):
        mime = 'image/gif'
    elif data[:4] in (b'RIFF',) and data[8:12] == b'WEBP':
        mime = 'image/webp'
    else:
        mime = 'application/octet-stream'
    return data, mime


class BrandedHandler(run_topup.TopupHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in (LOGO_PATH, '/static/wbu-official-logo.webp', '/favicon.ico', '/apple-touch-icon.png'):
            try:
                data, mime = _logo_bytes_and_type()
                self.send_response(200)
                self.send_header('Content-Type', mime)
                self.send_header('Cache-Control', 'public, max-age=3600')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception:
                return self.sh('Image not found', 404)
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), BrandedHandler).serve_forever()
