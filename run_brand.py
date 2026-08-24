import json
import os
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path
import run_topup

base = run_topup.base
wallet = run_topup.run_wallet
pricing = wallet.run_pricing
app_v2 = wallet.app_v2
LOGO_PATH = '/brand-logo.svg'
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
LOGO_FILE = Path(__file__).resolve().parent / 'static' / 'wbu-logo-v13.svg'
OWNER_TEST_EMAIL = os.environ.get('OWNER_TEST_EMAIL', 'centralinvestigations45@gmail.com').strip().lower()
_original_page = base.page
_original_home = base.home

# Secure owner/test entitlement. The email comparison is only trusted after Supabase
# validates the bearer token and returns the authenticated user's email.
_original_active_plan = wallet.active_plan
_original_paid = app_v2.paid

def _owner_user(token):
    try:
        u = app_v2.user(token)
        return u if u and str(u.get('email') or '').strip().lower() == OWNER_TEST_EMAIL else None
    except Exception:
        return None

def owner_active_plan(token, uid):
    if _owner_user(token):
        return 'unlimited-yearly', wallet.PLAN_WALLETS['unlimited-yearly']
    return _original_active_plan(token, uid)

def owner_paid(token, uid):
    if _owner_user(token):
        return True
    return _original_paid(token, uid)

wallet.active_plan = owner_active_plan
app_v2.paid = owner_paid

# Collection 01: original/unbranded virtual fashion only. No third-party brand marks or logos.
COLLECTION_CLOTHING=[('Classic Hoodie','classic-hoodie',False,475),('Fitted T-Shirt','fitted-tshirt',False,225),('Denim Jacket','denim-jacket',False,725),('Dark Denim Jeans','dark-denim-jeans',False,500),('Business Blazer','business-blazer',False,850),('Cocktail Dress','cocktail-dress',False,900),('Date Night Dress','date-night-dress',False,1100),('Athletic Set','athletic-set',False,650),('Satin Lounge Set','satin-lounge-set',False,600),('Premium Evening Gown','premium-evening-gown',True,9000),('Premium Tailored Suit','premium-tailored-suit',True,11000),('Premium Leather Outfit','premium-leather-outfit',True,12500),('Premium Silk Lingerie Set','premium-silk-lingerie',True,9500),('Premium Men’s Lounge Set','premium-mens-lounge',True,6500)]
COLLECTION_ACCESSORIES=[('Fashion Earrings','fashion-earrings',False,450),('Hoop Earrings','hoop-earrings',False,425),('Classic Watch','classic-watch',False,950),('Leather Strap Watch','leather-watch',False,1100),('Pendant Necklace','pendant-necklace',False,700),('Cuff Bracelet','cuff-bracelet',False,550),('Fashion Ring','fashion-ring',False,500),('Baseball Cap','baseball-cap',False,300),('Beanie','beanie',False,275),('Handbag','handbag',False,850),('Premium Luxury Handbag','premium-luxury-handbag',True,9500),('Premium Diamond Bracelet','premium-diamond-bracelet',True,16000),('Premium Diamond Necklace','premium-diamond-necklace',True,22000),('Premium Luxury Watch','premium-luxury-watch',True,20000)]
COLLECTION_SHOES=[('High-Top Sneakers','high-top-sneakers',False,750),('Running Sneakers','running-sneakers',False,700),('Classic Heels','classic-heels',False,850),('Ankle Boots','ankle-boots',False,900),('Work Boots','work-boots',False,950),('Loafers','loafers',False,800),('Premium Designer Heels','premium-designer-heels',True,6500),('Premium Work Boots','premium-work-boots',True,7000)]
for label,key,premium,price in COLLECTION_CLOTHING:
    if key not in wallet.ITEMS: pricing.CLOTHING.append((label,key,premium)); wallet.ITEMS[key]=(label,'clothing',price,premium)
for label,key,premium,price in COLLECTION_ACCESSORIES:
    if key not in wallet.ITEMS: pricing.ACCESSORIES.append((label,key,premium)); wallet.ITEMS[key]=(label,'accessories',price,premium)
for label,key,premium,price in COLLECTION_SHOES:
    if key not in wallet.ITEMS: pricing.SHOES.append((label,key,premium)); wallet.ITEMS[key]=(label,'shoes',price,premium)

# Lightweight original product illustrations shown on every live catalog card.
def product_art(label,key,category):
    icon = '👕' if category=='clothing' else ('👟' if category=='shoes' else '⌚')
    lk=key.lower()
    if any(x in lk for x in ('dress','gown','lingerie')): icon='👗'
    elif any(x in lk for x in ('heel','boot','loafer','sneaker')): icon='👢' if 'boot' in lk else ('👠' if 'heel' in lk else '👟')
    elif any(x in lk for x in ('earring','necklace','bracelet','ring')): icon='💎'
    elif 'handbag' in lk: icon='👜'
    elif any(x in lk for x in ('cap','beanie')): icon='🧢'
    return f'''<div class="product-art" aria-label="{base.esc(label)} product image"><div class="product-icon">{icon}</div><div class="product-name">{base.esc(label)}</div><div class="product-note">ORIGINAL · UNBRANDED</div></div>'''

_original_priced_cards=wallet.priced_cards
def visual_priced_cards(items,category):
    html=_original_priced_cards(items,category)
    for label,key,premium in items:
        needle='<h3 style="margin:8px 0 4px">'+base.esc(label)+'</h3>'
        html=html.replace(needle,product_art(label,key,category)+needle,1)
    return html
wallet.priced_cards=visual_priced_cards


def account_page_v2():
    body='''<main class="shell"><div class="card" style="max-width:720px;margin:20px auto;padding:24px"><div class="grad">WHAT BOUT US™ ACCOUNT</div><h1>Create or Sign In to Your Account</h1><p class="sub">Your email address is your username. A phone number is required for account recovery. Marketing emails are optional and require your consent.</p>
    <div class="field"><label>Display name</label><input id="name" autocomplete="name"></div>
    <div class="field"><label>Email address / username</label><input id="email" type="email" autocomplete="email"></div>
    <div class="field"><label>Mobile phone number</label><input id="phone" type="tel" autocomplete="tel" placeholder="(555) 555-5555"></div>
    <div class="field"><label>Password</label><input id="password" type="password" autocomplete="new-password" minlength="8" placeholder="At least 8 characters"></div>
    <label style="display:flex;gap:10px;align-items:flex-start;margin:14px 0"><input id="marketing" type="checkbox" style="margin-top:4px"><span class="sub">Send me What Bout Us™ news, discounts and special offers. I can unsubscribe at any time.</span></label>
    <div style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn" onclick="signup()">Create Free Account</button><button class="btn alt" onclick="login()">Sign In</button><button class="btn alt" onclick="logout()">Sign Out</button></div>
    <div id="msg" class="status" style="margin-top:14px"></div></div>
    <div class="card" style="max-width:720px;margin:18px auto;padding:24px"><h2>Account Recovery</h2><p class="sub">Forgot your password? Enter the email used for your account and we will send a secure reset link.</p><div class="field"><label>Account email</label><input id="recover-email" type="email"></div><button class="btn alt" onclick="recoverPassword()">Can't remember my password</button><hr style="border:0;border-top:1px solid #30303a;margin:22px 0"><p class="sub">Forgot which email you used? Your verified mobile number is collected during signup so SMS recovery can be enabled. SMS delivery requires the site's SMS provider to be connected before phone-based recovery can send messages.</p><div class="field"><label>Mobile phone number</label><input id="recover-phone" type="tel"></div><button class="btn alt" onclick="forgotEmail()">Can't remember my email</button><div id="recovery-msg" class="status" style="margin-top:12px"></div></div>'''+base.footer()+'''</main>
<script>
const A='wbu_access_token';
function val(id){return document.getElementById(id).value.trim()}
function msg(x){document.getElementById('msg').textContent=x}
function rmsg(x){document.getElementById('recovery-msg').textContent=x}
async function api(path,body){let r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),d={};try{d=await r.json()}catch(e){}return [r,d]}
async function signup(){let email=val('email'),phone=val('phone'),password=document.getElementById('password').value,name=val('name'),marketing=document.getElementById('marketing').checked;if(!email||!phone||!password)return msg('Email, mobile phone and password are required.');if(password.length<8)return msg('Please use a password with at least 8 characters.');let [r,d]=await api('/api/auth/signup-v2',{email,phone,password,display_name:name,marketing_opt_in:marketing});if(!r.ok)return msg(d.error||'Unable to create account.');if(d.access_token){localStorage.setItem(A,d.access_token);msg(d.owner_test?'Owner test account signed in — $400,000 virtual wallet enabled.':'Account created and signed in.');}else msg('Account created. Check your email to confirm your address, then sign in.');}
async function login(){let email=val('email'),password=document.getElementById('password').value;if(!email||!password)return msg('Enter your email and password.');let [r,d]=await api('/api/auth/login-v2',{email,password});if(!r.ok)return msg(d.error||'Unable to sign in.');localStorage.setItem(A,d.access_token);msg(d.owner_test?'Owner test account signed in — $400,000 virtual wallet enabled with no Square charge.':'Signed in successfully.');}
function logout(){localStorage.removeItem(A);msg('Signed out.');}
async function recoverPassword(){let email=val('recover-email');if(!email)return rmsg('Enter your account email.');let [r,d]=await api('/api/auth/recover-v2',{email});rmsg(r.ok?'If an account exists for that email, a secure reset message has been sent.':(d.error||'Unable to start password recovery.'));}
async function forgotEmail(){let phone=val('recover-phone');if(!phone)return rmsg('Enter the mobile number used on your account.');let [r,d]=await api('/api/auth/forgot-email-v2',{phone});rmsg(d.message||d.error||'Unable to start phone recovery.');}
</script>'''
    return base.page('Account — What Bout Us™',body)


def branded_nav():
    return '<div class="nav"><div class="shell navin"><a class="brand" href="/"><img src="'+LOGO_PATH+'?v=17" alt="What Bout Us™ AI Companions" style="width:150px;height:58px;object-fit:contain;display:block"></a><div class="links"><a href="/#companions">Companions</a><a href="/clothing">Clothing</a><a href="/accessories">Accessories</a><a href="/shoes">Shoes</a><a href="/account">Account</a></div></div></div>'

def branded_footer():
    return '<div class="fine"><img src="'+LOGO_PATH+'?v=17" alt="What Bout Us™ AI Companions" style="display:block;width:240px;max-width:70vw;height:auto;margin:0 auto 14px">© 2026 What Bout Us<span class="tm">™</span>. All Rights Reserved. · Adults 21+</div>'

def branded_page(title,body):
    html=_original_page(title,body); image=PUBLIC_URL+LOGO_PATH+'?v=17'
    meta='<meta name="description" content="What Bout Us™ — AI companions with conversation, voice, memory and personalized experiences."><meta property="og:type" content="website"><meta property="og:site_name" content="What Bout Us™"><meta property="og:title" content="What Bout Us™ — AI Companions"><meta property="og:description" content="Someone to talk to. Someone who remembers."><meta property="og:url" content="'+PUBLIC_URL+'/"><meta property="og:image" content="'+image+'"><link rel="icon" type="image/svg+xml" href="'+LOGO_PATH+'?v=17"><style>.product-art{height:150px;border-radius:14px;background:linear-gradient(145deg,#11131b,#22152b);border:1px solid #353847;display:flex;flex-direction:column;align-items:center;justify-content:center;margin:10px 0 12px;overflow:hidden}.product-icon{font-size:58px;filter:drop-shadow(0 8px 14px rgba(0,0,0,.35))}.product-name{font-size:12px;font-weight:900;margin-top:8px;text-align:center;padding:0 8px}.product-note{font-size:9px;letter-spacing:1.2px;color:#9da3b3;margin-top:5px}@media(max-width:600px){.nav .shell{padding-top:6px!important;padding-bottom:6px!important}.nav .brand img{width:132px!important;height:50px!important}.product-art{height:135px}.product-icon{font-size:52px}main.shell>div:first-child{margin-top:8px!important;margin-bottom:2px!important;padding-left:8px!important;padding-right:8px!important}}</style>'
    return html.replace('</head>',meta+'</head>',1)

def branded_home():
    html=_original_home(); hero='<div style="max-width:980px;margin:12px auto 2px;padding:0 14px;text-align:center"><img src="'+LOGO_PATH+'?v=17" alt="What Bout Us™ AI Companions" style="width:min(650px,92vw);height:auto;display:block;margin:auto"></div>'
    collection='''<section style="max-width:980px;margin:22px auto;padding:0 18px"><div class="card" style="padding:22px"><div class="grad">WHAT BOUT US™ COLLECTION 01</div><h2>Clothing, Shoes &amp; Accessories</h2><p class="sub">Original, unbranded virtual fashion for your companion — no outside logos. Shop standard styles or premium looks using your virtual style wallet.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="/clothing">Shop Clothing</a><a class="btn alt" href="/shoes">Shop Shoes</a><a class="btn alt" href="/accessories">Shop Accessories</a></div></div></section>'''
    marker='<main class="shell">'
    return html.replace(marker,marker+hero+collection,1) if marker in html else html

base.nav=branded_nav; base.footer=branded_footer; base.page=branded_page; base.home=branded_home

class BrandedHandler(run_topup.TopupHandler):
    def _json(self,status,obj):
        data=json.dumps(obj).encode('utf-8'); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def _body(self):
        try:
            n=int(self.headers.get('Content-Length','0') or 0); return json.loads(self.rfile.read(n).decode('utf-8') or '{}') if n else {}
        except Exception: return {}
    def do_POST(self):
        path=urlparse(self.path).path
        if path in ('/api/auth/signup-v2','/api/auth/login-v2','/api/auth/recover-v2','/api/auth/forgot-email-v2'):
            b=self._body()
            if path=='/api/auth/signup-v2':
                email=str(b.get('email') or '').strip().lower(); phone=str(b.get('phone') or '').strip(); password=str(b.get('password') or ''); name=str(b.get('display_name') or '').strip(); marketing=bool(b.get('marketing_opt_in'))
                if not email or '@' not in email or not phone or len(password)<8: return self._json(400,{'error':'Valid email, mobile phone and a password of at least 8 characters are required.'})
                s,o=app_v2.sb('/auth/v1/signup',method='POST',body={'email':email,'password':password,'data':{'display_name':name,'phone_number':phone,'marketing_opt_in':marketing}})
                if s not in (200,201): return self._json(s if s>=400 else 400,{'error':(o or {}).get('msg') or (o or {}).get('message') or 'Unable to create account.'})
                out=o if isinstance(o,dict) else {}; out['owner_test']=email==OWNER_TEST_EMAIL; return self._json(200,out)
            if path=='/api/auth/login-v2':
                email=str(b.get('email') or '').strip().lower(); password=str(b.get('password') or '')
                s,o=app_v2.sb('/auth/v1/token?grant_type=password',method='POST',body={'email':email,'password':password})
                if s!=200: return self._json(s if s>=400 else 401,{'error':(o or {}).get('error_description') or (o or {}).get('msg') or 'Invalid email or password.'})
                out=o if isinstance(o,dict) else {}; out['owner_test']=email==OWNER_TEST_EMAIL; return self._json(200,out)
            if path=='/api/auth/recover-v2':
                email=str(b.get('email') or '').strip().lower()
                if not email: return self._json(400,{'error':'Email is required.'})
                s,o=app_v2.sb('/auth/v1/recover',method='POST',body={'email':email})
                return self._json(200,{'ok':True}) if s in (200,201) else self._json(s if s>=400 else 400,{'error':'Unable to start password recovery.'})
            # Phone is collected and stored in authenticated user metadata. Sending SMS recovery
            # requires a configured SMS provider; never reveal an account email directly from a phone number.
            phone=str(b.get('phone') or '').strip()
            if not phone: return self._json(400,{'error':'Mobile phone number is required.'})
            return self._json(200,{'message':'Your phone number is used for recovery. SMS delivery must be connected before a recovery text can be sent; your account email will never be displayed publicly.'})
        return super().do_POST()
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/account': return self.sh(account_page_v2())
        if path in (LOGO_PATH,'/brand-logo','/brand-logo.jpg','/brand-logo.png','/favicon.ico'):
            try:
                data=LOGO_FILE.read_bytes()
                if b'<svg' not in data[:500]: raise ValueError('logo is not valid SVG')
            except Exception as exc:
                print('LOGO_ERROR',repr(exc),flush=True); self.send_error(500,'Logo asset unavailable'); return
            self.send_response(200); self.send_header('Content-Type','image/svg+xml; charset=utf-8'); self.send_header('Cache-Control','no-store, max-age=0'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        return super().do_GET()

if __name__=='__main__': ThreadingHTTPServer(('0.0.0.0',base.PORT),BrandedHandler).serve_forever()
