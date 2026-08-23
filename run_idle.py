import json
from http.server import ThreadingHTTPServer
import run_analytics

base = run_analytics.base
_original_companion_page = base.companion_page

IDLE_PROMPTS = [
    "Hey, you still there?",
    "I'm still here if you want to keep talking.",
    "Just checking in one more time — I'm here when you're ready.",
]


def idle_companion_page(name):
    html = _original_companion_page(name)
    prompts = json.dumps(IDLE_PROMPTS)
    script = f'''<script>
(function(){{
  const companion={json.dumps(name)};
  const prompts={prompts};
  let followups=0;
  let timer=null;
  let lastUserActivity=Date.now();

  function historyEl(){{return document.getElementById('history')}}
  function inputEl(){{return document.getElementById('message')}}
  function sendEl(){{return document.getElementById('send')}}
  function delay(){{return 30000 + Math.floor(Math.random()*10001)}}
  function canPrompt(){{
    const i=inputEl();
    return i && !i.disabled && document.visibilityState==='visible';
  }}
  function bubble(text){{
    const h=historyEl();
    if(!h)return;
    const d=document.createElement('div');
    d.className='bubble';
    d.textContent=companion+': '+text;
    h.appendChild(d);
    try{{d.scrollIntoView({{behavior:'smooth',block:'end'}})}}catch(e){{}}
  }}
  function schedule(){{
    if(timer)clearTimeout(timer);
    if(followups>=3)return;
    timer=setTimeout(()=>{{
      if(!canPrompt()){{schedule();return}}
      if(Date.now()-lastUserActivity < 29000){{schedule();return}}
      bubble(prompts[followups]);
      followups++;
      if(followups<3)schedule();
    }},delay());
  }}
  function userActive(){{
    lastUserActivity=Date.now();
    followups=0;
    schedule();
  }}

  document.addEventListener('input',e=>{{if(e.target&&e.target.id==='message')userActive()}});
  document.addEventListener('keydown',e=>{{if(e.target&&e.target.id==='message')userActive()}});
  document.addEventListener('click',e=>{{
    const b=sendEl();
    if(b && (e.target===b || b.contains(e.target)))userActive();
  }});
  document.addEventListener('visibilitychange',()=>{{if(document.visibilityState==='visible'){{lastUserActivity=Date.now();schedule()}}}});
  setTimeout(schedule,1500);
}})();
</script>'''
    return html.replace('</body>', script + '</body>')


base.companion_page = idle_companion_page


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), run_analytics.AnalyticsHandler).serve_forever()
