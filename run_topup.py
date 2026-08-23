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
    <a class="btn alt" href="/plans-virtual-money" style="margin-left:8px">How Plans &amp; Virtual Money Work</a>
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
    note = '''<section style="max-width:980px;margin:20px auto;padding:0 18px"><div class="card" style="padding:18px 20px"><strong>Plans &amp; Virtual Style Money</strong><p class="sub" style="margin:7px 0 12px">See how much virtual style money comes with each configured plan, how wardrobe spending works, and how subscribers can add $300 more for $5.00.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="/plans-virtual-money">View Plans &amp; Virtual Money</a><a class="btn alt" href="/style-money/topup">Add Virtual Money</a></div></div></section>'''
    marker = '<section style="max-width:980px;margin:54px auto 24px;padding:0 18px;text-align:center">'
    return html.replace(marker, note + marker, 1) if marker in html else html
base.home = topup_home


def plans_virtual_money_page():
    body = '''
<main class="shell">
  <a class="back" href="/">← Back to What Bout Us™</a>
  <div class="card" style="max-width:1000px;margin:12px auto 22px;padding:24px">
    <div class="grad">PLANS &amp; VIRTUAL STYLE MONEY</div>
    <h1>Choose Your Plan. Style Your Companion.</h1>
    <p class="lead">Every configured paid plan includes virtual style money that subscribers can spend on companion clothing, shoes and accessories. Each item has a virtual price tag, and your wallet keeps track of what you spend and what you have left.</p>
  </div>

  <section style="max-width:1000px;margin:0 auto 22px;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px">
    <div class="card" style="padding:22px;margin:0">
      <div class="grad">$9.99 MONTHLY</div>
      <h2 style="margin:8px 0">$3,000 Virtual</h2>
      <p class="sub" style="line-height:1.6">Includes 1 companion and a limited clothing, shoe and accessory selection. Subscribers can see the full catalog, but premium/high-end items require an upgrade.</p>
    </div>
    <div class="card" style="padding:22px;margin:0;border:1px solid #57334a">
      <div class="grad">$14.99 MONTHLY</div>
      <h2 style="margin:8px 0">$50,000 Virtual</h2>
      <p class="sub" style="line-height:1.6">Includes up to 2 companions and access to the premium/high-end clothing, shoe and accessory collection.</p>
    </div>
    <div class="card" style="padding:22px;margin:0;border:1px solid #d36580">
      <div class="grad">$149.99 YEARLY · BEST VALUE</div>
      <h2 style="margin:8px 0">$400,000 Virtual</h2>
      <p class="sub" style="line-height:1.6">Includes all 32 companions, full premium wardrobe and accessory access, voice-ready conversations and the complete Unlimited experience for the year.</p>
    </div>
  </section>

  <section style="max-width:1000px;margin:0 auto 22px">
    <div class="card" style="padding:24px">
      <div class="grad">HOW VIRTUAL MONEY WORKS</div>
      <h2 style="margin:8px 0 12px">Your Style Wallet Keeps the Total for You</h2>
      <p class="sub" style="line-height:1.7">When you buy a virtual clothing item, pair of shoes or accessory for a companion, the item's virtual price is deducted from your style wallet. Your wallet shows your starting allowance, total spent, remaining balance and recent purchases so you can keep tabs on your accessory and wardrobe spending.</p>
      <p class="sub" style="line-height:1.7">Buying an item does not charge real money from your card. It uses the virtual style money already in your What Bout Us™ wallet.</p>
    </div>
  </section>

  <section style="max-width:1000px;margin:0 auto 28px">
    <div class="card" style="padding:24px;border:1px solid #57334a">
      <div class="grad">NEED MORE?</div>
      <h2 style="margin:8px 0">Add $300 Virtual for $5.00</h2>
      <p class="sub" style="line-height:1.7">Active subscribers can purchase additional virtual style money. A $5.00 real-money payment adds $300 in virtual style money to the subscriber's wallet after the payment is confirmed.</p>
      <a class="btn" href="/style-money/topup">Add $300 for $5</a>
      <p class="sub" style="font-size:12px;line-height:1.6;margin-top:12px">Virtual style money is for What Bout Us™ companion clothing, shoes and accessories only. It has no cash value, cannot be withdrawn, cannot be transferred for cash and cannot be exchanged for real currency.</p>
    </div>
  </section>
  ''' + base.footer() + '''
</main>
'''
    return base.page('Plans & Virtual Money — What Bout Us™', body)


class TopupHandler(run_wallet.WalletHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/plans-virtual-money':
            return self.sh(plans_virtual_money_page())
        if path == '/style-money/topup':
            token, account, plan, cfg = self.account_plan()
            if not account:
                return self.sh(base.page('Add Virtual Style Money — What Bout Us™', '<main class="shell"><div class="card"><h1>Sign in required</h1><p class="sub">Please sign in with an active subscription before adding virtual style money.</p><a class="btn" href="/account">Sign In</a></div>'+base.footer()+'</main>'))
            if not plan or not cfg:
                return self.sh(base.page('Add Virtual Style Money — What Bout Us™', '<main class="shell"><div class="card"><h1>Subscription required</h1><p class="sub">An active paid subscription is required to purchase virtual style money.</p><a class="btn" href="/plans-virtual-money">View Plans</a></div>'+base.footer()+'</main>'))
            if SQUARE_STYLE_TOPUP_URL:
                self.send_response(302)
                self.send_header('Location', SQUARE_STYLE_TOPUP_URL)
                self.end_headers()
                return
            return self.sh(base.page('Add Virtual Style Money — What Bout Us™', '<main class="shell"><div class="card"><div class="grad">VIRTUAL STYLE MONEY</div><h1>$5.00 = $300 Virtual</h1><p class="sub">This top-up option is ready, but the secure Square payment link still needs to be connected before purchases can be processed.</p><a class="btn alt" href="/plans-virtual-money">How Plans &amp; Virtual Money Work</a></div>'+base.footer()+'</main>'))
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), TopupHandler).serve_forever()
