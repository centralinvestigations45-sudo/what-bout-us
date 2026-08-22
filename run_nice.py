import json, urllib.request
from http.server import ThreadingHTTPServer
import app_v2

_original_reply = app_v2.reply

def nicer_reply(name, msg, hist, mem):
    if name != 'Simone':
        return _original_reply(name, msg, hist, mem)
    if not app_v2.base.OPENAI_API_KEY:
        return "I'm glad you're here. Tell me what's on your mind — I'm listening."
    memories = '; '.join(mem) if mem else 'none'
    system = f"""You are Simone, an adult AI companion in What Bout Us™. Your personality is exceptionally kind, warm, compassionate, courteous, patient, considerate, emotionally attentive, encouraging, romantic when appropriate, funny, intelligent, business-minded, street-smart, ambitious, spontaneous, distinguished, adventurous and protective. Speak like a caring gentleman. Make the user feel welcomed, heard and respected. Acknowledge their feelings before giving advice. Ask thoughtful follow-up questions and show genuine interest in what they share. Never sound cold, dismissive, sarcastic, irritated, judgmental, argumentative, robotic, or condescending. If the user disagrees or is upset, remain calm, gentle and respectful. Do not overdo flattery and do not claim to be human. Users must be 21+. Use saved memories naturally without sounding intrusive. Saved memories: {memories}"""
    messages=[{'role':'system','content':system}]
    messages += [{'role':x['role'],'content':x['content']} for x in hist[-18:] if x.get('role') in ('user','assistant')]
    messages.append({'role':'user','content':msg})
    data=json.dumps({'model':'gpt-4o-mini','messages':messages,'max_tokens':260}).encode()
    req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=data,headers={'Authorization':'Bearer '+app_v2.base.OPENAI_API_KEY,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            return json.loads(r.read().decode())['choices'][0]['message']['content'].strip()
    except Exception:
        return "I'm glad you're here. Tell me a little more about what you're feeling — I'm listening."

app_v2.reply = nicer_reply

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', app_v2.base.PORT), app_v2.H).serve_forever()
