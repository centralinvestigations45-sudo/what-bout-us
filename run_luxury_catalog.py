from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import base64, os
import run_nia_test

run_faces=run_nia_test.run_faces
base=run_faces.base
rb=run_faces.run_brand
wallet=rb.wallet
pricing=rb.pricing

ASSETS={
 'shirts':os.environ.get('WBU_LUX_SHIRTS_B64',''),
 'dresses':os.environ.get('WBU_LUX_DRESSES_B64',''),
 'sneakers':os.environ.get('WBU_LUX_SNEAKERS_B64',''),
 'heels':os.environ.get('WBU_LUX_HEELS_B64',''),
 'exotic':os.environ.get('WBU_LUX_EXOTIC_B64',''),
 'accessories':os.environ.get('WBU_LUX_ACCESSORIES_B64','')
}
IMAGE_FOR_KEY={'classic-hoodie':'shirts','fitted-tshirt':'shirts','denim-jacket':'shirts','dark-denim-jeans':'shirts','business-blazer':'shirts','athletic-set':'shirts','premium-tailored-suit':'shirts','premium-mens-lounge':'shirts','cocktail-dress':'dresses','date-night-dress':'dresses','satin-lounge-set':'dresses','premium-evening-gown':'dresses','premium-silk-lingerie':'dresses','premium-leather-outfit':'dresses','high-top-sneakers':'sneakers','running-sneakers':'sneakers','classic-heels':'heels','premium-designer-heels':'heels','loafers':'exotic','ankle-boots':'exotic','work-boots':'exotic','premium-work-boots':'exotic','handbag':'accessories','premium-luxury-handbag':'accessories','fashion-earrings':'accessories','hoop-earrings':'accessories','classic-watch':'accessories','leather-watch':'accessories','pendant-necklace':'accessories','cuff-bracelet':'accessories','fashion-ring':'accessories','premium-diamond-bracelet':'accessories','premium-diamond-necklace':'accessories','premium-luxury-watch':'accessories','baseball-cap':'shirts','beanie':'shirts'}

NEW_CLOTHING=[('Luxury Cotton Dress Shirt','classic-hoodie',False,1400),('Premium Pima T-Shirt','fitted-tshirt',False,750),('Italian-Style Suede Jacket','denim-jacket',False,4200),('Premium Dark Denim','dark-denim-jeans',False,1800),('Tailored Executive Blazer','business-blazer',False,4200),('Silk Cocktail Dress','cocktail-dress',False,3500),('Luxury Date Night Dress','date-night-dress',False,4800),('Premium Athletic Set','athletic-set',False,2200),('Silk Lounge Set','satin-lounge-set',False,2600),('Couture Evening Gown','premium-evening-gown',True,15000),('Custom Tailored Suit','premium-tailored-suit',True,18000),('Luxury Leather Ensemble','premium-leather-outfit',True,14500),('Silk & Lace Lingerie Set','premium-silk-lingerie',True,12000),('Luxury Men’s Lounge Set','premium-mens-lounge',True,8500)]
NEW_SHOES=[('Luxury High-Top Sneakers','high-top-sneakers',False,3200),('Premium Leather Sneakers','running-sneakers',False,2800),('Luxury Red-Sole Style Heels','classic-heels',False,5200),('Premium Ankle Boots','ankle-boots',False,3600),('Heritage Leather Work Boots','work-boots',False,4200),('Exotic-Embossed Leather Loafers','loafers',False,6500),('Couture Red-Sole Style Heels','premium-designer-heels',True,11000),('Premium Handcrafted Boots','premium-work-boots',True,9500)]
NEW_ACCESSORIES=[('Luxury Drop Earrings','fashion-earrings',False,1800),('Premium Hoop Earrings','hoop-earrings',False,1600),('Executive Watch','classic-watch',False,4500),('Luxury Leather-Strap Watch','leather-watch',False,5200),('Fine Pendant Necklace','pendant-necklace',False,3200),('Luxury Cuff Bracelet','cuff-bracelet',False,2600),('Fine Fashion Ring','fashion-ring',False,2400),('Premium Baseball Cap','baseball-cap',False,900),('Luxury Knit Beanie','beanie',False,850),('Structured Leather Handbag','handbag',False,5200),('Luxury Leather Handbag','premium-luxury-handbag',True,14500),('Diamond-Style Tennis Bracelet','premium-diamond-bracelet',True,18000),('Diamond-Style Statement Necklace','premium-diamond-necklace',True,26000),('Prestige Luxury Watch','premium-luxury-watch',True,24000)]

pricing.CLOTHING[:]=[(a,b,c) for a,b,c,d in NEW_CLOTHING]
pricing.SHOES[:]=[(a,b,c) for a,b,c,d in NEW_SHOES]
pricing.ACCESSORIES[:]=[(a,b,c) for a,b,c,d in NEW_ACCESSORIES]
for label,key,premium,price in NEW_CLOTHING: wallet.ITEMS[key]=(label,'clothing',price,premium)
for label,key,premium,price in NEW_SHOES: wallet.ITEMS[key]=(label,'shoes',price,premium)
for label,key,premium,price in NEW_ACCESSORIES: wallet.ITEMS[key]=(label,'accessories',price,premium)

_raw_cards=getattr(rb,'_original_priced_cards',wallet.priced_cards)
def luxury_cards(items,category):
    html=_raw_cards(items,category)
    for label,key,premium in items:
        needle='<h3 style="margin:8px 0 4px">'+base.esc(label)+'</h3>'
        asset=IMAGE_FOR_KEY.get(key,'shirts')
        art=f'<div class="lux-product"><img src="/luxury-catalog/{asset}.jpg" alt="{base.esc(label)}"><div class="lux-tag">WHAT BOUT US™ LUXURY COLLECTION</div></div>'
        html=html.replace(needle,art+needle,1)
    return html
wallet.priced_cards=luxury_cards

_page=base.page
def luxury_page(title,body):
    html=_page(title,body)
    css='<style>.product-art{display:none!important}.lux-product{height:210px;border-radius:14px;overflow:hidden;margin:10px 0 12px;border:1px solid #47414b;background:#111;position:relative}.lux-product img{width:100%;height:100%;object-fit:cover;display:block}.lux-tag{position:absolute;left:10px;bottom:10px;background:rgba(8,8,12,.82);padding:6px 9px;border-radius:999px;font-size:9px;letter-spacing:1px;font-weight:800;color:#fff;border:1px solid rgba(255,255,255,.14)}@media(max-width:600px){.lux-product{height:185px}}</style>'
    return html.replace('</head>',css+'</head>',1)
base.page=luxury_page

_home=base.home
def luxury_home():
    html=_home()
    html=html.replace('Original, unbranded virtual fashion for your companion — no outside logos. Shop standard styles or premium looks using your virtual style wallet.','Photorealistic luxury fashion for your companion — premium shirts, tailored suits, dresses, sneakers, heels, exotic-style shoes, handbags, watches and jewelry. No outside logos.')
    return html
base.home=luxury_home

class Handler(run_nia_test.Handler):
    def do_GET(self):
        path=urlparse(self.path).path
        if path.startswith('/luxury-catalog/') and path.endswith('.jpg'):
            name=path.rsplit('/',1)[-1][:-4]; data=ASSETS.get(name)
            if not data: self.send_error(404); return
            raw=base64.b64decode(data)
            self.send_response(200); self.send_header('Content-Type','image/jpeg'); self.send_header('Cache-Control','public,max-age=86400'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        return super().do_GET()

if __name__=='__main__': ThreadingHTTPServer(('0.0.0.0',base.PORT),Handler).serve_forever()
