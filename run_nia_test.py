from http.server import ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import os
import run_faces

# TEMPORARY NIA TEST MODE
# Gives Nia a no-charge guest test window without changing the paid plans for other companions.
app_v2 = run_faces.run_brand.app_v2
app_v2.FREE.add('Nia')

_original_companion_page = run_faces.base.companion_page


def subscription_plans(name):
    safe_name = run_faces.base.esc(name)
    return f'''<div class="card" style="margin-top:18px"><h2>Choose Your {safe_name} Plan</h2><p class="sub">Pick the option that works best for you.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-top:14px"><div class="plan"><h3>WHAT BOUT US™+</h3><div class="price" style="font-size:30px">$9.99 <small>/ month</small></div><a class="btn alt" href="/checkout?plan=plus">Choose $9.99</a></div><div class="plan hot"><h3>UNLIMITED</h3><div class="price" style="font-size:30px">$14.99 <small>/ month</small></div><a class="btn" href="/checkout?plan=unlimited">Choose $14.99</a></div><div class="plan"><h3>UNLIMITED YEARLY</h3><div class="price" style="font-size:30px">$149.99 <small>/ year</small></div><a class="btn alt" href="/checkout?plan=unlimited_yearly">Choose $149.99</a></div></div></div>'''


def account_access():
    return '''<div class="card" style="margin-top:18px"><h2>Your What Bout Us™ Account</h2><p class="sub">Sign in to continue with your account, or create one to get started.</p><div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px"><a class="btn" href="/account">Sign In</a><a class="btn alt" href="/account">Sign Up</a></div></div>'''


def companion_page_with_nia_test(name):
    html = _original_companion_page(name)

    if name == 'Nia':
        # Let the existing guest-chat route treat Nia as a test companion in the browser.
        html = html.replace(
            'N==="Simone"||N==="Chloe"',
            'N==="Simone"||N==="Chloe"||N==="Nia"'
        )

        # Extend Nia's guest test window to 24 hours instead of the normal 2-minute demo.
        html = html.replace(
            'function guestState(){let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}',
            'function guestState(){if(N==="Nia")return 86400;let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}'
        )
        html = html.replace(' · 2-minute free demo', ' · OWNER TEST UNLOCKED')
        html = html.replace('Free demo starts with your first message.', 'Owner test mode · no charge')

        # Nia should speak her replies too. Use the device's English female voice when available.
        html = html.replace(
            'if(N==="Simone")say(d.reply);',
            '''if(N==="Simone")say(d.reply);if(N==="Nia"){try{let u=new SpeechSynthesisUtterance(d.reply),vs=speechSynthesis.getVoices(),v=vs.find(x=>/Samantha|Ava|Allison|Serena|female/i.test(x.name)&&/^en/i.test(x.lang))||vs.find(x=>/^en-US/i.test(x.lang))||vs.find(x=>/^en/i.test(x.lang));if(v)u.voice=v;u.rate=.92;u.pitch=1.08;speechSynthesis.cancel();speechSynthesis.speak(u)}catch(e){}}'''
        )

    # Leave Simone completely unchanged. Add device voice to every other companion.
    if name not in ('Simone', 'Nia'):
        male_names = {'Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Darius','Noah','Jack','Julius','Leo','Carter','Tyler'}
        want_male = name in male_names
        pitch = '.92' if want_male else '1.08'
        voice_pattern = 'Daniel|Aaron|Fred|Alex|Tom|male' if want_male else 'Samantha|Ava|Allison|Serena|Victoria|female'
        speech = f'''if(N==="Simone")say(d.reply);try{{let u=new SpeechSynthesisUtterance(d.reply),vs=speechSynthesis.getVoices().filter(x=>/^en/i.test(x.lang)),v=vs.find(x=>/{voice_pattern}/i.test(x.name))||vs.find(x=>/^en-US/i.test(x.lang))||vs[0];if(v)u.voice=v;u.rate=.92;u.pitch={pitch};speechSynthesis.cancel();speechSynthesis.speak(u)}}catch(e){{}}'''
        html = html.replace('if(N==="Simone")say(d.reply);', speech)

    # Give every companion the same three payment choices plus account access.
    panels = account_access() + subscription_plans(name)
    marker = '<div class="fine">© 2026 What Bout Us'
    if marker in html:
        html = html.replace(marker, panels + marker, 1)
    else:
        html = html.replace('</main>', panels + '</main>', 1)
    return html


run_faces.base.companion_page = companion_page_with_nia_test


class NiaTestHandler(run_faces.FacesHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/checkout':
            plan = parse_qs(u.query).get('plan', ['plus'])[0]
            if plan == 'unlimited_yearly':
                target = os.environ.get('SQUARE_UNLIMITED_YEARLY_URL', '').strip()
                if target:
                    self.send_response(302)
                    self.send_header('Location', target)
                    self.end_headers()
                    return
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', run_faces.base.PORT), NiaTestHandler).serve_forever()
