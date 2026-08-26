from http.server import ThreadingHTTPServer
import run_voice_livefix as live

base = live.base

TAGLINE = 'Someone to talk to. Someone who remembers.™'

_original_home = base.home
_original_footer = base.footer
_original_companion_page = base.companion_page


def _clean_brand_language(html):
    replacements = {
        'Real people. Real conversations.': TAGLINE,
        'Real people, real conversations.': TAGLINE,
        'Real People. Real Conversations.': TAGLINE,
        'real people. real conversations.': TAGLINE,
        'REAL PEOPLE. REAL CONVERSATIONS.': TAGLINE,
        'Someone to talk to, someone who remembers.': TAGLINE,
        'Someone to talk to. Someone who remembers.': TAGLINE,
        '🐦': '𝕏',
        '>Twitter<': '>X<',
        '>twitter<': '>X<',
        'aria-label="Twitter"': 'aria-label="X"',
        'title="Twitter"': 'title="X"',
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    return html


def _x_social_badge():
    return '''<div id="wbu-social-x" style="text-align:center;margin:12px auto 18px;font-size:14px;color:#c9c4df">
      <span style="display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.18);padding:8px 13px;border-radius:999px;background:rgba(255,255,255,.05)">
        <span aria-label="X" style="font-size:18px;font-weight:800">𝕏</span><span>X</span>
      </span>
    </div>'''


def footer_branding():
    html = _clean_brand_language(_original_footer())
    if 'wbu-social-x' not in html:
        html = _x_social_badge() + html
    return html


def home_branding():
    html = _clean_brand_language(_original_home())
    if TAGLINE not in html:
        marker = '<section'
        if marker in html:
            html = html.replace(marker, '<div style="text-align:center;padding:14px 18px;font-weight:700">'+TAGLINE+'</div>'+marker, 1)
    return html


def companion_page_branding(name):
    return _clean_brand_language(_original_companion_page(name))


base.footer = footer_branding
base.home = home_branding
base.companion_page = companion_page_branding


class Handler(live.Handler):
    pass


if __name__ == '__main__':
    print('WBU_BRANDING_LIVEFIX tagline + X branding enabled', flush=True)
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
