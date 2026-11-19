#!/usr/bin/env python3
"""Visuels des trois premiers posts Trails of Impact (Instagram 4:5, LinkedIn PDF)."""
import importlib.util, subprocess, sys, html
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent / "site2"
spec = importlib.util.spec_from_file_location("site_build", SITE / "build.py")
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

OUT_HTML = HERE / "slides" / "html"; OUT_PNG = HERE / "slides" / "png"
OUT_HTML.mkdir(parents=True, exist_ok=True); OUT_PNG.mkdir(parents=True, exist_ok=True)
FONTS = (SITE / "assets" / "fonts").as_uri()
VICTORIA = (SITE / "assets" / "img" / "victoria-900.webp").as_uri()

CSS = f"""
@font-face{{font-family:"Fraunces";font-style:normal;font-weight:100 900;src:url({FONTS}/fraunces-var.woff2) format("woff2")}}
@font-face{{font-family:"Fraunces";font-style:italic;font-weight:100 900;src:url({FONTS}/fraunces-var-italic.woff2) format("woff2")}}
@font-face{{font-family:"Barlow";font-weight:400;src:url({FONTS}/barlow-400.woff2) format("woff2")}}
@font-face{{font-family:"Barlow";font-weight:500;src:url({FONTS}/barlow-500.woff2) format("woff2")}}
@font-face{{font-family:"Barlow";font-weight:600;src:url({FONTS}/barlow-600.woff2) format("woff2")}}
@font-face{{font-family:"Barlow";font-weight:700;src:url({FONTS}/barlow-700.woff2) format("woff2")}}
@font-face{{font-family:"Barlow Condensed";font-weight:500;src:url({FONTS}/barlow-condensed-500.woff2) format("woff2")}}
@font-face{{font-family:"Barlow Condensed";font-weight:600;src:url({FONTS}/barlow-condensed-600.woff2) format("woff2")}}
@font-face{{font-family:"Barlow Condensed";font-weight:700;src:url({FONTS}/barlow-condensed-700.woff2) format("woff2")}}
:root{{--paper:#F6F1EA;--sand:#ECE3D4;--ink:#15231E;--ink2:#3A4A43;--forest:#1B3A30;--green:#2E5E4E;
--lat:#C96E4B;--latd:#A24F2E;--lats:#EDBFA6;--signal:#F2C230;--water:#3F98BE;--waters:#8FD0EA;--waterd:#0D2C39;--cream:#F6F1EA;--white:#FFFDF9}}
*{{box-sizing:border-box}}
html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;-webkit-font-smoothing:antialiased}}
.s{{position:relative;width:1080px;height:1350px;padding:104px 88px 0;overflow:hidden;font-family:Barlow;color:var(--ink)}}
.s>*:not(canvas):not(.foot){{position:relative}}
.forest{{background:var(--forest);color:var(--cream)}} .paper{{background:var(--paper)}} .sand{{background:var(--sand)}}
.lat{{background:var(--lat);color:var(--white)}} .deep{{background:var(--waterd);color:var(--cream)}}
canvas.topo{{position:absolute;inset:0;width:1080px;height:1350px}}
.forest canvas.topo{{color:rgba(246,241,234,.085)}} .deep canvas.topo{{color:rgba(143,208,234,.10)}}
.paper canvas.topo,.sand canvas.topo{{color:rgba(27,58,48,.07)}} .lat canvas.topo{{color:rgba(255,253,249,.13)}}
.eye{{display:flex;align-items:center;gap:20px;font:600 31px/1.2 "Barlow Condensed";letter-spacing:.14em;text-transform:uppercase}}
.eye::before{{content:"";flex:none;width:46px;height:5px;background:radial-gradient(circle at 2.5px 2.5px,currentColor 2.3px,transparent 2.8px) 0 0/11px 5px repeat-x}}
.forest .eye{{color:var(--lats)}} .paper .eye,.sand .eye{{color:var(--latd)}} .deep .eye{{color:var(--waters)}} .lat .eye{{color:var(--white)}}
h1{{margin:38px 0 0;font-family:Fraunces;font-weight:600;font-size:96px;line-height:1.0;letter-spacing:-.025em;font-optical-sizing:auto}}
h1 em{{font-style:italic;font-weight:500}}
.forest h1 em{{color:var(--lats)}} .paper h1 em,.sand h1 em{{color:var(--latd)}} .deep h1 em{{color:var(--waters)}} .lat h1 em{{color:var(--signal)}}
.body{{margin:34px 0 0;font-size:39px;line-height:1.42;max-width:880px}}
.forest .body,.deep .body{{color:rgba(246,241,234,.9)}}
.num{{font-family:"Barlow Condensed";font-weight:700;line-height:.82;letter-spacing:-.012em;font-variant-numeric:lining-nums tabular-nums}}
.foot{{position:absolute;left:88px;right:88px;bottom:62px;display:flex;align-items:center;justify-content:space-between;
font:700 25px/1 "Barlow Condensed";letter-spacing:.15em;text-transform:uppercase}}
.brand{{display:flex;align-items:center;gap:16px}} .brand svg{{width:50px;height:50px}}
.pager{{display:flex;align-items:center;gap:14px;opacity:.75}}
.paper .foot,.sand .foot{{color:var(--forest)}}
.mark-path{{fill:none;stroke-linecap:round}}
.diam{{flex:none;width:30px;height:30px;background:var(--signal);border:4px solid var(--ink);transform:rotate(45deg);margin-top:14px}}
.lat .diam,.forest .diam,.deep .diam{{border-color:var(--forest)}}
.src{{font:500 26px/1.35 Barlow;opacity:.72}}
.mc-t{{font-family:"Barlow Condensed";font-weight:700;font-size:14px;letter-spacing:.1em;fill:var(--cream)}}
.mc-s{{font-family:"Barlow Condensed";font-weight:500;font-size:13px;letter-spacing:.06em;fill:rgba(246,241,234,.75)}}
.mc-w{{font-family:"Barlow Condensed";font-weight:700;font-size:14px;letter-spacing:.1em;fill:var(--waters)}}
"""

TOPO_JS = r"""
(function(){
function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function perlin(seed){var r=rng(seed),p=[],i,j,tmp,perm=new Uint8Array(512);for(i=0;i<256;i++)p[i]=i;
for(i=255;i>0;i--){j=Math.floor(r()*(i+1));tmp=p[i];p[i]=p[j];p[j]=tmp;}for(i=0;i<512;i++)perm[i]=p[i&255];
function g(h,x,y){switch(h&7){case 0:return x+y;case 1:return -x+y;case 2:return x-y;case 3:return -x-y;case 4:return x;case 5:return -x;case 6:return y;default:return -y;}}
function f(t){return t*t*t*(t*(t*6-15)+10);}
return function(x,y){var X=Math.floor(x),Y=Math.floor(y);x-=X;y-=Y;X&=255;Y&=255;var u=f(x),v=f(y);
var aa=perm[X+perm[Y]],ab=perm[X+perm[Y+1]],ba=perm[X+1+perm[Y]],bb=perm[X+1+perm[Y+1]];
var l1=g(aa,x,y)+u*(g(ba,x-1,y)-g(aa,x,y));var l2=g(ab,x,y-1)+u*(g(bb,x-1,y-1)-g(ab,x,y-1));return l1+v*(l2-l1);};}
var MS=[null,[3,2],[2,1],[3,1],[0,1],[0,1,3,2],[0,2],[0,3],[3,0],[0,2],[3,0,2,1],[0,1],[3,1],[2,1],[3,2],null];
document.querySelectorAll('canvas.topo').forEach(function(cv){
var w=1080,h=1350;cv.width=w*2;cv.height=h*2;var ctx=cv.getContext('2d');ctx.setTransform(2,0,0,2,0,0);
var d=cv.dataset,noise=perlin(+d.seed||7),scale=(+d.scale||0.0024)*(900/1350);
var peaks=(d.peaks||'').split(';').filter(Boolean).map(function(s){return s.split(',').map(Number);});
var cell=6,cols=Math.ceil(w/cell)+2,rows=Math.ceil(h/cell)+2,F=new Float32Array(cols*rows),min=1e9,max=-1e9,m=Math.max(w,h);
for(var j=0;j<rows;j++)for(var i=0;i<cols;i++){var x=i*cell,y=j*cell,v=0,amp=1,fr=scale;
for(var o=0;o<4;o++){v+=amp*noise(x*fr+31.7,y*fr+12.3);amp*=.5;fr*=2.03;}
for(var k=0;k<peaks.length;k++){var P=peaks[k],dx=(x-P[0]*w)/(P[2]*m),dy=(y-P[1]*h)/(P[2]*m);v+=P[3]*Math.exp(-(dx*dx+dy*dy));}
F[j*cols+i]=v;if(v<min)min=v;if(v>max)max=v;}
var levels=+d.levels||22;ctx.strokeStyle=getComputedStyle(cv).color;ctx.lineCap='round';ctx.lineJoin='round';
for(var lv=1;lv<levels;lv++){var L=min+(max-min)*lv/levels,major=lv%5===0;ctx.lineWidth=major?2.2:1.2;ctx.globalAlpha=major?1:.7;ctx.beginPath();
for(var jj=0;jj<rows-1;jj++)for(var ii=0;ii<cols-1;ii++){var a=F[jj*cols+ii],b=F[jj*cols+ii+1],c=F[(jj+1)*cols+ii+1],e=F[(jj+1)*cols+ii];
var idx=(a>L?8:0)|(b>L?4:0)|(c>L?2:0)|(e>L?1:0),seg=MS[idx];if(!seg)continue;var x0=ii*cell,y0=jj*cell;
for(var s=0;s<seg.length;s+=2)for(var q=0;q<2;q++){var ed=seg[s+q],px,py;
if(ed===0){px=x0+cell*(L-a)/(b-a);py=y0;}else if(ed===1){px=x0+cell;py=y0+cell*(L-b)/(c-b);}
else if(ed===2){px=x0+cell*(L-e)/(c-e);py=y0+cell;}else{px=x0;py=y0+cell*(L-a)/(e-a);}
if(q===0)ctx.moveTo(px,py);else ctx.lineTo(px,py);}}
ctx.stroke();}});
})();
"""

def mark(size=50, ring="#F6F1EA", hole="#1B3A30", trail="#C96E4B"):
    return (f'<svg viewBox="0 0 200 200" width="{size}" height="{size}">'
            f'<path class="mark-path" d="M40,166 C40,128 108,148 104,104" stroke="{trail}" stroke-width="18"/>'
            f'<path class="mark-path" d="M104,104 C101,72 142,80 146,54" stroke="{trail}" stroke-width="12" stroke-dasharray="0.01 19"/>'
            f'<circle cx="157" cy="41" r="24" fill="{ring}"/><circle cx="157" cy="41" r="9" fill="{hole}"/></svg>')

def foot(i, n, theme):
    dark = theme in ("forest", "deep", "lat")
    ring = "#F6F1EA" if dark else "#1B3A30"
    hole = {"forest": "#1B3A30", "deep": "#0D2C39", "lat": "#C96E4B"}.get(theme, "#F6F1EA")
    trail = "#F6F1EA" if theme == "lat" else "#C96E4B"
    nxt = '<span aria-hidden="true">→</span>' if i < n else ''
    return (f'<div class="foot"><div class="brand">{mark(50, ring, hole, trail)}<span>Trails of Impact</span></div>'
            f'<div class="pager"><span>{i} / {n}</span>{nxt}</div></div>')

def page(theme, inner, i, n, seed=11, peaks="", levels=24, scale=0.0021, extra_css=""):
    return (f'<!doctype html><html lang="fr-CH"><head><meta charset="utf-8"><style>{CSS}{extra_css}</style></head>'
            f'<body><div class="s {theme}"><canvas class="topo" data-seed="{seed}" data-levels="{levels}" data-scale="{scale}" data-peaks="{peaks}"></canvas>'
            f'{inner}{foot(i, n, theme)}</div><script>{TOPO_JS}</script></body></html>')

def nb(s):
    """Typographie française : espaces insécables."""
    return B.fr_typo(s)

SLIDES = {}

# ---------------------------------------------------------------- Post 1 : 106
pts = B.even_points([("L", (112, 800), (900, 800)),
                     ("C", (900, 800), (988, 800), (988, 940), (900, 940)),
                     ("L", (900, 940), (180, 940)),
                     ("C", (180, 940), (92, 940), (92, 1080), (180, 1080)),
                     ("L", (180, 1080), (896, 1080))], 106)
dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8.2" fill="#C96E4B"/>' for x, y in pts)
SLIDES["p1-1"] = page("forest", nb(f"""
<p class="eye">Rentrée 2021 · région de Kpalimé, Togo</p>
<p class="num" style="margin:46px 0 0 -8px;font-size:330px;color:var(--cream)">106</p>
<h1 style="font-size:88px;margin-top:30px">enfants sont allés à l'école. <em>Un point pour chacun.</em></h1>
<svg viewBox="0 0 1080 1350" width="1080" height="1350" style="position:absolute;left:0;top:0">
  {dots}
  <circle cx="960" cy="1080" r="27" fill="#F6F1EA"/><circle cx="960" cy="1080" r="10" fill="#1B3A30"/>
  <text x="960" y="1146" text-anchor="middle" style="font:700 27px 'Barlow Condensed';letter-spacing:.14em;fill:#F6F1EA">L'ÉCOLE</text>
  <text x="104" y="1160" style="font:600 25px 'Barlow Condensed';letter-spacing:.1em;fill:rgba(246,241,234,.7)">LE CHEMIN DE L'ÉCOLE POUR TOUS</text>
</svg>"""), 1, 4, seed=11, peaks="0.80,0.16,0.15,1.35;0.14,0.30,0.12,0.7")

obst = "".join(f'<li style="display:flex;gap:34px;align-items:flex-start"><span class="diam"></span><span>{t}</span></li>'
               for t in ["Des frais de scolarité trop lourds.", "Des fournitures qui manquent.", "De l'eau à aller chercher, avant la classe."])
SLIDES["p1-2"] = page("paper", nb(f"""
<p class="eye">Pourquoi nous existons</p>
<h1>Entre un enfant et l'école, il y a <em>un chemin.</em></h1>
<p class="body">Sur ce chemin, les obstacles sont concrets. Ils ont un prix, une distance, un horaire.</p>
<ul style="list-style:none;margin:58px 0 0;padding:0 0 0 6px;display:grid;gap:40px;font:600 46px/1.2 Barlow;color:var(--forest)">{obst}</ul>
<p style="margin:64px 0 0;font:italic 500 54px/1.15 Fraunces;color:var(--latd)">On peut les mesurer, donc on peut les lever.</p>
"""), 2, 4, seed=29)

bal = [("Un projet à la fois", "Rien de nouveau tant que le projet en cours ne tient pas debout tout seul."),
       ("Les gens sur place décident", "Le besoin se définit avec le village et notre partenaire local."),
       ("Tout est publié", "Chaque étape, chaque document et chaque franc."),
       ("On revient à 1, 3 et 5 ans", "Un forage est réussi quand l'eau coule encore cinq ans plus tard.")]
bal_html = "".join(f'<li style="position:relative;padding-top:64px"><span class="diam" style="position:absolute;left:4px;top:0;margin:0"></span>'
                   f'<p style="margin:0;font:600 44px/1.08 Fraunces;letter-spacing:-.015em;color:var(--forest)">{t}</p>'
                   f'<p style="margin:16px 0 0;font:400 31px/1.4 Barlow;color:var(--ink2)">{d}</p></li>' for t, d in bal)
SLIDES["p1-3"] = page("sand", nb(f"""
<p class="eye">Notre méthode</p>
<h1 style="font-size:112px">Celle du <em>trail.</em></h1>
<p class="body">Un parcours balisé, des étapes vérifiées, et on ne s'arrête qu'une fois arrivé.</p>
<ul style="list-style:none;margin:62px 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:60px 64px">{bal_html}</ul>
"""), 3, 4, seed=41)

SLIDES["p1-4"] = page("forest", nb(f"""
<p class="eye">Association en création · Fribourg</p>
<h1 style="font-size:150px;line-height:.95;margin-top:54px">Un chemin<br><em>à la fois.</em></h1>
<p class="body" style="margin-top:56px">Premier projet à l'étude : l'eau potable à Govié-Akpato, près de Kpalimé, au Togo.</p>
<p class="body" style="margin-top:22px">Ici, nous publierons chaque étape. Y compris ce que nous ne savons pas encore.</p>
<div style="position:absolute;left:88px;right:88px;top:1000px;padding-top:34px;border-top:3px solid rgba(246,241,234,.35);display:flex;justify-content:space-between;align-items:baseline">
  <span style="font:600 31px 'Barlow Condensed';letter-spacing:.14em;text-transform:uppercase;color:var(--lats)">Suivez le chemin</span>
  <span style="font:700 60px 'Barlow Condensed';letter-spacing:.02em;color:var(--cream)">trailsofimpact.org</span>
</div>
"""), 4, 4, seed=23, peaks="0.75,0.30,0.18,1.2")

# ---------------------------------------------------------------- Post 2 : deux dossards
def bib(n, role, rot):
    holes = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#C96E4B" stroke="#15231E" stroke-width="2"/>' for x, y in [(30, 30), (370, 30), (30, 330), (370, 330)])
    return (f'<div style="position:relative;width:400px;height:360px;transform:rotate({rot}deg);filter:drop-shadow(0 18px 28px rgba(60,20,8,.35))">'
            f'<svg viewBox="0 0 400 360" width="400" height="360" style="position:absolute;inset:0">'
            f'<rect width="400" height="360" rx="14" fill="#FFFDF9"/><rect y="0" width="400" height="74" rx="14" fill="#F2C230"/>'
            f'<rect y="40" width="400" height="34" fill="#F2C230"/>{holes}</svg>'
            f'<p style="position:absolute;left:0;right:0;top:20px;margin:0;text-align:center;font:700 23px \'Barlow Condensed\';letter-spacing:.16em;color:#1C1A12">COMITÉ FONDATEUR</p>'
            f'<p class="num" style="position:absolute;left:0;right:0;top:100px;margin:0;text-align:center;font-size:170px;color:#1B3A30">{n}</p>'
            f'<p style="position:absolute;left:0;right:0;bottom:30px;margin:0;text-align:center;font:700 34px \'Barlow Condensed\';letter-spacing:.14em;color:#15231E">{role}</p></div>')

SLIDES["p2-1"] = page("lat", nb(f"""
<p class="eye">Nous recrutons · bénévolat à Fribourg</p>
<h1 style="font-size:124px;line-height:.98;margin-top:48px;color:var(--white)">Il reste <em>deux dossards.</em></h1>
<div style="display:flex;gap:48px;justify-content:center;margin-top:118px">{bib(2, "TRÉSORERIE", -4)}{bib(3, "SECRÉTARIAT", 3)}</div>
"""), 1, 4, seed=53, peaks="0.2,0.85,0.2,1.1")

def role_slide(n, title, items, i):
    li = "".join(f'<li style="display:flex;gap:34px;align-items:flex-start"><span class="diam"></span><span>{t}</span></li>' for t in items)
    return page("paper", nb(f"""
<p class="eye">Dossard n° {n} · comité fondateur</p>
<h1 style="font-size:118px">{title}</h1>
<ul style="list-style:none;margin:70px 0 0;padding:0 0 0 6px;display:grid;gap:46px;font:500 44px/1.3 Barlow;color:var(--forest);max-width:840px">{li}</ul>
<p class="num" style="position:absolute;right:70px;bottom:120px;margin:0;font-size:430px;color:transparent;-webkit-text-stroke:4px var(--lat);opacity:.55">{n}</p>
"""), i, 4, seed=61 + n)

SLIDES["p2-2"] = role_slide(2, "Trésorier·ère", ["Tenir les comptes et préparer le budget annuel.",
                                                "Publier les chiffres de notre carnet de route.",
                                                "Préparer la vérification des comptes."], 2)
SLIDES["p2-3"] = role_slide(3, "Secrétaire", ["Rédiger les procès-verbaux des séances.",
                                             "Tenir à jour la liste des membres.",
                                             "Gérer le courrier et les convocations."], 3)

chips = "".join(f'<li style="padding:16px 26px;border:2px solid rgba(246,241,234,.55);border-radius:999px;font:600 30px/1 \'Barlow Condensed\';letter-spacing:.1em;text-transform:uppercase">{c}</li>'
                for c in ["Bénévole", "Quelques heures par mois", "Fribourg et environs", "Dès l'hiver 2026–2027"])
SLIDES["p2-4"] = page("forest", nb(f"""
<p class="eye">Ce qu'il faut</p>
<h1 style="font-size:92px">De la rigueur, et l'envie de <em>tenir dans la durée.</em></h1>
<p class="body">Pas besoin d'être expert·e.</p>
<ul style="list-style:none;margin:44px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:16px">{chips}</ul>
<div style="position:absolute;left:88px;right:88px;top:910px;display:flex;gap:40px;align-items:center">
  <img src="{VICTORIA}" alt="" style="width:210px;height:210px;border-radius:50%;object-fit:cover;border:5px solid var(--lats)">
  <div><p style="margin:0;font:400 33px/1.4 Barlow;color:rgba(246,241,234,.9)">Vous formerez le comité fondateur avec Victoria Goepfert, fondatrice.</p>
  <p style="margin:18px 0 0;font:700 44px/1 'Barlow Condensed';letter-spacing:.02em;color:var(--cream)">victoria@trailsofimpact.org</p></div>
</div>
"""), 4, 4, seed=71, peaks="0.85,0.75,0.2,1.1")

# ---------------------------------------------------------------- Post 3 : l'eau
coupe_svg = B.mini_coupe().replace('<svg viewBox="0 0 320 400"', '<svg viewBox="0 0 320 400" width="560" height="700"')
SLIDES["p3-1"] = page("deep", nb(f"""
<p class="eye">Projet en étude · Govié-Akpato, Togo</p>
<h1 style="font-size:84px;max-width:900px">Quelque part entre 46 et 106 mètres, il y a <em>probablement</em> de l'eau.</h1>
<div style="position:absolute;left:250px;top:560px">{coupe_svg}</div>
"""), 1, 5, seed=29, peaks="0.72,0.35,0.2,-1.3", extra_css=".mc-s{font-size:12px}")

# Distances : village -> rivières (1,5 km et 2,7 km), échelle 0 à 3 km sur 860 px
X0, W = 110, 830
x = lambda km: X0 + W * km / 3.0
def river(km, label):
    xx = x(km)
    wave = " ".join(f"M{xx-26},{y} q13,-10 26,0 t26,0" for y in (992, 1012, 1032))
    return (f'<path d="{wave}" fill="none" stroke="#3F98BE" stroke-width="6" stroke-linecap="round"/>'
            f'<text x="{xx}" y="1090" text-anchor="middle" style="font:700 40px \'Barlow Condensed\';fill:#0D2C39">{label}</text>'
            f'<text x="{xx}" y="1126" text-anchor="middle" style="font:600 22px \'Barlow Condensed\';letter-spacing:.12em;fill:#3A4A43">RIVIÈRE</text>')
dist_svg = f"""<svg viewBox="0 0 1080 1350" width="1080" height="1350" style="position:absolute;left:0;top:0">
  <line x1="{X0}" y1="1012" x2="{x(2.7)}" y2="1012" stroke="#C96E4B" stroke-width="7" stroke-linecap="round" stroke-dasharray="0.1 18"/>
  <circle cx="{X0}" cy="1012" r="24" fill="#1B3A30"/><circle cx="{X0}" cy="1012" r="9" fill="#F6F1EA"/>
  <text x="{X0-22}" y="1090" style="font:700 40px 'Barlow Condensed';fill:#1B3A30">Le village</text>
  {river(1.5, "1,5 km")}{river(2.7, "2,7 km")}
</svg>"""
SLIDES["p3-2"] = page("paper", nb(f"""
<p class="eye">Govié-Akpato · région de Kpalimé</p>
<h1 style="font-size:104px">Un village, <em>deux rivières.</em></h1>
<div style="display:flex;gap:70px;margin-top:62px;align-items:flex-end">
  <div><p class="num" style="margin:0;font-size:190px;color:var(--latd)">≈ 794</p><p style="margin:14px 0 0;font:600 34px 'Barlow Condensed';letter-spacing:.12em;text-transform:uppercase;color:var(--forest)">habitants</p></div>
  <div><p class="num" style="margin:0;font-size:190px;color:var(--latd)">513</p><p style="margin:14px 0 0;font:600 34px 'Barlow Condensed';letter-spacing:.12em;text-transform:uppercase;color:var(--forest)">enfants</p></div>
</div>
<p class="body" style="margin-top:56px">Aujourd'hui, l'eau se puise dans deux rivières.</p>
{dist_svg}
<p class="src" style="position:absolute;left:88px;right:88px;top:1168px;margin:0">Premier recensement de notre partenaire local. L'étude des besoins le vérifiera.</p>
"""), 2, 5, seed=37)

def check(title, text, status, cls):
    st = {"now": "background:var(--signal);color:#1C1A12", "todo": "border:2px dashed var(--ink2);color:var(--ink2)",
          "part": "background:var(--forest);color:var(--cream)"}[cls]
    return (f'<li style="position:relative;padding:34px 0 34px 0;border-top:2px solid rgba(21,35,30,.18)">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:24px">'
            f'<p style="margin:0;font:600 48px/1.05 Fraunces;letter-spacing:-.015em;color:var(--forest)">{title}</p>'
            f'<span style="flex:none;padding:12px 20px;border-radius:999px;font:700 22px/1 \'Barlow Condensed\';letter-spacing:.12em;text-transform:uppercase;{st}">{status}</span></div>'
            f'<p style="margin:14px 0 0;font:400 32px/1.4 Barlow;color:var(--ink2);max-width:860px">{text}</p></li>')
SLIDES["p3-3"] = page("sand", nb(f"""
<p class="eye">Avant de forer</p>
<h1 style="font-size:112px">On vérifie <em>tout.</em></h1>
<ul style="list-style:none;margin:56px 0 0;padding:0">
{check("Le besoin réel", "Combien de familles boivent à quel point d'eau, qui y va, et à quelle heure. Mesuré avec le village et notre partenaire local.", "Printemps 2027", "todo")}
{check("Le meilleur emplacement", "Une seconde étude, par un hydrogéologue indépendant de l'entreprise de forage.", "Fait en partie", "part")}
{check("Le juste prix", "Trois devis sur le même cahier des charges, un paiement par étapes, une règle claire en cas de forage sec.", "1 devis sur 3", "now")}
</ul>
<p style="margin:26px 0 0;font:italic 500 37px/1.25 Fraunces;color:var(--latd)">Puis un essai de pompage et une analyse en laboratoire. Sans ces deux résultats, on ne construit rien.</p>
"""), 3, 5, seed=43)

unk = [("Le débit réel", "Seul un essai de pompage le dira."), ("La qualité de l'eau", "Une analyse en laboratoire est prévue."),
       ("Le coût final", "Nous attendons trois devis comparables."), ("Le nombre exact d'usagers", "L'étude des besoins le vérifiera.")]
unk_html = "".join(f'<li style="display:flex;gap:30px;align-items:flex-start;padding:30px 0;border-top:2px solid rgba(21,35,30,.16)">'
                   f'<span style="flex:none;width:62px;height:62px;border-radius:50%;border:3px dashed var(--water);display:grid;place-items:center;font:700 38px/1 Fraunces;color:var(--water)">?</span>'
                   f'<span><span style="display:block;font:600 46px/1.1 Fraunces;color:var(--forest);letter-spacing:-.015em">{t}</span>'
                   f'<span style="display:block;margin-top:10px;font:400 32px/1.35 Barlow;color:var(--ink2)">{d}</span></span></li>' for t, d in unk)
SLIDES["p3-4"] = page("paper", nb(f"""
<p class="eye">Transparence</p>
<h1 style="font-size:100px">Ce que nous ne savons <em>pas encore.</em></h1>
<ul style="list-style:none;margin:56px 0 0;padding:0">{unk_html}</ul>
<p style="margin:22px 0 0;font:italic 500 40px/1.25 Fraunces;color:var(--latd)">Nous l'écrirons dès que nous le saurons.</p>
"""), 4, 5, seed=47)

SLIDES["p3-5"] = page("deep", nb(f"""
<p class="eye">Le budget</p>
<h1 style="font-size:96px">Ce que coûte un forage <em>qui dure.</em></h1>
<div style="margin-top:70px;display:flex;height:120px;border-radius:14px;overflow:hidden;font:700 40px/1 'Barlow Condensed'">
  <div style="flex:11800;background:var(--water);display:flex;align-items:center;padding-left:30px;color:var(--white)">≈ 11 800 CHF</div>
  <div style="flex:3200;background:repeating-linear-gradient(-45deg,#8FD0EA 0 12px,#5FB3D6 12px 24px);display:flex;align-items:center;justify-content:center;color:var(--waterd)">≈ 3 200</div>
</div>
<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:44px;margin-top:34px;font:400 29px/1.4 Barlow;color:rgba(246,241,234,.86)">
  <p style="margin:0"><b style="display:block;font:700 28px 'Barlow Condensed';letter-spacing:.12em;text-transform:uppercase;color:var(--cream);margin-bottom:8px">Devis local, oct. 2025</b>Forage de 100 m, pompe solaire, château d'eau, quatre robinets, main-d'œuvre et transport.</p>
  <p style="margin:0"><b style="display:block;font:700 28px 'Barlow Condensed';letter-spacing:.12em;text-transform:uppercase;color:var(--waters);margin-bottom:8px">À prévoir en plus</b>Essai de pompage, analyses, contrôle indépendant, formation, fonds d'entretien, imprévus.</p>
</div>
<p class="num" style="margin:64px 0 0;font-size:150px;color:var(--cream)">≈ 15 000 CHF</p>
<p style="margin:22px 0 0;font:400 30px/1.4 Barlow;color:rgba(246,241,234,.75)">Estimation provisoire, à confirmer par trois devis comparables. Les dons ouvriront à la création officielle de l'association.</p>
<p style="position:absolute;left:88px;right:88px;top:1150px;margin:0;font:700 46px 'Barlow Condensed';letter-spacing:.02em;color:var(--waters)">trailsofimpact.org <span style="font-weight:600;color:rgba(246,241,234,.75)">· Le projet eau</span></p>
"""), 5, 5, seed=31, peaks="0.2,0.8,0.2,1.0")

if __name__ == "__main__":
    only = sys.argv[1:]
    for name, doc in SLIDES.items():
        if only and name not in only:
            continue
        f = OUT_HTML / f"{name}.html"; f.write_text(doc, encoding="utf-8")
        subprocess.run(["node", str(HERE / "render" / "render.js"), str(f), str(OUT_PNG / f"{name}.png"), "1080", "1350", "1"], check=True)
        print("ok", name)
