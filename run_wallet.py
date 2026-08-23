import json
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_pricing

base = run_pricing.base
app_v2 = run_pricing.run_idle.run_analytics.app_v2

# In-site virtual wardrobe money only. No cash value.
PLAN_WALLETS = {
    'plus': {'label': '$9.99 monthly', 'allowance': 3000, 'premium': False},
    'plus-monthly': {'label': '$9.99 monthly', 'allowance': 3000, 'premium': False},
    'plus_monthly': {'label': '$9.99 monthly', 'allowance': 3000, 'premium': False},
    'unlimited': {'label': '$14.99 monthly', 'allowance': 50000, 'premium': True},
    'unlimited-monthly': {'label': '$14.99 monthly', 'allowance': 50000, 'premium': True},
    'unlimited_monthly': {'label': '$14.99 monthly', 'allowance': 50000, 'premium': True},
    'unlimited-yearly': {'label': '$149.99 yearly', 'allowance': 400000, 'premium': True},
    'unlimited_yearly': {'label': '$149.99 yearly', 'allowance': 400000, 'premium': True},
    'annual-unlimited': {'label': '$149.99 yearly', 'allowance': 400000, 'premium': True},
}

# Extend the catalog requested by the owner.
run_pricing.CLOTHING.extend([
    ('Casual Jacket', 'casual-jacket', False),
    ('Winter Coat', 'winter-coat', False),
    ('Sports Jersey', 'sports-jersey', False),
    ('Athletic Shorts', 'athletic-shorts', False),
    ('Swim Trunks', 'swim-trunks', False),
    ('Women’s Swimsuit', 'womens-swimsuit', False),
    ('Men’s Boxers', 'mens-boxers', False),
    ('Men’s Briefs', 'mens-briefs', False),
    ('Women’s Panties', 'womens-panties', False),
    ('Women’s Lingerie Set', 'womens-lingerie-set', False),
    ('Premium Leather Jacket', 'premium-leather-jacket', True),
    ('Premium Designer Coat', 'premium-designer-coat', True),
    ('Premium Sports Gear', 'premium-sports-gear', True),
    ('Premium Swimwear', 'premium-swimwear', True),
    ('Premium Lingerie Set', 'premium-lingerie-set', True),
])
run_pricing.ACCESSORIES.extend([
    ('Eyeglasses', 'eyeglasses', False),
    ('Sunglasses', 'sunglasses', False),
    ('Premium Designer Eyeglasses', 'premium-designer-eyeglasses', True),
    ('Premium Designer Sunglasses', 'premium-designer-sunglasses', True),
])

ITEMS = {
    # Clothing
    'polo-shirt': ('Polo Shirt', 'clothing', 250, False),
    'long-sleeve-shirt': ('Long Sleeve Shirt', 'clothing', 300, False),
    'short-sleeve-shirt': ('Short Sleeve Shirt', 'clothing', 225, False),
    'dress-shirt': ('Dress Shirt', 'clothing', 450, False),
    'casual-pants': ('Casual Pants', 'clothing', 400, False),
    'khakis': ('Khakis', 'clothing', 425, False),
    'dress-pants': ('Dress Pants', 'clothing', 550, False),
    'casual-jacket': ('Casual Jacket', 'clothing', 700, False),
    'winter-coat': ('Winter Coat', 'clothing', 900, False),
    'sports-jersey': ('Sports Jersey', 'clothing', 450, False),
    'athletic-shorts': ('Athletic Shorts', 'clothing', 300, False),
    'swim-trunks': ('Swim Trunks', 'clothing', 350, False),
    'womens-swimsuit': ('Women’s Swimsuit', 'clothing', 450, False),
    'mens-boxers': ('Men’s Boxers', 'clothing', 150, False),
    'mens-briefs': ('Men’s Briefs', 'clothing', 150, False),
    'womens-panties': ('Women’s Panties', 'clothing', 150, False),
    'womens-lingerie-set': ('Women’s Lingerie Set', 'clothing', 650, False),
    'premium-designer-polo': ('Premium Designer Polo', 'clothing', 3500, True),
    'premium-tailored-dress-shirt': ('Premium Tailored Dress Shirt', 'clothing', 5000, True),
    'premium-tailored-dress-pants': ('Premium Tailored Dress Pants', 'clothing', 6500, True),
    'premium-leather-jacket': ('Premium Leather Jacket', 'clothing', 9500, True),
    'premium-designer-coat': ('Premium Designer Coat', 'clothing', 12000, True),
    'premium-sports-gear': ('Premium Sports Gear', 'clothing', 7500, True),
    'premium-swimwear': ('Premium Swimwear', 'clothing', 6000, True),
    'premium-lingerie-set': ('Premium Lingerie Set', 'clothing', 8500, True),
    # Shoes / socks
    'sandals': ('Sandals', 'shoes', 300, False),
    'casual-sneakers': ('Casual Sneakers', 'shoes', 650, False),
    'dress-shoes': ('Dress Shoes', 'shoes', 850, False),
    'everyday-socks': ('Everyday Socks', 'shoes', 100, False),
    'dress-socks': ('Dress Socks', 'shoes', 125, False),
    'ankle-socks': ('Ankle Socks', 'shoes', 100, False),
    'premium-sneakers': ('Premium Sneakers', 'shoes', 5500, True),
    'premium-dress-shoes': ('Premium Dress Shoes', 'shoes', 7000, True),
    'premium-boots': ('Premium Boots', 'shoes', 8500, True),
    # Accessories
    'mens-earrings': ('Men’s Earrings', 'accessories', 400, False),
    'womens-earrings': ('Women’s Earrings', 'accessories', 400, False),
    'mens-watch': ('Men’s Watch', 'accessories', 900, False),
    'womens-watch': ('Women’s Watch', 'accessories', 900, False),
    'mens-bracelet': ('Men’s Bracelet', 'accessories', 500, False),
    'womens-bracelet': ('Women’s Bracelet', 'accessories', 500, False),
    'necklace': ('Necklace', 'accessories', 650, False),
    'mens-chain': ('Men’s Chain', 'accessories', 850, False),
    'eyeglasses': ('Eyeglasses', 'accessories', 350, False),
    'sunglasses': ('Sunglasses', 'accessories', 450, False),
    'premium-mens-diamond-chain': ('Premium Men’s Diamond Chain', 'accessories', 25000, True),
    'premium-mens-luxury-watch': ('Premium Men’s Luxury Watch', 'accessories', 18000, True),
    'premium-womens-diamond-earrings': ('Premium Women’s Diamond Earrings', 'accessories', 20000, True),
    'womens-diamond-ring': ('Women’s Diamond Ring', 'accessories', 30000, True),
    'premium-designer-eyeglasses': ('Premium Designer Eyeglasses', 'accessories', 6000, True),
    'premium-designer-sunglasses': ('Premium Designer Sunglasses', 'accessories', 7500, True),
}


def fmt(n):
    return '${:,.0f}'.format(int(n or 0))


def active_plan(token, uid):
    rows = app_v2.get('subscriptions', token, 'user_id=eq.' + app_v2.q(uid) + '&status=eq.active&select=plan,status,created_at&order=created_at.desc&limit=1')
    if not rows:
        return None, None
    plan = str(rows[0].get('plan') or '').strip().lower()
    return plan, PLAN_WALLETS.get(plan)


def ensure_wallet(token, uid, plan, cfg):
    rows = app_v2.get('wardrobe_wallets', token, 'user_id=eq.' + app_v2.q(uid) + '&select=plan,allowance,balance&limit=1')
    now = datetime.now(timezone.utc).isoformat()
    if not rows:
        body = {'user_id': uid, 'plan': plan, 'allowance': cfg['allowance'], 'balance': cfg['allowance'], 'updated_at': now}
        app_v2.sb('/rest/v1/wardrobe_wallets', method='POST', token=token, body=body, prefer='return=minimal')
        return body
    w = rows[0]
    if str(w.get('plan')) != plan or int(w.get('allowance') or 0) != cfg['allowance']:
        patch = {'plan': plan, 'allowance': cfg['allowance'], 'balance': cfg['allowance'], 'updated_at': now}
        app_v2.sb('/rest/v1/wardrobe_wallets?user_id=eq.' + app_v2.q(uid), method='PATCH', token=token, body=patch, prefer='return=minimal')
        w.update(patch)
    return w


def wallet_payload(token, uid, plan, cfg):
    w = ensure_wallet(token, uid, plan, cfg)
    purchases = app_v2.get('wardrobe_purchases', token, 'user_id=eq.' + app_v2.q(uid) + '&select=companion_name,category,item_key,item_label,price,premium,created_at&order=created_at.desc&limit=50')
    allowance = int(w.get('allowance') or cfg['allowance'])
    balance = int(w.get('balance') or 0)
    return {
        'plan': plan,
        'plan_label': cfg['label'],
        'allowance': allowance,
        'spent': max(0, allowance - balance),
        'balance': balance,
        'premium_access': bool(cfg['premium']),
        'purchases': purchases,
    }


def priced_cards(items, category):
    out = []
    for label, key, premium in items:
        price = ITEMS[key][2]
        badge = '<span style="font-size:11px;font-weight:900;letter-spacing:.6px;color:#d36580">PREMIUM / UPGRADE TO BUY</span>' if premium else '<span style="font-size:11px;font-weight:900;letter-spacing:.6px;color:#72d8a0">AVAILABLE WITH $9.99+</span>'
        rule = '$14.99 monthly or $149.99 yearly required for this premium item.' if premium else 'Available to $9.99 members and all higher plans.'
        out.append(f'''<div class="card" style="padding:18px;margin:0"><div>{badge}</div><h3 style="margin:8px 0 4px">{base.esc(label)}</h3><div style="font-size:25px;font-weight:900;margin:8px 0">{fmt(price)} <span class="sub" style="font-size:12px">virtual</span></div><div class="sub" style="font-size:12px">{rule}</div><button class="btn {'alt' if premium else ''}" style="margin-top:12px" onclick="buyAndEquip('{category}','{key}','{base.esc(label)}',{price},{str(premium).lower()})">Buy &amp; Equip</button></div>''')
    return ''.join(out)


def wallet_catalog_page(title, subtitle, items, category):
    options = ''.join(f'<option value="{base.esc(n)}">{base.esc(n)}</option>' for n in base.ALL)
    cards = priced_cards(items, category)
    body = f'''
<main class="shell">
<a class="back" href="/">← Back to What Bout Us™</a>
<div class="card" style="max-width:1050px;margin:12px auto 18px">
<div class="grad">COMPANION STYLE</div><h1>{base.esc(title)}</h1><p class="lead">{base.esc(subtitle)}</p>{run_pricing._nav()}
<div class="field" style="max-width:420px"><label>Choose companion</label><select id="companion" style="width:100%;padding:12px;border-radius:12px;background:#15151b;color:#fff;border:1px solid #3b3b45">{options}</select></div>
<div id="chosen" class="status" style="margin-top:10px"></div></div>
<section style="max-width:1050px;margin:0 auto 18px"><div class="card" style="padding:20px">
<div class="grad">YOUR VIRTUAL STYLE WALLET</div><div id="wallet-status" class="sub" style="margin:8px 0 14px">Sign in to view your balance and spending.</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px"><div><div class="sub">Starting allowance</div><div id="wallet-allowance" style="font-size:26px;font-weight:900">—</div></div><div><div class="sub">Spent</div><div id="wallet-spent" style="font-size:26px;font-weight:900">—</div></div><div><div class="sub">Remaining</div><div id="wallet-balance" style="font-size:26px;font-weight:900">—</div></div></div>
<p class="sub" style="font-size:12px;margin-top:12px">Virtual style money is only for What Bout Us™ companion clothing, shoes and accessories. It has no cash value and cannot be withdrawn or exchanged for real money.</p>
<div style="margin-top:16px"><strong>Recent spending</strong><div id="wallet-history" class="sub" style="margin-top:7px">No purchases yet.</div></div></div></section>
<section style="max-width:1050px;margin:0 auto 32px"><p class="sub">Every item has a virtual price tag. All plans can see the full catalog. $9.99 members can buy standard items; premium/high-end items require an upgrade.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px">{cards}</div></section>{base.footer()}</main>
<script>(function(){{
const A='wbu_access_token',c=document.getElementById('companion'),chosen=document.getElementById('chosen'),f=n=>'$'+Number(n||0).toLocaleString();
function auth(){{const t=localStorage.getItem(A);return t?{{Authorization:'Bearer '+t}}:{{}}}}function k(){{return 'wbu_style_'+c.value}}
function style(){{let x=[];try{{x=JSON.parse(localStorage.getItem(k())||'[]')}}catch(e){{}}chosen.textContent=x.length?('Selected for '+c.value+': '+x.map(v=>v.label).join(', ')):('No style items selected for '+c.value+' yet.')}}
async function wallet(){{let r=await fetch('/api/wardrobe-wallet',{{headers:auth()}}),d={{}};try{{d=await r.json()}}catch(e){{}}if(!r.ok){{document.getElementById('wallet-status').textContent=d.error||'Sign in with an active subscription.';return}}document.getElementById('wallet-status').textContent=d.plan_label+' · Virtual style wallet';document.getElementById('wallet-allowance').textContent=f(d.allowance);document.getElementById('wallet-spent').textContent=f(d.spent);document.getElementById('wallet-balance').textContent=f(d.balance);let h=document.getElementById('wallet-history');h.innerHTML=(d.purchases&&d.purchases.length)?d.purchases.slice(0,12).map(x=>'<div style="padding:5px 0;border-bottom:1px solid #2d2d35">'+x.item_label+' · '+x.companion_name+' · '+f(x.price)+'</div>').join(''):'No purchases yet.'}}
window.buyAndEquip=async function(category,item,label,price,premium){{if(!localStorage.getItem(A))return alert('Please sign in with your subscription to use virtual style money.');let r=await fetch('/api/wardrobe-purchase',{{method:'POST',headers:{{'Content-Type':'application/json',...auth()}},body:JSON.stringify({{companion:c.value,category,item}})}}),d={{}};try{{d=await r.json()}}catch(e){{}}if(!r.ok)return alert(d.error||'Unable to complete this virtual purchase.');let x=[];try{{x=JSON.parse(localStorage.getItem(k())||'[]')}}catch(e){{}}x=x.filter(v=>!(v.category===category&&v.item===item));x.push({{category,item,label,premium}});localStorage.setItem(k(),JSON.stringify(x));style();wallet();alert(d.already_owned?(label+' is already owned for '+c.value+' and has been equipped.'):(label+' purchased for '+f(price)+' virtual money and equipped to '+c.value+'.'))}};
c.addEventListener('change',style);style();wallet();}})();</script>'''
    return base.page(title + ' — What Bout Us™', body)


run_pricing._catalog_page = wallet_catalog_page

# Add wallet allowances to the homepage plan summary.
_original_home = base.home
def wallet_home():
    html = _original_home()
    html = html.replace('Unlimited Yearly — $149.99/year</strong> · All 32 companions', 'Unlimited Yearly — $149.99/year</strong> · $400,000 virtual style money · All 32 companions', 1)
    html = html.replace('Unlimited Monthly — $14.99/month</strong> · Up to 2 companions', 'Unlimited Monthly — $14.99/month</strong> · $50,000 virtual style money · Up to 2 companions', 1)
    html = html.replace('Plus Monthly — $9.99/month</strong> · 1 companion', 'Plus Monthly — $9.99/month</strong> · $3,000 virtual style money · 1 companion', 1)
    return html
base.home = wallet_home


class WalletHandler(run_pricing.PricingHandler):
    def body_json(self):
        n = int(self.headers.get('Content-Length', '0') or 0)
        try:return json.loads(self.rfile.read(n).decode() or '{}')
        except Exception:return {}

    def account_plan(self):
        token = app_v2.tok(self.headers); account = app_v2.user(token) if token else None
        if not account:return None, None, None, None
        plan, cfg = active_plan(token, account['id']); return token, account, plan, cfg

    def do_GET(self):
        if urlparse(self.path).path == '/api/wardrobe-wallet':
            token, account, plan, cfg = self.account_plan()
            if not account:return self.sj({'error':'Please sign in to view your virtual style wallet.'},401)
            if not plan:return self.sj({'error':'An active subscription is required for virtual style money.'},402)
            if not cfg:return self.sj({'error':'This subscription plan does not have a virtual wallet configured yet.'},400)
            return self.sj(wallet_payload(token, account['id'], plan, cfg))
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != '/api/wardrobe-purchase':return super().do_POST()
        token, account, plan, cfg = self.account_plan()
        if not account:return self.sj({'error':'Please sign in to make a virtual wardrobe purchase.'},401)
        if not plan:return self.sj({'error':'An active subscription is required for virtual wardrobe purchases.'},402)
        if not cfg:return self.sj({'error':'This subscription plan does not have a virtual wallet configured yet.'},400)
        d=self.body_json(); companion=str(d.get('companion') or '').strip(); category=str(d.get('category') or '').strip(); item=str(d.get('item') or '').strip()
        if companion not in base.ALL or item not in ITEMS:return self.sj({'error':'Invalid companion or wardrobe item.'},400)
        label, expected, price, premium = ITEMS[item]
        if category != expected:return self.sj({'error':'Invalid wardrobe category.'},400)
        if premium and not cfg['premium']:return self.sj({'error':'This is a premium/high-end item. Upgrade to the $14.99 monthly or $149.99 yearly plan to buy and equip it.'},403)
        ensure_wallet(token, account['id'], plan, cfg)
        status, result = app_v2.sb('/rest/v1/rpc/spend_wardrobe_funds', method='POST', token=token, body={
            'p_user_id':account['id'],'p_plan':plan,'p_allowance':cfg['allowance'],'p_companion_name':companion,'p_category':category,'p_item_key':item,'p_item_label':label,'p_price':price,'p_premium':premium
        })
        if status not in (200,201) or not isinstance(result,list) or not result:
            msg='Not enough virtual style money for this item.' if 'insufficient' in str(result).lower() else 'Unable to complete this virtual purchase.'
            return self.sj({'error':msg},402 if 'insufficient' in str(result).lower() else 500)
        row=result[0]
        return self.sj({'ok':True,'item':label,'price':price,'balance':row.get('balance'),'spent':row.get('spent'),'already_owned':bool(row.get('already_owned'))})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), WalletHandler).serve_forever()
