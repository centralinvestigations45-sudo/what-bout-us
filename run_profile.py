from http.server import ThreadingHTTPServer
import run_current

base = run_current.base

_original_companion_page = base.companion_page


def companion_page(name):
    html = _original_companion_page(name)
    if name == 'Simone':
        # Highlight Libra directly under Simone's name while keeping the existing page intact.
        html = html.replace(
            '<h1>Simone</h1>',
            '<h1 style="margin-bottom:4px">Simone</h1>'
            '<div style="font-family:Georgia,Times New Roman,serif;font-size:27px;font-style:italic;font-weight:700;letter-spacing:2px;margin:0 0 14px;background:linear-gradient(90deg,#63d7ff,#d45fff,#ff688e);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 0 18px rgba(212,95,255,.24)">⚖️ Libra</div>'
            '<div style="font-size:17px;font-weight:700;margin:0 0 8px">Career: Private Investigator</div>'
            '<div style="font-size:16px;color:#c9c9cf;margin:0 0 16px">Birthday: October 15</div>'
        )
    return html

base.companion_page = companion_page

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), run_current.ProductionHandler).serve_forever()
