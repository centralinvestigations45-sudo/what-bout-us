import base64
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_topup

base = run_topup.base
LOGO_PATH = '/static/wbu-official-logo.jpg'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
LOGO_DATA_B64 = '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABEMDQ8NCxEPDg8TEhEVGiscGhgYGjUmKB8rPzdCQT43PDtFTmNURUleSzs8VnZXXmdqb3BvQ1N6g3lsgmNtb2v/2wBDARITExoXGjMcHDNrRzxHa2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2v/wgARCADcANwDASIAAhEBAxEB/8QAGgAAAgMBAQAAAAAAAAAAAAAAAAMBAgQFBv/EABgBAQEBAQEAAAAAAAAAAAAAAAABAgME/9oADAMBAAIQAxAAAAHggAAAABNQMZvOc155aAYoEkGhl3jHKkgBkAAAAAAAAAmp6irejhoxVlWN5U430edp33vztF1XVIcZMtzWZqadblYxAE5gAAAAAAMXp6Y6HK6PP64283o87lsLV57Opy+7rePn6Eay5epVm3nbEOm3m6Im8YHPgAAAAAABqyu643Yelk78tHL6vJ5bCZ49a9rldjfTh2pbHPbTPXdt1uOy61K3rduSNVy8wAAAAAAF6TZ2jnb/AFefkVtXzeibaM1b5ov2dNOToo4dMkWpjiy+aus75ydF6MGbXk48wCYAAAAAACXIneerzTb1xivKOfTTbOzrdWLSvl0bgJziWRbpi6tOXPfbg05coAzyAANnUs8+W7554PSx5o15AtUrXRHU71bMHT59+fqx7s3maU23xfGRrV1PMM1O1WY45sxyABf2HjPR6mD0vIfZwfT8yZb+d9UqPNx6B4vz/qfParGmN6dXN6EzOGnXSmTemLaa+RtnLqRmGYZrWczLZOdHQ5+/WN3P6XHs7HO63IL7M+ylV2qM2Pq5b1wMreafXNfW2Nzsh2DbFZCxz5bDZNzzG36MvCxa8kyARMATAJJApMBqbjd2uhOYzXrXGUhOcxak2uosgAQmAAAAGWTbUZNYq110zbLvaS10SPpnct6xAytQvK6ktVF26tIq6oJkAkAAddG8sLRpAmc1graucVMNE3W5erUCZRokhw1uplEmaxboFATIAPW7P0zrpSk1S1Zyt0ea+6zyGZW8NSYKtKtaqVJump2E3lI9eNV0RS9FATmAA5JY4SU0UDhIrhIOEkrxAPECvEA8QD5zkMWDIAf/xAApEAACAgEDAgcAAwEBAAAAAAABAgADEQQSExAhICIj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'
LOGO_DATA = base64.b64decode(LOGO_DATA_B64)

_original_nav = base.nav
_original_footer = base.footer
_original_page = base.page
_original_home = base.home


def branded_nav():
    return ('<div class="nav"><div class="shell navin">'
            '<a class="brand" href="/" style="display:flex;align-items:center;gap:10px">'
            '<img src="'+LOGO_PATH+'?v=3" alt="What Bout Us™ AI Companions" '
            'style="width:132px;height:58px;object-fit:contain;border-radius:10px;filter:drop-shadow(0 0 8px rgba(236,80,255,.35))">'
            '</a><div class="links"><a href="/#companions">Companions</a>'
            '<a href="/#plans">Plans</a><a href="/account">Account</a>'
            '<a href="/simone">Talk to Simone</a></div></div></div>')


def branded_footer():
    return ('<div class="fine">'
            '<img src="'+LOGO_PATH+'?v=3" alt="What Bout Us™ AI Companions" '
            'style="display:block;width:190px;max-width:62vw;height:auto;margin:0 auto 16px;border-radius:14px;filter:drop-shadow(0 0 12px rgba(236,80,255,.28))">'
            '© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>')


def branded_page(title, body):
    html = _original_page(title, body)
    meta = ('<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences.">'
            '<meta property="og:type" content="website">'
            '<meta property="og:site_name" content="What Bout Us™">'
            '<meta property="og:title" content="What Bout Us™ — AI Companions">'
            '<meta property="og:description" content="Someone to talk to. Someone who remembers.">'
            '<meta property="og:url" content="'+PUBLIC_URL+'/">'
            '<meta property="og:image" content="'+PUBLIC_URL+LOGO_PATH+'?v=3">'
            '<meta property="og:image:secure_url" content="'+PUBLIC_URL+LOGO_PATH+'?v=3">'
            '<meta property="og:image:type" content="image/jpeg">'
            '<meta property="og:image:width" content="220">'
            '<meta property="og:image:height" content="220">'
            '<meta property="og:image:alt" content="What Bout Us™ AI Companions official logo">'
            '<meta name="twitter:card" content="summary_large_image">'
            '<meta name="twitter:title" content="What Bout Us™ — AI Companions">'
            '<meta name="twitter:description" content="Someone to talk to. Someone who remembers.">'
            '<meta name="twitter:image" content="'+PUBLIC_URL+LOGO_PATH+'?v=3">'
            '<link rel="icon" href="'+LOGO_PATH+'?v=3" type="image/jpeg">'
            '<link rel="apple-touch-icon" href="'+LOGO_PATH+'?v=3">')
    return html.replace('</head>', meta + '</head>', 1)


def branded_home():
    html = _original_home()
    hero_logo = ('<div style="max-width:1180px;margin:18px auto -8px;padding:0 18px;text-align:center">'
                 '<img src="'+LOGO_PATH+'?v=3" alt="What Bout Us™ AI Companions" '
                 'style="width:min(360px,78vw);height:auto;border-radius:22px;filter:drop-shadow(0 0 20px rgba(236,80,255,.32))">'
                 '</div>')
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
        if path in (LOGO_PATH, '/favicon.ico', '/apple-touch-icon.png'):
            data = LOGO_DATA
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), BrandedHandler).serve_forever()
