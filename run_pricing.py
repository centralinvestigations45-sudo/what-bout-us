from http.server import ThreadingHTTPServer
import run_idle

base = run_idle.base
_original_home = base.home


def pricing_home():
    html = _original_home()

    # Clarify what each paid plan includes.
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
    <div style="display:grid;gap:10px">
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


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), run_idle.run_analytics.AnalyticsHandler).serve_forever()
