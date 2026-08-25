from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import json
import run_voice_hybrid as hybrid

base = hybrid.vc.base
_original_companion_page = base.companion_page


def companion_page_server_audio_only(name):
    html = _original_companion_page(name)
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
    print('WBU_LIVE_VOICE_FIX server-audio-only enabled for 30 companions', flush=True)
    print('WBU_LIVE_VOICE_ROSTER ' + json.dumps(hybrid.hybrid_roster(), separators=(',', ':')), flush=True)
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
