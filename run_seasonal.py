from http.server import ThreadingHTTPServer
from datetime import datetime, timezone
import run_voice_livefix as live

base = live.base
_original_page = base.page

THEMES = [
    ('2026-09-01','2026-10-31','Halloween After Dark','Luxury Halloween season','🎃','#ff7a18','#6b21a8','#120814'),
    ('2026-11-01','2026-11-30','Grateful Together','Warm autumn season','🍂','#d97706','#7c2d12','#160d08'),
    ('2026-12-01','2026-12-26','Christmas With Us','Holiday lights and winter warmth','🎄','#dc2626','#15803d','#08110c'),
    ('2026-12-27','2027-01-07','Midnight With Us','New Year celebration','✨','#f5d76e','#64748b','#080b12'),
    ('2027-01-08','2027-01-31','Winter Connections','Elegant winter season','❄️','#60a5fa','#7c3aed','#08111d'),
    ('2027-02-01','2027-02-14','Closer Than Ever','Valentine season','♥','#fb4b8b','#7f1d3f','#170912'),
    ('2027-02-15','2027-03-19','New Beginnings','Early spring season','🌱','#22c55e','#8b5cf6','#07130d'),
    ('2027-03-20','2027-04-30','Spring Together','Fresh spring season','🌷','#f472b6','#34d399','#0a1511'),
    ('2027-05-01','2027-05-31','Celebrating Her','May appreciation season','🌹','#e879a9','#d4af37','#160b11'),
    ('2027-06-01','2027-06-30','Celebrating Him','June appreciation season','⌚','#3b82f6','#b7791f','#07101a'),
    ('2027-07-01','2027-08-31','Summer Nights','Luxury summer season','🌅','#f97316','#2563eb','#07121a'),
    ('2027-09-01','2027-10-31','Halloween After Dark II','Cinematic Halloween season','🎃','#ff6500','#7e22ce','#100611'),
    ('2027-11-01','2027-11-30','Together & Thankful','Autumn gratitude season','🍁','#c56a1a','#8b3a22','#150d09'),
    ('2027-12-01','2027-12-26','A What Bout Us Christmas','Luxury Christmas season','🎄','#e11d48','#16a34a','#07110c'),
    ('2027-12-27','2028-01-07','Another Year Together','New Year celebration','🥂','#e7c96b','#94a3b8','#070a10'),
]


def _active_theme():
    today = datetime.now(timezone.utc).date().isoformat()
    for start, end, name, subtitle, icon, accent, accent2, bg in THEMES:
        if start <= today <= end:
            return dict(start=start,end=end,name=name,subtitle=subtitle,icon=icon,accent=accent,accent2=accent2,bg=bg)
    return None


def _theme_markup(theme):
    if not theme:
        return ''
    return f'''<style>
:root{{--wbu-season-a:{theme['accent']};--wbu-season-b:{theme['accent2']};--wbu-season-bg:{theme['bg']}}}
body{{background:radial-gradient(circle at 12% 6%,color-mix(in srgb,var(--wbu-season-a) 20%,transparent),transparent 30%),radial-gradient(circle at 88% 18%,color-mix(in srgb,var(--wbu-season-b) 18%,transparent),transparent 32%),var(--wbu-season-bg)!important}}
.nav{{border-bottom-color:color-mix(in srgb,var(--wbu-season-a) 45%,#292932)!important}}
.btn{{box-shadow:0 0 20px color-mix(in srgb,var(--wbu-season-a) 26%,transparent)}}
.card,.plan,.comp,.art{{border-color:color-mix(in srgb,var(--wbu-season-b) 34%,#35353e)!important}}
.wbu-season-strip{{margin:0 auto 8px;max-width:1180px;padding:11px 18px;text-align:center;font-weight:800;letter-spacing:.3px;background:linear-gradient(90deg,color-mix(in srgb,var(--wbu-season-a) 28%,#0b0b10),color-mix(in srgb,var(--wbu-season-b) 28%,#0b0b10));border-bottom:1px solid color-mix(in srgb,var(--wbu-season-a) 50%,transparent)}}
.wbu-season-strip small{{display:block;font-weight:500;color:#ddd;margin-top:2px}}
</style><div class="wbu-season-strip">{theme['icon']} {theme['name']} <small>{theme['subtitle']} · What Bout Us™ seasonal experience</small></div>'''


def seasonal_page(title, body):
    html = _original_page(title, body)
    theme = _active_theme()
    if not theme:
        return html
    marker = '<body>'
    return html.replace(marker, marker + _theme_markup(theme), 1)


base.page = seasonal_page


class Handler(live.Handler):
    pass


if __name__ == '__main__':
    theme = _active_theme()
    print('WBU_SEASONAL_THEME ' + (theme['name'] if theme else 'base'), flush=True)
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
