import json, os, time, urllib.request, urllib.error
from urllib.parse import urlparse, parse_qs, quote
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import app as base

SB=os.environ.get('SUPABASE_URL','https://kvoqreikxoiygrthanqx.supabase.co').rstrip('/')
KEY=os.environ.get('SUPABASE_ANON_KEY','').strip()
FREE={'Simone','Chloe'}
WARN="I'm sorry, but I have to go now. We can continue talking with a paid subscription. I'd really like to continue our conversation. I've really enjoyed talking with you."
HEIGHTS={'Alex':"5'10\"",'Damien':"6'4\"",'Logan':"6'0\"",'Jay':"5'11\"",'Kai':"6'2\"",'Mason':"6'5\"",'Ethan':"6'3\"",'Luca':"6'0\"",'Ace':"6'6\"",'Noah':"5'10\"",'Jack':"6'1\"",'Benji':"5'11\"",'Leo':"6'7\"",'Carter':"6'8\"",'Tyler':"6'2\"",'Simone':"6'1\"",'Lily':"5'0\"",'Aria':"5'4\"",'Mika':"5'2\"",'Zoey':"5'7\"",'Nova':"5'9\"",'Sophia':"5'6\"",'Isabella':"5'5\"",'Chloe':"5'8\"",'Ember':"5'10\"",'Hana':"5'3\"",'Riley':"6'0\"",'Vivien':"5'11\"",'Bella':"5'1\"",'Sahara':"5'7\"",'Skye':"6'1\"",'Nia':"5'6\""}

def sb(path,method='GET',token=None,body=None,prefer=None):
    if not KEY: raise RuntimeError('SUPABASE_ANON_KEY missing')
    h={'apikey':KEY,'Authorization':'Bearer '+(token or KEY),'Content-Type':'application/json'}
    if prefer:h['Prefer']=prefer
    req=urllib.request.Request(SB+path,data=None if body is None else json.dumps(body).encode(),headers=h,method=method)
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            raw=r.read();return r.status,(json.loads(raw.decode()) if raw else None)
    except urllib.error.HTTPError as e:
        raw=e.read()
        try:o=json.loads(raw.decode()) if raw else {}
        except:o={'error':raw.decode(errors='ignore')}
        return e.code,o

def tok(h):
    a=h.get('Authorization','');return a[7:].strip() if a.lower().startswith('bearer ') else ''
def user(t):
    if not t:return None
    s,o=sb('/auth/v1/user',token=t);return o if s==200 and isinstance(o,dict) and o.get('id') else None
def q(v):return quote(str(v),safe='')
def get(table,t,query):
    s,o=sb('/rest/v1/'+table+'?'+query,token=t);return o if s==200 and isinstance(o,list) else []
def comp(t,n):
    a=get('companions',t,'slug=eq.'+q(n.lower())+'&select=id,slug,name&limit=1');return a[0] if a else None
def paid(t,uid):
    a=get('subscriptions',t,'user_id=eq.'+q(uid)+'&select=plan,status&limit=1')
    return bool(a and a[0].get('status')=='active' and a[0].get('plan') in ('plus','unlimited'))
def trial(t,uid,cid,start=False):
    a=get('companion_trials',t,'user_id=eq.'+q(uid)+'&companion_id=eq.'+q(cid)+'&select=started_at,expires_at,consumed&limit=1');now=time.time()
    if not a:
        if not start:return False,120,False
        body={'user_id':uid,'companion_id':cid,'started_at':datetime.now(timezone.utc).isoformat(),'expires_at':datetime.fromtimestamp(now+120,timezone.utc).isoformat(),'consumed':False}
        s,_=sb('/rest/v1/companion_trials',method='POST',token=t,body=body,prefer='return=minimal');return True,(120 if s in (200,201) else 0),s not in (200,201)
    r=a[0]
    if r.get('consumed'):return True,0,True
    if not r.get('started_at'):
        if not start:return False,120,False
        body={'started_at':datetime.now(timezone.utc).isoformat(),'expires_at':datetime.fromtimestamp(now+120,timezone.utc).isoformat(),'updated_at':datetime.now(timezone.utc).isoformat()}
        sb('/rest/v1/companion_trials?user_id=eq.'+q(uid)+'&companion_id=eq.'+q(cid),method='PATCH',token=t,body=body);return True,120,False
    try:exp=datetime.fromisoformat((r.get('expires_at') or '').replace('Z','+00:00')).timestamp()
    except:exp=now
    rem=max(0,int(exp-now))
    if rem<=0:
        sb('/rest/v1/companion_trials?user_id=eq.'+q(uid)+'&companion_id=eq.'+q(cid),method='PATCH',token=t,body={'consumed':True,'updated_at':datetime.now(timezone.utc).isoformat()});return True,0,True
    return True,rem,False
def conv(t,uid,cid,create=False):
    a=get('conversations',t,'user_id=eq.'+q(uid)+'&companion_id=eq.'+q(cid)+'&select=id&order=updated_at.desc&limit=1')
    if a:return a[0]['id']
    if not create:return None
    s,o=sb('/rest/v1/conversations',method='POST',token=t,body={'user_id':uid,'companion_id':cid,'title':'Conversation'},prefer='return=representation')
    return o[0]['id'] if s in (200,201) and isinstance(o,list) and o else None
def history(t,uid,cid):
    c=conv(t,uid,cid)
    if not c:return []
    a=get('messages',t,'conversation_id=eq.'+q(c)+'&user_id=eq.'+q(uid)+'&select=role,content,created_at&order=created_at.desc&limit=30');return list(reversed(a))
def mems(t,uid,cid):
    return [x['memory'] for x in get('memories',t,'user_id=eq.'+q(uid)+'&companion_id=eq.'+q(cid)+'&select=memory&order=updated_at.desc&limit=10') if x.get('memory')]
def save(t,uid,c,role,text):
    sb('/rest/v1/messages',method='POST',token=t,body={'conversation_id':c,'user_id':uid,'role':role,'content':text},prefer='return=minimal')
    sb('/rest/v1/conversations?id=eq.'+q(c),method='PATCH',token=t,body={'updated_at':datetime.now(timezone.utc).isoformat()},prefer='return=minimal')
def remember(t,uid,cid,m):
    low=m.lower();cues=('my name is','i like ','i love ','my favorite','i work ','i live ','i have ','remember ','my birthday','my son','my daughter','my wife','my husband','my family')
    if len(m)>=12 and any(x in low for x in cues): sb('/rest/v1/memories',method='POST',token=t,body={'user_id':uid,'companion_id':cid,'memory':m},prefer='return=minimal')
def reply(name,msg,hist,mem):
    if not base.OPENAI_API_KEY:return "I'm here with you. Tell me a little more about that."
    sys=f"You are {name}, an adult AI companion in What Bout Us™. Be warm, concise and natural. Never claim to be human. Users must be 21+. Use saved memories naturally. Memories: {'; '.join(mem) if mem else 'none'}"
    ms=[{'role':'system','content':sys}]+[{'role':x['role'],'content':x['content']} for x in hist[-18:] if x.get('role') in ('user','assistant')]+[{'role':'user','content':msg}]
    data=json.dumps({'model':'gpt-4o-mini','messages':ms,'max_tokens':220}).encode()
    req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=data,headers={'Authorization':'Bearer '+base.OPENAI_API_KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:return json.loads(r.read().decode())['choices'][0]['message']['content'].strip()
    except:return "I'm here with you. Tell me a little more about that."

def account_page():
    js='''<script>const A="wbu_access_token";function m(x){document.getElementById("msg").textContent=x}async function go(k){let email=document.getElementById("email").value.trim(),password=document.getElementById("password").value,name=document.getElementById("name").value.trim();let r=await fetch("/api/auth/"+k,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,password,display_name:name})}),d=await r.json();if(!r.ok)return m(d.error||"Unable to continue.");if(d.access_token){localStorage.setItem(A,d.access_token);m("Signed in. You can return to your companion.")}else m("Account created. Check your email if confirmation is required, then sign in.")}function out(){localStorage.removeItem(A);m("Signed out.")}</script>'''
    return base.page('Account — What Bout Us™','<main class="shell"><div class="account card"><h1>Your Account</h1><p class="sub">A free account is optional for the Simone or Chloe demo. Sign in to save conversations and enable memory when available with your subscription.</p><div class="field"><label>Display name</label><input id="name"></div><div class="field"><label>Email</label><input id="email" type="email"></div><div class="field"><label>Password</label><input id="password" type="password"></div><button class="btn" onclick="go(\'signup\')">Create Free Account</button> <button class="btn alt" onclick="go(\'login\')">Sign In</button> <button class="btn alt" onclick="out()">Sign Out</button><div id="msg" class="status"></div></div>'+base.footer()+'</main>'+js)

def companion_page(n):
    intro="Hey U, I'm Simone. Tell me what you're thinking." if n=='Simone' else f"Hey, I'm {n}. What's on your mind?"
    js=f'''<script>
const N={json.dumps(n)},W={json.dumps(WARN)},A="wbu_access_token",G="wbu_guest_trial_"+N,H=document.getElementById("history"),I=document.getElementById("message"),B=document.getElementById("send"),S=document.getElementById("status"),L=document.getElementById("lock"),T=document.getElementById("timer");let paid=false,left=null,clock=null,warned=false,started=false;
function e(x){{let d=document.createElement("div");d.textContent=x;return d.innerHTML}}function h(){{let t=localStorage.getItem(A);return t?{{Authorization:"Bearer "+t}}:{{}}}}function bub(r,x){{H.innerHTML+='<div class="bubble '+(r==="user"?"you":"")+'">'+(r==="user"?"You: ":N+": ")+e(x)+"</div>"}}function lock(x){{I.disabled=B.disabled=true;L.style.display="block";L.innerHTML=e(x)+'<br><br><a class="btn" href="/checkout?plan=plus">Continue with a Paid Subscription</a>';S.textContent="Conversation locked"}}function on(){{I.disabled=B.disabled=false;L.style.display="none";S.textContent="Ready"}}async function say(x){{try{{let r=await fetch("/api/speech",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{text:x}})}});if(r.ok)return new Audio(URL.createObjectURL(await r.blob())).play()}}catch(e){{}}try{{speechSynthesis.speak(new SpeechSynthesisUtterance(x))}}catch(e){{}}}}function timer(s){{left=Math.max(0,Math.floor(s));started=true;if(clock)clearInterval(clock);draw();clock=setInterval(()=>{{left--;draw();if(left===10&&!warned){{warned=true;bub("assistant",W);say(W)}}if(left<=0){{clearInterval(clock);lock("Your free 2-minute conversation has ended. Subscribe to continue talking with "+N+".")}}}},1000)}}function draw(){{if(paid)return T.textContent="Paid member · conversation memory on";if(!started)return T.textContent=(N==="Simone"||N==="Chloe")?"Free demo starts with your first message.":"";T.textContent="Free time remaining: "+Math.floor(left/60)+":"+String(Math.max(0,left%60)).padStart(2,"0")}}function guestState(){{let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}}async function load(){{let token=localStorage.getItem(A);if(!token){{if(N==="Simone"||N==="Chloe"){{let r=guestState();if(r<=0)return lock("Your free 2-minute conversation has ended. Subscribe to continue where you left off.");on();if(r<120)timer(r);else draw();return}}return lock("This companion requires a paid subscription.")}}let r=await fetch("/api/session?companion="+encodeURIComponent(N),{{headers:h()}}),d=await r.json();if(r.status===401){{localStorage.removeItem(A);if(N==="Simone"||N==="Chloe"){{on();draw();return}}return lock("Your sign-in expired. Please sign in again.")}}paid=!!d.paid;(d.history||[]).forEach(x=>bub(x.role,x.content));if(paid){{on();return draw()}}if(d.locked)return lock(d.message||"Paid subscription required.");on();if(d.trial_started)timer(d.remaining);else draw()}}async function send(){{let m=I.value.trim();if(!m||I.disabled)return;let token=localStorage.getItem(A);let guest=!token&&(N==="Simone"||N==="Chloe");if(guest){{let r=guestState();if(r<=0)return lock("Your free 2-minute conversation has ended. Subscribe to continue where you left off.");if(!localStorage.getItem(G))localStorage.setItem(G,String(Date.now()));if(!started)timer(r)}}I.value="";bub("user",m);S.textContent=N+" is thinking...";B.disabled=true;let endpoint=guest?"/api/guest-chat":"/api/chat";let r=await fetch(endpoint,{{method:"POST",headers:{{"Content-Type":"application/json",...h()}},body:JSON.stringify({{companion:N,message:m}})}}),d=await r.json();if(!r.ok){{if(d.remaining===0)lock(d.error);else S.textContent=d.error||"Unable to continue.";if(!I.disabled)B.disabled=false;return}}bub("assistant",d.reply);paid=!!d.paid;if(!guest&&!paid&&d.remaining!==undefined&&!started)timer(d.remaining);if(N==="Simone")say(d.reply);S.textContent="Ready";if(!I.disabled)B.disabled=false}}I.addEventListener("keydown",x=>{{if(x.key==="Enter")send()}});load();
</script>'''
    extra=' · 2-minute free demo' if n in FREE else ' · paid subscription required'
    b=f'<main class="shell"><a class="back" href="/">← Back to all companions</a><div class="card"><div class="profile"><div class="bigavatar"><img src="{base.portrait(n)}" alt="{base.esc(n)}"></div><div><div class="grad">LIVE COMPANION</div><h1>{base.esc(n)}</h1><p class="lead" style="font-size:17px">{base.esc(base.TRAITS.get(n,"warm, supportive and engaging").capitalize())}.</p><span class="banner">Height {HEIGHTS[n]}{extra}</span></div></div><div class="bubble">{base.esc(intro)}</div><div id="history"></div><div id="timer" class="status"></div><div class="row"><input id="message" placeholder="Talk to {base.esc(n)}..." disabled><button id="send" class="btn" onclick="send()" disabled>Send</button></div><div id="status" class="status">Checking your account...</div><div id="lock" class="banner" style="display:none;margin-top:14px"></div></div>{base.footer()}</main>{js}'
    return base.page(n+' — What Bout Us™',b)

base.account_page=account_page
base.companion_page=companion_page

class H(base.H):
    def body_json(self):
        n=int(self.headers.get('Content-Length','0') or 0)
        try:return json.loads(self.rfile.read(n).decode() or '{}')
        except:return {}
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=='/api/session':
            t=tok(self.headers);u1=user(t)
            if not u1:return self.sj({'error':'Sign in required'},401)
            n=parse_qs(u.query).get('companion',['Simone'])[0]
            if n not in base.ALL:return self.sj({'error':'Unknown companion'},404)
            c=comp(t,n)
            if not c:return self.sj({'error':'Companion unavailable'},404)
            ph=paid(t,u1['id']);hi=history(t,u1['id'],c['id'])
            if ph:return self.sj({'paid':True,'history':hi,'locked':False})
            if n not in FREE:return self.sj({'paid':False,'history':hi,'locked':True,'message':'This companion requires a paid subscription.'})
            st,rem,done=trial(t,u1['id'],c['id'],False)
            return self.sj({'paid':False,'history':hi,'locked':done,'message':'Your free 2-minute conversation has ended. Subscribe to continue where you left off.' if done else '', 'trial_started':st,'remaining':rem})
        return super().do_GET()
    def do_POST(self):
        p=urlparse(self.path).path
        if p in ('/api/auth/signup','/api/auth/login'):
            d=self.body_json();email=str(d.get('email','')).strip();password=str(d.get('password',''));name=str(d.get('display_name','')).strip()
            if not email or len(password)<6:return self.sj({'error':'Use a valid email and a password of at least 6 characters.'},400)
            ep='/auth/v1/signup' if p.endswith('signup') else '/auth/v1/token?grant_type=password';body={'email':email,'password':password}
            if p.endswith('signup'):body['data']={'display_name':name}
            s,o=sb(ep,method='POST',body=body)
            if s not in (200,201):return self.sj({'error':(o.get('msg') or o.get('message') or 'Authentication failed.') if isinstance(o,dict) else 'Authentication failed.'},s)
            return self.sj(o)
        if p=='/api/guest-chat':
            d=self.body_json();n=str(d.get('companion','Simone'));m=str(d.get('message','')).strip()[:3000]
            if n not in FREE or not m:return self.sj({'error':'Invalid request'},400)
            rp=reply(n,m,[],[])
            return self.sj({'reply':rp,'paid':False,'remaining':120})
        if p=='/api/chat':
            d=self.body_json();t=tok(self.headers);u=user(t)
            if not u:return self.sj({'error':'Please sign in to continue.'},401)
            n=str(d.get('companion','Simone'));m=str(d.get('message','')).strip()[:3000]
            c=comp(t,n) if n in base.ALL else None
            if not c or not m:return self.sj({'error':'Invalid request'},400)
            ph=paid(t,u['id']);rem=None
            if not ph:
                if n not in FREE:return self.sj({'error':'A paid subscription is required for this companion.'},402)
                _,rem,done=trial(t,u['id'],c['id'],True)
                if done or rem<=0:return self.sj({'error':'Your free 2-minute conversation has ended. Subscribe to continue where you left off.','remaining':0},402)
            cv=conv(t,u['id'],c['id'],True)
            if not cv:return self.sj({'error':'Unable to save conversation.'},503)
            hi=history(t,u['id'],c['id']);rp=reply(n,m,hi,mems(t,u['id'],c['id']));save(t,u['id'],cv,'user',m);save(t,u['id'],cv,'assistant',rp);remember(t,u['id'],c['id'],m)
            if not ph:_,rem,_=trial(t,u['id'],c['id'])
            return self.sj({'reply':rp,'paid':ph,'remaining':rem})
        return super().do_POST()

if __name__=='__main__':
    ThreadingHTTPServer(('0.0.0.0',base.PORT),H).serve_forever()
