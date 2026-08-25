from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, os
import run_chloe_fix as chloe

base = chloe.base

# Give Chloe a fresh, versioned 2-minute trial state without changing
# Simone or the subscription rules for any other companion.
_original_companion_page = base.companion_page

def companion_page_chloe_unlock(name):
    html = _original_companion_page(name)
    if name == 'Chloe':
        html = html.replace('wbu_guest_trial_20260825d_', 'wbu_guest_trial_20260825e_')
    return html

base.companion_page = companion_page_chloe_unlock

class Handler(chloe.Handler):
    def do_POST(self):
        if urlparse(self.path).path != '/api/chloe-voice':
            return super().do_POST()
        d = self.body_json()
        text = str(d.get('text') or '').strip()
        if not text:
            return self._json_fixed(400, {'error':'Text is required.'})
        api_key = os.environ.get('ELEVENLABS_API_KEY','').strip()
        voice_id = os.environ.get('CHLOE_ELEVENLABS_VOICE_ID','').strip()
        if not api_key or not voice_id:
            return self._json_fixed(503, {'error':'Chloe voice is not configured.'})
        payload = json.dumps({'text':text[:2500],'model_id':'eleven_turbo_v2_5','voice_settings':{'stability':0.42,'similarity_boost':0.82,'style':0.28,'use_speaker_boost':True}}).encode('utf-8')
        req = Request('https://api.elevenlabs.io/v1/text-to-speech/'+voice_id+'?output_format=mp3_44100_128',data=payload,headers={'xi-api-key':api_key,'Content-Type':'application/json','Accept':'audio/mpeg'},method='POST')
        try:
            with urlopen(req,timeout=25) as r:
                audio=r.read()
            if not audio:
                return self._json_fixed(502, {'error':'Chloe voice returned no audio.'})
            return self._audio(200,audio)
        except HTTPError:
            return self._json_fixed(502, {'error':'Chloe voice service rejected the request.'})
        except (URLError,TimeoutError):
            return self._json_fixed(502, {'error':'Chloe voice service is temporarily unavailable.'})

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
