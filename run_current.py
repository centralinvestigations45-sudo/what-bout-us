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

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), app_v2.H).serve_forever()
