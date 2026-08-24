from http.server import ThreadingHTTPServer
from urllib.parse import urlparse
import base64, os
import run_nia_test

run_faces=run_nia_test.run_faces
base=run_faces.base
rb=run_faces.run_brand
wallet=rb.wallet
pricing=rb.pricing

# Hard catalog rule: all product imagery is intended to be unbranded and logo-free.
# Do not use Nike, Adidas, Under Armour, or any other third-party brand marks.
PHOTO_FOR_KEY={
 'classic-hoodie':'https://images.unsplash.com/photo-1603252109303-2751441dd157?auto=format&fit=crop&w=1200&q=88',
 'fitted-tshirt':'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1200&q=88',
 'denim-jacket':'https://unsplash.com/photos/oPk4vwSlblE/download?force=true&w=1200',
 'luxe-womens-leather-jacket':'https://unsplash.com/photos/L3jG_PgakzE/download?force=true&w=1200',
 'collector-leather-jacket':'https://unsplash.com/photos/fFn7075mjDk/download?force=true&w=1200',
 'dark-denim-jeans':'https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=1200&q=88',
 'business-blazer':'https://images.unsplash.com/photo-1598808503746-f34c53b9323e?auto=format&fit=crop&w=1200&q=88',
 'athletic-set':'https://unsplash.com/photos/WoBaiwgXWZI/download?force=true&w=1200',
 'premium-tailored-suit':'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1200&q=88',
 'premium-mens-lounge':'https://unsplash.com/photos/2r5adxul49E/download?force=true&w=1200',
 'cocktail-dress':'https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=1200&q=88',
 'date-night-dress':'https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=1200&q=88',
 'satin-lounge-set':'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?auto=format&fit=crop&w=1200&q=88',
 'premium-evening-gown':'https://images.unsplash.com/photo-1562137369-1a1a0bc66744?auto=format&fit=crop&w=1200&q=88',
 'premium-silk-lingerie':'https://images.unsplash.com/photo-1604014237800-1c9102c219da?auto=format&fit=crop&w=1200&q=88',
 'premium-leather-outfit':'https://unsplash.com/photos/gSxa9fwxBs4/download?force=true&w=1200',
 'high-top-sneakers':'https://unsplash.com/photos/Ze9RHS62p6Y/download?force=true&w=1200',
 'running-sneakers':'https://unsplash.com/photos/p5C9ZTeDzko/download?force=true&w=1200',
 'classic-heels':'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=1200&q=88',
 'premium-designer-heels':'https://images.unsplash.com/photo-1562273138-f46be4ebdf33?auto=format&fit=crop&w=1200&q=88',
 'loafers':'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?auto=format&fit=crop&w=1200&q=88',
 'ankle-boots':'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=1200&q=88',
 'work-boots':'https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&w=1200&q=88',
 'premium-work-boots':'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?auto=format&fit=crop&w=1200&q=88',
 'fashion-earrings':'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=1200&q=88',
 'hoop-earrings':'https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=1200&q=88',
 'mens-executive-watch':'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=88',
 'womens-luxury-watch':'https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=1200&q=88',
 'leather-watch':'https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=1200&q=88',
 'pendant-necklace':'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=1200&q=88',
 'cuff-bracelet':'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?auto=format&fit=crop&w=1200&q=88',
 'fashion-ring':'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=1200&q=88',
 'handbag':'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=1200&q=88',
 'premium-luxury-handbag':'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?auto=format&fit=crop&w=1200&q=88',
 'premium-diamond-bracelet':'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?auto=format&fit=crop&w=1200&q=88',
 'premium-diamond-necklace':'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=1200&q=88',
 'premium-luxury-watch':'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&w=1200&q=88',
 'baseball-cap':'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?auto=format&fit=crop&w=1200&q=88',
 'beanie':'https://images.unsplash.com/photo-1575428652377-a2d80e2277fc?auto=format&fit=crop&w=1200&q=88'
}

NEW_CLOTHING=[
 ('Luxury Cotton Dress Shirt','classic-hoodie',False,650),
 ('Premium Pima T-Shirt','fitted-tshirt',False,350),
 ('Premium Leather Jacket','denim-jacket',False,3500),
 ('Women’s Luxe Leather Jacket','luxe-womens-leather-jacket',True,5200),
 ('Collector Leather Jacket','collector-leather-jacket',True,7500),
 ('Premium Dark Denim Jeans','dark-denim-jeans',False,900),
 ('Tailored Executive Blazer','business-blazer',False,1600),
 ('Silk Cocktail Dress','cocktail-dress',False,1400),
 ('Luxury Date Night Dress','date-night-dress',False,1800),
 ('Premium Athletic Set','athletic-set',False,950),
 ('Silk Lounge Set','satin-lounge-set',False,1100),
 ('Couture Evening Gown','premium-evening-gown',True,6500),
 ('Custom Tailored Suit','premium-tailored-suit',True,7500),
 ('Luxury Leather Ensemble','premium-leather-outfit',True,9500),
 ('Silk & Lace Lingerie Set','premium-silk-lingerie',True,4200),
 ('Luxury Men’s Lounge Set','premium-mens-lounge',True,3200)
]
NEW_SHOES=[
 ('Luxury High-Top Sneakers','high-top-sneakers',False,1200),
 ('Premium Leather Sneakers','running-sneakers',False,1100),
 ('Luxury Evening Heels','classic-heels',False,1800),
 ('Premium Ankle Boots','ankle-boots',False,1400),
 ('Heritage Leather Work Boots','work-boots',False,1600),
 ('Exotic-Embossed Leather Loafers','loafers',False,2200),
 ('Couture Statement Heels','premium-designer-heels',True,4800),
 ('Premium Handcrafted Boots','premium-work-boots',True,4200)
]
NEW_ACCESSORIES=[
 ('Luxury Drop Earrings','fashion-earrings',False,700),
 ('Premium Hoop Earrings','hoop-earrings',False,650),
 ('Men’s Executive Watch','mens-executive-watch',False,1800),
 ('Women’s Luxury Watch','womens-luxury-watch',False,2200),
 ('Luxury Leather-Strap Watch','leather-watch',False,2100),
 ('Fine Pendant Necklace','pendant-necklace',False,1200),
 ('Luxury Cuff Bracelet','cuff-bracelet',False,950),
 ('Fine Fashion Ring','fashion-ring',False,900),
 ('Premium Baseball Cap','baseball-cap',False,450),
 ('Luxury Knit Beanie','beanie',False,400),
 ('Structured Leather Handbag','handbag',False,1900),
 ('Luxury Leather Handbag','premium-luxury-handbag',True,5200),
 ('Diamond-Style Tennis Bracelet','premium-diamond-bracelet',True,6500),
 ('Diamond-Style Statement Necklace','premium-diamond-necklace',True,8500),
 ('Prestige Luxury Watch','premium-luxury-watch',True,7500)
]

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
        src=PHOTO_FOR_KEY.get(key)
        if src:
            art=f'<div class="lux-product"><img src="{src}" alt="Photorealistic unbranded {base.esc(label)}"><div class="lux-tag">WHAT BOUT US™ LUXURY COLLECTION</div></div>'
            html=html.replace(needle,art+needle,1)
    return html
wallet.priced_cards=luxury_cards

_page=base.page
def luxury_page(title,body):
    html=_page(title,body)
    css='<style>.product-art{display:none!important}.product-icon{display:none!important}.lux-product{height:230px;border-radius:14px;overflow:hidden;margin:10px 0 12px;border:1px solid #47414b;background:#111;position:relative}.lux-product img{width:100%;height:100%;object-fit:cover;display:block}.lux-tag{position:absolute;left:10px;bottom:10px;background:rgba(8,8,12,.82);padding:6px 9px;border-radius:999px;font-size:9px;letter-spacing:1px;font-weight:800;color:#fff;border:1px solid rgba(255,255,255,.14)}@media(max-width:600px){.lux-product{height:200px}}</style>'
    return html.replace('</head>',css+'</head>',1)
base.page=luxury_page

_home=base.home
def luxury_home():
    html=_home()
    html=html.replace('Original, unbranded virtual fashion for your companion — no outside logos. Shop standard styles or premium looks using your virtual style wallet.','Luxury virtual fashion for your companion — premium shirts, tailored suits, dresses, leather, sneakers, heels, handbags, men’s and women’s watches, and jewelry. No third-party brand logos.')
    return html
base.home=luxury_home

class Handler(run_nia_test.Handler):
    def do_GET(self):
        return super().do_GET()

if __name__=='__main__':
    ThreadingHTTPServer(('0.0.0.0',base.PORT),Handler).serve_forever()
