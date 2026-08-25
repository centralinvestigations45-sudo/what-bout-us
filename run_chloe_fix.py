from http.server import ThreadingHTTPServer
import run_signup_fix as signup

base = signup.base
_original_companion_page = base.companion_page


def companion_page_fresh_trial(name):
    html = _original_companion_page(name)
    # Version the browser-side guest trial key so stale pre-fix timers cannot
    # immediately lock Chloe (or any other newly-free companion) after deploy.
    html = html.replace('G="wbu_guest_trial_"+N', 'G="wbu_guest_trial_20260825b_"+N')
    return html


base.companion_page = companion_page_fresh_trial

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), signup.Handler).serve_forever()
