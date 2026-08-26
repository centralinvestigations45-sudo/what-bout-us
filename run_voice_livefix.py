from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import json
import re
import run_voice_hybrid as hybrid

base = hybrid.vc.base
_original_companion_page = base.companion_page
_original_footer = base.footer

# Fresh versioned browser trial state so stale/consumed localStorage keys cannot
# leave the production conversation UI permanently locked after a deploy.
TRIAL_KEY = 'wbu_guest_trial_20260825_unlock2_'


def _support_signature_panel():
    return '''
<div style="max-width:920px;margin:28px auto 18px;padding:26px;border-radius:22px;background:linear-gradient(135deg,#09051a 0%,#17103b 48%,#330822 100%);border:1px solid rgba(255,72,206,.65);box-shadow:0 0 28px rgba(54,124,255,.18),0 0 34px rgba(255,41,181,.12);color:#fff;text-align:center">
  <div style="font-size:28px;font-weight:800;letter-spacing:.4px;background:linear-gradient(90deg,#39a9ff,#9a5cff,#ff43b7);-webkit-background-clip:text;background-clip:text;color:transparent">What Bout Us™</div>
  <div style="margin-top:7px;font-size:16px;font-style:italic;color:#d9d4ff">Someone to talk to, someone who remembers.</div>
  <div style="width:86px;height:2px;margin:16px auto;background:linear-gradient(90deg,#39a9ff,#ff43b7)"></div>
  <div style="font-size:18px;font-weight:700;margin-bottom:10px">Support Team</div>
  <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;font-size:15px">
    <a href="mailto:support@whatboutus.com" style="color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.2);padding:10px 14px;border-radius:999px;background:rgba(255,255,255,.06)">✉ support@whatboutus.com</a>
    <a href="https://www.whatboutus.com" style="color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.2);padding:10px 14px;border-radius:999px;background:rgba(255,255,255,.06)">🌐 www.whatboutus.com</a>
  </div>
  <div style="margin-top:18px;color:#cfc9e8;font-size:14px">Chat • Voice • Personality • 10 Languages</div>
  <div style="margin-top:10px;font-size:13px;color:#afa8ca">Thank you for being part of the What Bout Us community. ♡</div>
</div>'''


def footer_with_support_email():
    html = _original_footer()
    if 'wbu-support-signature' in html:
        return html
    panel = _support_signature_panel().replace('<div style="max-width:920px', '<div id="wbu-support-signature" style="max-width:920px', 1)
    return panel + html


base.footer = footer_with_support_email


def _fix_trial_access(html):
    # Normalize any older/versioned guest trial key to the current production key.
    html = re.sub(r'G="wbu_guest_trial_[^"]*"\+N', f'G="{TRIAL_KEY}"+N', html)
    html = html.replace('G="wbu_guest_trial_"+N', f'G="{TRIAL_KEY}"+N')

    # Every companion gets the same two-minute guest test. Paid access rules still
    # take over after that timer expires; this only fixes initial test access.
    html = html.replace('N==="Simone"||N==="Chloe"||N==="Nia"', 'true')
    html = html.replace('N==="Simone"||N==="Chloe"', 'true')
    html = html.replace(' · paid subscription required', ' · 2-minute free voice trial')
    return html


def companion_page_server_audio_only(name):
    html = _fix_trial_access(_original_companion_page(name))

    # Ensure the styled support signature is visible on companion pages whose
    # footer HTML may have been rendered before the footer wrapper was installed.
    if 'wbu-support-signature' not in html:
        marker = '<div class="fine">© 2026 What Bout Us'
        panel = _support_signature_panel().replace('<div style="max-width:920px', '<div id="wbu-support-signature" style="max-width:920px', 1)
        if marker in html:
            html = html.replace(marker, panel + marker, 1)
        else:
            html = html.replace('</main>', panel + '</main>', 1)

    # Simone and Chloe keep their dedicated voice paths, but receive the same
    # refreshed two-minute conversation test state as the rest of the roster.
    if name in ('Simone', 'Chloe'):
        return html

    name_json = json.dumps(name)
    script = f'''<script>
(function(){{
  const NAME={name_json};
  let lastText='';
  let currentAudio=null;
  let speaking=false;

  function voiceEnabled(){{
    try{{ return typeof window.wbuVoiceEnabled==='function' ? window.wbuVoiceEnabled() : true; }}catch(e){{ return true; }}
  }}

  function disableDeviceSpeech(){{
    try{{
      if(window.speechSynthesis){{
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak=function(){{ return; }};
      }}
    }}catch(e){{}}
  }}

  async function serverSpeak(text){{
    text=(text||'').trim();
    if(!text || !voiceEnabled() || speaking)return;
    speaking=true;
    try{{
      disableDeviceSpeech();
      if(currentAudio){{ try{{currentAudio.pause();}}catch(e){{}} currentAudio=null; }}
      const r=await fetch('/api/companion-voice',{{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify({{companion:NAME,text:text}})
      }});
      if(!r.ok)throw new Error('server voice unavailable');
      const blob=await r.blob();
      const url=URL.createObjectURL(blob);
      const a=new Audio(url);
      currentAudio=a;
      a.playsInline=true;
      a.onended=()=>{{speaking=false;URL.revokeObjectURL(url);}};
      a.onerror=()=>{{speaking=false;URL.revokeObjectURL(url);}};
      await a.play();
    }}catch(e){{
      speaking=false;
      console.warn('WBU server voice failed for '+NAME,e);
    }}
  }}

  function latestReply(){{
    const history=document.getElementById('history');
    if(!history)return '';
    const bubbles=[...history.querySelectorAll('.bubble:not(.you)')];
    if(!bubbles.length)return '';
    let t=(bubbles[bubbles.length-1].textContent||'').trim();
    t=t.replace(new RegExp('^'+NAME+':\\s*','i'),'').trim();
    return t;
  }}

  function checkReply(){{
    disableDeviceSpeech();
    const t=latestReply();
    if(t && t!==lastText){{ lastText=t; setTimeout(()=>serverSpeak(t),80); }}
  }}

  disableDeviceSpeech();
  document.addEventListener('DOMContentLoaded',function(){{
    disableDeviceSpeech();
    const history=document.getElementById('history');
    if(history){{
      const obs=new MutationObserver(checkReply);
      obs.observe(history,{{childList:true,subtree:true,characterData:true}});
    }}
    const send=document.getElementById('send');
    if(send)send.addEventListener('pointerdown',disableDeviceSpeech,{{passive:true}});
    setTimeout(disableDeviceSpeech,250);
    setTimeout(disableDeviceSpeech,1000);
  }});
}})();
</script>'''
    return html.replace('</body>', script + '</body>', 1)


base.companion_page = companion_page_server_audio_only


class Handler(hybrid.Handler):
    def do_GET(self):
        return super().do_GET()


if __name__ == '__main__':
    print('WBU_LIVE_VOICE_FIX conversation-unlock2 + server-audio-only + styled-support-signature enabled', flush=True)
    print('WBU_LIVE_VOICE_ROSTER ' + json.dumps(hybrid.hybrid_roster(), separators=(',', ':')), flush=True)
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
