from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import json
import run_idle

base = run_idle.base
_original_home = base.home
_original_companion_page = base.companion_page

BASIC_ACCESSORIES = [
    ('Classic Watch', 'watch'),
    ('Everyday Sunglasses', 'sunglasses'),
    ('Casual Cap', 'cap'),
    ('Simple Bracelet', 'bracelet'),
    ('Casual Sneakers', 'sneakers'),
]

PREMIUM_ACCESSORIES = [
    ('Luxury Chain', 'chain'),
    ('Diamond Piece', 'diamond'),
    ('Premium Boots', 'boots'),
    ('Designer Watch', 'designer-watch'),
    ('Luxury Sunglasses', 'luxury-sunglasses'),
    ('Premium Jacket', 'premium-jacket'),
]


def pricing_home():
    html = _original_home()

    html = html.replace(
        'Text conversations · Multiple companions · Conversation memory · Multiple languages',
        '1 companion · Limited accessory selection · Text conversations · Conversation memory · Multiple languages',
        1,
    )
    html = html.replace(
        'All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories',
        'Up to 2 companions · Voice-ready conversations · Premium style customization · Full premium accessory access, including high-end items such as chains, diamond pieces and premium boots',
        1,
    )
    html = html.replace(
        '<div class="price" style="font-size:32px">$149.99 <small>/ year</small></div><p class="sub" style="margin:6px 0 14px">2 months off</p>',
        '<div class="price" style="font-size:32px">$149.99 <small>/ year</small></div><p class="sub" style="margin:8px 0 6px"><strong>All 32 companions</strong> · Voice-ready conversations · Premium style customization · Full premium accessory access, including high-end chains, diamond pieces and premium boots</p><p class="sub" style="margin:6px 0 14px">2 months off</p>',
        1,
    )

    recommendation = '''
<section style="max-width:980px;margin:34px auto 20px;padding:0 18px">
  <div style="background:#131319;border:1px solid #57334a;border-radius:20px;padding:24px 22px">
    <div style="font-size:13px;font-weight:900;letter-spacing:1px;color:#d36580;margin-bottom:8px">WHICH PLAN IS BEST?</div>
    <h2 style="margin:0 0 10px">WHAT BOUT US™ UNLIMITED Yearly — Best Overall Value</h2>
    <p class="sub" style="line-height:1.65;margin:0 0 18px">The Unlimited Yearly plan at <strong>$149.99/year</strong> is the best overall value for someone who wants the complete What Bout Us™ experience. It includes <strong>all 32 companions</strong>, voice-ready conversations, premium style customization, and <strong>full access to the high-end accessory collection</strong>, including chains, diamond pieces, premium boots and other premium items. The <strong>$14.99 monthly plan</strong> also unlocks the full premium accessory collection, but it is limited to <strong>up to 2 companions</strong>. The <strong>$9.99 monthly plan</strong> includes 1 companion and a <strong>limited selection of accessories</strong>. Members on that plan still get accessories, just not the full premium/high-end collection available on the higher plans. Paying $14.99 each month for 12 months would total <strong>$179.88</strong>, so the $149.99 yearly plan saves <strong>$29.89</strong> while also opening the full 32-companion experience.</p>
    <p style="margin:18px 0 0"><a class="btn" href="/accessories">Browse Clothing &amp; Accessories</a></p>
    <div style="display:grid;gap:10px;margin-top:20px">
      <div><strong>1. Unlimited Yearly — $149.99/year</strong> · All 32 companions · Full premium accessories · Best overall value</div>
      <div><strong>2. Plus Yearly — $99.99/year</strong> · Best lower-cost yearly option</div>
      <div><strong>3. Unlimited Monthly — $14.99/month</strong> · Up to 2 companions · Full premium accessories</div>
      <div><strong>4. Plus Monthly — $9.99/month</strong> · 1 companion · Limited accessory selection</div>
    </div>
  </div>
</section>
'''
    marker = '<section style="max-width:980px;margin:54px auto 24px;padding:0 18px;text-align:center">'
    if marker in html:
        html = html.replace(marker, recommendation + marker, 1)
    else:
        footer = base.footer()
        html = html.replace(footer, recommendation + footer, 1)
    return html


base.home = pricing_home


def _cards(items, premium=False):
    rows = []
    for label, key in items:
        badge = '<span style="font-size:11px;font-weight:900;letter-spacing:.6px;color:#d36580">PREMIUM</span>' if premium else '<span style="font-size:11px;font-weight:900;letter-spacing:.6px;color:#72d8a0">AVAILABLE WITH $9.99+</span>'
        note = '<div class="sub" style="font-size:12px;margin-top:7px">$14.99 monthly and $149.99 yearly members can equip this item.</div>' if premium else '<div class="sub" style="font-size:12px;margin-top:7px">Included in the limited accessory selection.</div>'
        rows.append(f'''<div class="card" style="padding:18px;margin:0"><div>{badge}</div><h3 style="margin:8px 0 4px">{base.esc(label)}</h3>{note}<button class="btn {'alt' if premium else ''}" style="margin-top:12px" onclick="equip('{key}','{base.esc(label)}',{str(premium).lower()})">{'Preview / Equip' if premium else 'Equip'}</button></div>''')
    return ''.join(rows)


def accessories_page():
    options = ''.join(f'<option value="{base.esc(n)}">{base.esc(n)}</option>' for n in base.ALL)
    basic = _cards(BASIC_ACCESSORIES, False)
    premium = _cards(PREMIUM_ACCESSORIES, True)
    body = f'''
<main class="shell">
  <a class="back" href="/">← Back to What Bout Us™</a>
  <div class="card" style="max-width:1050px;margin:12px auto 24px">
    <div class="grad">COMPANION WARDROBE</div>
    <h1>Clothing &amp; Accessories</h1>
    <p class="lead">Choose a companion, then pick the clothing and accessories you want associated with that companion's look.</p>
    <div class="field" style="max-width:420px"><label>Choose companion</label><select id="companion" style="width:100%;padding:12px;border-radius:12px;background:#15151b;color:#fff;border:1px solid #3b3b45">{options}</select></div>
    <div id="chosen" class="status" style="margin-top:10px"></div>
  </div>
  <section style="max-width:1050px;margin:0 auto 28px">
    <h2>Included Accessories</h2>
    <p class="sub">$9.99 members can use this limited selection. Higher plans can use these too.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px">{basic}</div>
  </section>
  <section style="max-width:1050px;margin:0 auto 32px">
    <h2>Premium / High-End Collection</h2>
    <p class="sub">Visible to everyone. $14.99 monthly and $149.99 yearly members can equip these premium items. $9.99 members can preview them and upgrade to unlock them.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px">{premium}</div>
  </section>
  {base.footer()}
</main>
<script>
(function(){{
  const c=document.getElementById('companion');
  const chosen=document.getElementById('chosen');
  function key(){{return 'wbu_style_'+c.value}}
  function load(){{
    let x=[];try{{x=JSON.parse(localStorage.getItem(key())||'[]')}}catch(e){{}}
    chosen.textContent=x.length?('Equipped to '+c.value+': '+x.map(v=>v.label).join(', ')):('No accessories selected for '+c.value+' yet.');
  }}
  window.equip=function(item,label,premium){{
    let x=[];try{{x=JSON.parse(localStorage.getItem(key())||'[]')}}catch(e){{}}
    x=x.filter(v=>v.item!==item);x.push({{item:item,label:label,premium:premium}});localStorage.setItem(key(),JSON.stringify(x));load();
    if(premium) alert(label+' has been added as a premium selection. Premium access is for $14.99 monthly or $149.99 yearly members.');
  }};
  c.addEventListener('change',load);load();
}})();
</script>
'''
    return base.page('Clothing & Accessories — What Bout Us™', body)


def styled_companion_page(name):
    html = _original_companion_page(name)
    panel = f'''<div id="wbu-current-look" class="card" style="margin:16px 0;padding:14px 16px"><strong>Current look</strong><div id="wbu-style-list" class="sub" style="margin-top:5px">No accessories selected.</div><a href="/accessories" style="display:inline-block;margin-top:8px;text-decoration:underline;color:#fff">Change clothing &amp; accessories</a></div><script>(function(){{let x=[];try{{x=JSON.parse(localStorage.getItem('wbu_style_{name}')||'[]')}}catch(e){{}}let el=document.getElementById('wbu-style-list');if(el&&x.length)el.textContent=x.map(v=>v.label).join(' · ');}})();</script>'''
    marker = '<div id="history"></div>'
    if marker in html:
        html = html.replace(marker, panel + marker, 1)
    else:
        html = html.replace('</body>', panel + '</body>')
    return html


base.companion_page = styled_companion_page


class PricingHandler(run_idle.run_analytics.AnalyticsHandler):
    def do_GET(self):
        if urlparse(self.path).path == '/accessories':
            return self.sh(accessories_page())
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), PricingHandler).serve_forever()
