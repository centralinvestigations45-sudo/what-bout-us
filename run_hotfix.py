from http.server import ThreadingHTTPServer
import run_luxury_catalog as lux

base = lux.base
wallet = lux.wallet
pricing = lux.pricing

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
try:
    app_v2 = lux.run_nia_test.app_v2
    app_v2.FREE.update(base.ALL)
except Exception:
    pass

_original_companion_page = base.companion_page

MALE_NAMES = set(getattr(base, 'MEN', []))

def hotfix_companion_page(name):
    html = _original_companion_page(name)

    # Open the guest trial gate to every companion without changing paid-plan logic.
    html = html.replace('N==="Simone"||N==="Chloe"||N==="Nia"', 'true')
    html = html.replace('N==="Simone"||N==="Chloe"', 'true')
    html = html.replace(' · paid subscription required', ' · 2-minute free voice trial')

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
    marker = '<div class="fine">© 2026 What Bout Us'
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
    pass

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
