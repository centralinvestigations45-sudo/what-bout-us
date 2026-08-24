from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import mimetypes
import os
import run_brand

base = run_brand.base
STATIC = Path(__file__).resolve().parent / 'static'

# Live Square checkout routes for the two Unlimited plans.
SQUARE_UNLIMITED_URL = os.environ.get('SQUARE_UNLIMITED_URL', '').strip()
SQUARE_UNLIMITED_YEARLY_URL = os.environ.get('SQUARE_UNLIMITED_YEARLY_URL', '').strip()

STANDALONE = {
    'Simone': 'simone.jpg', 'Chloe': 'chloe.jpg', 'Darius': 'darius.jpg',
    'Isabella': 'isabella.jpg', 'Julius': 'julius.jpg', 'Malik': 'malik.jpg', 'Nia': 'nia.jpg',
}
_original_portrait = base.portrait

def portrait(name):
    if name in STANDALONE:
        return '/static/' + STANDALONE[name] + '?v=22'
    return _original_portrait(name)
base.portrait = portrait

_old_page = base.page
def face_page(title, body):
    html = _old_page(title, body)
    css = '<style>.avatar img,.bigavatar img{width:100%;height:100%;object-fit:cover;display:block}.avatar{width:78px;height:78px;overflow:hidden}.bigavatar{width:160px;height:160px;overflow:hidden}@media(max-width:480px){.avatar{width:74px;height:74px}}</style>'
    return html.replace('</head>', css + '</head>', 1)
base.page = face_page

class FacesHandler(run_brand.BrandedHandler):
    def do_GET(self):
        u = urlparse(self.path)
        path = u.path

        # Route Unlimited plan buttons directly to their correct Square subscriptions.
        if path == '/checkout':
            plan = parse_qs(u.query).get('plan', [''])[0]
            target = ''
            if plan == 'unlimited':
                target = SQUARE_UNLIMITED_URL
            elif plan == 'unlimited-yearly':
                target = SQUARE_UNLIMITED_YEARLY_URL
            if target:
                self.send_response(302)
                self.send_header('Location', target)
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                return

        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            allowed = set(STANDALONE.values()) | {'roster_sprite.svg'}
            if rel in allowed:
                f = STATIC / rel
                if f.exists() and f.is_file():
                    data = f.read_bytes()
                    ctype = 'image/svg+xml; charset=utf-8' if rel.endswith('.svg') else (mimetypes.guess_type(rel)[0] or 'application/octet-stream')
                    self.send_response(200)
                    self.send_header('Content-Type', ctype)
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.send_header('Content-Length', str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), FacesHandler).serve_forever()
