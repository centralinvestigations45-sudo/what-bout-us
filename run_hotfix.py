from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_luxury_catalog as lux

base = lux.base
wallet = lux.wallet
pricing = lux.pricing
app_v2 = lux.run_nia_test.app_v2

# Production footwear hotfix: remove duplicate/logo-bearing cards and correct Work Boots price.
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

# All 32 companions get the same 2-minute guest trial.
# Simone's existing ElevenLabs voice path is intentionally left untouched.
app_v2.FREE.update(base.ALL)

# Signup policy acknowledgement: users must actively confirm the refund and virtual-currency terms.
POLICY_VERSION = '2026-08-25-v1'
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
  if(k==="signup" && (!box || !box.checked)){
    return m("You must read and check the policy agreement before creating your account.");
  }
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

    # Open the guest trial gate to every companion without changing paid-plan logic.
    html = html.replace('N==="Simone"||N==="Chloe"||N==="Nia"', 'true')
    html = html.replace('N==="Simone"||N==="Chloe"', 'true')
    html = html.replace(' · paid subscription required', ' · 2-minute free voice trial')

    # Make refund/cancellation and virtual-currency expiration terms visible on every companion page.
    policy = '''<div class="card" style="margin-top:18px"><h2>Subscription & Virtual Currency Policy</h2><p class="sub"><strong>14-Day Refund Policy:</strong> Refund requests must be submitted within 14 days of the initial subscription purchase. After 14 days, subscription payments are non-refundable, except for duplicate charges, verified billing errors, unauthorized transactions, service failures we caused, or where required by law. You may cancel at any time to stop future renewal charges. Cancellation does not provide a refund for the current billing period.</p><p class="sub"><strong>31-Day Virtual Currency Window:</strong> Each issuance of virtual currency is valid for 31 days from the date it is issued. Any unused virtual currency expires at the end of that 31-day window and does not carry over. All virtual currency purchases are final and non-refundable. Virtual currency has no cash value, is non-transferable, and is not redeemable for cash, except where required by law.</p></div>'''
    marker = '<div class="fine">© 2026 What Bout Us'
    if marker in html:
        html = html.replace(marker, policy + marker, 1)

    # Simone already has the correct voice. Do not alter his audio controls or voice routing.
    if name == 'Simone':
        return html

    male = name in MALE_NAMES
    if male:
        voice_pattern = 'Daniel|Aaron|Alex|Tom|Fred|Ralph|Oliver|Arthur|male'
        pitch = '0.94'
        rate = '0.92'
    else:
        voice_pattern = 'Samantha|Ava|Allison|Serena|Victoria|Karen|Zoe|female'
        pitch = '1.05'
        rate = '0.93'

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
  function speak(text){{
    if(!enabled||!text||!window.speechSynthesis)return;
    const u=new SpeechSynthesisUtterance(text);
    const v=pickVoice(); if(v)u.voice=v;
    u.rate={rate}; u.pitch={pitch};
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  }}
  function latest(){{
    if(!history)return '';
    const bubbles=[...history.querySelectorAll('.bubble:not(.you)')];
    if(!bubbles.length)return '';
    return bubbles[bubbles.length-1].textContent.replace(new RegExp('^'+NAME+':\\\\s*'),'').trim();
  }}
  function prime(){{
    enabled=true;
    try{{const u=new SpeechSynthesisUtterance(' ');u.volume=0;speechSynthesis.speak(u);}}catch(e){{}}
    if(status)status.textContent=NAME+' voice enabled';
  }}
  if(enable)enable.addEventListener('click',prime);
  if(send)send.addEventListener('pointerdown',prime,{{passive:true}});
  if(replay)replay.addEventListener('click',()=>{{prime();last=latest()||last;if(last)speak(last);else if(status)status.textContent='Send '+NAME+' a message first.';}});
  if(history){{
    const obs=new MutationObserver(()=>{{const t=latest();if(t&&t!==last){{last=t;if(enabled)setTimeout(()=>speak(t),60);}}}});
    obs.observe(history,{{childList:true,subtree:true}});
  }}
}})();
</script>'''
    return html.replace('</body>', script + '</body>', 1)

base.companion_page = hotfix_companion_page

class Handler(lux.Handler):
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
            body = {
                'email': email,
                'password': password,
                'data': {
                    'display_name': name,
                    'policy_accepted': True,
                    'policy_version': POLICY_VERSION,
                    'policy_accepted_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
                }
            }
            s, o = app_v2.sb('/auth/v1/signup', method='POST', body=body)
            if s not in (200, 201):
                err = (o.get('msg') or o.get('message') or 'Authentication failed.') if isinstance(o, dict) else 'Authentication failed.'
                return self.sj({'error':err}, s)
            return self.sj(o)
        return super().do_POST()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
