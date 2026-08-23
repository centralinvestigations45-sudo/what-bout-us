from http.server import ThreadingHTTPServer
import run_idle

base = run_idle.base
_original_home = base.home


def pricing_home():
    html = _original_home()
    recommendation = '''
<section style="max-width:980px;margin:34px auto 20px;padding:0 18px">
  <div style="background:#131319;border:1px solid #57334a;border-radius:20px;padding:24px 22px">
    <div style="font-size:13px;font-weight:900;letter-spacing:1px;color:#d36580;margin-bottom:8px">WHICH PLAN IS BEST?</div>
    <h2 style="margin:0 0 10px">WHAT BOUT US™ UNLIMITED Yearly — Best Overall Value</h2>
    <p class="sub" style="line-height:1.65;margin:0 0 18px">The Unlimited Yearly plan at <strong>$149.99/year</strong> is the best overall value for someone who plans to use What Bout Us™ regularly. It includes access to all 32 companions, voice-ready conversations, premium style customization, and expanded accessories. Paying <strong>$14.99/month for 12 months would cost $179.88</strong>, so choosing the yearly plan saves <strong>$29.89</strong> over the year — about two months of the monthly price — while keeping the full Unlimited experience for the entire year.</p>
    <div style="display:grid;gap:10px">
      <div><strong>1. Unlimited Yearly — $149.99/year</strong> · Best overall value</div>
      <div><strong>2. Plus Yearly — $99.99/year</strong> · Best lower-cost yearly option</div>
      <div><strong>3. Unlimited Monthly — $14.99/month</strong> · Best if you want flexibility</div>
      <div><strong>4. Plus Monthly — $9.99/month</strong> · Great way to get started with a paid plan</div>
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
