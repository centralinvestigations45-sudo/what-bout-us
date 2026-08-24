from http.server import ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import os
import run_faces

# TEMPORARY NIA TEST MODE
# Gives Nia a no-charge guest test window without changing the paid plans for other companions.
app_v2 = run_faces.run_brand.app_v2
app_v2.FREE.add('Nia')

_original_companion_page = run_faces.base.companion_page


def companion_page_with_nia_test(name):
    html = _original_companion_page(name)
    if name != 'Nia':
        return html

    # Let the existing guest-chat route treat Nia as a test companion in the browser.
    html = html.replace(
        'N==="Simone"||N==="Chloe"',
        'N==="Simone"||N==="Chloe"||N==="Nia"'
    )

    # Extend Nia's guest test window to 24 hours instead of the normal 2-minute demo.
    html = html.replace(
        'function guestState(){let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}',
        'function guestState(){if(N==="Nia")return 86400;let x=Number(localStorage.getItem(G)||0);if(!x)return 120;return Math.max(0,120-Math.floor((Date.now()-x)/1000))}'
    )

    html = html.replace(' · 2-minute free demo', ' · OWNER TEST UNLOCKED')
    html = html.replace('Free demo starts with your first message.', 'Owner test mode · no charge')

    # Show all three Nia subscription choices directly on her page.
    plans = '''<div class="card" style="margin-top:18px"><h2>Choose Your Nia Plan</h2><p class="sub">Pick the option that works best for you.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-top:14px"><div class="plan"><h3>WHAT BOUT US™+</h3><div class="price" style="font-size:30px">$9.99 <small>/ month</small></div><a class="btn alt" href="/checkout?plan=plus">Choose $9.99</a></div><div class="plan hot"><h3>UNLIMITED</h3><div class="price" style="font-size:30px">$14.99 <small>/ month</small></div><a class="btn" href="/checkout?plan=unlimited">Choose $14.99</a></div><div class="plan"><h3>UNLIMITED YEARLY</h3><div class="price" style="font-size:30px">$149.99 <small>/ year</small></div><a class="btn alt" href="/checkout?plan=unlimited_yearly">Choose $149.99</a></div></div></div>'''
    marker = '<div class="fine">© 2026 What Bout Us'
    if marker in html:
        html = html.replace(marker, plans + marker, 1)
    else:
        html = html.replace('</main>', plans + '</main>', 1)
    return html


run_faces.base.companion_page = companion_page_with_nia_test


class NiaTestHandler(run_faces.FacesHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/checkout':
            plan = parse_qs(u.query).get('plan', ['plus'])[0]
            if plan == 'unlimited_yearly':
                target = os.environ.get('SQUARE_UNLIMITED_YEARLY_URL', '').strip()
                if target:
                    self.send_response(302)
                    self.send_header('Location', target)
                    self.end_headers()
                    return
        return super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', run_faces.base.PORT), NiaTestHandler).serve_forever()
