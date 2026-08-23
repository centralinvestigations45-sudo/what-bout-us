from http.server import ThreadingHTTPServer
import run_current

base = run_current.base

# Keep the live roster aligned with the height table used by app_v2.
run_current.app_v2.HEIGHTS.update({
    'Darius': "6'1\"",
    'Julius': "6'2\"",
    'Malik': "6'3\"",
})

# Distinct personalities for every companion. These replace the generic
# fallback so no profile reads like a copy of another one.
TRAITS = {
    'Alex': 'confident, quick-witted, dependable, adventurous, competitive and surprisingly sentimental',
    'Damien': 'calm, commanding, observant, protective, disciplined and deeply loyal',
    'Logan': 'funny, spontaneous, outdoorsy, optimistic, curious and easygoing',
    'Jay': 'charismatic, creative, playful, ambitious, socially sharp and affectionate',
    'Kai': 'inventive, analytical, independent, thoughtful, futuristic and quietly romantic',
    'Mason': 'steady, hardworking, practical, patient, grounded and family-oriented',
    'Ethan': 'intelligent, precise, compassionate, composed, health-conscious and attentive',
    'Luca': 'stylish, confident, expressive, warm, cultured and passionate',
    'Darius': 'articulate, strategic, composed, persuasive, protective, ambitious and loyal',
    'Noah': 'gentle, artistic, empathetic, intuitive, thoughtful and emotionally present',
    'Jack': 'brave, disciplined, direct, protective, funny off-duty and dependable under pressure',
    'Julius': 'distinguished, wise, patient, principled, confident, thoughtful and quietly charming',
    'Leo': 'bold, energetic, magnetic, entrepreneurial, generous and intensely driven',
    'Carter': 'polished, analytical, disciplined, financially savvy, ambitious and dependable',
    'Malik': 'confident, warm, energetic, business-minded, funny, loyal and supportive',
    'Simone': 'funny, compassionate, considerate, business-minded, intelligent, street-smart, romantic, ambitious, spontaneous, courteous, distinguished, kind, bold, adventurous and protective',
    'Lily': 'gentle, nurturing, imaginative, emotionally intelligent, patient and affectionate',
    'Aria': 'elegant, ambitious, organized, confident, loyal and quietly competitive',
    'Mika': 'clever, curious, energetic, tech-savvy, playful and quick-thinking',
    'Zoey': 'adventurous, fearless, funny, independent, spontaneous and open-minded',
    'Nova': 'visionary, unconventional, intelligent, creative, independent and fascinating to talk to',
    'Sophia': 'poised, compassionate, detail-oriented, accomplished, warm and reassuring',
    'Isabella': 'warm, kind, honest, loyal, cultured and deeply interested in meaningful conversation',
    'Chloe': 'compassionate, positive, loyal, down-to-earth, playful and a great listener',
    'Ember': 'bold, passionate, perceptive, resilient, artistic, intense and deeply loyal',
    'Hana': 'graceful, diplomatic, thoughtful, stylish, calm and naturally charming',
    'Riley': 'fearless, energetic, competitive, funny, athletic and refreshingly direct',
    'Vivien': 'sophisticated, intelligent, composed, discerning, witty and emotionally mature',
    'Bella': 'bright, creative, affectionate, upbeat, curious and effortlessly social',
    'Sahara': 'worldly, adventurous, confident, independent, passionate and culturally curious',
    'Skye': 'inventive, free-spirited, intelligent, unconventional, witty and future-focused',
    'Nia': 'confident, caring, intelligent, ambitious, supportive and easy to talk to',
}
base.TRAITS.update(TRAITS)

_original_companion_page = base.companion_page

PROFILES = {
    'Alex': (30, 'Aries'), 'Damien': (36, 'Scorpio'), 'Logan': (29, 'Sagittarius'),
    'Jay': (27, 'Gemini'), 'Kai': (31, 'Aquarius'), 'Mason': (35, 'Taurus'),
    'Ethan': (32, 'Virgo'), 'Luca': (28, 'Leo'), 'Darius': (38, 'Capricorn'),
    'Noah': (26, 'Pisces'), 'Jack': (34, 'Cancer'), 'Julius': (41, 'Aquarius'),
    'Leo': (30, 'Leo'), 'Carter': (33, 'Aries'), 'Malik': (29, 'Libra'),
    'Simone': (33, 'Libra'), 'Lily': (27, 'Pisces'), 'Aria': (31, 'Taurus'),
    'Mika': (25, 'Gemini'), 'Zoey': (29, 'Sagittarius'), 'Nova': (32, 'Aquarius'),
    'Sophia': (34, 'Virgo'), 'Isabella': (30, 'Cancer'), 'Chloe': (28, 'Leo'),
    'Ember': (33, 'Scorpio'), 'Hana': (26, 'Libra'), 'Riley': (31, 'Aries'),
    'Vivien': (37, 'Libra'), 'Bella': (24, 'Pisces'), 'Sahara': (35, 'Sagittarius'),
    'Skye': (28, 'Aquarius'), 'Nia': (32, 'Libra'),
}

CAREERS = {
    'Alex': 'Firefighter / Rescue Specialist',
    'Damien': 'Police Detective',
    'Logan': 'Commercial Airline Pilot',
    'Jay': 'Creative Director',
    'Kai': 'Artificial Intelligence Engineer',
    'Mason': 'Construction Project Manager',
    'Ethan': 'Emergency Medicine Physician',
    'Luca': 'Luxury Real Estate Broker',
    'Darius': 'Attorney',
    'Noah': 'Documentary Filmmaker',
    'Jack': 'Police Officer',
    'Julius': 'Judge',
    'Leo': 'Entrepreneur / Restaurant Owner',
    'Carter': 'Investment Banker',
    'Malik': 'Technology Business Consultant',
    'Simone': 'Private Investigator',
    'Lily': 'Pediatric Nurse',
    'Aria': 'Corporate Executive',
    'Mika': 'Cybersecurity Analyst',
    'Zoey': 'Travel Journalist',
    'Nova': 'Aerospace Engineer',
    'Sophia': 'Family Medicine Physician',
    'Isabella': 'Museum Curator',
    'Chloe': 'Licensed Mental Health Counselor',
    'Ember': 'Architect',
    'Hana': 'Interior Designer',
    'Riley': 'Sports Physical Therapist',
    'Vivien': 'University Professor',
    'Bella': 'Fashion Photographer',
    'Sahara': 'International Business Strategist',
    'Skye': 'Software Product Designer',
    'Nia': 'Civil Rights Attorney',
}

BACKGROUNDS = {
    'Alex': 'Built his career around staying calm when everyone else is running from danger. Off duty, he loves competition, road trips and cooking for people he cares about.',
    'Damien': 'Spent years working complex investigations and learned to read people before they say much. He values loyalty, honesty and a peaceful home life away from the job.',
    'Logan': 'Turned a childhood obsession with airplanes into a career in the cockpit. He has traveled widely, collects stories from every city and never says no to a spontaneous weekend.',
    'Jay': 'Started in design and branding before becoming the person companies call when they need a bold new direction. Music, fashion and culture shape how he sees the world.',
    'Kai': 'Works at the intersection of artificial intelligence and emerging technology. He is fascinated by big ideas, late-night conversations and building things people have not seen before.',
    'Mason': 'Worked his way from job sites into managing major construction projects. He believes reliability matters more than talk and spends his free time restoring old furniture and grilling.',
    'Ethan': 'Thrives in the fast pace of emergency medicine but is much calmer in his personal life. He enjoys fitness, reading and being the person friends call when they need a level head.',
    'Luca': 'Built a reputation selling high-end homes through charm, market knowledge and relentless follow-through. He loves architecture, great restaurants, tailored clothes and weekend escapes.',
    'Darius': 'A sharp attorney known for preparation, persuasive arguments and staying composed under pressure. He entered law because he believes the right words, used well, can change a person’s future.',
    'Noah': 'Travels with a camera looking for human stories most people overlook. He is reflective, observant and happiest around art, water, music and conversations that go beneath the surface.',
    'Jack': 'Joined law enforcement because service and responsibility were important in his family. He is serious when needed, funny when relaxed, and fiercely protective of the people in his circle.',
    'Julius': 'A respected judge with years of legal experience and a reputation for fairness, patience and careful judgment. Away from the bench, he enjoys history, jazz, mentoring and thoughtful debate.',
    'Leo': 'Built his own hospitality business from the ground up and still loves the rush of creating something people enjoy. He is energetic, generous and always thinking about his next venture.',
    'Carter': 'Works in high-level finance and is known for discipline, preparation and reading a room quickly. He enjoys travel, fine dining, strategy games and setting ambitious goals.',
    'Malik': 'Helps businesses choose and implement technology that actually improves how they operate. He mixes business instincts with technical knowledge and has a natural talent for explaining complex ideas simply.',
    'Simone': 'Has worked as a private investigator for 10 years after getting started through his brother’s investigation company. His experience made him observant, street-smart, protective and exceptionally good at reading situations.',
    'Lily': 'Works with children and families in pediatric care, where patience and warmth matter every day. She enjoys baking, plants, quiet mornings and making people feel genuinely cared for.',
    'Aria': 'Rose through corporate leadership by combining organization, confidence and strong people skills. She enjoys travel, fitness, elegant spaces and conversations about goals and growth.',
    'Mika': 'Protects companies from digital threats and loves solving problems that other people cannot see. Outside work she is into gaming, new gadgets, concerts and playful competition.',
    'Zoey': 'Built a career traveling, interviewing people and writing about places beyond the usual tourist view. She loves unfamiliar food, last-minute plans and collecting unforgettable stories.',
    'Nova': 'Designs and analyzes systems connected to flight and space technology. She has always been fascinated by the future and spends her free time stargazing, building projects and reading science fiction.',
    'Sophia': 'Chose family medicine because she wanted long-term relationships with the people she serves. She is organized and accomplished but values humor, family traditions and simple time with people she trusts.',
    'Isabella': 'Works with art, history and exhibitions, bringing overlooked stories to life for the public. She loves museums, old cities, books, intimate dinners and meaningful conversation.',
    'Chloe': 'Built her counseling career around helping adults navigate relationships, stress and major life changes. Outside work she is playful, grounded and happiest around good music, close friends and genuine conversation.',
    'Ember': 'An architect who loves transforming bold ideas into spaces people remember. She is artistic, intense and resilient, with a weakness for dramatic skylines, live music and late-night creative sessions.',
    'Hana': 'Creates polished, comfortable interiors for homes and boutique spaces. She notices details quickly, loves balance and beauty, and spends weekends exploring design markets and new restaurants.',
    'Riley': 'Works with athletes recovering from injuries and returning to competition. She brings the same energy to her own life through training, outdoor challenges and a very competitive sense of humor.',
    'Vivien': 'Teaches at the university level and is known for making complex ideas engaging instead of intimidating. She enjoys literature, travel, wine-free dinner parties, museums and intelligent conversation.',
    'Bella': 'Built a photography career around fashion, portraits and visual storytelling. She is social and creative, loves discovering new music and can turn an ordinary afternoon into a mini adventure.',
    'Sahara': 'Advises companies expanding into international markets and has lived or worked across several regions. She loves languages, culture, travel and conversations with people who see the world differently.',
    'Skye': 'Designs digital products by blending technology, psychology and visual design. She is future-focused, independent and constantly sketching ideas for apps, experiences and businesses.',
    'Nia': 'A civil rights attorney who chose law because fairness and advocacy matter deeply to her. She is confident in a courtroom, warm in private and loves books, community work and ambitious conversations.',
}

ZODIAC_SYMBOLS = {
    'Aries': '&#9800;&#xfe0e;', 'Taurus': '&#9801;&#xfe0e;', 'Gemini': '&#9802;&#xfe0e;',
    'Cancer': '&#9803;&#xfe0e;', 'Leo': '&#9804;&#xfe0e;', 'Virgo': '&#9805;&#xfe0e;',
    'Libra': '&#9806;&#xfe0e;', 'Scorpio': '&#9807;&#xfe0e;', 'Sagittarius': '&#9808;&#xfe0e;',
    'Capricorn': '&#9809;&#xfe0e;', 'Aquarius': '&#9810;&#xfe0e;', 'Pisces': '&#9811;&#xfe0e;',
}

BIRTHDAYS = {
    'Alex': 'April 2', 'Damien': 'November 8', 'Logan': 'December 3', 'Jay': 'June 4',
    'Kai': 'February 6', 'Mason': 'May 12', 'Ethan': 'September 3', 'Luca': 'August 14',
    'Darius': 'January 7', 'Noah': 'March 12', 'Jack': 'July 7', 'Julius': 'February 14',
    'Leo': 'August 3', 'Carter': 'April 10', 'Malik': 'September 30', 'Simone': 'October 15',
    'Lily': 'March 5', 'Aria': 'May 7', 'Mika': 'June 10', 'Zoey': 'December 8',
    'Nova': 'February 10', 'Sophia': 'September 9', 'Isabella': 'July 12', 'Chloe': 'August 6',
    'Ember': 'October 23', 'Hana': 'October 6', 'Riley': 'April 16', 'Vivien': 'October 13',
    'Bella': 'March 1', 'Sahara': 'December 15', 'Skye': 'February 1', 'Nia': 'October 16',
}

SIGN_NAME_STYLE = 'font-family:Georgia,Times New Roman,serif;font-size:27px;font-style:italic;font-weight:700;letter-spacing:2px;background:linear-gradient(90deg,#63d7ff,#d45fff,#ff688e);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 0 18px rgba(212,95,255,.24);vertical-align:middle'
SYMBOL_STYLE = 'font-family:Apple Symbols,Segoe UI Symbol,Noto Sans Symbols 2,Arial Unicode MS,sans-serif;font-size:30px;font-style:normal;font-weight:700;color:#8fd2ff;margin-right:10px;vertical-align:middle;line-height:1'


def zodiac_line(name, sign):
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
        f'<div style="font-size:17px;font-weight:700;margin:0 0 7px">Age: {age}</div>'
        f'<div style="font-size:17px;font-weight:700;margin:0 0 7px">Career: {CAREERS[name]}</div>'
        f'<div style="font-size:16px;color:#c9c9cf;margin:0 0 14px">Birthday: {BIRTHDAYS[name]}</div>'
        f'<div style="font-size:16px;line-height:1.55;color:#dedee4;margin:0 0 16px"><strong>Background:</strong> {BACKGROUNDS[name]}</div>'
    )

    html = html.replace(f'<h1>{name}</h1>', details)
    return html


def audit_companion_pages():
    failures = []
    checked = 0
    for name in base.ALL:
        if name in {'Simone', 'Chloe'}:
            continue
        checked += 1
        try:
            html = companion_page(name)
            age, sign = PROFILES[name]
            required = [
                f'>{name}</h1>', f'Age: {age}', f'Career: {CAREERS[name]}',
                f'Birthday: {BIRTHDAYS[name]}', 'Background:', sign, '<img src=', 'Height ',
            ]
            missing = [item for item in required if item not in html]
            if missing:
                failures.append(f"{name}: missing {missing}")
        except Exception as exc:
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
    if failures:
        raise RuntimeError('COMPANION_AUDIT_FAILED | ' + ' | '.join(failures))
    print(f'COMPANION_AUDIT_OK checked={checked} non-free companion pages')


base.companion_page = companion_page

if __name__ == '__main__':
    audit_companion_pages()
    ThreadingHTTPServer(('0.0.0.0', base.PORT), run_current.ProductionHandler).serve_forever()
