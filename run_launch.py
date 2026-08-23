import os
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer
import run_profile

base = run_profile.base

# Final homepage ordering: swap Simone with Alex and Chloe with Lily.
base.MEN = ['Simone','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Darius','Noah','Jack','Julius','Leo','Carter','Malik','Alex']
base.WOMEN = ['Chloe','Aria','Mika','Zoey','Nova','Sophia','Isabella','Lily','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye','Nia']
base.ALL = base.MEN + base.WOMEN

# Annual Square checkout URLs are separate from the existing monthly links.
SQUARE_PLUS_YEARLY_URL = os.environ.get('SQUARE_PLUS_YEARLY_URL', '').strip()
SQUARE_UNLIMITED_YEARLY_URL = os.environ.get('SQUARE_UNLIMITED_YEARLY_URL', '').strip()

# Approved What Bout Us jingle — Version 1.
JINGLE_URL = 'https://audio.soundbreak.ai/c400f54fbbbbb70e4ad0907b4a0db9bc/92d335c3524bf043daa63e2b284773bd.mp3'

_original_home = base.home


def annual_home():
    html = _original_home()

    plus_old = '''<div class="plan"><h3>WHAT BOUT US™+</h3><div class="price">$9.99 <small>/ month</small></div><p>Text conversations · Multiple companions · Conversation memory · Multiple languages</p><a class="btn alt" href="/checkout?plan=plus">Choose Plus</a></div>'''
    plus_new = '''<div class="plan"><h3>WHAT BOUT US™+</h3><div class="price">$9.99 <small>/ month</small></div><p>Text conversations · Multiple companions · Conversation memory · Multiple languages</p><a class="btn alt" href="/checkout?plan=plus">Choose Monthly</a><div style="margin-top:18px;padding-top:18px;border-top:1px solid #35353e"><div style="font-size:13px;font-weight:900;letter-spacing:.8px;color:#72d8a0;margin-bottom:5px">SAVE $19.89</div><div class="price" style="font-size:32px">$99.99 <small>/ year</small></div><p class="sub" style="margin:6px 0 14px">About 2 months free compared with monthly billing.</p><a class="btn" href="/checkout?plan=plus-yearly">Choose Yearly</a></div></div>'''

    unlimited_old = '''<div class="plan hot"><h3>WHAT BOUT US™ UNLIMITED</h3><div class="price">$14.99 <small>/ month</small></div><p>All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories</p><a class="btn" href="/checkout?plan=unlimited">Choose Unlimited</a></div>'''
    unlimited_new = '''<div class="plan hot"><div style="display:inline-block;background:#d36580;color:white;border-radius:999px;padding:6px 10px;font-size:11px;font-weight:900;letter-spacing:.7px;margin-bottom:10px">BEST VALUE</div><h3>WHAT BOUT US™ UNLIMITED</h3><div class="price">$14.99 <small>/ month</small></div><p>All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories</p><a class="btn alt" href="/checkout?plan=unlimited">Choose Monthly</a><div style="margin-top:18px;padding-top:18px;border-top:1px solid #57334a"><div style="font-size:13px;font-weight:900;letter-spacing:.8px;color:#72d8a0;margin-bottom:5px">SAVE $29.89</div><div class="price" style="font-size:32px">$149.99 <small>/ year</small></div><p class="sub" style="margin:6px 0 14px">About 2 months free compared with monthly billing.</p><a class="btn" href="/checkout?plan=unlimited-yearly">Choose Yearly</a></div></div>'''

    html = html.replace(plus_old, plus_new)
    html = html.replace(unlimited_old, unlimited_new)

    player = f'''
<div id="wbu-jingle-player" style="position:fixed;left:14px;right:14px;bottom:14px;z-index:9999;max-width:520px;margin:auto;background:#131319ee;border:1px solid #3b3b45;border-radius:18px;padding:12px 14px;box-shadow:0 10px 35px #0009;backdrop-filter:blur(12px)">
  <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
    <div style="min-width:0"><div style="font-weight:900;font-size:14px">What Bout Us™ Jingle</div><div id="wbu-jingle-status" style="font-size:11px;color:#aaa;margin-top:2px">Tap anywhere to start</div></div>
    <div style="display:flex;gap:7px;flex-shrink:0">
      <button type="button" onclick="wbuPlay()" aria-label="Play jingle" style="background:#d36580;color:#fff;border:0;border-radius:11px;padding:9px 11px;font-weight:800">Play</button>
      <button type="button" onclick="wbuPause()" aria-label="Pause jingle" style="background:#202026;color:#fff;border:1px solid #444;border-radius:11px;padding:9px 11px;font-weight:800">Pause</button>
      <button type="button" onclick="wbuStop()" aria-label="Stop jingle" style="background:#202026;color:#fff;border:1px solid #444;border-radius:11px;padding:9px 11px;font-weight:800">Stop</button>
    </div>
  </div>
</div>
<audio id="wbu-jingle" preload="auto" playsinline src="{JINGLE_URL}"></audio>
<script>
(function(){{
  const a=document.getElementById('wbu-jingle');
  const s=document.getElementById('wbu-jingle-status');
  let userPaused=false,userStopped=false,started=false;
  function status(t){{if(s)s.textContent=t}}
  window.wbuPlay=function(){{userPaused=false;userStopped=false;a.play().then(()=>{{started=true;status('Playing')}}).catch(()=>status('Tap anywhere to start'));}};
  window.wbuPause=function(){{userPaused=true;a.pause();status('Paused');}};
  window.wbuStop=function(){{userStopped=true;userPaused=false;a.pause();a.currentTime=0;status('Stopped');}};
  function tryStart(){{if(started||userPaused||userStopped)return;a.play().then(()=>{{started=true;status('Playing')}}).catch(()=>status('Tap anywhere to start'));}}
  // Try immediately. Browsers that allow sound autoplay will start at once.
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',tryStart,{once:true});else tryStart();
  // iPhone/Safari and many browsers block sound autoplay. The first click/tap anywhere on the site starts it.
  document.addEventListener('click',tryStart);
  document.addEventListener('touchend',tryStart,{passive:true});
  a.addEventListener('ended',()=>{{started=false;status('Finished');}});
}})();
</script>
'''
    html = html.replace('</body>', player + '</body>')
    return html


base.home = annual_home


class LaunchHandler(run_profile.run_current.ProductionHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/checkout':
            plan = parse_qs(u.query).get('plan', [''])[0]
            if plan in ('plus-yearly', 'unlimited-yearly'):
                target = SQUARE_PLUS_YEARLY_URL if plan == 'plus-yearly' else SQUARE_UNLIMITED_YEARLY_URL
                if target:
                    self.send_response(302)
                    self.send_header('Location', target)
                    self.end_headers()
                    return
                label = 'WHAT BOUT US™+ Annual — $99.99/year' if plan == 'plus-yearly' else 'WHAT BOUT US™ UNLIMITED Annual — $149.99/year'
                return self.sh(base.page('Annual Checkout — What Bout Us™', f'<main class="shell"><div class="card"><h1>{label}</h1><p class="sub">Secure annual billing through Square is being connected. This plan will renew once per year until canceled.</p><a class="btn alt" href="/#plans">Back to Plans</a></div>{base.footer()}</main>'))
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), LaunchHandler).serve_forever()
