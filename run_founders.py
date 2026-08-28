from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import run_voice_livefix as live

base = live.base
_original_home = base.home


def _founders_section():
    return r'''<section id="founders-club" style="max-width:980px;margin:26px auto;padding:0 18px">
  <div style="padding:28px;border-radius:26px;background:radial-gradient(circle at 75% 15%,rgba(191,151,73,.18),transparent 35%),linear-gradient(145deg,#080808,#151515);border:1px solid #8f7137;box-shadow:0 18px 50px rgba(0,0,0,.42)">
    <div style="text-align:center;color:#d8b86c;font-size:12px;font-weight:900;letter-spacing:3px">LIMITED 1-YEAR FOUNDING MEMBERSHIP</div>
    <h2 style="text-align:center;font-size:clamp(30px,6vw,52px);margin:10px 0 6px">What Bout Us™ Founders Club</h2>
    <p style="text-align:center;color:#c9c3b7;max-width:760px;margin:0 auto 24px;line-height:1.6">Be part of the original What Bout Us™ community with a one-year Founders Club membership and a distinctive virtual Black Card that separates Founding Members from standard members throughout the site.</p>

    <div style="max-width:760px;margin:0 auto 24px;aspect-ratio:1.65;border-radius:24px;padding:4%;position:relative;overflow:hidden;background:#050505;border:2px solid #c6a458;box-shadow:0 16px 42px rgba(0,0,0,.55),inset 0 0 0 2px #181818;color:#d9ba70">
      <div style="position:absolute;inset:0;background:repeating-linear-gradient(165deg,transparent 0 23px,rgba(209,175,91,.05) 24px 25px)"></div>
      <div style="position:relative;text-align:center;font-family:Georgia,serif;font-size:clamp(24px,5vw,48px);letter-spacing:4px">WHAT BOUT US</div>
      <div style="position:relative;text-align:center;font-size:clamp(10px,2vw,17px);letter-spacing:6px;margin-top:5px">FOUNDERS CLUB</div>
      <div style="position:relative;width:17%;aspect-ratio:1.25;border-radius:12px;background:linear-gradient(135deg,#f1d995,#9a762f);margin-top:5%;box-shadow:inset 0 0 0 2px rgba(0,0,0,.28)"></div>
      <div style="position:relative;width:100%;box-sizing:border-box;font-family:monospace;font-size:clamp(13px,4.2vw,36px);letter-spacing:clamp(0px,.35vw,3px);margin-top:5%;display:flex;justify-content:space-between;gap:1%;white-space:nowrap"><span>7249</span><span>6187</span><span>3521</span><span>7903</span></div>
      <div style="position:relative;display:flex;gap:8%;align-items:flex-end;margin-top:4%;font-size:clamp(9px,1.5vw,14px);letter-spacing:2px"><span>FOUNDING MEMBER</span><span>1-YEAR UNLIMITED ACCESS</span></div>
      <div style="position:absolute;right:6%;bottom:8%;width:13%;aspect-ratio:1;border:1px solid #c6a458;transform:rotate(30deg);display:flex;align-items:center;justify-content:center"><span style="transform:rotate(-30deg);font-family:Georgia,serif;font-size:clamp(18px,4vw,36px)">WB</span></div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;max-width:780px;margin:0 auto 24px">
      <div class="card" style="padding:16px"><b>Virtual Black Card</b><div class="sub">Exclusive Founding Member identity on the platform.</div></div>
      <div class="card" style="padding:16px"><b>12 Months Unlimited Access</b><div class="sub">Founders-level platform access for one full year from activation.</div></div>
      <div class="card" style="padding:16px"><b>Founder Recognition</b><div class="sub">Distinctive Founders Club status during the one-year membership term.</div></div>
    </div>

    <div style="text-align:center"><div style="font-size:42px;font-weight:900">$250</div><div class="sub" style="margin:4px 0 8px">One-Year Founding Membership</div><div style="display:inline-block;margin:0 0 16px;padding:9px 14px;border:1px solid #8f7137;border-radius:999px;color:#e5c77d;font-weight:900;font-size:12px;letter-spacing:1.3px">ALL SALES FINAL · NON-REFUNDABLE</div><br><a class="btn" href="/account" style="font-size:18px;padding:15px 28px">Create Account to Join</a><div style="max-width:760px;margin:14px auto 0;color:#aaa18f;font-size:11px;line-height:1.5">The $250 What Bout Us™ Founders Club membership provides 12 months of Founders access from activation. The purchase is final and non-refundable. The Founders Black Card is a virtual membership credential, not a bank, credit, debit, Visa, Mastercard, or other payment card.</div></div>
  </div>
</section>'''


def founders_home():
    html = _original_home()
    section = _founders_section()

    # Place the Founders Black Card immediately after the homepage
    # Clothing, Shoes & Accessories collection section.
    collection_anchor = 'WHAT BOUT US™ COLLECTION 01'
    anchor_pos = html.find(collection_anchor)
    if anchor_pos != -1:
        section_end = html.find('</section>', anchor_pos)
        if section_end != -1:
            insert_at = section_end + len('</section>')
            return html[:insert_at] + section + html[insert_at:]

    # Safe fallback if the collection markup changes later.
    marker = '<main class="shell">'
    if marker in html:
        return html.replace(marker, marker + section, 1)
    return section + html


base.home = founders_home


class Handler(live.Handler):
    pass


if __name__ == '__main__':
    print('WBU_FOUNDERS_CLUB homepage offer enabled', flush=True)
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
