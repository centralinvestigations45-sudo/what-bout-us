from http.server import ThreadingHTTPServer
from difflib import SequenceMatcher
import run_signup_fix as signup

base = signup.base
app_v2 = signup.app_v2
_original_companion_page = base.companion_page
_original_reply = app_v2.reply


def _norm(text):
    return ' '.join(str(text or '').lower().split())


def chloe_reply(name, msg, hist, mem):
    candidate = _original_reply(name, msg, hist, mem)
    if name != 'Chloe':
        return candidate

    previous = ''
    for item in reversed(hist or []):
        if item.get('role') == 'assistant' and item.get('content'):
            previous = item.get('content')
            break

    if previous:
        similarity = SequenceMatcher(None, _norm(previous), _norm(candidate)).ratio()
        if similarity >= 0.72:
            candidate = _original_reply(
                name,
                msg + '\n\nUse fresh wording and add a new thought. Do not repeat or closely paraphrase the previous reply.',
                hist,
                list(mem or []) + ['Chloe varies her wording, avoids repeated openings, and moves the conversation forward naturally.']
            )
    return candidate


app_v2.reply = chloe_reply


def companion_page_fresh_trial(name):
    html = _original_companion_page(name)
    html = html.replace('G="wbu_guest_trial_"+N', 'G="wbu_guest_trial_20260825c_"+N')

    if name == 'Chloe':
        # Remove browser speech synthesis for Chloe so the robotic device voice
        # cannot override the approved external voice setup.
        start = html.find("<div class=\"card\" style=\"margin-top:18px\"><h2>Chloe Voice</h2>")
        if start != -1:
            end = html.find("<div class=\"fine\">© 2026 What Bout Us", start)
            if end != -1:
                html = html[:start] + html[end:]
        html = html.replace("if(N===\"Simone\")say(d.reply);try{let u=new SpeechSynthesisUtterance(d.reply)", "if(N===\"Simone\")say(d.reply);if(N===\"Chloe\"){}else try{let u=new SpeechSynthesisUtterance(d.reply)")
        html = html.replace("if(N===\"Simone\")say(d.reply);if(N===\"Nia\")", "if(N===\"Simone\")say(d.reply);if(N===\"Chloe\"){}else if(N===\"Nia\")")
    return html


base.companion_page = companion_page_fresh_trial

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), signup.Handler).serve_forever()
