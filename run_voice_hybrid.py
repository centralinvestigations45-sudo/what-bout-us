from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, os
import run_voice_controls as vc

# Natural OpenAI speech voices supplement the ElevenLabs roster where the
# available ElevenLabs pool cannot guarantee a gender-matched unique voice.
OPENAI_VOICES = {
    'Alex': ('onyx', 'Natural adult man. Warm, confident, relaxed, and conversational. Clearly masculine voice, natural pacing, no robotic cadence or announcer tone.'),
    'Hana': ('coral', 'Warm, natural adult woman. Friendly and conversational, with relaxed pacing and no announcer tone.'),
    'Riley': ('nova', 'Bright, natural adult woman. Easygoing, expressive, and conversational. Avoid robotic cadence.'),
    'Vivien': ('shimmer', 'Elegant, warm adult woman. Smooth, confident, natural pacing with subtle emotion.'),
    'Bella': ('sage', 'Calm, intelligent adult woman. Grounded, reassuring, and human-sounding with gentle variation.'),
    'Sahara': ('ballad', 'Rich, expressive adult woman. Warm and distinctive, with natural pauses and conversational rhythm.'),
    'Skye': ('marin', 'Modern, confident adult woman. Clear, personable, relaxed, and naturally expressive.'),
    'Nia': ('alloy', 'Warm adult woman with a polished but casual conversational delivery. Natural pacing, never robotic.'),
    'Ember': ('verse', 'Natural adult woman. Warm, expressive, personable, and clearly feminine in presentation, with relaxed conversational pacing and no robotic cadence.'),
}


def _openai_speech(name, text):
    voice, instructions = OPENAI_VOICES[name]
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key:
        raise RuntimeError('OPENAI_API_KEY is not configured')
    payload = json.dumps({
        'model': 'gpt-4o-mini-tts',
        'voice': voice,
        'input': text[:2000],
        'instructions': instructions,
        'response_format': 'mp3',
    }).encode('utf-8')
    req = Request(
        'https://api.openai.com/v1/audio/speech',
        data=payload,
        headers={
            'Authorization': 'Bearer ' + key,
            'Content-Type': 'application/json',
            'Accept': 'audio/mpeg',
        },
        method='POST',
    )
    with urlopen(req, timeout=30) as r:
        audio = r.read()
    if not audio:
        raise RuntimeError('OpenAI speech returned no audio')
    return audio


def hybrid_roster():
    base_roster = vc._voice_roster()
    rows = []
    identities = []
    for row in base_roster.get('rows', []):
        row = dict(row)
        name = row.get('companion')
        if name in OPENAI_VOICES:
            voice = OPENAI_VOICES[name][0]
            row['provider'] = 'openai'
            row['voice_name'] = voice
            row['voice_id_suffix'] = voice
            row['voice_gender'] = 'male' if name == 'Alex' else 'female'
            row['assigned'] = True
            identities.append('openai:' + voice)
        else:
            row['provider'] = 'elevenlabs'
            identities.append('elevenlabs:' + str(row.get('voice_id_suffix') or row.get('voice_name') or name))
        rows.append(row)
    unique = len(set(identities))
    gender_ok = all((r.get('gender') == r.get('voice_gender')) for r in rows)
    return {
        'remaining_companions': len(rows),
        'assigned': sum(1 for r in rows if r.get('assigned')),
        'unique_assignments': unique,
        'all_30_unique': len(rows) == 30 and unique == 30 and all(r.get('assigned') for r in rows),
        'all_gender_matched': gender_ok,
        'openai_voice_count': len(OPENAI_VOICES),
        'elevenlabs_distinct_available': base_roster.get('eligible_distinct_voices', 0),
        'rows': rows,
    }


class Handler(vc.Handler):
    def do_GET(self):
        if urlparse(self.path).path == '/health/voices':
            return self._json_fixed(200, hybrid_roster())
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != '/api/companion-voice':
            return super().do_POST()
        d = self.body_json()
        name = str(d.get('companion') or '').strip()
        text = str(d.get('text') or '').strip()
        if name not in OPENAI_VOICES:
            if name in ('Simone', 'Chloe') or name not in getattr(vc.base, 'ALL', []):
                return self._json_fixed(400, {'error':'This companion uses a separate voice path.'})
            if not text:
                return self._json_fixed(400, {'error':'Text is required.'})
            voice = vc._voice_for(name)
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
            from urllib.parse import quote
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

        if not text:
            return self._json_fixed(400, {'error':'Text is required.'})
        try:
            audio = _openai_speech(name, text)
            return self._audio(200, audio)
        except HTTPError as e:
            try:
                detail = e.read().decode('utf-8')[:500]
            except Exception:
                detail = ''
            print('WBU_OPENAI_VOICE_ERROR', name, e.code, detail, flush=True)
            return self._json_fixed(502, {'error':'Natural voice service rejected the request.'})
        except (URLError, TimeoutError, RuntimeError) as e:
            print('WBU_OPENAI_VOICE_ERROR', name, repr(e), flush=True)
            return self._json_fixed(502, {'error':'Natural voice service is temporarily unavailable.'})


if __name__ == '__main__':
    probe = {}
    for name in OPENAI_VOICES:
        try:
            audio = _openai_speech(name, 'Hello. This is a quick voice check for What Bout Us.')
            probe[name] = {'ok': True, 'bytes': len(audio), 'voice': OPENAI_VOICES[name][0]}
        except Exception as e:
            probe[name] = {'ok': False, 'error': repr(e), 'voice': OPENAI_VOICES[name][0]}
    print('WBU_HYBRID_VOICE_PROBE ' + json.dumps(probe, separators=(',', ':')), flush=True)
    print('WBU_HYBRID_VOICE_ROSTER ' + json.dumps(hybrid_roster(), separators=(',', ':')), flush=True)
    ThreadingHTTPServer(('0.0.0.0', vc.base.PORT), Handler).serve_forever()
