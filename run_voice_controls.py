from http.server import ThreadingHTTPServer
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, os, time
import run_chloe_voice_split as split

base = split.base
_original_companion_page = base.companion_page
_voice_cache = {'at': 0, 'voices': []}


def _available_voices():
    now = time.time()
    if _voice_cache['voices'] and now - _voice_cache['at'] < 1800:
        return _voice_cache['voices']
    api_key = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    if not api_key:
        return []
    req = Request('https://api.elevenlabs.io/v1/voices', headers={'xi-api-key': api_key, 'Accept': 'application/json'})
    try:
        with urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode('utf-8'))
        voices = data.get('voices') or []
        simone_id = os.environ.get('ELEVENLABS_VOICE_ID', '').strip()
        chloe_id = os.environ.get('CHLOE_ELEVENLABS_VOICE_ID', '').strip()
        voices = [v for v in voices if v.get('voice_id') and v.get('voice_id') not in {simone_id, chloe_id}]
        _voice_cache['at'] = now
        _voice_cache['voices'] = voices
        return voices
    except Exception:
        return _voice_cache['voices']


def _gender(v):
    labels = v.get('labels') or {}
    g = str(labels.get('gender') or labels.get('sex') or '').lower()
    name = str(v.get('name') or '').lower()
    if g in ('male', 'female'):
        return g
    if any(x in name for x in ('female', 'woman', 'girl')):
        return 'female'
    if any(x in name for x in ('male', 'man', 'boy')):
        return 'male'
    return ''


def _voice_for(name):
    voices = _available_voices()
    if not voices:
        return None
    male_names = set(getattr(base, 'MEN', []))
    wanted = 'male' if name in male_names else 'female'
    pool = [v for v in voices if _gender(v) == wanted]
    if not pool:
        pool = voices
    companions = [n for n in getattr(base, 'ALL', []) if n not in ('Simone', 'Chloe')]
    try:
        idx = companions.index(name)
    except ValueError:
        idx = sum(ord(c) for c in name)
    return pool[idx % len(pool)] if pool else None


def companion_page_with_voice_toggle(name):
    html = _original_companion_page(name)
    if 'id="wbu-voice-enabled"' in html:
        return html

    control = f'''<div class="card" style="margin-top:18px"><label style="display:flex;gap:12px;align-items:center;cursor:pointer"><input id="wbu-voice-enabled" type="checkbox" checked style="width:22px;height:22px;flex:0 0 auto"><span><strong>Speak replies aloud</strong><br><span class="sub">Turn this off any time you want text-only conversation with {base.esc(name)}.</span></span></label></div>'''

    footer_marker = '<div class="fine">© 2026 What Bout Us'
    if footer_marker in html:
        html = html.replace(footer_marker, control + footer_marker, 1)
    else:
        html = html.replace('</main>', control + '</main>', 1)

    companion_json = json.dumps(name)
    script = f'''<script>
(function(){{
  const COMPANION={companion_json};
  function box(){{ return document.getElementById('wbu-voice-enabled'); }}
  function key(){{ return 'wbu_voice_enabled_' + String(COMPANION).toLowerCase(); }}
  window.wbuVoiceEnabled=function(){{ const b=box(); return !b || b.checked; }};
  document.addEventListener('DOMContentLoaded',function(){{
    const b=box(); if(!b)return;
    const saved=localStorage.getItem(key());
    b.checked=saved===null ? true : saved==='1';
    b.addEventListener('change',function(){{
      localStorage.setItem(key(),b.checked?'1':'0');
      if(!b.checked){{ try{{speechSynthesis.cancel();}}catch(e){{}} if(window.wbuNaturalAudio){{try{{window.wbuNaturalAudio.pause();}}catch(e){{}}}} }}
    }});
  }});

  async function naturalSay(text){{
    if(!window.wbuVoiceEnabled() || !text)return;
    try{{
      if(window.wbuNaturalAudio){{try{{window.wbuNaturalAudio.pause();}}catch(e){{}}}}
      const r=await fetch('/api/companion-voice',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{companion:COMPANION,text:text}})}});
      if(!r.ok)throw new Error('voice unavailable');
      const blob=await r.blob(),url=URL.createObjectURL(blob),a=new Audio(url);
      window.wbuNaturalAudio=a;a.playsInline=true;
      a.onended=()=>URL.revokeObjectURL(url);
      a.onerror=()=>URL.revokeObjectURL(url);
      await a.play();
    }}catch(e){{}}
  }}

  if(COMPANION!=='Simone' && COMPANION!=='Chloe' && window.speechSynthesis && typeof window.speechSynthesis.speak==='function'){{
    const originalSpeak=window.speechSynthesis.speak.bind(window.speechSynthesis);
    window.speechSynthesis.speak=function(utterance){{
      if(!window.wbuVoiceEnabled())return;
      const text=utterance && utterance.text ? utterance.text : '';
      if(text){{naturalSay(text);return;}}
      return originalSpeak(utterance);
    }};
  }}

  function wrap(fnName){{
    const fn=window[fnName];
    if(typeof fn!=='function')return;
    window[fnName]=function(){{if(!window.wbuVoiceEnabled())return;return fn.apply(this,arguments);}};
  }}
  wrap('say');wrap('chloeSay');
}})();
</script>'''
    html = html.replace('</body>', script + '</body>', 1)
    return html


base.companion_page = companion_page_with_voice_toggle


class Handler(split.Handler):
    def do_POST(self):
        path = urlparse(self.path).path
        if path != '/api/companion-voice':
            return super().do_POST()
        d = self.body_json()
        name = str(d.get('companion') or '').strip()
        text = str(d.get('text') or '').strip()
        if name in ('Simone', 'Chloe') or name not in getattr(base, 'ALL', []):
            return self._json_fixed(400, {'error':'This companion uses a separate voice path.'})
        if not text:
            return self._json_fixed(400, {'error':'Text is required.'})
        voice = _voice_for(name)
        if not voice:
            return self._json_fixed(503, {'error':'No natural companion voice is available.'})
        api_key = os.environ.get('ELEVENLABS_API_KEY', '').strip()
        vid = str(voice.get('voice_id') or '').strip()
        if not api_key or not vid:
            return self._json_fixed(503, {'error':'Natural voice is not configured.'})
        idx = sum(ord(c) for c in name)
        stability = 0.38 + (idx % 9) * 0.025
        style = 0.12 + (idx % 7) * 0.035
        payload = json.dumps({'text':text[:2500],'model_id':'eleven_turbo_v2_5','voice_settings':{'stability':round(min(stability,0.62),2),'similarity_boost':0.8,'style':round(min(style,0.33),2),'use_speaker_boost':True}}).encode('utf-8')
        req = Request('https://api.elevenlabs.io/v1/text-to-speech/'+quote(vid)+'?output_format=mp3_44100_128',data=payload,headers={'xi-api-key':api_key,'Content-Type':'application/json','Accept':'audio/mpeg'},method='POST')
        try:
            with urlopen(req,timeout=25) as r:
                audio=r.read()
            if not audio:
                return self._json_fixed(502, {'error':'Natural voice returned no audio.'})
            return self._audio(200,audio)
        except HTTPError:
            return self._json_fixed(502, {'error':'Natural voice service rejected the request.'})
        except (URLError,TimeoutError):
            return self._json_fixed(502, {'error':'Natural voice service is temporarily unavailable.'})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
