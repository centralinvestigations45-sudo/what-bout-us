import json
import os
import urllib.request
import urllib.error
from urllib.parse import urlsplit, quote
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "zyvhtiIsOyDz7MdFNCoL").strip()

HTML = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>What Bout Us</title><style>body{margin:0;background:#08080a;color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{max-width:720px;margin:auto;padding:30px 18px}.brand{color:#aaa;letter-spacing:2px}.card{background:#151519;border:1px solid #393940;border-radius:26px;padding:25px;margin-top:18px}h1{font-size:44px;margin:0 0 20px}.bubble{background:#29292f;border-radius:22px;padding:19px;margin:14px 0;font-size:20px;line-height:1.4}.you{background:#202026}.row{display:flex;gap:12px;margin-top:20px}input{flex:1;background:#09090b;color:white;border:1px solid #555;border-radius:18px;padding:17px;font-size:17px}button{background:#d36580;color:white;border:0;border-radius:18px;padding:0 24px;font-size:18px;font-weight:bold}.status{color:#aaa;margin-top:12px;font-size:13px}</style></head><body><div class="wrap"><div class="brand">WHAT BOUT US</div><div class="card"><h1>Simone</h1><div class="bubble">Hey U, I'm Simone. Tell me what you're thinking.</div><div id="history"></div><div class="row"><input id="message" placeholder="Talk to Simone..."><button onclick="sendMessage()">Send</button></div><div id="status" class="status">Ready</div></div></div><script>
let currentAudio=null;
function browserFallback(text){try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.rate=.96;u.pitch=.9;speechSynthesis.speak(u)}catch(e){console.log(e)}}
async function speakReply(text){const status=document.getElementById('status');try{if(currentAudio){currentAudio.pause();currentAudio=null}status.textContent='Simone is speaking...';const r=await fetch('/api/speech',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});if(!r.ok){const e=await r.text();console.log('Speech unavailable',e);status.textContent='Voice unavailable';return browserFallback(text)}const blob=await r.blob();if(!blob.size){status.textContent='Voice unavailable';return browserFallback(text)}const url=URL.createObjectURL(blob);currentAudio=new Audio(url);currentAudio.playsInline=true;currentAudio.onended=()=>{URL.revokeObjectURL(url);status.textContent='Ready'};try{await currentAudio.play()}catch(e){status.textContent='Tap screen then send again';browserFallback(text)}}catch(e){console.log('Speech error',e);status.textContent='Voice unavailable';browserFallback(text)}}
async function sendMessage(){const input=document.getElementById('message'),history=document.getElementById('history'),status=document.getElementById('status'),message=input.value.trim();if(!message)return;input.value='';history.innerHTML+='<div class="bubble you">You: '+escapeHtml(message)+'</div>';status.textContent='Simone is thinking...';try{const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});const data=await response.json();if(!response.ok)throw new Error(data.error||'Connection error');history.innerHTML+='<div class="bubble">Simone: '+escapeHtml(data.reply)+'</div>';await speakReply(data.reply)}catch(error){history.innerHTML+='<div class="bubble">Simone: I am having trouble connecting right now.</div>';status.textContent=error.message}}
function escapeHtml(text){const div=document.createElement('div');div.textContent=text;return div.innerHTML}document.getElementById('message').addEventListener('keydown',e=>{if(e.key==='Enter')sendMessage()});</script></body></html>"""

SYSTEM = """You are Simone, the lead male AI companion in What Bout Us. Your presentation is inspired by a warm, confident, upbeat Black American adult man, without stereotypes or caricature. Never claim to be human. Sound like a real conversation, not customer service: relaxed, emotionally intelligent, personable, witty, attentive, and natural. Use contractions and varied spoken rhythm. Avoid canned assistant phrases and stiff explanatory language. Your default energy is happy, grounded, confident and easygoing. Humor can be playful. When an adult conversation naturally becomes romantic or flirtatious, you may become smoother, warmer, lower-key, sexy and seductive while remaining respectful, consensual and appropriate. Never force flirtation. Write replies that sound good aloud: short clauses, natural pauses, ordinary spoken English, and usually a few conversational sentences."""

class Handler(BaseHTTPRequestHandler):
    def send_data(self,status,body,content_type):
        self.send_response(status); self.send_header('Content-Type',content_type); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
    def clean_path(self):
        path=urlsplit(self.path).path; return path.rstrip('/') or '/'
    def read_json(self):
        length=int(self.headers.get('Content-Length','0')); return json.loads(self.rfile.read(length))
    def do_GET(self):
        path=self.clean_path()
        if path=='/health': return self.send_data(200,b'ok','text/plain')
        if path=='/voice-health':
            body=json.dumps({'key_configured':bool(ELEVENLABS_API_KEY),'voice_id':ELEVENLABS_VOICE_ID,'voice_id_length':len(ELEVENLABS_VOICE_ID)}).encode()
            return self.send_data(200,body,'application/json')
        if path=='/': return self.send_data(200,HTML.encode(),'text/html; charset=utf-8')
        return self.send_data(404,b'Not found','text/plain')
    def do_POST(self):
        path=self.clean_path()
        try:
            data=self.read_json()
            if path=='/api/chat':
                if not OPENAI_API_KEY: raise RuntimeError('OPENAI_API_KEY is not configured')
                message=str(data.get('message','')).strip()
                if not message: raise ValueError('Message required')
                payload=json.dumps({'model':'gpt-4o-mini','messages':[{'role':'system','content':SYSTEM},{'role':'user','content':message}],'temperature':0.92,'max_tokens':300}).encode()
                req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=payload,headers={'Authorization':'Bearer '+OPENAI_API_KEY,'Content-Type':'application/json'},method='POST')
                with urllib.request.urlopen(req,timeout=30) as response: result=json.loads(response.read())
                reply=result['choices'][0]['message']['content'].strip(); return self.send_data(200,json.dumps({'reply':reply}).encode(),'application/json')
            if path=='/api/speech':
                if not ELEVENLABS_API_KEY: raise RuntimeError('ELEVENLABS_API_KEY is not configured')
                if not ELEVENLABS_VOICE_ID: raise RuntimeError('ELEVENLABS_VOICE_ID is not configured')
                text=str(data.get('text','')).strip()
                if not text: raise ValueError('Text required')
                payload=json.dumps({'text':text[:4000],'model_id':'eleven_multilingual_v2','voice_settings':{'stability':0.45,'similarity_boost':0.75}}).encode('utf-8')
                url='https://api.elevenlabs.io/v1/text-to-speech/'+quote(ELEVENLABS_VOICE_ID,safe='')
                req=urllib.request.Request(url,data=payload,headers={'xi-api-key':ELEVENLABS_API_KEY.strip(),'Content-Type':'application/json','Accept':'audio/mpeg'},method='POST')
                try:
                    with urllib.request.urlopen(req,timeout=45) as response:
                        audio=response.read(); ctype=response.headers.get('Content-Type','audio/mpeg')
                    if not audio: raise RuntimeError('ElevenLabs returned empty audio')
                    print('ELEVENLABS OK bytes=',len(audio),'voice=',ELEVENLABS_VOICE_ID,flush=True)
                    return self.send_data(200,audio,ctype if 'audio' in ctype else 'audio/mpeg')
                except urllib.error.HTTPError as e:
                    detail=e.read().decode('utf-8','replace')
                    print('ELEVENLABS ERROR status=',e.code,'voice=',ELEVENLABS_VOICE_ID,'detail=',detail,flush=True)
                    return self.send_data(502,json.dumps({'error':'ElevenLabs request failed','status':e.code,'detail':detail}).encode(),'application/json')
            return self.send_data(404,b'Not found','text/plain')
        except Exception as error:
            print('APP ERROR',repr(error),flush=True)
            return self.send_data(500,json.dumps({'error':str(error)}).encode(),'application/json')
    def log_message(self,format,*args): print(format % args,flush=True)

print('What Bout Us starting on port',PORT,flush=True)
ThreadingHTTPServer(('0.0.0.0',PORT),Handler).serve_forever()
