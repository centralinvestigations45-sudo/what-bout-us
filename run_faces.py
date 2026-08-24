from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
import base64
import mimetypes
import re
from PIL import Image
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
_portrait_cache = {}

def portrait(name):
    if name in STANDALONE:
        return '/static/' + STANDALONE[name] + '?v=21'
    if name in SPRITE_POS:
        return '/portrait/' + name.lower() + '.jpg?v=21'
    return _original_portrait(name)
base.portrait = portrait

_old_page = base.page
def face_page(title, body):
    html = _old_page(title, body)
    css = '<style>.avatar img,.bigavatar img{width:100%;height:100%;object-fit:cover;display:block}.avatar{width:78px;height:78px;overflow:hidden}.bigavatar{width:160px;height:160px;overflow:hidden}@media(max-width:480px){.avatar{width:74px;height:74px}}</style>'
    return html.replace('</head>', css + '</head>', 1)
base.page = face_page

def sprite_jpeg():
    text = (STATIC / 'roster_sprite.svg').read_text(encoding='utf-8')
    match = re.search(r'<image[^>]+href=["\']data:image/jpeg;base64,([^"\']+)', text, re.I | re.S)
    if not match:
        return None
    return base64.b64decode(re.sub(r'\s+', '', match.group(1)))

def individual_portrait(name):
    if name in _portrait_cache:
        return _portrait_cache[name]
    raw = sprite_jpeg()
    if not raw:
        return None
    x, y = SPRITE_POS[name]
    with Image.open(BytesIO(raw)) as sheet:
        crop = sheet.convert('RGB').crop((x, y, x + 64, y + 64)).resize((512, 512), Image.Resampling.LANCZOS)
        out = BytesIO()
        crop.save(out, format='JPEG', quality=92, optimize=True)
        data = out.getvalue()
    _portrait_cache[name] = data
    return data

class FacesHandler(run_brand.BrandedHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith('/portrait/') and path.endswith('.jpg'):
            key = path.rsplit('/', 1)[-1][:-4]
            name = next((n for n in SPRITE_NAMES if n.lower() == key), None)
            if name:
                data = individual_portrait(name)
                if data:
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.send_header('Content-Length', str(len(data)))
                    self.end_headers(); self.wfile.write(data); return
        if path.startswith('/static/'):
            rel = path[len('/static/'):]
            allowed = set(STANDALONE.values()) | {'roster_sprite.svg'}
            if rel in allowed:
                f = STATIC / rel
                if f.exists() and f.is_file():
                    data = f.read_bytes()
                    ctype = 'image/svg+xml; charset=utf-8' if rel.endswith('.svg') else (mimetypes.guess_type(rel)[0] or 'application/octet-stream')
                    self.send_response(200); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', 'public, max-age=3600'); self.send_header('X-Content-Type-Options', 'nosniff'); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data); return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), FacesHandler).serve_forever()
