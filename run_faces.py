from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import mimetypes
import run_brand

base = run_brand.base
STATIC = Path(__file__).resolve().parent / 'static'

# Prefer full standalone portraits when available. All remaining companions are
# sourced from the embedded roster sprite rather than generated initials.
STANDALONE = {
    'Simone': 'simone.jpg',
    'Chloe': 'chloe.jpg',
    'Darius': 'darius.jpg',
    'Isabella': 'isabella.jpg',
    'Julius': 'julius.jpg',
    'Nia': 'nia.jpg',
}
SPRITE_NAMES = {
    'Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Noah','Jack','Leo','Carter',
    'Lily','Aria','Mika','Zoey','Nova','Sophia','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye'
}

def sharp_portrait(name):
    if name in STANDALONE:
        return '/static/' + STANDALONE[name] + '?v=18'
    if name in SPRITE_NAMES:
        return '/static/roster_sprite.svg#' + name.lower()
    # Keep a graceful fallback for any roster changes.
    return run_brand.base.portrait(name) if name not in ('Malik',) else '/static/malik.jpg?v=18'

# Avoid recursion in fallback by keeping the original before patching.
_original_portrait = base.portrait

def portrait(name):
    if name in STANDALONE:
        return '/static/' + STANDALONE[name] + '?v=18'
    if name in SPRITE_NAMES:
        return '/static/roster_sprite.svg#' + name.lower()
    if name == 'Malik' and (STATIC / 'malik.jpg').exists():
        return '/static/malik.jpg?v=18'
    return _original_portrait(name)

base.portrait = portrait

# Add a small rendering polish that avoids browser smoothing making tiny raster
# faces look softer than necessary on cards.
_old_page = base.page

def face_page(title, body):
    html = _old_page(title, body)
    css = '<style>.avatar img,.bigavatar img{object-fit:cover;backface-visibility:hidden;transform:translateZ(0);filter:contrast(1.025) saturate(1.015)}.avatar{width:78px;height:78px}.bigavatar{width:160px;height:160px}@media(max-width:480px){.avatar{width:74px;height:74px}}</style>'
    return html.replace('</head>', css + '</head>', 1)

base.page = face_page

class FacesHandler(run_brand.BrandedHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            allowed = set(STANDALONE.values()) | {'malik.jpg','roster_sprite.svg'}
            if rel in allowed:
                f = STATIC / rel
                if f.exists() and f.is_file():
                    data = f.read_bytes()
                    ctype = 'image/svg+xml; charset=utf-8' if rel.endswith('.svg') else (mimetypes.guess_type(rel)[0] or 'application/octet-stream')
                    self.send_response(200)
                    self.send_header('Content-Type', ctype)
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.send_header('Content-Length', str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), FacesHandler).serve_forever()
