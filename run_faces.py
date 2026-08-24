from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import mimetypes
import re
import run_brand

base = run_brand.base
STATIC = Path(__file__).resolve().parent / 'static'

STANDALONE = {
    'Simone': 'simone.jpg', 'Chloe': 'chloe.jpg', 'Darius': 'darius.jpg',
    'Isabella': 'isabella.jpg', 'Julius': 'julius.jpg', 'Malik': 'malik.jpg', 'Nia': 'nia.jpg',
}
SPRITE_NAMES = [
    'Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Noah','Jack','Leo','Carter',
    'Lily','Aria','Mika','Zoey','Nova','Sophia','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye'
]
SPRITE_POS = {name: ((i % 5) * 64, (i // 5) * 64) for i, name in enumerate(SPRITE_NAMES)}
_original_portrait = base.portrait

def portrait(name):
    if name in STANDALONE:
        return '/static/' + STANDALONE[name] + '?v=20'
    if name in SPRITE_POS:
        return '/portrait/' + name.lower() + '.svg?v=20'
    return _original_portrait(name)
base.portrait = portrait

_old_page = base.page
def face_page(title, body):
    html = _old_page(title, body)
    css = '<style>.avatar img,.bigavatar img{width:100%;height:100%;object-fit:cover;display:block;backface-visibility:hidden}.avatar{width:78px;height:78px;overflow:hidden}.bigavatar{width:160px;height:160px;overflow:hidden}@media(max-width:480px){.avatar{width:74px;height:74px}}</style>'
    return html.replace('</head>', css + '</head>', 1)
base.page = face_page

def self_contained_portrait(name):
    """Return a standalone SVG crop with the sprite's embedded JPEG intact.
    This avoids Safari/iOS having to load an external SVG from inside another SVG.
    """
    sprite_path = STATIC / 'roster_sprite.svg'
    if not sprite_path.exists():
        return None
    x, y = SPRITE_POS[name]
    text = sprite_path.read_text(encoding='utf-8')
    # Make the sprite itself the portrait document and crop by viewBox.
    text = re.sub(r'<svg\b[^>]*>',
                  f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="{x} {y} 64 64" preserveAspectRatio="xMidYMid slice">',
                  text, count=1)
    return text.encode('utf-8')

class FacesHandler(run_brand.BrandedHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith('/portrait/') and path.endswith('.svg'):
            key = path.rsplit('/',1)[-1][:-4]
            name = next((n for n in SPRITE_NAMES if n.lower() == key), None)
            if name:
                svg = self_contained_portrait(name)
                if svg:
                    self.send_response(200)
                    self.send_header('Content-Type','image/svg+xml; charset=utf-8')
                    self.send_header('Cache-Control','public, max-age=3600')
                    self.send_header('X-Content-Type-Options','nosniff')
                    self.send_header('Content-Length',str(len(svg)))
                    self.end_headers(); self.wfile.write(svg); return
        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            allowed = set(STANDALONE.values()) | {'roster_sprite.svg'}
            if rel in allowed:
                f = STATIC / rel
                if f.exists() and f.is_file():
                    data=f.read_bytes()
                    ctype='image/svg+xml; charset=utf-8' if rel.endswith('.svg') else (mimetypes.guess_type(rel)[0] or 'application/octet-stream')
                    self.send_response(200); self.send_header('Content-Type',ctype); self.send_header('Cache-Control','public, max-age=3600'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), FacesHandler).serve_forever()
