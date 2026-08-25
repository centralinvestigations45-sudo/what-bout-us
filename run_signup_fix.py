import json
import os
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse, quote
import run_hotfix as hot

base = hot.base
app_v2 = hot.app_v2
PUBLIC_URL = 'https://what-bout-us-app-production.up.railway.app'
OWNER_TEST_EMAIL = os.environ.get('OWNER_TEST_EMAIL', 'centralinvestigations45@gmail.com').strip().lower()
POLICY_VERSION = '2026-08-25-v2'


def account_page_fixed():
    body = '''<main class="shell"><div class="card" style="max-width:760px;margin:20px auto;padding:24px"><div class="grad">WHAT BOUT US™ ACCOUNT</div><h1>Create or Sign In to Your Account</h1><p class="sub">Your email address is your username. A phone number is required for account recovery. Marketing emails are optional.</p>
    <div class="field"><label>Display name</label><input id="name" autocomplete="name"></div>
    <div class="field"><label>Email address / username</label><input id="email" type="email" autocomplete="email"></div>
    <div class="field"><label>Mobile phone number</label><input id="phone" type="tel" autocomplete="tel" placeholder="(555) 555-5555"></div>
    <div class="field"><label>Password</label><input id="password" type="password" autocomplete="new-password" minlength="8" placeholder="At least 8 characters"></div>
    <div class="card" style="margin:16px 0;padding:16px;border:1px solid #56505c"><label style="display:flex;gap:10px;align-items:flex-start;cursor:pointer"><input id="policy_accept" type="checkbox" style="width:21px;height:21px;margin-top:3px;flex:0 0 auto"><span><strong>I have read and agree to the What Bout Us™ Subscription & Virtual Currency Policy.</strong><br><span class="sub">I understand subscription refund requests must be made within 14 days of the initial subscription purchase. I understand What Bout Us™ virtual currency is digital in-app value only, has no cash value, cannot be transferred or redeemed for cash, and is not money held in a bank account. Virtual currency purchases are final and non-refundable except where required by law. Each issuance expires 31 days after it is issued, and unused virtual currency does not carry over.</span></span></label></div>
    <label style="display:flex;gap:10px;align-items:flex-start;margin:14px 0"><input id="marketing" type="checkbox" style="margin-top:4px"><span class="sub">Send me What Bout Us™ news, discounts and special offers. I can unsubscribe at any time.</span></label>
    <div style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn" onclick="signup()">Create Free Account</button><button class="btn alt" onclick="login()">Sign In</button><button class="btn alt" onclick="logout()">Sign Out</button></div>
    <div id="msg" class="status" style="margin-top:14px"></div></div>
    <div class="card" style="max-width:760px;margin:18px auto;padding:24px"><h2>Account Recovery</h2><p class="sub">Forgot your password? Enter the email used for your account and we will send a secure reset link.</p><div class="field"><label>Account email</label><input id="recover-email" type="email"></div><button class="btn alt" onclick="recoverPassword()">Can't remember my password</button><div id="recovery-msg" class="status" style="margin-top:12px"></div></div>'''+base.footer()+'''</main>
<script>
const A='wbu_access_token';
function val(id){return document.getElementById(id).value.trim()}
function msg(x){document.getElementById('msg').textContent=x}
function rmsg(x){document.getElementById('recovery-msg').textContent=x}
function accepted(){return !!document.getElementById('policy_accept').checked}
async function api(path,body){let r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}),d={};try{d=await r.json()}catch(e){}return [r,d]}
async function signup(){let email=val('email'),phone=val('phone'),password=document.getElementById('password').value,name=val('name'),marketing=document.getElementById('marketing').checked;if(!accepted())return msg('You must read and check the Subscription & Virtual Currency Policy before creating your account.');if(!email||!phone||!password)return msg('Email, mobile phone and password are required.');if(password.length<8)return msg('Please use a password with at least 8 characters.');let [r,d]=await api('/api/auth/signup-v2',{email,phone,password,display_name:name,marketing_opt_in:marketing,accepted_policy:true,policy_version:'2026-08-25-v2'});if(!r.ok)return msg(d.error||'Unable to create account.');if(d.access_token){localStorage.setItem(A,d.access_token);msg(d.owner_test?'Owner test account signed in — testing access enabled with no Square charge.':'Account created and signed in.');}else msg('Account created. Check your email to confirm your address, then return here and sign in.');}
async function login(){let email=val('email'),password=document.getElementById('password').value;if(!accepted())return msg('Please check the Subscription & Virtual Currency Policy box before signing in.');if(!email||!password)return msg('Enter your email and password.');let [r,d]=await api('/api/auth/login-v2',{email,password,accepted_policy:true,policy_version:'2026-08-25-v2'});if(!r.ok)return msg(d.error||'Unable to sign in.');localStorage.setItem(A,d.access_token);msg(d.owner_test?'Owner test account signed in — testing access enabled with no Square charge.':'Signed in successfully.');}
function logout(){localStorage.removeItem(A);msg('Signed out.');}
async function recoverPassword(){let email=val('recover-email');if(!email)return rmsg('Enter your account email.');let [r,d]=await api('/api/auth/recover-v2',{email});rmsg(r.ok?'If an account exists for that email, a secure reset message has been sent.':(d.error||'Unable to start password recovery.'));}
const qp=new URLSearchParams(location.search);if(qp.get('confirmed')==='1')setTimeout(()=>msg('Email confirmed. Check the policy box, then sign in with the password you created.'),50);
</script>'''
    return base.page('Account — What Bout Us™', body)


class Handler(hot.Handler):
    def _json_fixed(self, status, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if urlparse(self.path).path == '/account':
            return self.sh(account_page_fixed())
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/auth/signup-v2':
            d = self.body_json()
            if d.get('accepted_policy') is not True:
                return self._json_fixed(400, {'error':'You must read and agree to the Subscription & Virtual Currency Policy before creating an account.'})
            email = str(d.get('email') or '').strip().lower()
            phone = str(d.get('phone') or '').strip()
            password = str(d.get('password') or '')
            name = str(d.get('display_name') or '').strip()
            marketing = bool(d.get('marketing_opt_in'))
            if not email or '@' not in email or not phone or len(password) < 8:
                return self._json_fixed(400, {'error':'Valid email, mobile phone and a password of at least 8 characters are required.'})
            redirect = quote(PUBLIC_URL + '/account?confirmed=1', safe='')
            meta = {'display_name':name,'phone_number':phone,'marketing_opt_in':marketing,'policy_accepted':True,'policy_version':POLICY_VERSION,'policy_accepted_at':datetime.now(timezone.utc).isoformat()}
            s, o = app_v2.sb('/auth/v1/signup?redirect_to=' + redirect, method='POST', body={'email':email,'password':password,'data':meta})
            if s not in (200, 201):
                err = (o or {}).get('msg') or (o or {}).get('message') or 'Unable to create account.'
                return self._json_fixed(s if s >= 400 else 400, {'error':err})
            out = o if isinstance(o, dict) else {}
            out['owner_test'] = email == OWNER_TEST_EMAIL
            return self._json_fixed(200, out)

        if path == '/api/auth/login-v2':
            d = self.body_json()
            if d.get('accepted_policy') is not True:
                return self._json_fixed(400, {'error':'Please agree to the Subscription & Virtual Currency Policy before signing in.'})
            email = str(d.get('email') or '').strip().lower()
            password = str(d.get('password') or '')
            s, o = app_v2.sb('/auth/v1/token?grant_type=password', method='POST', body={'email':email,'password':password})
            if s != 200:
                err = (o or {}).get('error_description') or (o or {}).get('msg') or 'Invalid email or password.'
                return self._json_fixed(s if s >= 400 else 401, {'error':err})
            out = o if isinstance(o, dict) else {}
            token = out.get('access_token')
            if token:
                app_v2.sb('/auth/v1/user', method='PUT', token=token, body={'data':{'policy_accepted':True,'policy_version':POLICY_VERSION,'policy_accepted_at':datetime.now(timezone.utc).isoformat()}})
            out['owner_test'] = email == OWNER_TEST_EMAIL
            return self._json_fixed(200, out)

        if path == '/api/auth/recover-v2':
            d = self.body_json()
            email = str(d.get('email') or '').strip().lower()
            if not email:
                return self._json_fixed(400, {'error':'Email is required.'})
            redirect = quote(PUBLIC_URL + '/account', safe='')
            s, _ = app_v2.sb('/auth/v1/recover?redirect_to=' + redirect, method='POST', body={'email':email})
            return self._json_fixed(200, {'ok':True}) if s in (200,201) else self._json_fixed(400, {'error':'Unable to start password recovery.'})

        return super().do_POST()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
