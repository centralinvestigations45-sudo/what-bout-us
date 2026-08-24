from http.server import ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, quote
import os
import run_faces

app_v2 = run_faces.run_brand.app_v2
app_v2.FREE.add('Nia')

_original_companion_page = run_faces.base.companion_page
_original_page = run_faces.base.page


def crisp_page(title, body):
    html = _original_page(title, body)
    css = '''<style>
.avatar{width:64px!important;height:64px!important}.avatar img{width:64px!important;height:64px!important;object-fit:cover!important;display:block!important;image-rendering:auto!important;filter:contrast(1.04) saturate(1.03)}
.bigavatar{width:96px!important;height:96px!important}.bigavatar img{width:96px!important;height:96px!important;object-fit:cover!important;display:block!important;image-rendering:auto!important;filter:contrast(1.04) saturate(1.03)}
</style>'''
    return html.replace('</head>', css + '</head>', 1)

run_faces.base.page = crisp_page


def subscription_plans(name):
    safe_name = run_faces.base.esc(name)
    slug = quote(name, safe='')
    return f'''<div class="card" style="margin-top:18px"><h2>Choose Your {safe_name} Plan</h2><p class="sub">Pick the option that works best for you.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-top:14px"><div class="plan"><h3>WHAT BOUT US™+</h3><div class="price" style="font-size:30px">$9.99 <small>/ month</small></div><a class="btn alt" href="/checkout?plan=plus&companion={slug}">Choose $9.99</a></div><div class="plan hot"><h3>UNLIMITED</h3><div class="price" style="font-size:30px">$14.99 <small>/ month</small></div><a class="btn" href="/checkout?plan=unlimited&companion={slug}">Choose $14.99</a></div><div class="plan"><h3>UNLIMITED YEARLY</h3><div class="price" style="font-size:30px">$149.99 <small>/ year</small></div><a class="btn alt" href="/checkout?plan=unlimited_yearly&companion={slug}">Choose $149.99</a></div></div></div>'''


def account_access():
    return '''<div class="card" style="margin-top:18px"><h2>Your What Bout Us™ Account</h2><p class="sub">Sign in to continue with your account, or create one to get started.</p><div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px"><a class="btn" href="/account">Sign In</a><a class="btn alt" href="/account">Sign Up</a></div></div>'''


def companion_page(name):
    html = _original_companion_page(name)

    if name == 'Simone':
        # Keep Simone's existing voice path untouched. Owner testing should have no countdown.
        html = html.replace(
            'function guestState(){let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}',
            'function guestState(){if(N==="Simone")return 86400;let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}'
        )
        html = html.replace('if(!started)timer(r)', 'if(!started&&N!=="Simone")timer(r)')
        html = html.replace(' · 2-minute free demo', ' · OWNER TEST UNLOCKED', 1)
        html = html.replace('Free demo starts with your first message.', 'Owner test mode · no countdown', 1)
        # Put Simone's plan choices above the conversation so they are impossible to miss.
        anchor = '<div class="card"><div class="profile">'
        if anchor in html:
            html = html.replace(anchor, subscription_plans(name) + anchor, 1)

    if name == 'Nia':
        html = html.replace('N==="Simone"||N==="Chloe"','N==="Simone"||N==="Chloe"||N==="Nia"')
        html = html.replace(
            'function guestState(){let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}',
            'function guestState(){if(N==="Nia")return 86400;let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}'
        )
        html = html.replace(' · 2-minute free demo', ' · OWNER TEST UNLOCKED', 1)
        html = html.replace('Free demo starts with your first message.', 'Owner test mode · no charge', 1)
        html = html.replace(
            'if(N==="Simone")say(d.reply);',
            '''if(N==="Simone")say(d.reply);if(N==="Nia"){try{let u=new SpeechSynthesisUtterance(d.reply),vs=speechSynthesis.getVoices(),v=vs.find(x=>/Samantha|Ava|Allison|Serena|female/i.test(x.name)&&/^en/i.test(x.lang))||vs.find(x=>/^en-US/i.test(x.lang))||vs.find(x=>/^en/i.test(x.lang));if(v)u.voice=v;u.rate=.92;u.pitch=1.08;speechSynthesis.cancel();speechSynthesis.speak(u)}catch(e){}}'''
        )

    if name not in ('Simone','Nia'):
        male = name in {'Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Darius','Noah','Jack','Julius','Leo','Carter','Tyler'}
        pattern = 'Daniel|Aaron|Fred|Alex|Tom|male' if male else 'Samantha|Ava|Allison|Serena|Victoria|female'
        pitch = '.92' if male else '1.08'
        speech = f'''if(N==="Simone")say(d.reply);try{{let u=new SpeechSynthesisUtterance(d.reply),vs=speechSynthesis.getVoices().filter(x=>/^en/i.test(x.lang)),v=vs.find(x=>/{pattern}/i.test(x.name))||vs.find(x=>/^en-US/i.test(x.lang))||vs[0];if(v)u.voice=v;u.rate=.92;u.pitch={pitch};speechSynthesis.cancel();speechSynthesis.speak(u)}}catch(e){{}}'''
        html = html.replace('if(N==="Simone")say(d.reply);', speech)

    panels = account_access() + ('' if name == 'Simone' else subscription_plans(name))
    marker = '<div class="fine">© 2026 What Bout Us'
    if marker in html:
        html = html.replace(marker, panels + marker, 1)
    return html


run_faces.base.companion_page = companion_page


class Handler(run_faces.FacesHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/checkout':
            q = parse_qs(u.query)
            plan = q.get('plan', ['plus'])[0]
            companion = q.get('companion', [''])[0]

            if plan == 'unlimited_yearly':
                target = os.environ.get('SQUARE_UNLIMITED_YEARLY_URL', '').strip()
                if target:
                    self.send_response(302); self.send_header('Location', target); self.end_headers(); return

            if plan == 'unlimited':
                target = os.environ.get('SQUARE_UNLIMITED_URL', '').strip()
                if target:
                    self.send_response(302); self.send_header('Location', target); self.end_headers(); return

            if plan == 'plus' and companion != 'Nia':
                generic = os.environ.get('SQUARE_PLUS_GENERIC_URL', '').strip()
                if generic:
                    self.send_response(302); self.send_header('Location', generic); self.end_headers(); return
                safe = run_faces.base.esc(companion or 'this companion')
                body = f'''<main class="shell"><div class="card" style="max-width:700px;margin:40px auto"><h1>$9.99 Checkout</h1><p class="lead">The generic $9.99 What Bout Us™ checkout for {safe} is being connected.</p><p class="sub">The $14.99 monthly and $149.99 yearly Square checkouts are available now.</p><a class="btn" href="/checkout?plan=unlimited&companion={quote(companion, safe='')}">Choose $14.99/month</a> <a class="btn alt" href="/checkout?plan=unlimited_yearly&companion={quote(companion, safe='')}">Choose $149.99/year</a></div>{run_faces.base.footer()}</main>'''
                return self.sh(run_faces.base.page('Checkout — What Bout Us™', body))

        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', run_faces.base.PORT), Handler).serve_forever()
