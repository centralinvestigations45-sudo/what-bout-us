from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import json
import run_idle

base = run_idle.base
_original_home = base.home
_original_companion_page = base.companion_page

CLOTHING = [
    ('Polo Shirt', 'polo-shirt', False),
    ('Long Sleeve Shirt', 'long-sleeve-shirt', False),
    ('Short Sleeve Shirt', 'short-sleeve-shirt', False),
    ('Dress Shirt', 'dress-shirt', False),
    ('Casual Pants', 'casual-pants', False),
    ('Khakis', 'khakis', False),
    ('Dress Pants', 'dress-pants', False),
    ('Premium Designer Polo', 'premium-designer-polo', True),
    ('Premium Tailored Dress Shirt', 'premium-tailored-dress-shirt', True),
    ('Premium Tailored Dress Pants', 'premium-tailored-dress-pants', True),
]

SHOES = [
    ('Sandals', 'sandals', False),
    ('Casual Sneakers', 'casual-sneakers', False),
    ('Dress Shoes', 'dress-shoes', False),
    ('Everyday Socks', 'everyday-socks', False),
    ('Dress Socks', 'dress-socks', False),
    ('Ankle Socks', 'ankle-socks', False),
    ('Premium Sneakers', 'premium-sneakers', True),
    ('Premium Dress Shoes', 'premium-dress-shoes', True),
    ('Premium Boots', 'premium-boots', True),
]

ACCESSORIES = [
    ('Fashion and Watches', 'fashion-and-watches', False),
    ('Women’s Earrings', 'womens-earrings', False),
    ('Men’s Watch', 'mens-watch', False),
    ('Women’s Watch', 'womens-watch', False),
    ('Men’s Bracelet', 'mens-bracelet', False),
    ('Women’s Bracelet', 'womens-bracelet', False),
    ('Necklace', 'necklace', False),
    ('Men’s Chain', 'mens-chain', False),
    ('Premium Men’s Diamond Chain', 'premium-mens-diamond-chain', True),
    ('Premium Men’s Luxury Watch', 'premium-mens-luxury-watch', True),
    ('Premium Women’s Diamond Earrings', 'premium-womens-diamond-earrings', True),
    ('Women’s Diamond Ring', 'womens-diamond-ring', True),
]


def pricing_home():
    html = _original_home()
    html = html.replace('Text conversations · Multiple companions · Conversation memory · Multiple languages','1 companion · Limited clothing, shoes and accessory selection · Text conversations · Conversation memory · Multiple languages',1)
    html = html.replace('All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories','Up to 2 companions · Voice-ready conversations · Premium style customization · Full premium clothing, shoe and accessory access',1)
    return html
base.home = pricing_home


def _cards(items, category):
    rows=[]
    for label,key,premium in items:
        badge='<span style="font-size:11px;font-weight:900;letter-spacing:.6px;color:#d36580">PREMIUM / UPGRADE TO EQUIP</span>' if premium else '<span style="font-size:11px;font-weight:900;letter-spacing:.6px;color:#72d8a0">AVAILABLE WITH $9.99+</span>'
        note='<div class="sub" style="font-size:12px;margin-top:7px">Visible to all plans. Premium plan required to equip.</div>' if premium else '<div class="sub" style="font-size:12px;margin-top:7px">Included in the standard selection.</div>'
        button='Preview / Equip' if premium else 'Equip'
        rows.append(f'''<div class="card" style="padding:18px;margin:0"><div>{badge}</div><h3 style="margin:8px 0 4px">{base.esc(label)}</h3>{note}<button class="btn {'alt' if premium else ''}" style="margin-top:12px" onclick="equip('{category}','{key}','{base.esc(label)}',{str(premium).lower()})">{button}</button></div>''')
    return ''.join(rows)


def _nav():
    return '<div style="display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 18px"><a class="btn alt" href="/clothing">Clothing</a><a class="btn alt" href="/shoes">Shoes</a><a class="btn alt" href="/accessories">Accessories</a></div>'


def _catalog_page(title,subtitle,items,category):
    options=''.join(f'<option value="{base.esc(n)}">{base.esc(n)}</option>' for n in base.ALL)
    cards=_cards(items,category)
    body=f'''<main class="shell"><a class="back" href="/">← Back to What Bout Us™</a><div class="card" style="max-width:1050px;margin:12px auto 24px"><div class="grad">COMPANION STYLE</div><h1>{base.esc(title)}</h1><p class="lead">{base.esc(subtitle)}</p>{_nav()}<div class="field" style="max-width:420px"><label>Choose companion</label><select id="companion" style="width:100%;padding:12px;border-radius:12px;background:#15151b;color:#fff;border:1px solid #3b3b45">{options}</select></div><div id="chosen" class="status" style="margin-top:10px"></div></div><section style="max-width:1050px;margin:0 auto 32px"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px">{cards}</div></section>{base.footer()}</main><script>(function(){{const c=document.getElementById('companion');const chosen=document.getElementById('chosen');function key(){{return 'wbu_style_'+c.value}}function load(){{let x=[];try{{x=JSON.parse(localStorage.getItem(key())||'[]')}}catch(e){{}}chosen.textContent=x.length?('Selected for '+c.value+': '+x.map(v=>v.label).join(', ')):('No style items selected for '+c.value+' yet.')}}window.equip=function(category,item,label,premium){{let x=[];try{{x=JSON.parse(localStorage.getItem(key())||'[]')}}catch(e){{}}x=x.filter(v=>!(v.category===category&&v.item===item));x.push({{category:category,item:item,label:label,premium:premium}});localStorage.setItem(key(),JSON.stringify(x));load();}};c.addEventListener('change',load);load();}})();</script>'''
    return base.page(title+' — What Bout Us™',body)

def clothing_page(): return _catalog_page('Clothing','Pick shirts and pants for your companion, from casual basics to premium tailored looks.',CLOTHING,'clothing')
def shoes_page(): return _catalog_page('Shoes & Socks','Pick footwear and socks for your companion, including sandals, sneakers, dress shoes and premium footwear.',SHOES,'shoes')
def accessories_page(): return _catalog_page('Accessories','Pick fashion, watches, earrings, bracelets, necklaces, chains and rings for your companion.',ACCESSORIES,'accessories')

def styled_companion_page(name):
    html=_original_companion_page(name)
    panel=f'''<div id="wbu-current-look" class="card" style="margin:16px 0;padding:14px 16px"><strong>Current style selections</strong><div id="wbu-style-list" class="sub" style="margin-top:5px">No style items selected.</div><div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:10px"><a href="/clothing" style="text-decoration:underline;color:#fff">Clothing</a><a href="/shoes" style="text-decoration:underline;color:#fff">Shoes</a><a href="/accessories" style="text-decoration:underline;color:#fff">Accessories</a></div></div><script>(function(){{let x=[];try{{x=JSON.parse(localStorage.getItem('wbu_style_{name}')||'[]')}}catch(e){{}}let el=document.getElementById('wbu-style-list');if(el&&x.length)el.textContent=x.map(v=>v.label).join(' · ');}})();</script>'''
    marker='<div id="history"></div>'
    return html.replace(marker,panel+marker,1) if marker in html else html.replace('</body>',panel+'</body>')
base.companion_page=styled_companion_page

class PricingHandler(run_idle.run_analytics.AnalyticsHandler):
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/clothing': return self.sh(clothing_page())
        if path=='/shoes': return self.sh(shoes_page())
        if path=='/accessories': return self.sh(accessories_page())
        return super().do_GET()

if __name__=='__main__': ThreadingHTTPServer(('0.0.0.0',base.PORT),PricingHandler).serve_forever()
