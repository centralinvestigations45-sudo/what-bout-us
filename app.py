import json, os, html, urllib.request
from urllib.parse import urlparse, parse_qs, unquote, quote
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT=int(os.environ.get('PORT','8080')); OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY',''); ELEVENLABS_API_KEY=os.environ.get('ELEVENLABS_API_KEY',''); ELEVENLABS_VOICE_ID=os.environ.get('ELEVENLABS_VOICE_ID','zyvhtiIsOyDz7MdFNCoL').strip(); SQUARE_PLUS_URL=os.environ.get('SQUARE_PLUS_URL','').strip(); SQUARE_UNLIMITED_URL=os.environ.get('SQUARE_UNLIMITED_URL','').strip()
MEN=['Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Darius','Noah','Jack','Julius','Leo','Carter','Tyler','Simone']; WOMEN=['Lily','Aria','Mika','Zoey','Nova','Sophia','Isabella','Chloe','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye','Nia']; ALL=MEN+WOMEN
TRAITS={'Simone':'funny, compassionate, considerate, business-minded, intelligent, street-smart, romantic, ambitious, spontaneous, courteous, distinguished, kind, bold, adventurous and protective'}
def esc(s): return html.escape(str(s),quote=True)
STANDALONE=['Simone','Chloe','Darius','Isabella','Julius','Nia']
def portrait(name):
 if name=='Simone': return '/static/simone.jpg'
 if name in STANDALONE: return '/static/'+name.lower()+'.jpg?v=19'
 i=ALL.index(name); hue=(i*37)%360; initials=esc(name[:1]); return 'data:image/svg+xml;utf8,'+quote(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="24" fill="hsl({hue},28%,28%)"/><text x="60" y="72" text-anchor="middle" font-family="Arial" font-size="44" fill="white">{initials}</text></svg>''')
def url(n): return '/companion/'+quote(n.lower())
CSS='''*{box-sizing:border-box}body{margin:0;background:#08080b;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit;text-decoration:none}.shell{max-width:1180px;margin:auto;padding:0 18px}.nav{position:sticky;top:0;z-index:20;background:#08080bee;border-bottom:1px solid #292932}.navin{height:70px;display:flex;align-items:center;justify-content:space-between}.brand{font-weight:900;font-size:22px}.tm{font-size:.48em;vertical-align:super;margin-left:2px}.grad{background:linear-gradient(90deg,#63d7ff,#d45fff,#ff688e);-webkit-background-clip:text;color:transparent}.links{display:flex;gap:18px;color:#bbb}.hero{min-height:500px;display:grid;grid-template-columns:1.1fr .9fr;align-items:center;gap:34px}.hero h1{font-size:clamp(50px,8vw,88px);line-height:.94;margin:12px 0}.lead,.sub{color:#bbb;line-height:1.55}.lead{font-size:20px}.art{min-height:340px;border:1px solid #333;border-radius:32px;display:grid;place-items:center;text-align:center;background:radial-gradient(circle at 65% 30%,#5d1b6b,transparent 34%),#101016}.section{padding:58px 0}.section h2{font-size:40px}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:12px}.comp{background:#131319;border:1px solid #303039;border-radius:18px;padding:10px;text-align:center}.avatar{width:82px;height:82px;margin:0 auto 9px;border-radius:16px;overflow:hidden;background:#222}.avatar img,.bigavatar img{width:100%;height:100%;object-fit:cover}.comp small{display:block;color:#72d8a0;font-size:9px;margin-top:4px}.plans{display:grid;grid-template-columns:1fr 1fr;gap:18px}.plan,.card{background:#131319;border:1px solid #35353e;border-radius:25px;padding:26px}.plan.hot{border-color:#d36580}.price{font-size:40px;font-weight:900}.btn{display:inline-block;background:#d36580;border:0;color:#fff;border-radius:16px;padding:14px 19px;font-weight:800;cursor:pointer}.btn.alt{background:#19191f;border:1px solid #444}.fine{text-align:center;color:#888;font-size:12px;padding:35px 0 55px}.back{display:inline-block;margin:24px 0;color:#aaa}.profile{display:grid;grid-template-columns:190px 1fr;gap:24px;align-items:center}.bigavatar{width:165px;height:165px;border-radius:24px;overflow:hidden}.bubble{background:#29292f;border-radius:22px;padding:17px;margin:12px 0;font-size:18px}.you{background:#202026}.row{display:flex;gap:10px}.row input{flex:1;background:#09090b;color:#fff;border:1px solid #555;border-radius:18px;padding:16px;font-size:17px}.status{color:#aaa;font-size:13px;margin-top:10px}.chips{display:flex;flex-wrap:wrap;gap:9px}.chip{background:#202026;border:1px solid #45454d;border-radius:999px;padding:10px 13px}.banner{display:inline-block;background:#17121a;border:1px solid #57334a;border-radius:18px;padding:12px;color:#edc6d1}@media(max-width:850px){.hero{grid-template-columns:1fr}.grid{grid-template-columns:repeat(4,1fr)}.plans{grid-template-columns:1fr}.profile{grid-template-columns:1fr}.links{display:none}}@media(max-width:480px){.grid{grid-template-columns:repeat(2,1fr)}}'''
def footer(): return '<div class="fine">© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>'
def nav(): return '<div class="nav"><div class="shell navin"><a class="brand" href="/"><span class="grad">WHAT BOUT US<span class="tm">™</span></span></a><div class="links"><a href="/#companions">Companions</a><a href="/#plans">Plans</a><a href="/account">Account</a><a href="/simone">Talk to Simone</a></div></div></div>'
def page(t,b): return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(t)}</title><style>{CSS}</style></head><body>{nav()}{b}</body></html>'
def cards(names): return ''.join(f'<a class="comp" href="{url(n)}"><div class="avatar"><img src="{portrait(n)}" alt="{esc(n)} AI companion"></div><b>{esc(n)}</b><small>LIVE</small></a>' for n in names)
def home():
 b=f'''<main class="shell"><section class="hero"><div><div class="grad">AI COMPANIONS</div><h1>Someone to talk to.<br><span class="grad">Someone who remembers.</span></h1><p class="lead">Meet 32 distinct AI companions with personality, conversation, multiple languages and premium customization.</p><a class="btn" href="#companions">Meet the Companions</a> <a class="btn alt" href="/simone">Talk to Simone</a></div><div class="art"><div><h2>What <span class="grad">Bout Us<span class="tm">™</span></span></h2><p>AI COMPANIONS</p></div></div></section><section id="companions" class="section"><h2>32 AI Companions</h2><p class="sub">16 men. 16 women. Tap any picture to open a live conversation.</p><h3>16 MEN</h3><div class="grid">{cards(MEN)}</div><h3 style="margin-top:28px">16 WOMEN</h3><div class="grid">{cards(WOMEN)}</div></section><section id="plans" class="section"><h2>Choose Your Experience</h2><div class="plans"><div class="plan"><h3>WHAT BOUT US™+</h3><div class="price">$9.99 <small>/ month</small></div><p>Text conversations · Multiple companions · Conversation memory · Multiple languages</p><a class="btn alt" href="/checkout?plan=plus">Choose Plus</a></div><div class="plan hot"><h3>WHAT BOUT US™ UNLIMITED</h3><div class="price">$14.99 <small>/ month</small></div><p>All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories</p><a class="btn" href="/checkout?plan=unlimited">Choose Unlimited</a></div></div></section>{footer()}</main>'''; return page('What Bout Us™ — AI Companions',b)
def companion_page(name):
 intro="Hey U, I'm Simone. Tell me what you're thinking." if name=='Simone' else f"Hey, I'm {name}. What's on your mind?"
 premium='''<div class="card" style="margin-top:18px"><h2>Premium Style</h2><p class="sub">Expanded accessories and style customization.</p><div class="chips"><span class="chip">Casual</span><span class="chip">Business</span><span class="chip">Athletic</span><span class="chip">Streetwear</span><span class="chip">Sunglasses</span><span class="chip">Watch</span><span class="chip">Chain</span><span class="chip">Hat</span><span class="chip">Ring</span></div></div>''' if name=='Simone' else ''
 b=f'''<main class="shell"><a class="back" href="/">← Back to all companions</a><div class="card"><div class="profile"><div class="bigavatar"><img src="{portrait(name)}" alt="{esc(name)}"></div><div><div class="grad">LIVE COMPANION</div><h1>{esc(name)}</h1><p class="lead" style="font-size:17px">{esc(TRAITS.get(name,'warm, supportive and engaging').capitalize())}.</p>{'<span class="banner">Simone voice is enabled.</span>' if name=='Simone' else ''}</div></div><div class="bubble">{esc(intro)}</div><div id="history"></div><div class="row"><input id="message" placeholder="Talk to {esc(name)}..."><button class="btn" onclick="sendMessage()">Send</button></div><div id="status" class="status">Ready</div></div>{premium}{footer()}</main><script>const NAME={json.dumps(name)},H=document.getElementById('history');function x(t){{let d=document.createElement('div');d.textContent=t;return d.innerHTML}}async function sendMessage(){{let i=document.getElementById('message'),m=i.value.trim(),s=document.getElementById('status');if(!m)return;i.value='';H.innerHTML+='<div class="bubble you">You: '+x(m)+'</div>';s.textContent=NAME+' is thinking...';try{{let r=await fetch('/api/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:m,companion:NAME}})}}),d=await r.json();H.innerHTML+='<div class="bubble">'+NAME+': '+x(d.reply)+'</div>';s.textContent='Ready';if(NAME==='Simone'){{let q=await fetch('/api/speech',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{text:d.reply}})}});if(q.ok)new Audio(URL.createObjectURL(await q.blob())).play()}}}}catch(e){{s.textContent='Connection error'}}}}</script>'''; return page(name+' — What Bout Us™',b)
def chat_reply(c,m):
 if not OPENAI_API_KEY:return "I'm here with you. Tell me a little more about that."
 sys=f'You are {c}, an adult AI companion in What Bout Us™. Be warm, concise and natural. Never claim to be human. Users must be 21+.'; data=json.dumps({'model':'gpt-4o-mini','messages':[{'role':'system','content':sys},{'role':'user','content':m}],'max_tokens':220}).encode(); req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=data,headers={'Authorization':'Bearer '+OPENAI_API_KEY,'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=30) as r:return json.loads(r.read().decode())['choices'][0]['message']['content'].strip()
 except:return "I'm here with you. Tell me a little more about that."
def audio(t):
 if not(ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID):return None
 data=json.dumps({'text':t[:1200],'model_id':'eleven_multilingual_v2'}).encode(); req=urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/'+quote(ELEVENLABS_VOICE_ID),data=data,headers={'xi-api-key':ELEVENLABS_API_KEY,'Content-Type':'application/json','Accept':'audio/mpeg'})
 try:
  with urllib.request.urlopen(req,timeout=35) as r:return r.read()
 except:return None
class H(BaseHTTPRequestHandler):
 def sh(self,s,status=200):
  b=s.encode();self.send_response(status);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def sj(self,d,status=200):
  b=json.dumps(d).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);p=u.path
  if p=='/static/simone.jpg':
   try:
    b=open(os.path.join(os.path.dirname(__file__),'static','simone.jpg'),'rb').read();self.send_response(200);self.send_header('Content-Type','image/jpeg');self.send_header('Cache-Control','public, max-age=3600');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
   except:return self.sh('Image not found',404)
  if p=='/health':return self.sj({'ok':True,'companions':32,'simonePhoto':True,'copyright':2026,'trademark':True})
  if p=='/':return self.sh(home())
  if p=='/simone':self.send_response(302);self.send_header('Location','/companion/simone');self.end_headers();return
  if p.startswith('/companion/'):
   slug=unquote(p.split('/companion/',1)[1]).lower();n=next((x for x in ALL if x.lower()==slug),None);return self.sh(companion_page(n)) if n else self.sh('Not found',404)
  if p=='/account':return self.sh(page('Account — What Bout Us™','<main class="shell"><div class="card"><h1>Your Account</h1><p>Account authentication is being connected.</p></div>'+footer()+'</main>'))
  if p=='/checkout':
   plan=parse_qs(u.query).get('plan',['plus'])[0];target=SQUARE_UNLIMITED_URL if plan=='unlimited' else SQUARE_PLUS_URL
   if target:self.send_response(302);self.send_header('Location',target);self.end_headers();return
   return self.sh(page('Checkout — What Bout Us™','<main class="shell"><div class="card"><h1>Secure Checkout</h1><p>Square checkout is being connected.</p></div>'+footer()+'</main>'))
  return self.sh('Not found',404)
 def do_POST(self):
  n=int(self.headers.get('Content-Length','0') or 0)
  try:d=json.loads(self.rfile.read(n).decode() or '{}')
  except:d={}
  if self.path=='/api/chat':return self.sj({'reply':chat_reply(str(d.get('companion','Simone')),str(d.get('message',''))[:3000])})
  if self.path=='/api/speech':
   a=audio(str(d.get('text','')))
   if not a:return self.sj({'error':'Voice unavailable'},503)
   self.send_response(200);self.send_header('Content-Type','audio/mpeg');self.send_header('Content-Length',str(len(a)));self.end_headers();self.wfile.write(a);return
  return self.sj({'error':'Not found'},404)
 def log_message(self,*a):pass
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',PORT),H).serve_forever()