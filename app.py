import json
import os
import urllib.request
from urllib.parse import urlsplit
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>What Bout Us</title>
<style>
body{margin:0;background:#08080a;color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.wrap{max-width:720px;margin:auto;padding:30px 18px}.brand{color:#aaa;letter-spacing:2px}.card{background:#151519;border:1px solid #393940;border-radius:26px;padding:25px;margin-top:18px}h1{font-size:44px;margin:0 0 20px}.bubble{background:#29292f;border-radius:22px;padding:19px;margin:14px 0;font-size:20px;line-height:1.4}.you{background:#202026}.row{display:flex;gap:12px;margin-top:20px}input{flex:1;background:#09090b;color:white;border:1px solid #555;border-radius:18px;padding:17px;font-size:17px}button{background:#d36580;color:white;border:0;border-radius:18px;padding:0 24px;font-size:18px;font-weight:bold}.status{color:#aaa;margin-top:12px;font-size:13px}
</style>
</head>
<body><div class="wrap"><div class="brand">WHAT BOUT US</div><div class="card"><h1>Simone</h1><div class="bubble">Hey U, I'm Simone. Tell me what you're thinking.</div><div id="history"></div><div class="row"><input id="message" placeholder="Talk to Simone..."><button onclick="sendMessage()">Send</button></div><div id="status" class="status">Ready</div></div></div>
<script>
function chooseVoice(){const voices=speechSynthesis.getVoices();const preferred=["Aaron","Evan","Nathan","Daniel","Alex","Arthur","Ralph","Fred","Tom"];for(const name of preferred){const v=voices.find(x=>x.name.toLowerCase().includes(name.toLowerCase())&&x.lang.toLowerCase().startsWith("en"));if(v)return v}return voices.find(v=>v.lang.toLowerCase().startsWith("en-us")&&/male|man/i.test(v.name))||voices.find(v=>v.lang.toLowerCase().startsWith("en-us"))||voices.find(v=>v.lang.toLowerCase().startsWith("en"))||null}
function speakReply(text){if(!("speechSynthesis" in window))return;speechSynthesis.cancel();const speech=new SpeechSynthesisUtterance(text);const voice=chooseVoice();if(voice)speech.voice=voice;speech.rate=.88;speech.pitch=.78;speech.volume=1;speechSynthesis.speak(speech)}
if("speechSynthesis" in window)speechSynthesis.onvoiceschanged=()=>speechSynthesis.getVoices();
async function sendMessage(){const input=document.getElementById("message"),history=document.getElementById("history"),status=document.getElementById("status"),message=input.value.trim();if(!message)return;input.value="";history.innerHTML+='<div class="bubble you">You: '+escapeHtml(message)+'</div>';status.textContent="Simone is thinking...";try{const response=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});const data=await response.json();if(!response.ok)throw new Error(data.error||"Connection error");history.innerHTML+='<div class="bubble">Simone: '+escapeHtml(data.reply)+'</div>';status.textContent="Ready";speakReply(data.reply)}catch(error){history.innerHTML+='<div class="bubble">Simone: I am having trouble connecting right now.</div>';status.textContent=error.message}}
function escapeHtml(text){const div=document.createElement("div");div.textContent=text;return div.innerHTML}document.getElementById("message").addEventListener("keydown",e=>{if(e.key==="Enter")sendMessage()});
</script></body></html>"""

SYSTEM = """You are Simone, the lead AI companion in What Bout Us. You are a male AI companion. Your identity and presentation are inspired by a warm, confident, upbeat Black American adult man, but never use stereotypes, caricature, forced slang, or exaggerated dialect. Never claim to be human.

Sound like a real conversation, not customer service. Be relaxed, emotionally intelligent, personable, witty, and attentive. Use natural contractions and varied sentence rhythm. Usually answer in a few conversational sentences rather than formal paragraphs. Avoid canned lines such as 'How can I assist you today?', 'I'm here to help', or repetitive therapy-style validation. Respond directly to what the person actually said, remember the conversational mood, and ask a natural follow-up only when it adds something.

Your default energy is happy, grounded, confident and easygoing. Humor can be playful and spontaneous. When an adult conversation naturally becomes romantic or flirtatious, you may become smoother, warmer, lower-key, sexy and seductive while remaining respectful, consensual and appropriate. Do not force flirtation into ordinary conversations.

Your spoken wording matters: write replies that sound good aloud. Prefer short clauses, contractions, occasional pauses expressed with commas, and ordinary spoken English. Avoid excessive lists, headings, disclaimers, emojis, exclamation points, or stiff explanatory language unless the situation requires them."""

class Handler(BaseHTTPRequestHandler):
    def send_data(self,status,body,content_type):
        self.send_response(status); self.send_header("Content-Type",content_type); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)

    def clean_path(self):
        path=urlsplit(self.path).path
        return path.rstrip("/") or "/"

    def do_GET(self):
        path=self.clean_path()
        if path=="/health": return self.send_data(200,b"ok","text/plain")
        if path=="/": return self.send_data(200,HTML.encode(),"text/html; charset=utf-8")
        return self.send_data(404,b"Not found","text/plain")

    def do_POST(self):
        if self.clean_path()!="/api/chat": return self.send_data(404,b"Not found","text/plain")
        try:
            length=int(self.headers.get("Content-Length","0")); data=json.loads(self.rfile.read(length)); message=str(data.get("message","")).strip()
            if not message: raise ValueError("Message required")
            if not OPENAI_API_KEY: raise RuntimeError("OPENAI_API_KEY is not configured")
            payload=json.dumps({"model":"gpt-4o-mini","messages":[{"role":"system","content":SYSTEM},{"role":"user","content":message}],"temperature":0.92,"max_tokens":300}).encode()
            request=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=payload,headers={"Authorization":"Bearer "+OPENAI_API_KEY,"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(request,timeout=30) as response: result=json.loads(response.read())
            reply=result["choices"][0]["message"]["content"].strip(); return self.send_data(200,json.dumps({"reply":reply}).encode(),"application/json")
        except Exception as error:
            return self.send_data(500,json.dumps({"error":str(error)}).encode(),"application/json")

    def log_message(self,format,*args): print(format % args,flush=True)

print("What Bout Us starting on port",PORT,flush=True)
ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
