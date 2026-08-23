from http.server import ThreadingHTTPServer
import run_current

base = run_current.base

_original_companion_page = base.companion_page

PROFILES = {
    'Alex': (30, 'Aries'),
    'Damien': (36, 'Scorpio'),
    'Logan': (29, 'Sagittarius'),
    'Jay': (27, 'Gemini'),
    'Kai': (31, 'Aquarius'),
    'Mason': (35, 'Taurus'),
    'Ethan': (32, 'Virgo'),
    'Luca': (28, 'Leo'),
    'Darius': (38, 'Capricorn'),
    'Noah': (26, 'Pisces'),
    'Jack': (34, 'Cancer'),
    'Julius': (41, 'Aquarius'),
    'Leo': (30, 'Leo'),
    'Carter': (33, 'Aries'),
    'Malik': (29, 'Libra'),
    'Simone': (33, 'Libra'),
    'Lily': (27, 'Pisces'),
    'Aria': (31, 'Taurus'),
    'Mika': (25, 'Gemini'),
    'Zoey': (29, 'Sagittarius'),
    'Nova': (32, 'Aquarius'),
    'Sophia': (34, 'Virgo'),
    'Isabella': (30, 'Cancer'),
    'Chloe': (28, 'Leo'),
    'Ember': (33, 'Scorpio'),
    'Hana': (26, 'Libra'),
    'Riley': (31, 'Aries'),
    'Vivien': (37, 'Libra'),
    'Bella': (24, 'Pisces'),
    'Sahara': (35, 'Sagittarius'),
    'Skye': (28, 'Aquarius'),
    'Nia': (32, 'Libra'),
}

# Numeric HTML entities + text-presentation selector prevent iPhone from
# replacing zodiac glyphs with unsupported/color emoji boxes.
ZODIAC_SYMBOLS = {
    'Aries': '&#9800;&#xfe0e;',
    'Taurus': '&#9801;&#xfe0e;',
    'Gemini': '&#9802;&#xfe0e;',
    'Cancer': '&#9803;&#xfe0e;',
    'Leo': '&#9804;&#xfe0e;',
    'Virgo': '&#9805;&#xfe0e;',
    'Libra': '&#9806;&#xfe0e;',
    'Scorpio': '&#9807;&#xfe0e;',
    'Sagittarius': '&#9808;&#xfe0e;',
    'Capricorn': '&#9809;&#xfe0e;',
    'Aquarius': '&#9810;&#xfe0e;',
    'Pisces': '&#9811;&#xfe0e;',
}

BIRTHDAYS = {
    'Alex': 'April 2',
    'Damien': 'November 8',
    'Logan': 'December 3',
    'Jay': 'June 4',
    'Kai': 'February 6',
    'Mason': 'May 12',
    'Ethan': 'September 3',
    'Luca': 'August 14',
    'Darius': 'January 7',
    'Noah': 'March 12',
    'Jack': 'July 7',
    'Julius': 'February 14',
    'Leo': 'August 3',
    'Carter': 'April 10',
    'Malik': 'September 30',
    'Simone': 'October 15',
    'Lily': 'March 5',
    'Aria': 'May 7',
    'Mika': 'June 10',
    'Zoey': 'December 8',
    'Nova': 'February 10',
    'Sophia': 'September 9',
    'Isabella': 'July 12',
    'Chloe': 'August 6',
    'Ember': 'October 23',
    'Hana': 'October 6',
    'Riley': 'April 16',
    'Vivien': 'October 13',
    'Bella': 'March 1',
    'Sahara': 'December 15',
    'Skye': 'February 1',
    'Nia': 'October 16',
}

SIGN_NAME_STYLE = 'font-family:Georgia,Times New Roman,serif;font-size:27px;font-style:italic;font-weight:700;letter-spacing:2px;background:linear-gradient(90deg,#63d7ff,#d45fff,#ff688e);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 0 18px rgba(212,95,255,.24);vertical-align:middle'
SYMBOL_STYLE = 'font-family:Apple Symbols,Segoe UI Symbol,Noto Sans Symbols 2,Arial Unicode MS,sans-serif;font-size:30px;font-style:normal;font-weight:700;color:#8fd2ff;margin-right:10px;vertical-align:middle;line-height:1'


def zodiac_line(name, sign):
    # Simone keeps the requested scales icon; everyone else gets their proper zodiac glyph.
    symbol = '&#9878;&#xfe0e;' if name == 'Simone' else ZODIAC_SYMBOLS[sign]
    return (
        '<div style="margin:0 0 10px;display:flex;align-items:center">'
        f'<span aria-hidden="true" style="{SYMBOL_STYLE}">{symbol}</span>'
        f'<span style="{SIGN_NAME_STYLE}">{sign}</span>'
        '</div>'
    )


def companion_page(name):
    html = _original_companion_page(name)
    profile = PROFILES.get(name)
    if not profile:
        return html

    age, sign = profile
    details = (
        f'<h1 style="margin-bottom:4px">{name}</h1>'
        f'{zodiac_line(name, sign)}'
        f'<div style="font-size:17px;font-weight:700;margin:0 0 12px">Age: {age}</div>'
    )

    if name == 'Simone':
        details += '<div style="font-size:17px;font-weight:700;margin:0 0 8px">Career: Private Investigator</div>'

    birthday = BIRTHDAYS.get(name)
    if birthday:
        details += f'<div style="font-size:16px;color:#c9c9cf;margin:0 0 16px">Birthday: {birthday}</div>'

    html = html.replace(f'<h1>{name}</h1>', details)
    return html


base.companion_page = companion_page

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', base.PORT), run_current.ProductionHandler).serve_forever()
