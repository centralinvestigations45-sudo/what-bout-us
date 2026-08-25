from http.server import ThreadingHTTPServer
import json
import run_voice_controls as vc

if __name__ == '__main__':
    try:
        print('WBU_VOICE_ROSTER ' + json.dumps(vc._voice_roster(), separators=(',', ':')), flush=True)
    except Exception as e:
        print('WBU_VOICE_ROSTER_ERROR ' + repr(e), flush=True)
    ThreadingHTTPServer(('0.0.0.0', vc.base.PORT), vc.Handler).serve_forever()
