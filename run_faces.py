from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import mimetypes
import run_brand

base = run_brand.base
STATIC = Path(__file__).resolve().parent / 'static'

STANDALONE = {
    'Simone': 'simone.jpg', 'Chloe': 'chloe.jpg', 'Darius': 'darius.jpg',
    'Isabella': 'isabella.jpg', 'Julius': 'julius.jpg', 'Malik': 'malik.jpg', 'Nia': 'nia.jpg',
}
SPRITE_NAMES = [
    'Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Noah','Jack','Leo','Carter','Malik',
    'Lily','Aria','Mika','Zoey','Nova','Sophia','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye'
]
SPRITE_POS = {name: ((i % 5) * 64, (i // 5) * 64) for i, name in enumerate(SPRITE_NAMES)}
_original_portrait = base.portrait

def portrait(name):
    if name in STANDALONE:
        return '/static/' + STANDALONE[name] + '?v=19'
    if name in SPRITE_POS:
        return '/portrait/' + name.lower() + '.svg?v=19'
    if name == 'Malik' and (STATIC / 'malik.jpg').exists():
        return '/static/malik.jpg?v=19'
    return _original_portrait(name)
base.portrait = portrait

_old_page = base.page
def face_page(title, body):
    html = _old_page(title, body)
    css = '<style>.avatar img,.bigavatar img{width:100%;height:100%;object-fit:cover;display:block;backface-visibility:hidden}.avatar{width:78px;height:78px;overflow:hidden}.bigavatar{width:160px;height:160px;overflow:hidden}@media(max-width:480px){.avatar{width:74px;height:74px}}</style>'
    return html.replace('</head>', css + '</head>', 1)
base.page = face_page

class FacesHandler(run_brand.BrandedHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith('/portrait/') and path.endswith('.svg'):
            key = path.rsplit('/',1)[-1][:-4]
            name = next((n for n in SPRITE_NAMES if n.lower() == key), None)
            if name:
                x,y = SPRITE_POS[name]
                # SVG wrapper gives each card a real image document and crops the 320x320 sprite.
                svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 64 64" preserveAspectRatio="xMidYMid slice"><image href="/static/roster_sprite.svg?v=19" x="{-x}" y="{-y}" width="320" height="320"/></svg>'''.encode()
                self.send_response(200); self.send_header('Content-Type','image/svg+xml; charset=utf-8'); self.send_header('Cache-Control','public, max-age=3600'); self.send_header('Content-Length',str(len(svg))); self.end_headers(); self.wfile.write(svg); return
        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            allowed = set(STANDALONE.values()) | {'malik.jpg','roster_sprite.svg'}
            if rel in allowed:
                f = STATIC / rel
                if f.exists() and f.is_file():
                    data=f.read_bytes(); ctype='image/svg+xml; charset=utf-8' if rel.endswith('.svg') else (mimetypes.guess_type(rel)[0] or 'application/octet-stream')
                    self.send_response(200); self.send_header('Content-Type',ctype); self.send_header('Cache-Control','public, max-age=3600'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), FacesHandler).serve_forever()
