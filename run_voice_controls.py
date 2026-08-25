from http.server import ThreadingHTTPServer
import json
import run_chloe_voice_split as split

base = split.base
_original_companion_page = base.companion_page


def companion_page_with_voice_toggle(name):
    html = _original_companion_page(name)
    if 'id="wbu-voice-enabled"' in html:
        return html

    control = f'''<div class="card" style="margin-top:18px"><label style="display:flex;gap:12px;align-items:center;cursor:pointer"><input id="wbu-voice-enabled" type="checkbox" checked style="width:22px;height:22px;flex:0 0 auto"><span><strong>Speak replies aloud</strong><br><span class="sub">Turn this off any time you want text-only conversation with {name}.</span></span></label></div>'''

    footer_marker = '<div class="fine">© 2026 What Bout Us'
    if footer_marker in html:
        html = html.replace(footer_marker, control + footer_marker, 1)
    else:
        html = html.replace('</main>', control + '</main>', 1)

    script = r'''<script>
(function(){
  const NAME = window.NAME || (typeof window.NAME !== 'undefined' ? window.NAME : null);
  function box(){ return document.getElementById('wbu-voice-enabled'); }
  function key(){
    const n = (typeof window.NAME !== 'undefined' && window.NAME) ? window.NAME : document.querySelector('h1')?.textContent || 'companion';
    return 'wbu_voice_enabled_' + String(n).toLowerCase();
  }
  window.wbuVoiceEnabled = function(){ const b=box(); return !b || b.checked; };
  document.addEventListener('DOMContentLoaded', function(){
    const b=box(); if(!b)return;
    const saved=localStorage.getItem(key());
    b.checked = saved === null ? true : saved === '1';
    b.addEventListener('change', function(){
      localStorage.setItem(key(), b.checked ? '1' : '0');
      if(!b.checked){ try{ speechSynthesis.cancel(); }catch(e){} }
    });
  });

  if(window.speechSynthesis && typeof window.speechSynthesis.speak === 'function'){
    const originalSpeak = window.speechSynthesis.speak.bind(window.speechSynthesis);
    window.speechSynthesis.speak = function(utterance){
      if(window.wbuVoiceEnabled()) return originalSpeak(utterance);
    };
  }

  const wrapFunction = function(fnName){
    const fn = window[fnName];
    if(typeof fn !== 'function') return;
    window[fnName] = function(){
      if(!window.wbuVoiceEnabled()) return;
      return fn.apply(this, arguments);
    };
  };
  wrapFunction('say');
  wrapFunction('chloeSay');
})();
</script>'''
    html = html.replace('</body>', script + '</body>', 1)
    return html


base.companion_page = companion_page_with_voice_toggle


class Handler(split.Handler):
    pass


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), Handler).serve_forever()
