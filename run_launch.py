import os
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer
import run_profile

base = run_profile.base

# Final homepage ordering: swap Simone with Alex and Chloe with Lily.
base.MEN = ['Simone','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Darius','Noah','Jack','Julius','Leo','Carter','Malik','Alex']
base.WOMEN = ['Chloe','Aria','Mika','Zoey','Nova','Sophia','Isabella','Lily','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye','Nia']
base.ALL = base.MEN + base.WOMEN

# Annual Square checkout URLs are separate from the existing monthly links.
SQUARE_PLUS_YEARLY_URL = os.environ.get('SQUARE_PLUS_YEARLY_URL', '').strip()
SQUARE_UNLIMITED_YEARLY_URL = os.environ.get('SQUARE_UNLIMITED_YEARLY_URL', '').strip()

_original_home = base.home


def annual_home():
    html = _original_home()

    plus_old = '''<div class="plan"><h3>WHAT BOUT US™+</h3><div class="price">$9.99 <small>/ month</small></div><p>Text conversations · Multiple companions · Conversation memory · Multiple languages</p><a class="btn alt" href="/checkout?plan=plus">Choose Plus</a></div>'''
    plus_new = '''<div class="plan"><h3>WHAT BOUT US™+</h3><div class="price">$9.99 <small>/ month</small></div><p>Text conversations · Multiple companions · Conversation memory · Multiple languages</p><a class="btn alt" href="/checkout?plan=plus">Choose Monthly</a><div style="margin-top:18px;padding-top:18px;border-top:1px solid #35353e"><div style="font-size:13px;font-weight:900;letter-spacing:.8px;color:#72d8a0;margin-bottom:5px">SAVE $19.89</div><div class="price" style="font-size:32px">$99.99 <small>/ year</small></div><p class="sub" style="margin:6px 0 14px">About 2 months free compared with monthly billing.</p><a class="btn" href="/checkout?plan=plus-yearly">Choose Yearly</a></div></div>'''

    unlimited_old = '''<div class="plan hot"><h3>WHAT BOUT US™ UNLIMITED</h3><div class="price">$14.99 <small>/ month</small></div><p>All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories</p><a class="btn" href="/checkout?plan=unlimited">Choose Unlimited</a></div>'''
    unlimited_new = '''<div class="plan hot"><div style="display:inline-block;background:#d36580;color:white;border-radius:999px;padding:6px 10px;font-size:11px;font-weight:900;letter-spacing:.7px;margin-bottom:10px">BEST VALUE</div><h3>WHAT BOUT US™ UNLIMITED</h3><div class="price">$14.99 <small>/ month</small></div><p>All 32 companions · Voice-ready conversations · Premium style customization · Expanded accessories</p><a class="btn alt" href="/checkout?plan=unlimited">Choose Monthly</a><div style="margin-top:18px;padding-top:18px;border-top:1px solid #57334a"><div style="font-size:13px;font-weight:900;letter-spacing:.8px;color:#72d8a0;margin-bottom:5px">SAVE $29.89</div><div class="price" style="font-size:32px">$149.99 <small>/ year</small></div><p class="sub" style="margin:6px 0 14px">About 2 months free compared with monthly billing.</p><a class="btn" href="/checkout?plan=unlimited-yearly">Choose Yearly</a></div></div>'''

    html = html.replace(plus_old, plus_new)
    html = html.replace(unlimited_old, unlimited_new)
    return html


base.home = annual_home


class LaunchHandler(run_profile.run_current.ProductionHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/checkout':
            plan = parse_qs(u.query).get('plan', [''])[0]
            if plan in ('plus-yearly', 'unlimited-yearly'):
                target = SQUARE_PLUS_YEARLY_URL if plan == 'plus-yearly' else SQUARE_UNLIMITED_YEARLY_URL
                if target:
                    self.send_response(302)
                    self.send_header('Location', target)
                    self.end_headers()
                    return
                label = 'WHAT BOUT US™+ Annual — $99.99/year' if plan == 'plus-yearly' else 'WHAT BOUT US™ UNLIMITED Annual — $149.99/year'
                return self.sh(base.page('Annual Checkout — What Bout Us™', f'<main class="shell"><div class="card"><h1>{label}</h1><p class="sub">Secure annual billing through Square is being connected. This plan will renew once per year until canceled.</p><a class="btn alt" href="/#plans">Back to Plans</a></div>{base.footer()}</main>'))
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), LaunchHandler).serve_forever()
