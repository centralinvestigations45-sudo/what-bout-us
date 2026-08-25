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

# Chloe hotfix: keep Simone untouched, remove Chloe demo lock for owner testing,
# and add an explicit iPhone-safe voice enable/replay control.
_original_companion_page = base.companion_page

def hotfix_companion_page(name):
    html = _original_companion_page(name)
    if name != 'Chloe':
        return html

    html = html.replace(
        'function guestState(){let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}',
        'function guestState(){if(N==="Chloe")return 86400;let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}'
    )
    html = html.replace('if(!started)timer(r)', 'if(!started&&N!=="Chloe")timer(r)')
    html = html.replace(' · 2-minute free demo', ' · OWNER TEST UNLOCKED', 1)
    html = html.replace('Free demo starts with your first message.', 'Owner test mode · Chloe voice enabled', 1)

    controls = '''<div class="card" style="margin-top:18px"><h2>Chloe Voice</h2><p class="sub">On iPhone, tap Enable Chloe Voice once. Chloe can then speak after replies. Use Replay Last Reply any time.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><button id="chloe-enable" type="button" class="btn">Enable Chloe Voice</button><button id="chloe-replay" type="button" class="btn alt">Replay Last Reply</button></div><div id="chloe-voice-status" class="status" style="margin-top:10px">Voice ready to enable</div></div>'''
    marker = '<div class="fine">© 2026 What Bout Us'
    if marker in html:
        html = html.replace(marker, controls + marker, 1)

    script = r'''<script>
(function(){
  const enable=document.getElementById('chloe-enable');
  const replay=document.getElementById('chloe-replay');
  const status=document.getElementById('chloe-voice-status');
  const history=document.getElementById('history');
  const send=document.getElementById('send');
  let enabled=false,last='';
  function voice(){
    const vs=(window.speechSynthesis&&speechSynthesis.getVoices)?speechSynthesis.getVoices():[];
    return vs.find(v=>/Samantha|Ava|Allison|Serena|Victoria|Karen|female/i.test(v.name)&&/^en/i.test(v.lang))||vs.find(v=>/^en-US/i.test(v.lang))||vs.find(v=>/^en/i.test(v.lang))||null;
  }
  function speak(text){
    if(!text||!window.speechSynthesis)return;
    const u=new SpeechSynthesisUtterance(text);
    const v=voice(); if(v)u.voice=v;
    u.rate=.92; u.pitch=1.08;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  }
  function latest(){
    if(!history)return '';
    const bubbles=[...history.querySelectorAll('.bubble:not(.you)')];
    if(!bubbles.length)return '';
    return bubbles[bubbles.length-1].textContent.replace(/^Chloe:\s*/,'').trim();
  }
  if(enable)enable.addEventListener('click',()=>{enabled=true;status.textContent='Chloe voice enabled';speak('Chloe voice enabled.');});
  if(replay)replay.addEventListener('click',()=>{last=latest()||last;if(last)speak(last);else status.textContent='Send Chloe a message first.';});
  if(send)send.addEventListener('pointerdown',()=>{enabled=true;try{const u=new SpeechSynthesisUtterance(' ');u.volume=0;speechSynthesis.speak(u);}catch(e){}},{passive:true});
  if(history){
    const obs=new MutationObserver(()=>{const t=latest();if(t&&t!==last){last=t;if(enabled)setTimeout(()=>speak(t),60);}});
    obs.observe(history,{childList:true,subtree:true});
  }
})();
</script>'''
    return html.replace('</body>', script + '</body>', 1)

base.companion_page = hotfix_companion_page

class Handler(lux.Handler):
    pass

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
