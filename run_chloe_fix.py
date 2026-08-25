from http.server import ThreadingHTTPServer
from difflib import SequenceMatcher
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import os
import run_signup_fix as signup

base = signup.base
app_v2 = signup.app_v2
_original_companion_page = base.companion_page
_original_reply = app_v2.reply


def _norm(text):
    return ' '.join(str(text or '').lower().split())


def chloe_reply(name, msg, hist, mem):
    candidate = _original_reply(name, msg, hist, mem)
    if name != 'Chloe':
        return candidate

    previous = ''
    for item in reversed(hist or []):
        if item.get('role') == 'assistant' and item.get('content'):
            previous = item.get('content')
            break

    if previous:
        similarity = SequenceMatcher(None, _norm(previous), _norm(candidate)).ratio()
        if similarity >= 0.72:
            candidate = _original_reply(
                name,
                msg + '\n\nUse fresh wording and add a new thought. Do not repeat or closely paraphrase the previous reply.',
                hist,
                list(mem or []) + ['Chloe varies her wording, avoids repeated openings, and moves the conversation forward naturally.']
            )
    return candidate


app_v2.reply = chloe_reply


def companion_page_fresh_trial(name):
    html = _original_companion_page(name)
    html = html.replace('G="wbu_guest_trial_"+N', 'G="wbu_guest_trial_20260825d_"+N')

    if name == 'Chloe':
        # Never use device/browser speech synthesis for Chloe. Her replies are
        # rendered by the server-side natural voice endpoint below.
        start = html.find('<div class="card" style="margin-top:18px"><h2>Chloe Voice</h2>')
        if start != -1:
            end = html.find('<div class="fine">© 2026 What Bout Us', start)
            if end != -1:
                html = html[:start] + html[end:]

        html = html.replace('if(N==="Simone")say(d.reply);try{let u=new SpeechSynthesisUtterance(d.reply)', 'if(N==="Simone")say(d.reply);if(N==="Chloe")chloeSay(d.reply);else try{let u=new SpeechSynthesisUtterance(d.reply)')
        html = html.replace('if(N==="Simone")say(d.reply);if(N==="Nia")', 'if(N==="Simone")say(d.reply);if(N==="Chloe")chloeSay(d.reply);else if(N==="Nia")')

        script = r'''<script>
(function(){
  let chloeAudio=null;
  window.chloeSay=async function(text){
    if(!text)return;
    const status=document.getElementById('chloe-voice-status');
    try{
      if(chloeAudio){chloeAudio.pause();chloeAudio=null;}
      if(status)status.textContent='Chloe is speaking…';
      const r=await fetch('/api/chloe-voice',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:text})});
      if(!r.ok){let d={};try{d=await r.json()}catch(e){}throw new Error(d.error||'Voice unavailable');}
      const blob=await r.blob();
      const url=URL.createObjectURL(blob);
      chloeAudio=new Audio(url);
      chloeAudio.playsInline=true;
      chloeAudio.onended=()=>{URL.revokeObjectURL(url);if(status)status.textContent='Voice ready';};
      chloeAudio.onerror=()=>{URL.revokeObjectURL(url);if(status)status.textContent='Tap Play Last Reply';};
      await chloeAudio.play();
    }catch(e){if(status)status.textContent='Tap Play Last Reply';}
  };
  document.addEventListener('DOMContentLoaded',function(){
    const history=document.getElementById('history');
    const fine=document.querySelector('.fine');
    const wrap=document.createElement('div');
    wrap.className='card';wrap.style.marginTop='18px';
    wrap.innerHTML='<h2>Chloe Voice</h2><p class="sub">Natural voice is on. If iPhone blocks automatic audio, tap Play Last Reply once.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><button id="chloe-play" type="button" class="btn">Play Last Reply</button></div><div id="chloe-voice-status" class="status" style="margin-top:10px">Voice ready</div>';
    if(fine&&fine.parentNode)fine.parentNode.insertBefore(wrap,fine);
    const b=document.getElementById('chloe-play');
    if(b)b.addEventListener('click',function(){
      if(!history)return;
      const bubbles=[...history.querySelectorAll('.bubble:not(.you)')];
      if(!bubbles.length)return;
      const t=bubbles[bubbles.length-1].textContent.replace(/^Chloe:\s*/,'').trim();
      if(t)window.chloeSay(t);
    });
  });
})();
</script>'''
        html = html.replace('</body>', script + '</body>', 1)
    return html


base.companion_page = companion_page_fresh_trial


class Handler(signup.Handler):
    def _audio(self, status, data, content_type='audio/mpeg'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/chloe-voice':
            d = self.body_json()
            text = str(d.get('text') or '').strip()
            if not text:
                return self._json_fixed(400, {'error':'Text is required.'})
            text = text[:2500]
            api_key = os.environ.get('ELEVENLABS_API_KEY', '').strip()
            voice_id = os.environ.get('ELEVENLABS_VOICE_ID', '').strip()
            if not api_key or not voice_id:
                return self._json_fixed(503, {'error':'Chloe voice is not configured.'})
            payload = json.dumps({
                'text': text,
                'model_id': 'eleven_turbo_v2_5',
                'voice_settings': {
                    'stability': 0.42,
                    'similarity_boost': 0.82,
                    'style': 0.28,
                    'use_speaker_boost': True
                }
            }).encode('utf-8')
            req = Request(
                'https://api.elevenlabs.io/v1/text-to-speech/' + voice_id + '?output_format=mp3_44100_128',
                data=payload,
                headers={'xi-api-key':api_key,'Content-Type':'application/json','Accept':'audio/mpeg'},
                method='POST'
            )
            try:
                with urlopen(req, timeout=25) as r:
                    audio = r.read()
                if not audio:
                    return self._json_fixed(502, {'error':'Chloe voice returned no audio.'})
                return self._audio(200, audio)
            except HTTPError as e:
                return self._json_fixed(502, {'error':'Chloe voice service rejected the request.'})
            except (URLError, TimeoutError):
                return self._json_fixed(502, {'error':'Chloe voice service is temporarily unavailable.'})
        return super().do_POST()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
