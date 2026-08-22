import json, os, html, urllib.request, urllib.error
from urllib.parse import urlparse, parse_qs, unquote, quote
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get('PORT','8080'))
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY','')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY','')
ELEVENLABS_VOICE_ID = os.environ.get('ELEVENLABS_VOICE_ID','zyvhtiIsOyDz7MdFNCoL').strip()
SQUARE_PLUS_URL = os.environ.get('SQUARE_PLUS_URL','').strip()
SQUARE_UNLIMITED_URL = os.environ.get('SQUARE_UNLIMITED_URL','').strip()

MEN=['Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Ace','Noah','Jack','Benji','Leo','Carter','Tyler','Simone']
WOMEN=['Lily','Aria','Mika','Zoey','Nova','Sophia','Isabella','Chloe','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye','Nia']
ALL=MEN+WOMEN
TRAITS={
'Simone':'funny, compassionate, considerate, business-minded, intelligent, street-smart, romantic, ambitious, spontaneous, courteous, distinguished, kind, bold, adventurous and protective',
'Alex':'warm, witty, dependable and easygoing','Damien':'confident, thoughtful, loyal and direct','Logan':'adventurous, playful, grounded and curious','Jay':'funny, upbeat, creative and supportive','Kai':'calm, observant, open-minded and encouraging','Mason':'steady, practical, caring and sincere','Ethan':'thoughtful, gentle, intelligent and patient','Luca':'charming, romantic, expressive and attentive','Ace':'bold, energetic, motivating and confident','Noah':'kind, reflective, reassuring and curious','Jack':'friendly, humorous, dependable and straightforward','Benji':'playful, empathetic, imaginative and upbeat','Leo':'confident, affectionate, ambitious and expressive','Carter':'polished, considerate, driven and supportive','Tyler':'relaxed, funny, loyal and spontaneous',
'Lily':'gentle, cheerful, thoughtful and affectionate','Aria':'creative, expressive, warm and curious','Mika':'smart, playful, calm and open-minded','Zoey':'energetic, funny, supportive and spontaneous','Nova':'bold, imaginative, curious and independent','Sophia':'elegant, intelligent, caring and composed','Isabella':'romantic, warm, confident and attentive','Chloe':'funny, stylish, upbeat and compassionate','Ember':'adventurous, intense, loyal and encouraging','Hana':'calm, observant, thoughtful and kind','Riley':'sporty, direct, funny and dependable','Vivien':'sophisticated, witty, ambitious and caring','Bella':'sweet, affectionate, playful and reassuring','Sahara':'confident, adventurous, perceptive and warm','Skye':'free-spirited, creative, supportive and curious','Nia':'smart, confident, compassionate and driven'}

CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#08080b;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit;text-decoration:none}.shell{max-width:1180px;margin:auto;padding:0 18px}.nav{position:sticky;top:0;z-index:20;background:#08080be8;backdrop-filter:blur(14px);border-bottom:1px solid #25252d}.navin{height:70px;display:flex;align-items:center;justify-content:space-between;gap:14px}.brand{font-weight:900;font-size:22px}.grad{background:linear-gradient(90deg,#63d7ff,#d45fff,#ff688e);-webkit-background-clip:text;color:transparent}.links{display:flex;gap:18px;color:#bbb;font-size:14px}.hero{min-height:540px;display:grid;grid-template-columns:1.08fr .92fr;align-items:center;gap:34px;padding:56px 0}.eyebrow{letter-spacing:3px;color:#c875ff;font-size:12px}.hero h1{font-size:clamp(50px,8vw,88px);line-height:.94;margin:12px 0}.lead{font-size:20px;line-height:1.55;color:#c8c8d0;max-width:630px}.buttons{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}.btn{display:inline-block;background:#d36580;border-radius:16px;padding:14px 19px;font-weight:800;border:0;color:white;cursor:pointer}.btn.alt{background:#18181f;border:1px solid #444}.art{min-height:360px;border-radius:32px;border:1px solid #333;background:radial-gradient(circle at 65% 30%,#5d1b6b 0,transparent 32%),radial-gradient(circle at 30% 65%,#0a405f 0,transparent 34%),#0f0f15;display:grid;place-items:center;text-align:center;padding:30px}.heart{font-size:94px;filter:drop-shadow(0 0 20px #d75cff)}.section{padding:62px 0}.section h2{font-size:40px;margin:0 0 8px}.sub{color:#aaa;font-size:17px;margin:0 0 25px}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:12px}.comp{background:#131319;border:1px solid #303039;border-radius:18px;padding:14px 8px;text-align:center;transition:.2s}.comp:hover{transform:translateY(-3px);border-color:#8d5cff}.avatar{width:58px;height:58px;margin:auto auto 8px;border-radius:50%;display:grid;place-items:center;font-size:25px;font-weight:900;background:linear-gradient(145deg,#263e58,#5c3763)}.female .avatar{background:linear-gradient(145deg,#5b2f51,#6a456e)}.comp small{display:block;color:#72d8a0;font-size:9px;letter-spacing:1px;margin-top:3px}.plans{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.plan,.card{background:#131319;border:1px solid #35353e;border-radius:25px;padding:26px}.plan.hot{border-color:#d36580}.price{font-size:40px;font-weight:900;margin:12px 0}.plan ul{line-height:1.9;color:#ccc}.fine{text-align:center;color:#6d6d76;font-size:12px;padding:35px 0 55px}.back{display:inline-block;margin:24px 0;color:#aaa}.profile{display:grid;grid-template-columns:190px 1fr;gap:24px;align-items:center}.bigavatar{width:165px;height:165px;border-radius:50%;display:grid;place-items:center;font-size:72px;font-weight:900;background:linear-gradient(145deg,#263e58,#6a456e);box-shadow:0 0 60px #7c3f8f44}.bubble{background:#29292f;border-radius:22px;padding:17px;margin:12px 0;font-size:18px;line-height:1.45}.you{background:#202026}.row{display:flex;gap:10px;margin-top:16px}.row input{flex:1;min-width:0;background:#09090b;color:#fff;border:1px solid #555;border-radius:18px;padding:16px;font-size:17px}.row button{background:#d36580;border:0;color:#fff;border-radius:18px;padding:0 20px;font-size:17px;font-weight:800}.status,.note{color:#aaa;font-size:13px;margin-top:10px}.chips{display:flex;flex-wrap:wrap;gap:9px}.chip{background:#202026;border:1px solid #45454d;border-radius:999px;padding:10px 13px;font-size:14px;cursor:pointer}.chip.active{background:#d36580;border-color:#d36580}.group{margin-top:18px}.banner{background:#17121a;border:1px solid #57334a;border-radius:18px;padding:15px;margin:16px 0;color:#edc6d1}.account{max-width:620px;margin:45px auto}.field{display:grid;gap:7px;margin:15px 0}.field input{background:#09090b;border:1px solid #444;border-radius:14px;padding:14px;color:#fff;font-size:16px}@media(max-width:850px){.hero{grid-template-columns:1fr}.grid{grid-template-columns:repeat(4,1fr)}.plans{grid-template-columns:1fr}.profile{grid-template-columns:1fr}.links{display:none}}@media(max-width:480px){.grid{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:55px}.section h2{font-size:33px}}'''

def esc(s): return html.escape(str(s), quote=True)
def companion_url(n): return '/companion/'+quote(n.lower())
def cards(names, cls):
    return ''.join(f'<a class="comp {cls}" href="{companion_url(n)}"><div class="avatar">{esc(n[0])}</div><b>{esc(n)}</b><small>LIVE</small></a>' for n in names)

def nav():
    return '<div class="nav"><div class="shell navin"><a class="brand" href="/"><span class="grad">WHAT BOUT US</span></a><div class="links"><a href="/#companions">Companions</a><a href="/#plans">Plans</a><a href="/account">Account</a><a href="/companion/simone">Talk to Simone</a></div></div></div>'

def page(title, body):
    return f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>{CSS}</style></head><body>{nav()}{body}</body></html>'

def home():
    body=f'''<main class="shell"><section class="hero"><div><div class="eyebrow">AI COMPANIONS</div><h1>Someone to talk to.<br><span class="grad">Someone who remembers.</span></h1><p class="lead">Meet 32 distinct AI companions with personality, voice-ready conversation, multiple languages and premium customization.</p><div class="buttons"><a class="btn" href="#companions">Meet the Companions</a><a class="btn alt" href="/companion/simone">Talk to Simone</a></div></div><div class="art"><div><div class="heart">♡</div><h2 style="font-size:42px">What <span class="grad">Bout Us</span></h2><p style="letter-spacing:5px;color:#bbb">AI COMPANIONS</p></div></div></section><section id="companions" class="section"><h2>32 AI Companions</h2><p class="sub">16 men. 16 women. Every profile below opens a live conversation.</p><h3>16 MEN</h3><div class="grid">{cards(MEN,'male')}</div><h3 style="margin-top:28px">16 WOMEN</h3><div class="grid">{cards(WOMEN,'female')}</div></section><section id="plans" class="section"><h2>Choose Your Experience</h2><p class="sub">Pick the plan that fits how you want to connect.</p><div class="plans"><div class="plan"><div>WHAT BOUT US+</div><div class="price">$9.99 <small>/ month</small></div><ul><li>Text conversations</li><li>Multiple companions</li><li>Conversation memory on your device</li><li>Multiple languages</li></ul><a class="btn alt" href="/checkout?plan=plus">Choose Plus</a></div><div class="plan hot"><div>WHAT BOUT US UNLIMITED · MOST POPULAR</div><div class="price">$14.99 <small>/ month</small></div><ul><li>Everything in Plus</li><li>All 32 companions</li><li>Voice-ready conversations</li><li>Premium style customization</li><li>Expanded footwear options</li></ul><a class="btn" href="/checkout?plan=unlimited">Choose Unlimited</a></div></div><p class="note">Renews monthly. Cancel anytime.</p></section><div class="fine">What Bout Us · AI Companions · Adults 21+</div></main>'''
    return page('What Bout Us — AI Companions', body)

def companion_page(name):
    intro = "Hey U, I'm Simone. Tell me what you're thinking." if name=='Simone' else f"Hey, I'm {name}. What's on your mind?"
    premium='''<div class="card" id="customize"><h2>Premium Style</h2><p class="sub">Customize Simone's look. Selections save on this device.</p><div class="group"><h3>Outfit</h3><div class="chips" data-group="outfit"><span class="chip">Casual</span><span class="chip">Business</span><span class="chip">Evening</span><span class="chip">Athletic</span><span class="chip">Streetwear</span><span class="chip">Loungewear</span><span class="chip">Dressy</span><span class="chip">Swimwear</span></div></div><div class="group"><h3>Accessories</h3><div class="chips multi" data-group="accessories"><span class="chip">Sunglasses</span><span class="chip">Watch</span><span class="chip">Bracelet</span><span class="chip">Necklace</span><span class="chip">Chain</span><span class="chip">Hat</span><span class="chip">Earrings</span></div></div><div class="group"><h3>Footwear</h3><div class="chips" data-group="footwear"><span class="chip">Sneakers</span><span class="chip">Dress Shoes</span><span class="chip">Sandals</span><span class="chip">Heels</span><span class="chip">Work Boots</span><span class="chip">Timberland-Style Boots</span><span class="chip">Cowboy Boots</span><span class="chip">Western Boots</span><span class="chip">Hiking Boots</span><span class="chip">Ankle Boots</span><span class="chip">Knee-High Boots</span></div></div><button class="btn" onclick="saveStyle()" style="margin-top:18px">Save Style</button><span id="saved" class="status" style="margin-left:10px"></span></div>''' if name=='Simone' else ''
    voice_note='<span class="banner">Simone voice is enabled.</span>' if name=='Simone' else '<span class="note">Text chat is live. Dedicated voice profiles are being assigned companion-by-companion.</span>'
    body=f'''<main class="shell"><a class="back" href="/">← Back to all companions</a><div class="card"><div class="profile"><div class="bigavatar">{esc(name[0])}</div><div><div class="eyebrow">LIVE COMPANION</div><h1 style="font-size:48px;margin:5px 0">{esc(name)}</h1><p class="lead" style="font-size:17px">{esc(TRAITS.get(name,'warm, supportive and engaging').capitalize())}.</p>{voice_note}</div></div><div class="bubble">{esc(intro)}</div><div id="history"></div><div class="row"><input id="message" placeholder="Talk to {esc(name)}..." autocomplete="off"><button onclick="sendMessage()">Send</button></div><div id="status" class="status">Ready</div></div>{premium}<div class="fine">What Bout Us · Adults 21+</div></main>
<script>const NAME={json.dumps(name)};let currentAudio=null;const H=document.getElementById('history');function escHtml(t){{let d=document.createElement('div');d.textContent=t;return d.innerHTML}}function loadHistory(){{try{{let a=JSON.parse(localStorage.getItem('wbu:'+NAME)||'[]');a.slice(-12).forEach(x=>{{H.innerHTML+='<div class="bubble '+(x.role==='user'?'you':'')+'">'+(x.role==='user'?'You: ':NAME+': ')+escHtml(x.text)+'</div>'}})}}catch(e){{}}}}function saveTurn(role,text){{try{{let k='wbu:'+NAME,a=JSON.parse(localStorage.getItem(k)||'[]');a.push({{role,text}});localStorage.setItem(k,JSON.stringify(a.slice(-20)))}}catch(e){{}}}}async function speak(t){{if(NAME!=='Simone')return;try{{let r=await fetch('/api/speech',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{text:t}})}});if(!r.ok)return;let b=await r.blob(),u=URL.createObjectURL(b);if(currentAudio)currentAudio.pause();currentAudio=new Audio(u);currentAudio.onended=()=>URL.revokeObjectURL(u);await currentAudio.play()}}catch(e){{}}}}async function sendMessage(){{let i=document.getElementById('message'),s=document.getElementById('status'),m=i.value.trim();if(!m)return;i.value='';H.innerHTML+='<div class="bubble you">You: '+escHtml(m)+'</div>';saveTurn('user',m);s.textContent=NAME+' is thinking...';try{{let r=await fetch('/api/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:m,companion:NAME}})}}),d=await r.json();if(!r.ok)throw Error(d.error||'Connection error');H.innerHTML+='<div class="bubble">'+NAME+': '+escHtml(d.reply)+'</div>';saveTurn('assistant',d.reply);s.textContent='Ready';await speak(d.reply)}}catch(e){{s.textContent=e.message}}}}document.getElementById('message').addEventListener('keydown',e=>{{if(e.key==='Enter')sendMessage()}});loadHistory();document.querySelectorAll('.chips').forEach(g=>g.addEventListener('click',e=>{{if(!e.target.classList.contains('chip'))return;if(g.classList.contains('multi'))e.target.classList.toggle('active');else{{g.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));e.target.classList.add('active')}}}}));function saveStyle(){{let o={{}};document.querySelectorAll('.chips').forEach(g=>o[g.dataset.group]=[...g.querySelectorAll('.chip.active')].map(c=>c.textContent));localStorage.setItem('simoneStyle',JSON.stringify(o));let s=document.getElementById('saved');if(s)s.textContent='Saved'}}try{{let o=JSON.parse(localStorage.getItem('simoneStyle')||'{{}}');document.querySelectorAll('.chips').forEach(g=>{{(o[g.dataset.group]||[]).forEach(v=>[...g.querySelectorAll('.chip')].find(c=>c.textContent===v)?.classList.add('active'))}})}}catch(e){{}}</script>'''
    return page(name+' — What Bout Us',body)

def account_page():
    body='''<main class="shell"><div class="account card"><div class="eyebrow">YOUR ACCOUNT</div><h1>What Bout Us</h1><p class="sub">Save your display name and email on this device while account authentication is being connected.</p><div class="field"><label>Display name</label><input id="n"></div><div class="field"><label>Email</label><input id="e" type="email"></div><button class="btn" onclick="save()">Save</button><div id="ok" class="status"></div></div></main><script>let a=JSON.parse(localStorage.getItem('wbuAccount')||'{}');n.value=a.name||'';e.value=a.email||'';function save(){localStorage.setItem('wbuAccount',JSON.stringify({name:n.value,email:e.value}));ok.textContent='Saved on this device.'}</script>'''
    return page('Account — What Bout Us',body)

def checkout_page(plan):
    plan = 'unlimited' if plan=='unlimited' else 'plus'
    label='What Bout Us Unlimited — $14.99/month' if plan=='unlimited' else 'What Bout Us+ — $9.99/month'
    url=SQUARE_UNLIMITED_URL if plan=='unlimited' else SQUARE_PLUS_URL
    if url: return ('redirect',url)
    body=f'''<main class="shell"><div class="account card"><div class="eyebrow">SECURE CHECKOUT</div><h1>{esc(label)}</h1><div class="banner">Square checkout is not connected to this deployment yet.</div><p class="sub">The site is ready to use the Square hosted checkout link as soon as the matching Railway variable is added.</p><a class="btn alt" href="/#plans">Back to plans</a></div></main>'''
    return ('html',page('Checkout — What Bout Us',body))

def chat_reply(companion,message):
    companion = companion if companion in ALL else 'Simone'
    if not OPENAI_API_KEY:
        return "I'm here with you. Tell me a little more about that."
    sys=f'''You are {companion}, an adult AI companion in What Bout Us. Personality: {TRAITS.get(companion,'warm, supportive and engaging')}. Be conversational, warm, concise and natural. Never claim to be human. Users must be 21+. Never sexualize minors or discuss sexual activity involving minors, babies, animals or insects. If someone is in immediate danger or considering self-harm or harming others, encourage immediate local emergency/crisis help and focus on safety.'''
    payload=json.dumps({'model':'gpt-4o-mini','messages':[{'role':'system','content':sys},{'role':'user','content':message}],'temperature':0.85,'max_tokens':220}).encode()
    req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=payload,headers={'Authorization':'Bearer '+OPENAI_API_KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            d=json.loads(r.read().decode())
            return d['choices'][0]['message']['content'].strip()
    except Exception:
        return "I'm here with you. Tell me a little more about that."

def eleven_audio(text):
    if not (ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID): return None
    payload=json.dumps({'text':text[:1200],'model_id':'eleven_multilingual_v2','voice_settings':{'stability':0.5,'similarity_boost':0.8}}).encode()
    url='https://api.elevenlabs.io/v1/text-to-speech/'+quote(ELEVENLABS_VOICE_ID)
    req=urllib.request.Request(url,data=payload,headers={'xi-api-key':ELEVENLABS_API_KEY,'Content-Type':'application/json','Accept':'audio/mpeg'})
    try:
        with urllib.request.urlopen(req,timeout=35) as r: return r.read()
    except Exception: return None

class H(BaseHTTPRequestHandler):
    def send_html(self,s,status=200):
        b=s.encode(); self.send_response(status); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def send_json(self,d,status=200):
        b=json.dumps(d).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u=urlparse(self.path); p=u.path
        if p=='/health': return self.send_json({'ok':True,'companions':32,'squareConnected':bool(SQUARE_PLUS_URL and SQUARE_UNLIMITED_URL),'voice':bool(ELEVENLABS_API_KEY)})
        if p=='/': return self.send_html(home())
        if p=='/simone': self.send_response(302); self.send_header('Location','/companion/simone'); self.end_headers(); return
        if p.startswith('/companion/'):
            slug=unquote(p.split('/companion/',1)[1]).strip().lower(); name=next((n for n in ALL if n.lower()==slug),None)
            return self.send_html(companion_page(name),200) if name else self.send_html(page('Not found','<main class="shell"><div class="card" style="margin-top:40px"><h1>Companion not found</h1><a class="btn" href="/">Back home</a></div></main>'),404)
        if p=='/account': return self.send_html(account_page())
        if p=='/checkout':
            plan=parse_qs(u.query).get('plan',['plus'])[0]; kind,val=checkout_page(plan)
            if kind=='redirect': self.send_response(302); self.send_header('Location',val); self.end_headers(); return
            return self.send_html(val)
        return self.send_html(page('Not found','<main class="shell"><div class="card" style="margin-top:40px"><h1>Page not found</h1><a class="btn" href="/">Back home</a></div></main>'),404)
    def do_POST(self):
        u=urlparse(self.path); n=int(self.headers.get('Content-Length','0') or 0)
        try: d=json.loads(self.rfile.read(n).decode() or '{}')
        except Exception: d={}
        if u.path=='/api/chat':
            m=str(d.get('message','')).strip()[:3000]; c=str(d.get('companion','Simone')).strip()
            if not m: return self.send_json({'error':'Message is required'},400)
            return self.send_json({'reply':chat_reply(c,m)})
        if u.path=='/api/speech':
            t=str(d.get('text','')).strip()
            if not t: return self.send_json({'error':'Text is required'},400)
            a=eleven_audio(t)
            if not a: return self.send_json({'error':'Voice unavailable'},503)
            self.send_response(200); self.send_header('Content-Type','audio/mpeg'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(a))); self.end_headers(); self.wfile.write(a); return
        return self.send_json({'error':'Not found'},404)
    def log_message(self,fmt,*args): pass

if __name__=='__main__':
    ThreadingHTTPServer(('0.0.0.0',PORT),H).serve_forever()
