import os
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_topup

base = run_topup.base
LOGO_PATH = '/static/wbu-social-preview.jpg'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
_original_nav = base.nav
_original_footer = base.footer
_original_page = base.page


def branded_nav():
    return ('<div class="nav"><div class="shell navin">'
            '<a class="brand" href="/" style="display:flex;align-items:center;gap:10px">'
            '<img src="'+LOGO_PATH+'" alt="What Bout Us AI Companions" '
            'style="width:118px;height:54px;object-fit:contain;border-radius:10px">'
            '</a><div class="links"><a href="/#companions">Companions</a>'
            '<a href="/#plans">Plans</a><a href="/account">Account</a>'
            '<a href="/simone">Talk to Simone</a></div></div></div>')


def branded_footer():
    return ('<div class="fine"><img src="'+LOGO_PATH+'" alt="What Bout Us AI Companions" '
            'style="display:block;width:150px;max-width:55vw;height:auto;margin:0 auto 14px;border-radius:12px">'
            '© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>')


def branded_page(title, body):
    html = _original_page(title, body)
    meta = ('<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences.">'
            '<meta property="og:type" content="website">'
            '<meta property="og:site_name" content="What Bout Us™">'
            '<meta property="og:title" content="What Bout Us™ — AI Companions">'
            '<meta property="og:description" content="Someone to talk to. Someone who remembers.">'
            '<meta property="og:url" content="'+PUBLIC_URL+'/">'
            '<meta property="og:image" content="'+PUBLIC_URL+LOGO_PATH+'">'
            '<meta property="og:image:secure_url" content="'+PUBLIC_URL+LOGO_PATH+'">'
            '<meta property="og:image:type" content="image/jpeg">'
            '<meta property="og:image:width" content="400">'
            '<meta property="og:image:height" content="210">'
            '<meta property="og:image:alt" content="What Bout Us AI Companions logo">'
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="What Bout Us™ — AI Companions">'
            '<meta name="twitter:description" content="Someone to talk to. Someone who remembers.">'
            '<meta name="twitter:image" content="'+PUBLIC_URL+LOGO_PATH+'">'
            '<link rel="icon" href="'+LOGO_PATH+'" type="image/jpeg">'
            '<link rel="apple-touch-icon" href="'+LOGO_PATH+'">')
    return html.replace('</head>', meta + '</head>', 1)


base.nav = branded_nav
base.footer = branded_footer
base.page = branded_page


class BrandedHandler(run_topup.TopupHandler):
    def do_GET(self):
        if urlparse(self.path).path == LOGO_PATH:
            try:
                p = os.path.join(os.path.dirname(__file__), 'static', 'wbu-social-preview.jpg')
                data = open(p, 'rb').read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception:
                return self.sh('Image not found', 404)
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), BrandedHandler).serve_forever()
