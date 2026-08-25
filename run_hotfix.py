from http.server import ThreadingHTTPServer
from urllib.parse import urlparse, unquote
import os, hmac
import run_luxury_catalog as lux

base = lux.base
wallet = lux.wallet
pricing = lux.pricing
app_v2 = lux.run_nia_test.app_v2

SAFE_SHOES = [
    ('Luxury Evening Heels', 'classic-heels', False, 1800),
    ('Heritage Leather Work Boots', 'work-boots', False, 429),
    ('Exotic-Embossed Leather Loafers', 'loafers', False, 2200),
    ('Couture Statement Heels', 'premium-designer-heels', True, 4800),
    ('Premium Handcrafted Boots', 'premium-work-boots', True, 4200),
]
pricing.SHOES[:] = [(label, key, premium) for label, key, premium, price in SAFE_SHOES]
for label, key, premium, price in SAFE_SHOES:
    wallet.ITEMS[key] = (label, 'shoes', price, premium)

# Public visitors: all 32 companions have one 2-minute free trial.
app_v2.FREE.update(base.ALL)

POLICY_VERSION = '2026-08-25-v1'
OWNER_TOKEN = os.environ.get('WBU_OWNER_TEST_TOKEN', '').strip()


def owner_cookie_ok(headers):
    if not OWNER_TOKEN:
        return False
    raw = headers.get('Cookie', '')
    for part in raw.split(';'):
        part = part.strip()
        if part.startswith('wbu_owner_test='):
            val = part.split('=', 1)[1]
            return hmac.compare_digest(val, OWNER_TOKEN)
    return False


_original_account_page = app_v2.account_page

def policy_account_page():
    html = _original_account_page()
    checkbox = '''<div class="card" style="margin:16px 0;padding:16px"><label style="display:flex;gap:10px;align-items:flex-start;cursor:pointer"><input id="policy_accept" type="checkbox" style="width:20px;height:20px;margin-top:3px;flex:0 0 auto"><span><strong>I have read and agree to the What Bout Us™ Subscription & Virtual Currency Policy.</strong><br><span class="sub">I understand subscription refund requests must be made within 14 days of the initial subscription purchase. I also understand all virtual currency purchases are final and non-refundable, each issuance expires 31 days after it is issued, unused virtual currency does not carry over, and virtual currency has no cash value, except where required by law.</span></span></label></div>'''
    html = html.replace('<button class="btn" onclick="go(\'signup\')">Create Free Account</button>', checkbox + '<button class="btn" onclick="go(\'signup\')">Create Free Account</button>', 1)
    override = '''<script>
window.go=async function(k){
  const email=document.getElementById("email").value.trim();
  const password=document.getElementById("password").value;
  const name=document.getElementById("name").value.trim();
  const box=document.getElementById("policy_accept");
  if(k==="signup" && (!box || !box.checked)) return m("You must read and check the policy agreement before creating your account.");
  const r=await fetch("/api/auth/"+k,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,password,display_name:name,accepted_policy:k!=="signup"||!!(box&&box.checked),policy_version:"2026-08-25-v1"})});
  const d=await r.json();
  if(!r.ok)return m(d.error||"Unable to continue.");
  if(d.access_token){localStorage.setItem("wbu_access_token",d.access_token);m("Signed in. You can return to your companion.")}
  else m("Account created. Check your email if confirmation is required, then sign in.");
};
</script>'''
    return html.replace('</body>', override + '</body>', 1)

app_v2.account_page = policy_account_page

_original_companion_page = base.companion_page
MALE_NAMES = set(getattr(base, 'MEN', []))

def hotfix_companion_page(name):
    html = _original_companion_page(name)

    # Public 2-minute trial for every companion.
    html = html.replace('N==="Simone"||N==="Chloe"||N==="Nia"', 'true')
    html = html.replace('N==="Simone"||N==="Chloe"', 'true')
    html = html.replace(' · paid subscription required', ' · 2-minute free voice trial')

    policy = '''<div class="card" style="margin-top:18px"><h2>Subscription & Virtual Currency Policy</h2><p class="sub"><strong>14-Day Refund Policy:</strong> Refund requests must be submitted within 14 days of the initial subscription purchase. After 14 days, subscription payments are non-refundable, except for duplicate charges, verified billing errors, unauthorized transactions, service failures we caused, or where required by law. You may cancel at any time to stop future renewal charges. Cancellation does not provide a refund for the current billing period.</p><p class="sub"><strong>31-Day Virtual Currency Window:</strong> Each issuance of virtual currency is valid for 31 days from the date it is issued. Any unused virtual currency expires at the end of that 31-day window and does not carry over. All virtual currency purchases are final and non-refundable. Virtual currency has no cash value, is non-transferable, and is not redeemable for cash, except where required by law.</p></div>'''
    marker = '<div class="fine">© 2026 What Bout Us'
    if marker in html:
        html = html.replace(marker, policy + marker, 1)

    if name == 'Simone':
        return html

    male = name in MALE_NAMES
    if male:
        voice_pattern, pitch, rate = 'Daniel|Aaron|Alex|Tom|Fred|Ralph|Oliver|Arthur|male', '0.94', '0.92'
    else:
        voice_pattern, pitch, rate = 'Samantha|Ava|Allison|Serena|Victoria|Karen|Zoe|female', '1.05', '0.93'

    controls = f'''<div class="card" style="margin-top:18px"><h2>{base.esc(name)} Voice</h2><p class="sub">Your 2-minute trial includes voice. On iPhone, tap Enable Voice once, then talk normally.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><button id="trial-voice-enable" type="button" class="btn">Enable Voice</button><button id="trial-voice-replay" type="button" class="btn alt">Replay Last Reply</button></div><div id="trial-voice-status" class="status" style="margin-top:10px">Voice ready</div></div>'''
    if marker in html:
        html = html.replace(marker, controls + marker, 1)

    script = f'''<script>
(function(){{
  const NAME={name!r};
  const enable=document.getElementById('trial-voice-enable');
  const replay=document.getElementById('trial-voice-replay');
  const status=document.getElementById('trial-voice-status');
  const history=document.getElementById('history');
  const send=document.getElementById('send');
  let enabled=false,last='';
  function pickVoice(){{
    const vs=(window.speechSynthesis&&speechSynthesis.getVoices)?speechSynthesis.getVoices().filter(v=>/^en/i.test(v.lang)):[];
    return vs.find(v=>/{voice_pattern}/i.test(v.name))||vs.find(v=>/^en-US/i.test(v.lang))||vs[0]||null;
  }}
  function speak(text){{if(!enabled||!text||!window.speechSynthesis)return;const u=new SpeechSynthesisUtterance(text);const v=pickVoice();if(v)u.voice=v;u.rate={rate};u.pitch={pitch};speechSynthesis.cancel();speechSynthesis.speak(u)}}
  function latest(){{if(!history)return '';const bubbles=[...history.querySelectorAll('.bubble:not(.you)')];if(!bubbles.length)return '';return bubbles[bubbles.length-1].textContent.replace(new RegExp('^'+NAME+':\\\\s*'),'').trim()}}
  function prime(){{enabled=true;try{{const u=new SpeechSynthesisUtterance(' ');u.volume=0;speechSynthesis.speak(u)}}catch(e){{}}if(status)status.textContent=NAME+' voice enabled'}}
  if(enable)enable.addEventListener('click',prime);
  if(send)send.addEventListener('pointerdown',prime,{{passive:true}});
  if(replay)replay.addEventListener('click',()=>{{prime();last=latest()||last;if(last)speak(last);else if(status)status.textContent='Send '+NAME+' a message first.'}});
  if(history){{const obs=new MutationObserver(()=>{{const t=latest();if(t&&t!==last){{last=t;if(enabled)setTimeout(()=>speak(t),60)}}}});obs.observe(history,{{childList:true,subtree:true}})}}
}})();
</script>'''
    return html.replace('</body>', script + '</body>', 1)

base.companion_page = hotfix_companion_page


def owner_html(name):
    html = base.companion_page(name)
    html = html.replace(
        'function guestState(){let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}',
        'function guestState(){return 86400}'
    )
    html = html.replace('if(!started)timer(r)', 'if(!started){}')
    html = html.replace(' · 2-minute free demo', ' · OWNER TEST UNLOCKED')
    html = html.replace(' · 2-minute free voice trial', ' · OWNER TEST UNLOCKED')
    html = html.replace('Free demo starts with your first message.', 'Owner test mode · no countdown')
    html = html.replace('Your free 2-minute conversation has ended. Subscribe to continue where you left off.', 'Owner test mode active.')
    return html


class Handler(lux.Handler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/owner-test':
            from urllib.parse import parse_qs
            supplied = parse_qs(u.query).get('token', [''])[0]
            if OWNER_TOKEN and hmac.compare_digest(supplied, OWNER_TOKEN):
                self.send_response(302)
                self.send_header('Set-Cookie', f'wbu_owner_test={OWNER_TOKEN}; Path=/; Max-Age=2592000; HttpOnly; Secure; SameSite=Strict')
                self.send_header('Location', '/')
                self.end_headers()
                return
            return self.sh(base.page('Owner Test — What Bout Us™', '<main class="shell"><div class="card"><h1>Owner test access denied</h1></div></main>'), 403)

        if owner_cookie_ok(self.headers) and u.path.startswith('/companion/'):
            slug = unquote(u.path.split('/companion/', 1)[1]).lower()
            name = next((x for x in base.ALL if x.lower() == slug), None)
            if name:
                return self.sh(owner_html(name))
        return super().do_GET()

    def do_POST(self):
        p = urlparse(self.path).path
        if p == '/api/auth/signup':
            d = self.body_json()
            if d.get('accepted_policy') is not True:
                return self.sj({'error':'You must read and agree to the Subscription & Virtual Currency Policy before creating an account.'}, 400)
            email = str(d.get('email','')).strip()
            password = str(d.get('password',''))
            name = str(d.get('display_name','')).strip()
            if not email or len(password) < 6:
                return self.sj({'error':'Use a valid email and a password of at least 6 characters.'}, 400)
            body = {'email':email,'password':password,'data':{'display_name':name,'policy_accepted':True,'policy_version':POLICY_VERSION,'policy_accepted_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}}
            s, o = app_v2.sb('/auth/v1/signup', method='POST', body=body)
            if s not in (200, 201):
                err = (o.get('msg') or o.get('message') or 'Authentication failed.') if isinstance(o, dict) else 'Authentication failed.'
                return self.sj({'error':err}, s)
            return self.sj(o)
        return super().do_POST()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
