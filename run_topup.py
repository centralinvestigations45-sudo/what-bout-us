import os
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_wallet

base = run_wallet.base

# Real-money purchase: $5.00 buys $300 in non-cash virtual style money.
# The Square payment link is configured in Railway and must only credit the wallet after verified payment.
SQUARE_STYLE_TOPUP_URL = os.environ.get('SQUARE_STYLE_TOPUP_URL', '').strip()

_original_catalog_page = run_wallet.wallet_catalog_page


def topup_catalog_page(title, subtitle, items, category):
    html = _original_catalog_page(title, subtitle, items, category)
    topup = '''
<section style="max-width:1050px;margin:0 auto 18px">
  <div class="card" style="padding:20px;border:1px solid #57334a">
    <div class="grad">ADD VIRTUAL STYLE MONEY</div>
    <h2 style="margin:8px 0">$5.00 = $300 Virtual Style Money</h2>
    <p class="sub" style="line-height:1.6">Active subscribers can add more virtual style money whenever they want. Pay $5.00 to receive $300 in What Bout Us™ virtual style money after the payment is confirmed.</p>
    <a class="btn" href="/style-money/topup">Add $300 for $5</a>
    <p class="sub" style="font-size:12px;margin-top:10px">Virtual style money has no cash value, cannot be withdrawn, transferred for cash, or exchanged for real currency.</p>
  </div>
</section>
'''
    marker = '<section style="max-width:1050px;margin:0 auto 32px">'
    return html.replace(marker, topup + marker, 1)


run_wallet.run_pricing._catalog_page = topup_catalog_page

_original_home = base.home

def topup_home():
    html = _original_home()
    note = '''<section style="max-width:980px;margin:20px auto;padding:0 18px"><div class="card" style="padding:18px 20px"><strong>Need more virtual style money?</strong><p class="sub" style="margin:7px 0 12px">Subscribers can add $300 in virtual style money for $5.00.</p><a class="btn alt" href="/style-money/topup">Add Virtual Money</a></div></section>'''
    marker = '<section style="max-width:980px;margin:54px auto 24px;padding:0 18px;text-align:center">'
    return html.replace(marker, note + marker, 1) if marker in html else html
base.home = topup_home


class TopupHandler(run_wallet.WalletHandler):
    def do_GET(self):
        if urlparse(self.path).path == '/style-money/topup':
            token, account, plan, cfg = self.account_plan()
            if not account:
                return self.sh(base.page('Add Virtual Style Money — What Bout Us™', '<main class="shell"><div class="card"><h1>Sign in required</h1><p class="sub">Please sign in with an active subscription before adding virtual style money.</p><a class="btn" href="/account">Sign In</a></div>'+base.footer()+'</main>'))
            if not plan or not cfg:
                return self.sh(base.page('Add Virtual Style Money — What Bout Us™', '<main class="shell"><div class="card"><h1>Subscription required</h1><p class="sub">An active paid subscription is required to purchase virtual style money.</p><a class="btn" href="/">View Plans</a></div>'+base.footer()+'</main>'))
            if SQUARE_STYLE_TOPUP_URL:
                self.send_response(302)
                self.send_header('Location', SQUARE_STYLE_TOPUP_URL)
                self.end_headers()
                return
            return self.sh(base.page('Add Virtual Style Money — What Bout Us™', '<main class="shell"><div class="card"><div class="grad">VIRTUAL STYLE MONEY</div><h1>$5.00 = $300 Virtual</h1><p class="sub">This top-up option is ready, but the secure Square payment link still needs to be connected before purchases can be processed.</p><a class="btn alt" href="/">Back to What Bout Us™</a></div>'+base.footer()+'</main>'))
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), TopupHandler).serve_forever()
