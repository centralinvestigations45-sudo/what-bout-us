import json
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer
import run_launch

base = run_launch.base
app_v2 = run_launch._app_v2
_original_companion_page = base.companion_page


def tracked_companion_page(name):
    html = _original_companion_page(name)
    tracker = f'''<script>
(function(){{
  const companion={json.dumps(name)};
  const key='wbu_analytics_session_'+companion;
  let sid=sessionStorage.getItem(key);
  if(!sid){{sid=(crypto.randomUUID?crypto.randomUUID():('xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{{const r=Math.random()*16|0,v=c==='x'?r:(r&3|8);return v.toString(16)}})));sessionStorage.setItem(key,sid)}}
  const started=Date.now();
  function authHeaders(){{const t=localStorage.getItem('wbu_access_token');return t?{{'Authorization':'Bearer '+t}}:{{}}}}
  function send(event,beacon){{
    const payload=JSON.stringify({{session_id:sid,companion:companion,event:event,duration_seconds:Math.max(0,Math.floor((Date.now()-started)/1000))}});
    if(beacon && navigator.sendBeacon){{try{{navigator.sendBeacon('/api/analytics',payload);return}}catch(e){{}}}}
    fetch('/api/analytics',{{method:'POST',headers:{{'Content-Type':'application/json',...authHeaders()}},body:payload,keepalive:true}}).catch(()=>{{}});
  }}
  send('open',false);
  const beat=setInterval(()=>send('heartbeat',false),15000);
  document.addEventListener('click',e=>{{const a=e.target.closest&&e.target.closest('a[href^="/checkout"]');if(a)send('checkout',false)}});
  document.addEventListener('visibilitychange',()=>{{if(document.hidden)send('heartbeat',true)}});
  window.addEventListener('pagehide',()=>{{clearInterval(beat);send('close',true)}});
}})();
</script>'''
    return html.replace('</body>', tracker + '</body>')


base.companion_page = tracked_companion_page


class AnalyticsHandler(run_launch.LaunchHandler):
    def _analytics_json(self):
        n = int(self.headers.get('Content-Length', '0') or 0)
        try:
            return json.loads(self.rfile.read(n).decode() or '{}')
        except Exception:
            return {}

    def do_POST(self):
        if urlparse(self.path).path != '/api/analytics':
            return super().do_POST()

        data = self._analytics_json()
        name = str(data.get('companion', '')).strip()
        event = str(data.get('event', '')).strip().lower()
        try:
            sid = str(uuid.UUID(str(data.get('session_id', ''))))
        except Exception:
            return self.sj({'error': 'invalid analytics session'}, 400)
        if name not in base.ALL or event not in ('open', 'heartbeat', 'close', 'checkout'):
            return self.sj({'error': 'invalid analytics event'}, 400)
        try:
            duration = max(0, min(int(data.get('duration_seconds', 0) or 0), 43200))
        except Exception:
            duration = 0

        token = app_v2.tok(self.headers)
        account = app_v2.user(token) if token else None
        uid = account.get('id') if isinstance(account, dict) else None
        now = datetime.now(timezone.utc).isoformat()

        if event == 'open':
            body = {
                'session_id': sid,
                'companion_name': name,
                'opened_at': now,
                'last_seen_at': now,
                'duration_seconds': duration,
                'updated_at': now,
            }
            if uid:
                body['user_id'] = uid
            app_v2.sb('/rest/v1/companion_analytics?on_conflict=session_id', method='POST', token=token or None, body=body, prefer='resolution=merge-duplicates,return=minimal')
        else:
            patch = {'last_seen_at': now, 'duration_seconds': duration, 'updated_at': now}
            if uid:
                patch['user_id'] = uid
            if event == 'checkout':
                patch['checkout_clicked_at'] = now
            app_v2.sb('/rest/v1/companion_analytics?session_id=eq.' + app_v2.q(sid), method='PATCH', token=token or None, body=patch, prefer='return=minimal')

        return self.sj({'ok': True})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), AnalyticsHandler).serve_forever()
