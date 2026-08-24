from http.server import ThreadingHTTPServer
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
    return html


run_faces.base.companion_page = companion_page_with_nia_test

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', run_faces.base.PORT), run_faces.FacesHandler).serve_forever()
