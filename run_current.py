import os
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer
import run_nice

app_v2 = run_nice.app_v2
base = app_v2.base

# Final 16-men roster: Malik replaces Tyler; Darius and Julius remain locked in.
base.MEN = ['Alex','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Darius','Noah','Jack','Julius','Leo','Carter','Malik','Simone']
base.ALL = base.MEN + base.WOMEN

# Keep height data aligned with the live roster.
app_v2.HEIGHTS.pop('Tyler', None)
app_v2.HEIGHTS['Malik'] = "6'3\""

# Keep distinct companion traits for the newly locked roster members.
base.TRAITS.update({
    'Darius':'thoughtful, loyal, calm, mature, dependable and a great listener',
    'Julius':'distinguished, wise, confident, patient, thoughtful and dependable',
    'Malik':'confident, warm, energetic, ambitious, funny, loyal and supportive',
    'Chloe':'compassionate, positive, loyal, down-to-earth and a great listener',
    'Isabella':'warm, kind, honest, loyal and deeply interested in meaningful conversation',
    'Nia':'confident, caring, intelligent, supportive and easy to talk to'
})

# Approved permanent portraits saved in the production repository.
APPROVED = {'Simone','Darius','Julius','Malik','Chloe','Isabella','Nia'}
_original_portrait = base.portrait
def production_portrait(name):
    if name in APPROVED:
        return '/static/' + name.lower() + '.jpg'
    return _original_portrait(name)
base.portrait = production_portrait

class ProductionHandler(app_v2.H):
    def do_GET(self):
        p = urlparse(self.path).path
        if p.startswith('/static/') and p.endswith('.jpg'):
            filename = os.path.basename(p)
            name = filename[:-4].capitalize()
            if name in APPROVED:
                try:
                    data = open(os.path.join(os.path.dirname(__file__), 'static', filename), 'rb').read()
                    self.send_response(200)
                    self.send_header('Content-Type','image/jpeg')
                    self.send_header('Cache-Control','public, max-age=3600')
                    self.send_header('Content-Length',str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except OSError:
                    self.send_error(404)
                    return
        return super().do_GET()

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), ProductionHandler).serve_forever()
