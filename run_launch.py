from http.server import ThreadingHTTPServer
import run_profile

base = run_profile.base

# Final homepage ordering: swap Simone with Alex and Chloe with Lily.
base.MEN = ['Simone','Damien','Logan','Jay','Kai','Mason','Ethan','Luca','Darius','Noah','Jack','Julius','Leo','Carter','Malik','Alex']
base.WOMEN = ['Chloe','Aria','Mika','Zoey','Nova','Sophia','Isabella','Lily','Ember','Hana','Riley','Vivien','Bella','Sahara','Skye','Nia']
base.ALL = base.MEN + base.WOMEN

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), run_profile.run_current.ProductionHandler).serve_forever()
