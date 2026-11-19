#!/usr/bin/env python3
"""Assemble le site Trails of Impact.

dist/      : site complet, polices hébergées sur le site (pour la mise en ligne)
artifact/  : même site, page d'accueil en fragment + Google Fonts (aperçu Claude)
"""
import math, random, re, shutil, html, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES_DIR = ROOT / "pages"
EMAIL = "contact@trailsofimpact.org"

# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
PAGES = [
    dict(slug="index", nav="Accueil", title="Trails of Impact · Association Fribourg–Togo pour l'école",
         desc="Association fribourgeoise en création : nous levons un à un les obstacles entre les enfants de la région de Kpalimé (Togo) et l'école. Un chemin à la fois.",
         hero="dark"),
    dict(slug="histoire", nav="Notre histoire", title="Notre histoire · Trails of Impact",
         desc="Tout a commencé en 2021 avec 106 enfants scolarisés dans la région de Kpalimé. Pourquoi une association, pourquoi « Trails », nos engagements.",
         hero=None),
    dict(slug="eau", nav="Le projet eau", title="Forage solaire à Govié-Akpato (Togo) · Trails of Impact",
         desc="Descendre jusqu'à l'eau : le projet de forage solaire à Govié-Akpato, près de Kpalimé (Togo), balise après balise. Ce que nous savons, ce que nous ne savons pas encore, le budget.",
         hero="earth"),
    dict(slug="fribourg", nav="À Fribourg", title="Atelier en classe (5H–8H) à Fribourg · Trails of Impact",
         desc="« Le chemin de l'école, ici et là-bas » : un atelier de 90 minutes pour les classes de 5H à 8H du canton de Fribourg.",
         hero=None),
    dict(slug="carnet", nav="Carnet de route", title="Carnet de route · Trails of Impact",
         desc="Chaque étape, chaque document, chaque franc : le carnet de route public de Trails of Impact.",
         hero=None),
    dict(slug="rejoindre", nav="Nous rejoindre", title="Nous rejoindre · Trails of Impact",
         desc="Rejoindre le comité fondateur, donner un coup de main, inviter l'atelier en classe ou être prévenu·e à l'ouverture des dons.",
         hero=None),
]
BY = {p["slug"]: p for p in PAGES}

def href(slug):
    return f"{slug}.html"

# --------------------------------------------------------------------------
# Logo (piste C « la trace »)
# --------------------------------------------------------------------------
LOGO = ('<svg viewBox="0 0 200 200" aria-hidden="true" focusable="false">'
        '<path class="logo-path" d="M40,166 C40,128 108,148 104,104" stroke-width="15"/>'
        '<path class="logo-path" d="M104,104 C101,72 142,80 146,54" stroke-width="10" stroke-dasharray="0.01 18"/>'
        '<circle class="logo-dot" cx="40" cy="168" r="10"/>'
        '<circle class="logo-ring" cx="157" cy="41" r="22"/>'
        '<circle class="logo-hole" cx="157" cy="41" r="8"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'%3E"
           "%3Crect width='200' height='200' rx='44' fill='%231B3A30'/%3E"
           "%3Cpath d='M40,166 C40,128 108,148 104,104' fill='none' stroke='%23C96E4B' stroke-width='18' stroke-linecap='round'/%3E"
           "%3Cpath d='M104,104 C101,72 142,80 146,54' fill='none' stroke='%23C96E4B' stroke-width='12' stroke-linecap='round' stroke-dasharray='0.01 19'/%3E"
           "%3Ccircle cx='157' cy='41' r='24' fill='%23F6F1EA'/%3E%3Ccircle cx='157' cy='41' r='9' fill='%231B3A30'/%3E%3C/svg%3E")

def brand(link=True):
    inner = f'{LOGO}<span class="brand__word" aria-hidden="true">Trails<i>of</i>Impact</span>'
    if link:
        return f'<a class="brand" href="index.html" aria-label="Trails of Impact, accueil">{inner}</a>'
    return f'<span class="brand">{inner}</span>'

# --------------------------------------------------------------------------
# Géométrie : courbes de Bézier
# --------------------------------------------------------------------------
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])

def sample(segs, n=400):
    pts = []
    for s in segs:
        if s[0] == "L":
            a, b = s[1], s[2]
            for i in range(n):
                t = i / n
                pts.append((a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t))
        else:
            for i in range(n):
                pts.append(bez(s[1], s[2], s[3], s[4], i / n))
    last = segs[-1]
    pts.append(last[2] if last[0] == "L" else last[4])
    return pts

def path_d(segs):
    first = segs[0][1]
    d = f"M{first[0]:.1f},{first[1]:.1f}"
    for s in segs:
        if s[0] == "L":
            d += f" L{s[2][0]:.1f},{s[2][1]:.1f}"
        else:
            d += f" C{s[2][0]:.1f},{s[2][1]:.1f} {s[3][0]:.1f},{s[3][1]:.1f} {s[4][0]:.1f},{s[4][1]:.1f}"
    return d

def even_points(segs, count, end_trim=0.0):
    pts = sample(segs)
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.dist(pts[i-1], pts[i]))
    total = cum[-1] - end_trim
    out, j = [], 0
    for k in range(count):
        target = total * k / (count - 1)
        while j < len(cum) - 2 and cum[j+1] < target:
            j += 1
        seg = cum[j+1] - cum[j] or 1
        t = (target - cum[j]) / seg
        out.append((pts[j][0] + (pts[j+1][0]-pts[j][0])*t, pts[j][1] + (pts[j+1][1]-pts[j][1])*t))
    return out

# --------------------------------------------------------------------------
# Carte du héros : Fribourg -> Kpalimé
# --------------------------------------------------------------------------
def hero_map():
    S = (430, 52)
    s1 = ("C", S, (488, 112), (318, 122), (336, 200))
    s2 = ("C", (336, 200), (348, 256), (470, 268), (428, 334))
    s3 = ("C", (428, 334), (398, 380), (286, 374), (278, 436))
    s4 = ("C", (278, 436), (270, 496), (200, 500), (172, 556))
    solid = path_d([s1, s2, s3])
    dotted = path_d([s4])
    return f'''<svg viewBox="0 0 520 610" xmlns="http://www.w3.org/2000/svg">
  <path class="m-solid" d="{solid}" pathLength="1"/>
  <path class="m-dots m-fade" style="--d:2.5s" d="{dotted}"/>
  <circle class="m-start" cx="430" cy="52" r="8"/>
  <text class="m-t" x="412" y="45" text-anchor="end">FRIBOURG</text>
  <text class="m-s" x="412" y="65" text-anchor="end">46°48′ N · 7°09′ E</text>
  <g class="m-fade" style="--d:1.15s">
    <circle class="m-mark" cx="336" cy="200" r="6.5"/>
    <text class="m-t" x="318" y="196" text-anchor="end">2021</text>
    <text class="m-s" x="318" y="215" text-anchor="end">106 enfants scolarisés</text>
  </g>
  <g class="m-fade" style="--d:1.85s">
    <circle class="m-mark" cx="428" cy="334" r="6.5"/>
    <text class="m-t" x="410" y="322" text-anchor="end">OCT. 2025</text>
    <text class="m-s" x="410" y="341" text-anchor="end">Première étude à Akpato</text>
  </g>
  <g class="m-fade" style="--d:2.45s">
    <circle class="m-pulse" cx="278" cy="436" r="9"/>
    <circle class="m-here" cx="278" cy="436" r="9"/>
    <text class="m-y" x="304" y="431">NOV. 2026</text>
    <text class="m-s" x="304" y="450">Nous en sommes ici</text>
  </g>
  <g class="m-fade" style="--d:2.9s">
    <text class="m-s" x="236" y="528">2027 · l'eau à Akpato</text>
    <circle class="m-ring" cx="172" cy="560" r="15"/>
    <circle class="m-hole" cx="172" cy="560" r="5.5"/>
    <text class="m-t" x="150" y="556" text-anchor="end">KPALIMÉ</text>
    <text class="m-s" x="150" y="576" text-anchor="end">6°54′ N · 0°38′ E</text>
  </g>
</svg>'''

# --------------------------------------------------------------------------
# Les 106 points
# --------------------------------------------------------------------------
def dots_svgs():
    # Bureau : une vague de gauche à droite
    d_segs = [("C", (40, 196), (240, 206), (250, 70), (470, 90)),
              ("C", (470, 90), (690, 110), (720, 218), (920, 170)),
              ("C", (920, 170), (1040, 142), (1080, 72), (1140, 64))]
    pts = even_points(d_segs, 106, end_trim=0)
    circles = "".join(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="5.2"/>' for x, y in pts[:-1])
    desk = f'''<svg class="d-d" viewBox="0 0 1200 250" role="img" aria-label="106 points, un par enfant, alignés sur un chemin qui mène à l'école">
  {circles}
  <circle class="d-ring" cx="1160" cy="60" r="17"/><circle class="d-hole" cx="1160" cy="60" r="6.5"/>
  <text class="d-t" x="1160" y="26" text-anchor="middle">L'ÉCOLE</text>
  <text class="d-s" x="40" y="236">RENTRÉE 2021</text>
</svg>'''
    # Mobile : un lacet
    m_segs = [("L", (28, 44), (300, 44)),
              ("C", (300, 44), (352, 44), (352, 154), (300, 154)),
              ("L", (300, 154), (60, 154)),
              ("C", (60, 154), (8, 154), (8, 264), (60, 264)),
              ("L", (60, 264), (300, 264)),
              ("C", (300, 264), (352, 264), (352, 374), (300, 374)),
              ("L", (300, 374), (60, 374)),
              ("C", (60, 374), (8, 374), (8, 484), (60, 484)),
              ("L", (60, 484), (250, 484))]
    mp = even_points(m_segs, 106)
    mc = "".join(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="5"/>' for x, y in mp)
    mob = f'''<svg class="d-m" viewBox="0 0 360 540" role="img" aria-label="106 points, un par enfant, alignés sur un chemin qui mène à l'école">
  <text class="d-s" x="28" y="22">RENTRÉE 2021</text>
  {mc}
  <circle class="d-ring" cx="286" cy="484" r="16"/><circle class="d-hole" cx="286" cy="484" r="6"/>
  <text class="d-t" x="286" y="526" text-anchor="middle">L'ÉCOLE</text>
</svg>'''
    return desk + mob

# --------------------------------------------------------------------------
# Mini-coupe (accueil)
# --------------------------------------------------------------------------
def mini_coupe():
    top, H = 78, 300  # sol à y=78, 110 m sur 300 px
    y = lambda d: top + d * H / 110
    hatch = "".join(f'<line x1="{x}" y1="{y(46):.1f}" x2="{x+40}" y2="{y(46)+40:.1f}"/>' for x in range(70, 230, 14))
    return f'''<svg viewBox="0 0 320 400" role="img" aria-label="Coupe du sous-sol à Akpato : roche altérée de 0 à 10 mètres, roche dure en dessous, eau probable entre 46 et 106 mètres, forage prévu jusqu'à 100 mètres.">
  <defs><clipPath id="mc-col"><rect x="112" y="{top}" width="80" height="{H}" rx="6"/></clipPath>
  <pattern id="mc-h" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="10" height="10" fill="#1B4A5E"/><rect width="3" height="10" fill="#3F98BE"/></pattern></defs>
  <g clip-path="url(#mc-col)">
    <rect x="112" y="{top}" width="80" height="{y(10)-top:.1f}" fill="#B85C33"/>
    <rect x="112" y="{y(10):.1f}" width="80" height="{top+H-y(10):.1f}" fill="#2E3431"/>
    <rect x="112" y="{y(46):.1f}" width="80" height="{y(106)-y(46):.1f}" fill="url(#mc-h)" opacity=".9"/>
  </g>
  <rect x="112" y="{top}" width="80" height="{H}" rx="6" fill="none" stroke="rgba(246,241,234,.5)" stroke-width="1.5"/>
  <line x1="108" y1="{top}" x2="262" y2="{top}" stroke="#F6F1EA" stroke-width="2.5"/>
  <line x1="152" y1="{top}" x2="152" y2="{y(100):.1f}" stroke="#F6F1EA" stroke-width="4" stroke-linecap="round" stroke-dasharray="0.1 10"/>
  <g fill="none" stroke="#F6F1EA" stroke-width="2" stroke-dasharray="3 4" stroke-linecap="round">
    <path d="M206,{top} L212,40 M232,{top} L226,40 M209,58 L229,58"/>
    <rect x="203" y="14" width="34" height="26" rx="4"/>
  </g>
  <text class="mc-s" x="246" y="30" style="font-size:12px">à venir</text>
  <g class="mc-s" text-anchor="end">
    <text x="102" y="{top+5}">0 m</text><text x="102" y="{y(10)+4:.1f}">10 m</text>
    <text x="102" y="{y(46)+4:.1f}" class="mc-w">46 m</text><text x="102" y="{y(100)+4:.1f}">100 m</text>
  </g>
  <g stroke="rgba(246,241,234,.6)" stroke-width="1.5">
    <line x1="106" y1="{y(10):.1f}" x2="112" y2="{y(10):.1f}"/><line x1="106" y1="{y(46):.1f}" x2="112" y2="{y(46):.1f}"/><line x1="106" y1="{y(100):.1f}" x2="112" y2="{y(100):.1f}"/>
  </g>
  <text class="mc-t" x="202" y="{(top+y(10))/2+5:.1f}">Altérites</text>
  <text class="mc-t" x="202" y="{y(26):.1f}">Socle</text>
  <text class="mc-s" x="202" y="{y(26)+17:.1f}">roche dure</text>
  <text class="mc-w" x="202" y="{y(72):.1f}">Eau probable</text>
  <text class="mc-s" x="202" y="{y(72)+17:.1f}">46 à 106 m</text>
  <text class="mc-s" x="202" y="{y(100)+4:.1f}">Forage prévu</text>
</svg>'''

# --------------------------------------------------------------------------
# Coupe de la page « Le projet eau »
# --------------------------------------------------------------------------
def coupe():
    Y = lambda d: 22 + d * 76 / 110
    ticks = "".join(f'<div class="c-tick" style="top:{Y(d):.2f}%"><span>{d} m</span></div>' for d in range(0, 111, 10))
    rnd = random.Random(7)
    paths = []
    socle_top = Y(10)
    for _ in range(46):
        d0 = rnd.uniform(12, 110)
        x = rnd.uniform(23, 98)
        yl = (Y(d0) - socle_top) / (100 - socle_top) * 100
        pts = [(x, yl)]
        for _ in range(rnd.randint(2, 4)):
            x += rnd.uniform(-4.5, 4.5); yl += rnd.uniform(0.6, 2.6)
            pts.append((x, yl))
        dmid = d0 + 3
        cls = ' class="wet"' if 46 <= dmid <= 106 else ''
        d = "M" + " L".join(f"{px:.2f},{py:.2f}" for px, py in pts)
        paths.append(f'<path{cls} d="{d}"/>')
    fiss = '<svg class="c-fiss" viewBox="0 0 100 100" preserveAspectRatio="none">' + "".join(paths) + '</svg>'
    notes = [
        (5, "Altérites · roche altérée, 0 à 10 m", ""),
        (27, "Socle · roche dure, l'eau circule dans ses fissures", ""),
        (46, "46 m · premières venues d'eau possibles", "is-water"),
        (76, "Zone d'eau probable · 46 à 106 m", "is-water"),
        (100, "100 m · fin prévue du forage", ""),
    ]
    notes_html = '<ul class="c-notes">' + "".join(
        f'<li class="{c}" style="top:{Y(d):.2f}%">{t}</li>' for d, t, c in notes) + '</ul>'
    tower = '''<svg class="c-tower" viewBox="0 0 170 170">
  <path d="M0,166 L70,166 L70,90" fill="none" stroke="#7F888D" stroke-width="5" stroke-linejoin="round"/>
  <g stroke="#5E4B3B" stroke-width="4" stroke-linecap="round"><line x1="46" y1="168" x2="56" y2="90"/><line x1="94" y1="168" x2="84" y2="90"/><line x1="50" y1="140" x2="90" y2="114"/><line x1="90" y1="140" x2="50" y2="114"/></g>
  <rect x="38" y="86" width="64" height="6" rx="2" fill="#5E4B3B"/>
  <rect x="38" y="22" width="64" height="64" rx="8" fill="rgba(255,253,249,.85)" stroke="#2F3532" stroke-width="3"/>
  <rect data-tank x="41" y="86" width="58" height="0" rx="5" fill="#3F98BE"/>
  <path d="M94,150 L132,150" stroke="#7F888D" stroke-width="4" stroke-linecap="round"/>
  <g stroke="#7F888D" stroke-width="3" stroke-linecap="round"><line x1="104" y1="150" x2="104" y2="157"/><line x1="114" y1="150" x2="114" y2="157"/><line x1="124" y1="150" x2="124" y2="157"/><line x1="132" y1="150" x2="132" y2="157"/></g>
  <g data-drops class="c-drops" style="opacity:0" fill="#8FD0EA"><circle class="c-drop" cx="104" cy="161" r="2.4"/><circle class="c-drop" cx="114" cy="161" r="2.4" style="animation-delay:.3s"/><circle class="c-drop" cx="124" cy="161" r="2.4" style="animation-delay:.6s"/><circle class="c-drop" cx="132" cy="161" r="2.4" style="animation-delay:.15s"/></g>
  <line x1="152" y1="168" x2="152" y2="122" stroke="#5E4B3B" stroke-width="4"/>
  <path d="M130,112 L166,98 L169,110 L133,124 Z" fill="#22405A" stroke="#A9C0D1" stroke-width="1.5"/>
</svg>'''
    return (f'<div class="c-sky"></div><div class="c-alt"></div><div class="c-socle"></div>'
            f'<div class="c-wet"></div>{fiss}<div class="c-ground"></div>'
            f'<div class="c-ruler">{ticks}</div>'
            f'<div class="c-tube"><i></i></div><div class="c-bit"></div>'
            f'{tower}<span class="c-site">Akpato</span>{notes_html}'
            f'<div class="c-read"><span class="label" data-read-label>Profondeur</span><span class="num" data-read-num>0 m</span></div>')

# --------------------------------------------------------------------------
# Fiche « Mon chemin de l'école »
# --------------------------------------------------------------------------
WORKSHEET = '''<figure class="worksheet" role="img" aria-label="Aperçu de la fiche d'atelier « Mon chemin de l'école »">
  <div class="worksheet__paper">
    <p class="worksheet__title">Mon chemin de l'école</p>
    <svg viewBox="0 0 300 124">
      <path class="ws-ico" d="M22,70 L44,50 L66,70 M28,66 L28,94 L60,94 L60,66 M40,94 L40,80 L49,80 L49,94"/>
      <path class="ws-ico" d="M236,94 L236,62 L286,62 L286,94 Z M236,62 L261,46 L286,62 M261,46 L261,26 M261,26 L276,31 L261,36 M254,94 L254,80 L268,80 L268,94"/>
      <path class="ws-path" d="M70,88 C110,40 140,112 178,72 C200,48 214,96 230,84"/>
      <text class="ws-t" x="44" y="116" text-anchor="middle">MAISON</text>
      <text class="ws-t" x="261" y="116" text-anchor="middle">ÉCOLE</text>
    </svg>
    <p class="worksheet__line">Je pars de <span class="blank"></span></p>
    <p class="worksheet__line">Je mets <span class="blank blank--s"></span> minutes</p>
    <p class="worksheet__line">En chemin, je croise <span class="blank"></span></p>
  </div>
</figure>'''

# --------------------------------------------------------------------------
# Carnet de route
# --------------------------------------------------------------------------
LOG = [
    ("done", "Rentrée 2021", "Le chemin de l'école pour tous",
     "106 enfants scolarisés dans la région de Kpalimé, avec l'association Assilé-Assimé. Coordination sur le terrain : Victoria Goepfert.",
     'fiche projet, <a href="histoire.html#galerie">photos de la rentrée</a>, cartes de remerciement aux donateurs'),
    ("done", "Octobre 2025", "Première étude géophysique à Akpato",
     "Un point de forage retenu, l'eau probable entre 46 et 106 m, sous 10 m de roche altérée. Un premier repérage, à confirmer par une étude indépendante.",
     "rapport d'étude, 2 pages"),
    ("done", "Octobre 2025", "Premier devis local",
     "8 403 000 FCFA, soit environ 11 800 CHF : forage de 100 m, pompe solaire, château d'eau, quatre robinets. Il servira de base de comparaison.",
     "devis détaillé, 8 pages"),
    ("now", "Novembre 2026", "Nom, identité, site et projet de statuts",
     "Trails of Impact prend forme à Fribourg. Les statuts sont en préparation, le comité fondateur se constitue.", ""),
    ("todo", "Hiver 2026–2027", "Comité fondateur et assemblée constitutive",
     "Trois personnes, des statuts adoptés, un compte bancaire au nom de l'association.", ""),
    ("todo", "Hiver 2026–2027", "Demande d'exonération fiscale",
     "Auprès du Service cantonal des contributions de Fribourg, pour que vos dons soient déductibles.", ""),
    ("todo", "Printemps 2027", "Étude des besoins à Akpato",
     "Avec le village et notre partenaire : familles concernées, distances, temps passé à chercher l'eau, usages.", ""),
    ("todo", "Printemps 2027", "Cahier des charges, trois devis, contrôle indépendant",
     "Le même cahier des charges pour toutes les entreprises, un hydrogéologue indépendant, un paiement par étapes.", ""),
    ("todo", "2027", "Financement",
     "Cotisations, dons et demandes de soutien auprès des communes et des fondations.", ""),
    ("todo", "2027", "Forage, essai de pompage, analyse de l'eau",
     "On ne construit rien sans un débit mesuré et une eau déclarée potable.", ""),
    ("todo", "2027", "Construction et comité de gestion",
     "Pompe solaire, château d'eau, robinets. Un comité formé sur place, des pièces de rechange, une caisse d'entretien.", ""),
    ("finish", "Puis à 1, 3 et 5 ans", "Bilans publics",
     "Débit, pannes, réparations, usage : publiés ici, que les nouvelles soient bonnes ou non.", ""),
]
STATUS = {"done": ("status--done", "Fait"), "now": ("status--now", "En cours"),
          "todo": ("status--todo", "À venir"), "finish": ("status--todo", "Arrivée")}

def log_html():
    items = []
    for kind, when, title, text, proof in LOG:
        cls, lab = STATUS[kind]
        li_cls = "todo finish" if kind == "finish" else kind
        proof_html = f'<p class="proof">{proof}</p>' if proof else ""
        items.append(f'<li class="{li_cls}"><p class="when">{when}</p><span class="rail" aria-hidden="true"></span>'
                     f'<div class="what"><div class="head"><h3>{title}</h3><span class="status {cls}">{lab}</span></div>'
                     f'<p>{text}</p>{proof_html}</div></li>')
    return '<ol class="log">' + "".join(items) + '</ol>'

def tally_html():
    done = sum(1 for k, *_ in LOG if k == "done")
    now = sum(1 for k, *_ in LOG if k == "now")
    todo = sum(1 for k, *_ in LOG if k in ("todo", "finish"))
    return (f'<div class="tally"><div><p class="num t-lat">{done}</p><span>balises franchies</span></div>'
            f'<div><p class="num">{now}</p><span>en cours</span></div>'
            f'<div><p class="num" style="color:var(--ink-3)">{todo}</p><span>à venir</span></div></div>')

# --------------------------------------------------------------------------
# Panneaux et sources
# --------------------------------------------------------------------------
SIGNS = {
    "index": ("Où voulez-vous aller ?", "Chaque page est une étape. Les temps indiqués sont des temps de lecture.",
              ["histoire", "eau", "fribourg", "carnet", "rejoindre"]),
    "histoire": ("La suite du chemin.", "De 2021 au projet en cours.", ["eau", "carnet", "rejoindre"]),
    "eau": ("Et ici, en Suisse ?", "Le projet eau a aussi une version pour les classes fribourgeoises.", ["fribourg", "carnet", "rejoindre"]),
    "fribourg": ("Voir où nous en sommes.", "Tout ce qui est fait, en cours et à venir.", ["carnet", "eau", "rejoindre"]),
    "carnet": ("Prendre un dossard.", "Le carnet de route s'écrit à plusieurs.", ["rejoindre", "eau", "index"]),
    "rejoindre": ("Retour au départ.", "Ou un dernier détour par le projet eau.", ["index", "eau", "histoire"]),
}
SOURCES = {
    "index": [
        ("source-1", "UNICEF et OMS, « Women and girls bear brunt of water and sanitation crisis », communiqué du 6 juillet 2023.",
         "https://www.unicef.org/press-releases/women-and-girls-bear-brunt-water-and-sanitation-crisis-new-unicef-who-report"),
        ("source-2", "Foster, T. et al. (2019), « Functionality of handpump water supplies: a review of data from sub-Saharan Africa and the Asia-Pacific region ».",
         "https://waterpointdata.org/wp-content/uploads/2020/11/Functionality-of-handpump-water-supplies.pdf"),
    ],
    "eau": [
        ("source-1", "UNICEF et OMS, « Women and girls bear brunt of water and sanitation crisis », communiqué du 6 juillet 2023.",
         "https://www.unicef.org/press-releases/women-and-girls-bear-brunt-water-and-sanitation-crisis-new-unicef-who-report"),
        ("source-2", "Foster, T. et al. (2019), fonctionnement des pompes à main en Afrique subsaharienne.",
         "https://waterpointdata.org/wp-content/uploads/2020/11/Functionality-of-handpump-water-supplies.pdf"),
        ("source-3", "Banque de France, taux de change du 11 novembre 2026.",
         "https://www.banque-france.fr/fr/statistiques/taux-et-cours/taux-de-change-parites-quotidiennes-2026-11-11"),
        ("source-4", "Étude géophysique d'implantation de forage à Akpato (octobre 2025) et devis local (octobre 2025), documents internes consultables sur demande.", None),
    ],
}

def strip_tags(s):
    s = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", s)
    s = re.sub(r"<svg[\s\S]*?</svg>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)

def reading_minutes(text):
    words = len(re.findall(r"[\wÀ-ÿ’'-]+", text))
    return max(1, round(words / 190))

def signs_html(slug, mins):
    title, sub, dests = SIGNS[slug]
    here = BY[slug]["nav"]
    plates = "".join(
        f'<a class="sign" href="{href(d)}"><span>{BY[d]["nav"]}</span><span class="t">{mins[d]} min</span></a>'
        for d in dests)
    return f'''<section class="signs" aria-labelledby="signs-title">
  <div class="wrap signs__grid">
    <div class="stack">
      <p class="label label--rule t-lat">Prochaine étape</p>
      <h2 class="t-h2" id="signs-title">{title}</h2>
      <p class="muted">{sub}</p>
    </div>
    <nav class="signpost" aria-label="Pages suivantes">
      <p class="sign-here"><span>{here}</span><small>Vous êtes ici</small></p>
      {plates}
    </nav>
  </div>
</section>'''

def sources_html(slug):
    if slug not in SOURCES:
        return ""
    lis = []
    for sid, txt, url in SOURCES[slug]:
        link = f' <a href="{url}" target="_blank" rel="noopener">{url.split("/")[2]}</a>' if url else ""
        lis.append(f'<li id="{sid}">{txt}{link}</li>')
    return f'<aside class="sources"><div class="wrap"><h2>Sources</h2><ol>{"".join(lis)}</ol></div></aside>'

# --------------------------------------------------------------------------
# Gabarit
# --------------------------------------------------------------------------
def header_html(slug, mins):
    links = []
    for p in PAGES:
        cur = ' aria-current="page"' if p["slug"] == slug else ""
        cls = ' class="btn btn--lat"' if p["slug"] == "rejoindre" else ""
        links.append(f'<a{cls} href="{href(p["slug"])}"{cur}>{p["nav"]}</a>')
    items = ""
    for p in PAGES:
        cur = ' aria-current="page"' if p["slug"] == slug else ""
        items += f'<li><a href="{href(p["slug"])}"{cur}>{p["nav"]}<small>{mins[p["slug"]]} min</small></a></li>'
    return f'''<a class="skip" href="#contenu">Aller au contenu</a>
<header class="site-header">
  <div class="wrap">
    {brand()}
    <nav class="nav" aria-label="Navigation principale">{"".join(links)}</nav>
    <button class="burger" type="button" data-menu-open aria-expanded="false" aria-controls="menu"><b>Menu</b><span aria-hidden="true"><i></i><i></i></span></button>
  </div>
  <div class="trail-progress" aria-hidden="true"><i></i></div>
</header>
<div class="menu on-dark" id="menu" role="dialog" aria-modal="true" aria-label="Menu" hidden>
  <div class="wrap">
    <div class="menu__top">{brand()}<button class="menu__close" type="button" data-menu-close>Fermer <span aria-hidden="true">×</span></button></div>
    <ul>{items}</ul>
    <a class="btn btn--lat" href="rejoindre.html">Nous rejoindre <span class="arr" aria-hidden="true">→</span></a>
  </div>
</div>'''

def footer_html():
    links = "".join(f'<li><a href="{href(p["slug"])}">{p["nav"]}</a></li>' for p in PAGES)
    return f'''<footer class="site-footer on-dark">
  <canvas class="topo" data-topo data-seed="23" data-levels="20" data-scale="0.003" aria-hidden="true"></canvas>
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        {brand()}
        <p class="foot-slogan">Un chemin à la fois.</p>
        <p class="foot-meta">Association en création · Fribourg, Suisse</p>
      </div>
      <nav aria-label="Pages du site"><h2>Le site</h2><ul>{links}</ul></nav>
      <div><h2>Transparence</h2><ul>
        <li><a href="carnet.html">Carnet de route</a></li>
        <li><a href="carnet.html#comptes">Les comptes</a></li>
        <li><a href="carnet.html#charte">Charte des images</a></li>
        <li><a href="eau.html#savoir">Ce que nous ne savons pas encore</a></li>
      </ul></div>
      <div><h2>Contact</h2>
        <p class="mail"><span class="mail__addr" data-email>{EMAIL}</span><button class="mail__copy" type="button" data-copy="email">Copier</button></p>
        <p class="foot-meta">Nous répondons personnellement.</p>
        <p style="margin-top:14px"><a class="link-arrow" href="rejoindre.html#contact">Écrire un message <span aria-hidden="true">→</span></a></p>
        <p class="foot-meta" style="margin-top:18px">Suivre le chemin : <a href="https://www.instagram.com/trails_of_impact/" rel="me noopener" target="_blank">Instagram</a> · <a href="https://www.tiktok.com/@trails.of.impact" rel="me noopener" target="_blank">TikTok</a></p>
      </div>
    </div>
    <div class="foot-bottom"><span>© 2026 Trails of Impact</span><span>Association en création · mis à jour en novembre 2026</span></div>
  </div>
</footer>'''

GOOGLE_FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700'
                '&family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,400'
                '&family=Fraunces:ital,opsz,wght@0,9..144,400..700;1,9..144,400..700&display=swap">')
LOCAL_FONTS = '<link rel="stylesheet" href="assets/fonts.css">'

# --------------------------------------------------------------------------
# Référencement : données structurées (schema.org, JSON-LD)
# --------------------------------------------------------------------------
ORG_ID = "https://trailsofimpact.org/#organisation"
# Profils officiels de l'association (Instagram, TikTok, LinkedIn) : à ajouter ici
# dès que leurs adresses sont confirmées. Ils relient le site à ses réseaux pour Google.
SAME_AS = ["https://www.instagram.com/trails_of_impact/", "https://www.tiktok.com/@trails.of.impact"]

def page_url(slug):
    return SITE_URL + ("" if slug == "index" else slug + ".html")

def json_ld(p):
    if p["slug"] == "404":
        return ""
    org = {
        "@type": "NGO", "@id": ORG_ID,
        "name": "Trails of Impact",
        "url": SITE_URL,
        "logo": {"@type": "ImageObject", "url": SITE_URL + "assets/img/logo-512.png", "width": 512, "height": 512},
        "image": SITE_URL + "assets/img/partage.jpg",
        "description": ("Association en création à Fribourg (Suisse). Elle lève un à un les obstacles "
                        "entre les enfants de la région de Kpalimé, au Togo, et l'école : frais de scolarité, "
                        "matériel scolaire, accès à l'eau."),
        "slogan": "Un chemin à la fois.",
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressLocality": "Fribourg",
                    "addressRegion": "FR", "addressCountry": "CH"},
        "areaServed": [{"@type": "Place", "name": "Région de Kpalimé, Togo"},
                       {"@type": "AdministrativeArea", "name": "Canton de Fribourg, Suisse"}],
        "founder": {"@type": "Person", "name": "Victoria Goepfert"},
        "knowsAbout": ["Accès à l'éducation", "Scolarisation", "Accès à l'eau potable",
                       "Forage", "Togo", "Kpalimé"],
    }
    if SAME_AS:
        org["sameAs"] = SAME_AS
    if p["slug"] == "index":
        graph = [org, {"@type": "WebSite", "@id": SITE_URL + "#site", "url": SITE_URL,
                       "name": "Trails of Impact", "inLanguage": "fr-CH", "publisher": {"@id": ORG_ID}}]
    else:
        graph = [{"@type": "WebPage", "@id": page_url(p["slug"]), "url": page_url(p["slug"]),
                  "name": p["title"], "description": p["desc"], "inLanguage": "fr-CH",
                  "isPartOf": {"@id": SITE_URL + "#site"}, "publisher": {"@id": ORG_ID},
                  "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                      {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE_URL},
                      {"@type": "ListItem", "position": 2, "name": p["nav"], "item": page_url(p["slug"])}]}}]
    data = json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{data}</script>\n'

def head_inner(p, fonts):
    desc = html.escape(p["desc"], quote=True)
    title = html.escape(p["title"], quote=True)
    return (f'<title>{p["title"]}</title>\n'
            f'<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<meta name="description" content="{desc}">\n'
            f'<meta name="theme-color" content="#1B3A30">\n'
            f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="Trails of Impact">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n'
            f'<meta property="og:url" content="{page_url(p["slug"])}">\n'
            f'<meta property="og:locale" content="fr_CH">\n'
            f'<meta property="og:image" content="{SITE_URL}assets/img/partage.jpg">\n'
            f'<meta property="og:image:width" content="1200">\n'
            f'<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="Des enfants de la région de Kpalimé, au Togo, posent avec leurs cartables neufs, rentrée 2021.">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<link rel="icon" href="{FAVICON}">\n'
            f'<link rel="apple-touch-icon" href="assets/img/logo-180.png">\n'
            f'<link rel="canonical" href="{page_url(p["slug"])}">\n'
            + json_ld(p) +
            f'{fonts}\n<link rel="stylesheet" href="assets/site.css">\n')

# --------------------------------------------------------------------------
# Typographie française : espaces insécables
# --------------------------------------------------------------------------
NNBSP, NBSP = " ", " "
def fr_typo(text):
    parts = re.split(r"(<script[\s\S]*?</script>|<style[\s\S]*?</style>|<svg[\s\S]*?</svg>|<[^>]+>)", text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part); continue
        s = part
        s = re.sub(r" ([?!;])", NNBSP + r"\1", s)
        s = re.sub(r" :(?=\s|$)", NBSP + ":", s)
        s = s.replace("« ", "«" + NBSP).replace(" »", NBSP + "»")
        s = re.sub(r"(\d) (\d{3})\b", r"\1" + NNBSP + r"\2", s)
        s = re.sub(r"(\d) (\d{3})\b", r"\1" + NNBSP + r"\2", s)
        s = re.sub(r"(\d) (m|km|min|CHF|FCFA|ans|litres|mètres|enfants)\b", r"\1" + NBSP + r"\2", s)
        s = s.replace("≈ ", "≈" + NBSP).replace("N° ", "N°" + NBSP)
        out.append(s)
    return "".join(out)

# --------------------------------------------------------------------------
# Photos de la rentrée 2021
# --------------------------------------------------------------------------
BIG = {"hero-1", "hero-2", "hero-3", "hero-4", "meres", "groupe"}
def widths(name):
    return (1920, 1080) if name in BIG else (1600, 800)

def pic(name, alt="", sizes="100vw", flags=""):
    big, small = widths(name)
    load = ' fetchpriority="high"' if "eager" in flags else ' loading="lazy"'
    return (f'<img src="assets/img/{name}-{big}.webp" srcset="assets/img/{name}-{small}.webp {small}w, '
            f'assets/img/{name}-{big}.webp {big}w" sizes="{sizes}" alt="{html.escape(alt, quote=True)}"'
            f'{load} decoding="async" width="{big}" height="{round(big * 1717 / 2576)}">')

KP = "région de Kpalimé"
PHOTOS = [
    ("hero-1", "Des enfants lèvent la main, leur cartable neuf porté devant eux.", f"Les nouveaux cartables, rentrée 2021, {KP}"),
    ("groupe", "Un grand groupe d'enfants pose avec ses cartables neufs devant une maison.", f"Distribution des cartables, rentrée 2021, {KP}"),
    ("fournitures", "Deux enfants découvrent leurs cahiers et leurs livres, assis sur un banc.", f"Distribution des fournitures, rentrée 2021, {KP}"),
    ("sourires", "Des enfants sourient, leur cartable neuf contre eux.", f"Rentrée 2021, {KP}"),
    ("pupitres", "Des élèves en uniforme beige appuyés sur des pupitres en bois, devant la végétation.", f"Rentrée 2021, {KP}"),
    ("hero-2", "Des femmes dansent en tenant des branches, des bébés dans le dos.", f"Rentrée 2021, {KP}"),
    ("pupitres-2", "Des élèves assis sur des pupitres en bois, à l'ombre des hautes herbes.", f"Rentrée 2021, {KP}"),
    ("meres", "Des femmes du village écoutent, accoudées à un pupitre en bois.", f"Rentrée 2021, {KP}"),
    ("hero-3", "Des élèves en uniforme et en habits colorés, devant de hautes herbes.", f"Rentrée 2021, {KP}"),
    ("jeunes", "Des jeunes du village assis sur des pupitres, attentifs.", f"Rentrée 2021, {KP}"),
    ("danse", "Des femmes en pagnes colorés, des bébés dans le dos.", f"Rentrée 2021, {KP}"),
    ("terre-rouge", "Deux petits garçons en habits colorés sur la terre rouge.", f"Rentrée 2021, {KP}"),
    ("uniformes", "Des élèves en uniforme, rassemblés devant la végétation.", f"Rentrée 2021, {KP}"),
    ("hero-4", "Avocats et oranges empilés dans des bassines colorées, sur un marché.", f"Marché, {KP}, 2021"),
]
PH = {n: (a, c) for n, a, c in PHOTOS}
FILM_ORDER = ["fournitures", "sourires", "pupitres", "danse", "jeunes", "terre-rouge", "pupitres-2", "uniformes"]

def film_html():
    def items(hidden):
        out = []
        for n in FILM_ORDER:
            alt, cap = PH[n]
            out.append(f'<li><figure>{pic(n, "" if hidden else alt, "(max-width: 700px) 70vw, 520px")}'
                       f'<figcaption>{cap}</figcaption></figure></li>')
        return "".join(out)
    return (f'<div class="film__viewport" role="region" aria-label="Photos de la rentrée 2021" tabindex="0">'
            f'<div class="film__track"><ul class="film__reel">{items(False)}</ul>'
            f'<ul class="film__reel" aria-hidden="true">{items(True)}</ul></div></div>')

def gallery_html():
    cells = []
    for i, (n, alt, cap) in enumerate(PHOTOS):
        big, _ = widths(n)
        cls = "g-item g-feature" if i == 0 else ("g-item g-wide" if i in (5, 9) else "g-item")
        cells.append(f'<li class="{cls}"><button type="button" data-lb="{i}" data-src="assets/img/{n}-{big}.webp" '
                     f'data-cap="{html.escape(cap, quote=True)}" aria-label="Agrandir la photo : {html.escape(alt, quote=True)}">'
                     f'{pic(n, alt, "(max-width: 700px) 100vw, 600px")}<span class="g-cap">{cap}</span></button></li>')
    return ('<ul class="gallery">' + "".join(cells) + '</ul>'
            '<dialog class="lightbox" id="lightbox" aria-label="Photo agrandie">'
            '<figure><img alt="" data-lb-img><figcaption data-lb-cap></figcaption></figure>'
            '<button type="button" class="lb-btn lb-close" data-lb-close>Fermer <span aria-hidden="true">×</span></button>'
            '<button type="button" class="lb-btn lb-prev" data-lb-prev aria-label="Photo précédente">←</button>'
            '<button type="button" class="lb-btn lb-next" data-lb-next aria-label="Photo suivante">→</button>'
            '</dialog>')

# --------------------------------------------------------------------------
# Construction
# --------------------------------------------------------------------------
def render_body(slug, mins):
    src = (PAGES_DIR / f"{slug}.html").read_text(encoding="utf-8")
    rep = {
        "{{HERO_MAP}}": hero_map(), "{{DOTS}}": dots_svgs(), "{{MINI_COUPE}}": mini_coupe(),
        "{{WORKSHEET}}": WORKSHEET, "{{COUPE}}": coupe(), "{{LOG}}": log_html(), "{{TALLY}}": tally_html(),
        "{{SIGNS}}": signs_html(slug, mins), "{{SOURCES}}": sources_html(slug),
        "{{FILM}}": film_html(), "{{GALLERY}}": gallery_html(),
    }
    for k, v in rep.items():
        src = src.replace(k, v)
    src = re.sub(r"\{\{PIC:([\w-]+)\|([^|}]*)\|?([^|}]*)\|?([^}]*)\}\}",
                 lambda m: pic(m.group(1), m.group(2), m.group(3) or "100vw", m.group(4)), src)
    assert "{{" not in src, f"placeholder left in {slug}"
    return src

def build():
    # temps de lecture
    mins = {p["slug"]: 1 for p in PAGES}
    for p in PAGES:
        raw = (PAGES_DIR / f"{p['slug']}.html").read_text(encoding="utf-8")
        raw = raw.replace("{{SIGNS}}", "").replace("{{SOURCES}}", "")
        raw = render_body(p["slug"], mins) if "{{" in raw else raw
        mins[p["slug"]] = reading_minutes(strip_tags(raw))

    for target in ("dist", "artifact"):
        out = ROOT / target
        if out.exists():
            shutil.rmtree(out)
        (out / "assets").mkdir(parents=True)
        shutil.copy(ROOT / "assets/site.css", out / "assets/site.css")
        shutil.copy(ROOT / "assets/site.js", out / "assets/site.js")
        shutil.copytree(ROOT / "assets/img", out / "assets/img")
        if target == "dist":
            shutil.copy(ROOT / "assets/fonts.css", out / "assets/fonts.css")
            shutil.copytree(ROOT / "assets/fonts", out / "assets/fonts")
        fonts = LOCAL_FONTS if target == "dist" else GOOGLE_FONTS
        for p in PAGES:
            slug = p["slug"]
            body = (header_html(slug, mins) + '\n<main id="contenu">\n' + render_body(slug, mins)
                    + '\n</main>\n' + footer_html() + '\n<script src="assets/site.js"></script>\n')
            body = fr_typo(body)
            hero_attr = f' data-hero="{p["hero"]}"' if p["hero"] else ""
            if target == "artifact" and slug == "index":
                doc = (head_inner(p, fonts)
                       + '<script>document.documentElement.lang="fr-CH";document.documentElement.classList.add("js");'
                       + (f'document.body.setAttribute("data-hero","{p["hero"]}");' if p["hero"] else "")
                       + '</script>\n' + body)
            else:
                doc = ('<!doctype html>\n<html lang="fr-CH">\n<head>\n<meta charset="utf-8">\n'
                       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                       + head_inner(p, fonts)
                       + '<script>document.documentElement.classList.add("js")</script>\n'
                       + f'</head>\n<body{hero_attr}>\n' + body + '</body>\n</html>\n')
            (out / f"{slug}.html").write_text(doc, encoding="utf-8")
        if target == "dist":
            write_hosting_files(out, mins)
    print("minutes:", mins)

SITE_URL = "https://trailsofimpact.org/"

NOT_FOUND = '''<section class="phero" aria-labelledby="nf-title">
  <canvas class="topo" data-topo data-seed="97" data-levels="22" data-scale="0.0026" data-peaks="0.8,0.4,0.16,1.2" aria-hidden="true"></canvas>
  <div class="wrap">
    <div class="stack" style="--gap:24px;max-width:820px">
      <p class="label label--rule t-lat">Erreur 404 · hors sentier</p>
      <h1 id="nf-title" class="t-display">Ce chemin n'existe pas.</h1>
      <p class="lead">La page que vous cherchez a peut-être changé d'adresse. Reprenez le sentier depuis le départ.</p>
      <div class="hero__actions">
        <a class="btn btn--lat" href="index.html">Retour à l'accueil <span class="arr" aria-hidden="true">→</span></a>
        <a class="btn btn--line" href="carnet.html">Carnet de route</a>
      </div>
    </div>
  </div>
</section>'''

def write_hosting_files(out, mins):
    """Fichiers pour l'hébergement GitHub Pages sur trailsofimpact.org."""
    (out / "CNAME").write_text("trailsofimpact.org\n", encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>{page_url(p['slug'])}</loc><lastmod>{today}</lastmod></url>\n" for p in PAGES)
    (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n',
                                     encoding="utf-8")
    p = dict(slug="404", nav="", title="Page introuvable · Trails of Impact",
             desc="Cette page n'existe pas. Retour à l'accueil de Trails of Impact.", hero=None)
    body = fr_typo(header_html("404", mins) + '\n<main id="contenu">\n' + NOT_FOUND + '\n</main>\n'
                   + footer_html() + '\n<script src="assets/site.js"></script>\n')
    doc = ('<!doctype html>\n<html lang="fr-CH">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + head_inner(p, LOCAL_FONTS).replace('<link rel="canonical" href="https://trailsofimpact.org/404.html">\n', '')
           + '<meta name="robots" content="noindex">\n'
           + '<script>document.documentElement.classList.add("js")</script>\n</head>\n<body>\n' + body + '</body>\n</html>\n')
    # Sur une adresse inconnue (/a/b), les liens relatifs casseraient : on les rend absolus.
    doc = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:)([^"]+)"', r'\1="/\2"', doc)
    doc = re.sub(r'(srcset)="([^"]+)"', lambda m: m.group(1) + '="' + re.sub(r'(^|, )assets/', r'\1/assets/', m.group(2)) + '"', doc)
    (out / "404.html").write_text(doc, encoding="utf-8")

if __name__ == "__main__":
    build()
