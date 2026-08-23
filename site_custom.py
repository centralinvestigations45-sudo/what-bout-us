from http.server import ThreadingHTTPServer
import app
import app_v2

# Keep the existing 32-companion roster, but make Simone and Chloe the front pair on Page 1.
FEATURED = ['Simone', 'Chloe']
MEN_REST = [n for n in app.MEN if n != 'Simone']
WOMEN_REST = [n for n in app.WOMEN if n != 'Chloe']
BIRTHDAYS = {'Simone': 'October 15'}
ZODIAC = {'Simone': 'Libra'}
PROFESSIONS = {'Simone': 'Private Investigator'}


def cards(names):
    out = []
    for n in names:
        profession = PROFESSIONS.get(n)
        birthday = BIRTHDAYS.get(n)
        zodiac = ZODIAC.get(n)
        profession_html = f'<small>{app.esc(profession)}</small>' if profession else ''
        birthday_html = f'<small>Birthday: {app.esc(birthday)}</small>' if birthday else ''
        zodiac_html = f'<small>Zodiac: {app.esc(zodiac)}</small>' if zodiac else ''
        out.append(
            f'<a class="comp" href="{app.url(n)}">'
            f'<div class="avatar"><img src="{app.portrait(n)}" alt="{app.esc(n)} AI companion"></div>'
            f'<b>{app.esc(n)}</b><small>LIVE</small>{profession_html}{birthday_html}{zodiac_html}</a>'
        )
    return ''.join(out)


def home():
    b = f'''<main class="shell"><section class="hero"><div><div class="grad">AI COMPANIONS</div><h1>Someone to talk to.<br><span class="grad">Someone who remembers.</span></h1><p class="lead">Meet 32 distinct AI companions with personality, conversation, multiple languages and premium customization.</p><a class="btn" href="#companions">Meet the Companions</a> <a class="btn alt" href="/simone">Talk to Simone</a></div><div class="art"><div><h2>What <span class="grad">Bout Us<span class="tm">™</span></span></h2><p>AI COMPANIONS</p></div></div></section><section id="companions" class="section"><h2>32 AI Companions</h2><p class="sub">16 men. 16 women. Tap any picture to open a live conversation.</p><h3>FEATURED</h3><div class="grid">{cards(FEATURED)}</div><h3 style="margin-top:28px">MEN</h3><div class="grid">{cards(MEN_REST)}</div><h3 style="margin-top:28px">WOMEN</h3><div class="grid">{cards(WOMEN_REST)}</div></section><section id="plans" class="section"><h2>Choose Your Experience</h2><div class="plans"><div class="plan"><h3>WHAT BOUT US™+</h3><div class="price">$9.99 <small>/ month</small></div><p>Text conversations · Multiple companions · Conversation memory · Multiple languages</p><a class="btn alt" href="/checkout?plan=plus">Choose Plus</a></div><div class="plan hot"><h3>WHAT BOUT US™ UNLIMITED</h3><div class="price">$14.99 <small>/ month</small></div><p>All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories</p><a class="btn" href="/checkout?plan=unlimited">Choose Unlimited</a></div></div></section>{app.footer()}</main>'''
    return app.page('What Bout Us™ — AI Companions', b)


# Add Simone's profession first, then birthday and zodiac, without changing chat/voice behavior.
_original_companion_page = app_v2.companion_page

def companion_page(name):
    html = _original_companion_page(name)
    if name == 'Simone':
        html = html.replace('<h1>Simone</h1>', '<h1>Simone</h1><div class="banner" style="margin-bottom:12px">Private Investigator</div>')
        html = html.replace('Height 6\'1" · 2-minute free demo', 'Height 6\'1" · Birthday October 15 · Zodiac Libra · 2-minute free demo')
    return html

app.cards = cards
app.home = home
app_v2.companion_page = companion_page
app.companion_page = companion_page

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', app.PORT), app_v2.H).serve_forever()
