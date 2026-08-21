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
body{margin:0;background:#08080a;color:white;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:720px;margin:auto;padding:30px 18px}.brand{color:#aaa;letter-spacing:2px}.card{background:#151519;border:1px solid #393940;border-radius:26px;padding:25px;margin-top:18px}h1{font-size:44px;margin:0 0 20px}.bubble{background:#29292f;border-radius:22px;padding:19px;margin:14px 0;font-size:20px;line-height:1.4}.you{background:#202026}.row{display:flex;gap:12px;margin-top:20px}input{flex:1;background:#09090b;color:white;border:1px solid #555;border-radius:18px;padding:17px;font-size:17px}button{background:#d36580;color:white;border:0;border-radius:18px;padding:0 24px;font-size:18px;font-weight:bold}.status{color:#aaa;margin-top:12px;font-size:13px}
</style>
</head>
<body><div class="wrap"><div class="brand">WHAT BOUT US</div><div class="card"><h1>Simone</h1><div class="bubble">Hey U, I'm Simone. Tell me what you're thinking.</div><div id="history"></div><div class="row"><input id="message" placeholder="Talk to Simone..."><button onclick="sendMessage()">Send</button></div><div id="status" class="status">Ready</div></div></div>
<script>
async function sendMessage(){const input=document.getElementById("message"),history=document.getElementById("history"),status=document.getElementById("status"),message=input.value.trim();if(!message)return;input.value="";history.innerHTML+='<div class="bubble you">You: '+escapeHtml(message)+'</div>';status.textContent="Simone is thinking...";try{const response=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})});const data=await response.json();if(!response.ok)throw new Error(data.error||"Connection error");history.innerHTML+='<div class="bubble">Simone: '+escapeHtml(data.reply)+'</div>';status.textContent="Ready";if("speechSynthesis" in window){speechSynthesis.cancel();const speech=new SpeechSynthesisUtterance(data.reply);speech.rate=.94;speech.pitch=.9;speechSynthesis.speak(speech)}}catch(error){history.innerHTML+='<div class="bubble">Simone: I am having trouble connecting right now.</div>';status.textContent=error.message}}
function escapeHtml(text){const div=document.createElement("div");div.textContent=text;return div.innerHTML}document.getElementById("message").addEventListener("keydown",e=>{if(e.key==="Enter")sendMessage()});
</script></body></html>"""

SYSTEM = """You are Simone, the lead AI companion in What Bout Us.
Simone is a happy, warm, confident Black male AI companion.
He is conversational, emotionally intelligent, playful, caring, and supportive without being patronizing.
His normal personality is upbeat, relaxed, funny and personable.
When an adult conversation naturally becomes romantic or flirtatious, his tone can become smooth, sexy and seductive while remaining respectful and appropriate.
Never claim to be human. Respond naturally rather than sounding robotic."""

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
            payload=json.dumps({"model":"gpt-4o-mini","messages":[{"role":"system","content":SYSTEM},{"role":"user","content":message}],"temperature":0.9,"max_tokens":300}).encode()
            request=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=payload,headers={"Authorization":"Bearer "+OPENAI_API_KEY,"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(request,timeout=30) as response: result=json.loads(response.read())
            reply=result["choices"][0]["message"]["content"].strip(); return self.send_data(200,json.dumps({"reply":reply}).encode(),"application/json")
        except Exception as error:
            return self.send_data(500,json.dumps({"error":str(error)}).encode(),"application/json")

    def log_message(self,format,*args): print(format % args,flush=True)

print("What Bout Us starting on port",PORT,flush=True)
ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
