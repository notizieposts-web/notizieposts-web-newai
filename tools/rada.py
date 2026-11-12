"""Rada, la fatina degli aiuti: un solo disegno originale (testa, capelli lilla, ali, vestito a petali, bacchetta), nove espressioni, animata.
Uso:
  import rada; rada.svg('idea', 48)            SVG da mettere nella pagina (colori del tema, animazioni in rada.CSS)
  python3 tools/rada.py <repo>                 scrive i file img/rada/rada-<espressione>.svg (colori fissi, animazioni dentro il file)
Espressioni: ciao, parla, idea, pensa, spiega, felice, coraggio, curiosa, conta.
Il disegno è originale di Radar AI. Le animazioni si fermano con "riduci movimento".
"""
import os, sys

EXPR = ['ciao', 'parla', 'idea', 'pensa', 'spiega', 'felice', 'coraggio', 'curiosa', 'conta']
LABEL = {'ciao': 'Rada saluta', 'parla': 'Rada parla', 'idea': 'Rada ha un\'idea', 'pensa': 'Rada pensa', 'spiega': 'Rada spiega',
         'felice': 'Rada festeggia', 'coraggio': 'Rada ti incoraggia', 'curiosa': 'Rada è curiosa', 'conta': 'Rada fa i conti'}
# colori della fatina: fissi, uguali in tema chiaro e scuro (il personaggio non cambia colore)
PAL = {'O': '#2B2250', 'S': '#FAD7BE', 'S2': '#F2BFA0', 'H': '#8E6CF0', 'H2': '#B9A3FF', 'D': '#7C5CFF', 'D2': '#B9A8FF', 'B': '#16A2B8',
       'G': '#E2DAFF', 'G2': '#FFE7A3', 'GW': '#9B87FF', 'Y': '#FFC94D', 'P': '#F59AB5', 'T': '#0A9BB5', 'I': '#2B2250', 'M': '#FFFFFF', 'W': '#FFFFFF', 'V': '#7C5CFF'}
PAL.update({'A': '#FAD7BE', 'R': '#4B3FBF', 'R2': '#6A5CE0', 'BE': '#F4F2FB', 'HT': '#3A2E9A', 'GL': '#C99A2E'})
SAGE = dict(PAL, A='#3F31A3', H='#2E2470', R='#5B4BC8', R2='#DCD5FF', BE='#F6F4FC', BK='#F59E2B')
CHARS = {'saggio': ('Sapio', 'il gufo saggio'), 'fatina': ('Rada', 'la fatina')}
THEME = PAL
FIXED = PAL

# animazioni: valgono per l'SVG nella pagina (rada.CSS) e, identiche, dentro i file
ANIM = '''.rd-wingL{transform-box:fill-box;transform-origin:100% 70%;animation:rd-flapL .38s ease-in-out infinite alternate}
.rd-wingR{transform-box:fill-box;transform-origin:0% 70%;animation:rd-flapR .38s ease-in-out infinite alternate}
.rd-star{transform-box:fill-box;transform-origin:center;animation:rd-star 2.2s ease-in-out infinite}
.rd-dust{transform-box:fill-box;transform-origin:center;animation:rd-dust 3s ease-in infinite}.rd-dust.b{animation-delay:1s}.rd-dust.c{animation-delay:2s}
.rd-shine{animation:rd-shine 3s ease-in-out infinite}
.rd-all{transform-box:fill-box;transform-origin:50% 100%;animation:rd-float 2.4s ease-in-out infinite}
.rd-look{animation:rd-look 5s ease-in-out infinite}
.rd-swing{transform-box:fill-box;transform-origin:100% 0%;animation:rd-swing 1.6s ease-in-out infinite alternate}
.rd-tip{transform-box:fill-box;transform-origin:center;animation:rd-tip 1.2s ease-in-out infinite alternate}
.rd-cheek{animation:rd-cheek 2.4s ease-in-out infinite}
.rd-dust,.rd-look,.rd-eyes,.rd-mouth-t,.rd-wave,.rd-bulb,.rd-ping,.rd-spark,.rd-dot,.rd-drop,.rd-sym,.rd-armL,.rd-armR,.rd-q{transform-box:fill-box;transform-origin:center}
.rd-eyes{animation:rd-blink 3.2s infinite}
.rd-ping{animation:rd-ping 2.4s ease-out infinite;transform-origin:50% 100%}
.rd-ping.b{animation-delay:.5s}
.rd-wave{transform-origin:0% 100%;animation:rd-wave .55s ease-in-out infinite alternate}
.rd-mouth-t{animation:rd-talk .24s ease-in-out infinite alternate}
.rd-snd{animation:rd-fade 1s ease-in-out infinite}.rd-snd.b{animation-delay:.3s}
.rd-bulb{animation:rd-pop 1.4s ease-in-out infinite alternate}
.rd-dot{animation:rd-fade 1.6s ease-in-out infinite}.rd-dot.b{animation-delay:.25s}.rd-dot.c{animation-delay:.5s}
.rd-spark{animation:rd-twinkle 1.1s ease-in-out infinite alternate}.rd-spark.b{animation-delay:.35s}.rd-spark.c{animation-delay:.7s}
.rd-jump{animation:rd-jump .5s cubic-bezier(.3,0,.5,1) infinite alternate}
.rd-drop{animation:rd-drop 1.8s ease-in infinite}
.rd-sym{animation:rd-bob 1.8s ease-in-out infinite alternate}.rd-sym.b{animation-delay:.4s}.rd-sym.c{animation-delay:.8s}
.rd-q{animation:rd-tilt 1.6s ease-in-out infinite alternate}
.rd-point{transform-box:fill-box;transform-origin:0% 100%;animation:rd-point .8s ease-in-out infinite alternate}
.rd-fist{transform-box:fill-box;transform-origin:100% 100%;animation:rd-fist .5s ease-in-out infinite alternate}
@keyframes rd-float{0%,100%{transform:translateY(0) rotate(0deg) scale(1,1)}25%{transform:translateY(-5px) rotate(-2.5deg) scale(.98,1.03)}50%{transform:translateY(-7px) rotate(0deg) scale(1,1)}75%{transform:translateY(-5px) rotate(2.5deg) scale(.98,1.03)}}
@keyframes rd-flapL{from{transform:rotate(8deg) scaleX(1)}to{transform:rotate(-14deg) scaleX(.72)}}
@keyframes rd-flapR{from{transform:rotate(-8deg) scaleX(1)}to{transform:rotate(14deg) scaleX(.72)}}
@keyframes rd-star{0%,100%{transform:rotate(0deg) scale(1)}50%{transform:rotate(72deg) scale(1.22)}}
@keyframes rd-dust{0%{transform:translateY(8px) scale(.3);opacity:0}20%{opacity:1}100%{transform:translateY(-26px) scale(1) rotate(90deg);opacity:0}}
@keyframes rd-shine{0%,100%{opacity:.35}50%{opacity:.75}}
@keyframes rd-look{0%,30%,100%{transform:translateX(0)}38%,55%{transform:translateX(-2.5px)}63%,80%{transform:translateX(2.5px)}}
@keyframes rd-swing{from{transform:rotate(-12deg)}to{transform:rotate(10deg)}}
@keyframes rd-tip{from{transform:scale(.85)}to{transform:scale(1.25)}}
@keyframes rd-cheek{0%,100%{opacity:.35}50%{opacity:.75}}
@keyframes rd-blink{0%,93%,100%{transform:scaleY(1)}96.5%{transform:scaleY(.08)}}
@keyframes rd-ping{0%{opacity:.9;transform:scale(.5)}100%{opacity:0;transform:scale(1.25)}}
@keyframes rd-wave{from{transform:rotate(-18deg)}to{transform:rotate(24deg)}}
@keyframes rd-talk{from{transform:scaleY(.3)}to{transform:scaleY(1.4)}}
@keyframes rd-fade{0%,100%{opacity:.15}50%{opacity:1}}
@keyframes rd-pop{from{transform:scale(.8) rotate(-6deg)}to{transform:scale(1.2) rotate(6deg)}}
@keyframes rd-twinkle{from{transform:scale(.4) rotate(0deg);opacity:.3}to{transform:scale(1.1) rotate(25deg);opacity:1}}
@keyframes rd-jump{from{transform:translateY(0) scale(1.04,.96)}to{transform:translateY(-12px) scale(.97,1.04)}}
@keyframes rd-drop{0%{transform:translateY(-3px);opacity:0}25%{opacity:1}100%{transform:translateY(9px);opacity:0}}
@keyframes rd-bob{from{transform:translateY(4px) rotate(-8deg)}to{transform:translateY(-5px) rotate(8deg)}}
@keyframes rd-tilt{from{transform:rotate(-14deg) translateY(2px)}to{transform:rotate(14deg) translateY(-3px)}}
@keyframes rd-point{from{transform:rotate(4deg)}to{transform:rotate(-16deg)}}
@keyframes rd-fist{from{transform:rotate(-6deg)}to{transform:rotate(16deg)}}
@media (prefers-reduced-motion:reduce){.rd-all,.rd-all *{animation:none!important}}'''

CSS = '<style id="rada-css">.rd{flex:none;overflow:visible;vertical-align:middle}\n' + ANIM + '\n.rd-row{display:flex;gap:.7rem;align-items:center}.rd-row>:last-child{flex:1;min-width:0}</style>'


EX, EY = (52, 34), (68, 34)


def _eyes(kind, lashes=True):
    def dot(x, y, r=4.1):
        return ('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="{O}"/><circle cx="%s" cy="%s" r="%s" fill="{M}"/><circle cx="%s" cy="%s" r="%s" fill="{M}"/>'
                % (x, y, r, round(r * 1.12, 2), round(x + r * .35, 2), round(y - r * .45, 2), round(r * .38, 2), round(x - r * .35, 2), round(y + r * .4, 2), round(r * .18, 2)))
    lash = '<path d="M46.5 31 l-3 -2 M47.5 28.6 l-2 -2.8 M73.5 31 l3 -2 M72.5 28.6 l2 -2.8" stroke="{O}" stroke-width="1.4" stroke-linecap="round"/>'
    brow = lambda d: '<path d="%s" fill="none" stroke="{H}" stroke-width="2.2" stroke-linecap="round"/>' % d
    arc = lambda x: '<path d="M%s 35 Q%s 29.5 %s 35" fill="none" stroke="{O}" stroke-width="2.6" stroke-linecap="round"/>' % (x - 4.5, x, x + 4.5)
    if not lashes: lash = ''
    if kind == 'happy': return arc(52) + arc(68) + lash
    if kind == 'up': return dot(52.5, 32.5, 3.9) + dot(68.5, 32.5, 3.9) + lash + brow('M47 25.5 Q52 23 56 25') + brow('M64 25 Q68 23 73 25.5')
    if kind == 'soft': return dot(52, 34.5, 3.9) + dot(68, 34.5, 3.9) + lash + brow('M47 27.5 L56 25.5') + brow('M73 27.5 L64 25.5')
    if kind == 'curious': return dot(52, 34.5, 3.4) + dot(68, 33.5, 4.9) + lash + brow('M63.5 25.5 Q68.5 21.5 74 25')
    if kind == 'wide': return dot(52, 33.5, 4.6) + dot(68, 33.5, 4.6) + lash + brow('M46.5 25 Q52 21.5 56.5 24.5') + brow('M63.5 24.5 Q68 21.5 73.5 25')
    if kind == 'focus': return dot(52, 34.5, 3.6) + dot(68, 34.5, 3.6) + lash + brow('M47 26 L56.5 27.5') + brow('M73 26 L63.5 27.5')
    return dot(52, 34) + dot(68, 34) + lash


def _mouth(kind):
    if kind == 'open': return '<path d="M54.5 41.5 Q60 50.5 65.5 41.5 Z" fill="{O}"/><ellipse cx="60" cy="46" rx="2.8" ry="1.6" fill="{P}"/>'
    if kind == 'talk': return '<ellipse class="rd-mouth-t" cx="60" cy="43.5" rx="3.4" ry="2.9" fill="{O}"/>'
    if kind == 'o': return '<ellipse cx="61" cy="43.5" rx="2.1" ry="2.5" fill="{O}"/>'
    if kind == 'flat': return '<path d="M56 44 Q60 45.5 64 42.5" fill="none" stroke="{O}" stroke-width="2.2" stroke-linecap="round"/>'
    if kind == 'small': return '<path d="M56 42.5 Q60 46 64 42.5" fill="none" stroke="{O}" stroke-width="2.2" stroke-linecap="round"/>'
    return '<path d="M54.5 41.5 Q60 47.5 65.5 41.5" fill="none" stroke="{O}" stroke-width="2.4" stroke-linecap="round"/>'


def _arm(d, hx, hy, cls=''):
    """braccio con contorno: prima la linea scura, poi la pelle; la mano è un cerchietto"""
    return ('<g%s><path d="%s" fill="none" stroke="{O}" stroke-width="6.6" stroke-linecap="round"/><path d="%s" fill="none" stroke="{A}" stroke-width="4.2" stroke-linecap="round"/>'
            '<circle cx="%s" cy="%s" r="3.9" fill="{S}" stroke="{O}" stroke-width="1.3"/></g>') % ((' class="%s"' % cls) if cls else '', d, d, hx, hy)


def _wand(x1, y1, x2, y2, cls='rd-star'):
    return ('<path d="M%s %s L%s %s" stroke="{O}" stroke-width="2.6" stroke-linecap="round"/><path d="M%s %s L%s %s" stroke="{Y}" stroke-width="1.2" stroke-linecap="round"/>' % (x1, y1, x2, y2, x1, y1, x2, y2) +
            '<g transform="translate(%s %s)"><circle class="rd-ping" r="8" fill="{G2}" opacity=".75"/><path class="%s" d="M0 -7 L2 -2.4 L7 -2.2 L3.1 1 L4.4 6 L0 3.2 L-4.4 6 L-3.1 1 L-7 -2.2 L-2 -2.4 Z" fill="{Y}" stroke="{O}" stroke-width="1.1" stroke-linejoin="round"/></g>' % (x2, y2, cls))

L_DOWN = _arm('M50 61 Q42 70 42 80', 42, 80, 'rd-swing')
R_DOWN = _arm('M70 61 Q78 70 78 80', 78, 80, 'rd-swing')
SPARK = '<path class="rd-spark %s" d="M%s %s l2.2 5 l5 2.2 l-5 2.2 l-2.2 5 l-2.2 -5 l-5 -2.2 l5 -2.2 z" fill="%s"/>'

POSE = {
    'ciao': dict(eyes='normal', mouth='smile', arms=L_DOWN + _arm('M70 61 Q84 54 86 38', 86, 38, 'rd-wave'), extra=''),
    'parla': dict(eyes='normal', mouth='talk', arms=R_DOWN + '<g class="rd-point">' + _arm('M50 61 Q40 62 36 54', 36, 54) + '</g>',
                  extra='<path class="rd-snd" d="M30 36 Q26 43 30 50" fill="none" stroke="{T}" stroke-width="2.2" stroke-linecap="round"/><path class="rd-snd b" d="M24 32 Q18 43 24 54" fill="none" stroke="{T}" stroke-width="2.2" stroke-linecap="round"/>'),
    'idea': dict(eyes='wide', mouth='open', arms=L_DOWN + '<g class="rd-point">' + _arm('M70 61 Q82 58 87 49', 87, 49) + _wand(88, 47, 100, 24, 'rd-bulb rd-star') + '</g>',
                 extra='<path d="M100 8 v-5 M89 13 l-3.5 -3.5 M111 13 l3.5 -3.5 M86 24 h-4 M114 24 h4" stroke="{Y}" stroke-width="2.4" stroke-linecap="round"/>'),
    'pensa': dict(eyes='up', mouth='flat', arms=L_DOWN + _arm('M70 61 Q78 54 66 49', 65, 49),
                  extra='<circle class="rd-dot" cx="86" cy="18" r="2.4" fill="{T}"/><circle class="rd-dot b" cx="94" cy="9" r="3.4" fill="{T}"/><circle class="rd-dot c" cx="104" cy="-2" r="4.8" fill="{T}"/>'),
    'spiega': dict(eyes='normal', mouth='open', arms=L_DOWN + '<g class="rd-point">' + _arm('M70 61 Q80 58 84 52', 84, 52) + _wand(85, 50, 92, 38) + '</g>',
                   extra='<g><rect x="95" y="2" width="25" height="31" rx="4" fill="{W}" stroke="{O}" stroke-width="2"/><path d="M99.5 10.5 h3 M99.5 17.5 h3 M99.5 24.5 h3" stroke="{T}" stroke-width="2.8" stroke-linecap="round"/><path d="M106 10.5 h9.5 M106 17.5 h9.5 M106 24.5 h6.5" stroke="{O}" stroke-width="2" stroke-linecap="round"/></g>'),
    'felice': dict(eyes='happy', mouth='open', arms='<g class="rd-fist">' + _arm('M50 61 Q38 50 36 36', 36, 36) + '</g>' + '<g class="rd-wave">' + _arm('M70 61 Q82 50 84 36', 84, 36) + _wand(85, 34, 94, 18) + '</g>',
                   extra=(SPARK % ('', 18, 4, '{Y}')) + (SPARK % ('b', 104, 40, '{P}')) + (SPARK % ('c', 10, 54, '{T}')) + (SPARK % ('b', 106, 2, '{Y}')), jump=True),
    'coraggio': dict(eyes='soft', mouth='small', arms='<g class="rd-fist">' + _arm('M50 61 Q38 58 38 46', 38, 46) + '</g>' + R_DOWN,
                     extra='<path class="rd-drop" d="M80 14 q3.4 5 0 7.6 q-3.4 -2.6 0 -7.6 z" fill="{T}"/><path d="M26 36 l4.5 2.5 M24 45 h5.5 M27 54 l4.5 -2.5" stroke="{Y}" stroke-width="2.4" stroke-linecap="round"/>'),
    'curiosa': dict(eyes='curious', mouth='o', arms=L_DOWN + _arm('M70 61 Q88 52 86 28', 86, 28),
                    extra='<g class="rd-q"><path d="M96 2 q0 -8 7.5 -8 q7.5 0 7.5 7 q0 4.6 -5 7 q-2.4 1.1 -2.4 4.6" fill="none" stroke="{T}" stroke-width="3.2" stroke-linecap="round"/><circle cx="103.6" cy="18.5" r="2.2" fill="{T}"/></g>'),
    'conta': dict(eyes='focus', mouth='small', arms='<g class="rd-fist">' + _arm('M50 61 Q38 60 36 48', 36, 48) + '</g><g class="rd-point">' + _arm('M70 61 Q82 60 84 48', 84, 48) + '</g>',
                  extra='<path class="rd-sym" d="M14 20 h11 M19.5 14.5 v11" stroke="{T}" stroke-width="3" stroke-linecap="round"/><path class="rd-sym b" d="M96 12 l9 9 M105 12 l-9 9" stroke="{Y}" stroke-width="3" stroke-linecap="round"/><path class="rd-sym c" d="M98 32 h11 M98 37.5 h11" stroke="{P}" stroke-width="2.8" stroke-linecap="round"/>'),
}

WINGS = ('<g class="rd-wingL"><path d="M51 62 C34 28 4 30 10 52 C13 62 30 66 51 66 Z" fill="{G}" stroke="{GW}" stroke-width="1.8" stroke-linejoin="round" opacity=".95"/>'
         '<path d="M51 68 C34 70 18 84 26 92 C33 98 46 84 51 72 Z" fill="{G}" stroke="{GW}" stroke-width="1.8" stroke-linejoin="round" opacity=".95"/>'
         '<path d="M48 63 C36 50 22 44 16 48 M48 70 C40 76 32 84 30 89" fill="none" stroke="{GW}" stroke-width="1" opacity=".8"/>'
         '<circle cx="24" cy="50" r="1.6" fill="{M}"/><circle cx="31" cy="85" r="1.3" fill="{M}"/></g>'
         '<g class="rd-wingR"><path d="M69 62 C86 28 116 30 110 52 C107 62 90 66 69 66 Z" fill="{G}" stroke="{GW}" stroke-width="1.8" stroke-linejoin="round" opacity=".95"/>'
         '<path d="M69 68 C86 70 102 84 94 92 C87 98 74 84 69 72 Z" fill="{G}" stroke="{GW}" stroke-width="1.8" stroke-linejoin="round" opacity=".95"/>'
         '<path d="M72 63 C84 50 98 44 104 48 M72 70 C80 76 88 84 90 89" fill="none" stroke="{GW}" stroke-width="1" opacity=".8"/>'
         '<circle cx="96" cy="50" r="1.6" fill="{M}"/><circle cx="89" cy="85" r="1.3" fill="{M}"/></g>')

BODY = ('<path d="M55 92 L54 106 M65 92 L66 106" stroke="{O}" stroke-width="6" stroke-linecap="round"/><path d="M55 92 L54 106 M65 92 L66 106" stroke="{S}" stroke-width="3.8" stroke-linecap="round"/>'
        '<path d="M47 108.5 Q48 103 54 104.5 Q57 106 56 108.5 Z M73 108.5 Q72 103 66 104.5 Q63 106 64 108.5 Z" fill="{D}" stroke="{O}" stroke-width="1.3" stroke-linejoin="round"/>'
        '<path d="M45 70 Q60 64 75 70 L86 93 Q79 99 73 93 Q66.5 99.5 60 93 Q53.5 99.5 47 93 Q41 99 34 93 Z" fill="{D}" stroke="{O}" stroke-width="1.6" stroke-linejoin="round"/>'
        '<path d="M49 72 Q60 68 71 72 L77 89 Q72 92 68 88 Q64 92 60 88 Q56 92 52 88 Q48 92 43 89 Z" fill="{D2}" opacity=".85"/>'
        '<path d="M50 57 Q60 53 70 57 L72 71 Q60 74 48 71 Z" fill="{B}" stroke="{O}" stroke-width="1.6" stroke-linejoin="round"/>'
        '<circle cx="60" cy="71" r="2.2" fill="{Y}" stroke="{O}" stroke-width=".9"/><circle cx="53.5" cy="70.4" r="1.2" fill="{Y}"/><circle cx="66.5" cy="70.4" r="1.2" fill="{Y}"/>'
        '<path d="M57.5 51 h5 v6 h-5 Z" fill="{S2}"/>')

HEAD = ('<path d="M31 32 C28 3 92 3 89 32 L91 50 Q85 57 79 50 L41 50 Q35 57 29 50 Z" fill="{H}" stroke="{O}" stroke-width="1.6" stroke-linejoin="round"/>'
        '<path d="M38.5 30 L27 22 L38 39 Z M81.5 30 L93 22 L82 39 Z" fill="{S}" stroke="{O}" stroke-width="1.4" stroke-linejoin="round"/>'
        '<ellipse cx="60" cy="33" rx="22.5" ry="21" fill="{S}" stroke="{O}" stroke-width="1.6"/>'
        '<g class="rd-cheek"><ellipse cx="45.5" cy="40.5" rx="3.6" ry="2.4" fill="{P}" opacity=".7"/><ellipse cx="74.5" cy="40.5" rx="3.6" ry="2.4" fill="{P}" opacity=".7"/></g>')

BANGS = ('<path d="M36 28 C35 6 85 6 84 28 C79 20 74 23 70 16 C66 23 58 23 55.5 15.5 C52 22.5 42 21 36 28 Z" fill="{H}" stroke="{O}" stroke-width="1.6" stroke-linejoin="round"/>'
         '<path class="rd-shine" d="M44 14 Q50 9 58 9" fill="none" stroke="{H2}" stroke-width="2.6" stroke-linecap="round"/>'
         '<g transform="translate(80 13)"><path class="rd-tip" d="M0 -5.5 L1.6 -1.8 L5.5 -1.7 L2.4 .8 L3.4 4.7 L0 2.5 L-3.4 4.7 L-2.4 .8 L-5.5 -1.7 L-1.6 -1.8 Z" fill="{Y}" stroke="{O}" stroke-width="1" stroke-linejoin="round"/></g>')

DUST = ('<path class="rd-dust" d="M14 98 l1.4 3.2 l3.2 1.4 l-3.2 1.4 l-1.4 3.2 l-1.4 -3.2 l-3.2 -1.4 l3.2 -1.4 z" fill="{Y}"/>'
        '<path class="rd-dust b" d="M104 100 l1.2 2.8 l2.8 1.2 l-2.8 1.2 l-1.2 2.8 l-1.2 -2.8 l-2.8 -1.2 l2.8 -1.2 z" fill="{P}"/>'
        '<circle class="rd-dust c" cx="92" cy="104" r="1.9" fill="{T}"/>')


# Sapio, il gufo saggio: disegno originale (viola, tocco da laureato, occhiali dorati, libro)
OWL_BACK = ('<path d="M37 26 L31 4 L49 15 Z M83 26 L89 4 L71 15 Z" fill="{R}" stroke="{O}" stroke-width="1.6" stroke-linejoin="round"/>'
            '<path d="M60 9 C81 9 87 31 86 56 C85 84 76 102 60 102 C44 102 35 84 34 56 C33 31 39 9 60 9 Z" fill="{R}" stroke="{O}" stroke-width="1.6"/>'
            '<ellipse cx="60" cy="73" rx="17" ry="22" fill="{R2}"/>'
            '<path d="M50 62 q3 3 6 0 q3 3 6 0 q3 3 6 0 M47 70 q3 3 6 0 q3 3 6 0 q3 3 6 0 q3 3 6 0 M47 78 q3 3 6 0 q3 3 6 0 q3 3 6 0 q3 3 6 0 M50 86 q3 3 6 0 q3 3 6 0 q3 3 6 0" fill="none" stroke="{R}" stroke-width="1.2" stroke-linecap="round" opacity=".7"/>'
            '<path d="M51 101 l-3 5 M53 101 v6 M55 101 l3 5 M65 101 l-3 5 M67 101 v6 M69 101 l3 5" stroke="{BK}" stroke-width="2.2" stroke-linecap="round"/>'
            '<path d="M41 22 Q51 26 60 31 Q69 26 79 22 Q74 46 60 51 Q46 46 41 22 Z" fill="{BE}" opacity=".0"/>'
            '<circle cx="51" cy="34" r="11" fill="{BE}" stroke="{O}" stroke-width="1.2"/><circle cx="69" cy="34" r="11" fill="{BE}" stroke="{O}" stroke-width="1.2"/>'
            '<g class="rd-cheek"><ellipse cx="43" cy="43" rx="3.2" ry="2" fill="{P}" opacity=".6"/><ellipse cx="77" cy="43" rx="3.2" ry="2" fill="{P}" opacity=".6"/></g>')
OWL_FACE = ('<g fill="none" stroke="{GL}" stroke-width="1.7"><circle cx="52" cy="34" r="6.8"/><circle cx="68" cy="34" r="6.8"/><path d="M58.6 32.6 Q60 31 61.4 32.6"/></g>')
OWL_CAP = ('<path d="M47 9 L47 15 Q60 20.5 73 15 L73 9 Z" fill="{O}"/>'
           '<path d="M34 6 L60 -5 L86 6 L60 16 Z" fill="{O}" stroke="{O}" stroke-width="1.2" stroke-linejoin="round"/>'
           '<path d="M40 6 L60 -1.5 L80 6" fill="none" stroke="#5A4E8C" stroke-width="1"/>'
           '<circle cx="60" cy="5" r="1.8" fill="{Y}"/>'
           '<g class="rd-swing"><path d="M60 5 L80 9 L81 20" fill="none" stroke="{Y}" stroke-width="1.6" stroke-linecap="round"/><path d="M78.5 19 h5 l-1 6 h-3 Z" fill="{Y}" stroke="{O}" stroke-width=".8"/></g>')
OWL_BOOK = ('<g class="rd-sym"><path d="M92 92 Q99 88 106 92 Q113 88 120 92 L120 104 Q113 100 106 104 Q99 100 92 104 Z" fill="{W}" stroke="{O}" stroke-width="1.4" stroke-linejoin="round"/>'
            '<path d="M106 92 V104 M95 95 h7 M95 98 h6 M109 95 h7 M109 98 h6" stroke="{L}" stroke-width="1.1" stroke-linecap="round"/></g>')


def _beak(kind):
    if kind in ('open', 'talk', 'o'):
        low = '<path%s d="M57.2 46 L62.8 46 L60 50.5 Z" fill="{BK}" stroke="{O}" stroke-width="1" stroke-linejoin="round"/>' % (' class="rd-mouth-t"' if kind == 'talk' else '')
        return '<path d="M56.5 45 Q60 47 63.5 45 L60 49 Z" fill="{O}"/>' + low + '<path d="M55.5 40.5 L64.5 40.5 L60 46 Z" fill="{BK}" stroke="{O}" stroke-width="1.1" stroke-linejoin="round"/>'
    return '<path d="M55.5 40.5 L64.5 40.5 L60 48 Z" fill="{BK}" stroke="{O}" stroke-width="1.1" stroke-linejoin="round"/>'


def _body(expr, ch='fatina'):
    p = POSE[expr]
    head = '<ellipse cx="60" cy="114" rx="26" ry="3" fill="{O}" opacity=".14"/>' + DUST + '<g class="rd-all"><g%s>' % (' class="rd-jump"' if p.get('jump') else '')
    eyes = '<g class="rd-look"><g class="rd-eyes">' + _eyes(p['eyes'], ch == 'fatina') + '</g></g>'
    if ch == 'saggio':
        arms = p['arms'].replace('stroke-width="4.2"', 'stroke-width="7.4"').replace('stroke-width="6.6"', 'stroke-width="9.8"').replace('r="3.9" fill="{S}"', 'r="4.6" fill="{A}"')
        return (head + OWL_BACK + eyes + OWL_FACE + _beak(p['mouth']) + OWL_CAP +
                arms + p['extra'] + ('' if expr in ('spiega', 'conta', 'idea') else OWL_BOOK) + '</g></g>')
    return head + WINGS + BODY + HEAD + eyes + _mouth(p['mouth']) + BANGS + p['arms'] + p['extra'] + '</g></g>'


def _fill(s, pal):
    for k, v in pal.items(): s = s.replace('{' + k + '}', v)
    return s


def svg(expr='ciao', px=48, cls='', ch='saggio'):
    """SVG decorativo per la pagina (aria-hidden), con le animazioni di rada.CSS."""
    return _fill('<svg class="rd%s" data-rd="%s" viewBox="-8 -28 140 148" width="%d" height="%d" aria-hidden="true" focusable="false">%s</svg>' % (
        (' ' + cls) if cls else '', expr, px, round(px * 148 / 140), _body(expr, ch)), SAGE if ch == 'saggio' else PAL)


def standalone(expr, ch='saggio'):
    nm = CHARS[ch][0]
    return _fill('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -28 140 148" width="280" height="296" role="img" aria-labelledby="t"><title id="t">%s</title><style>%s</style>%s</svg>\n' % (
        LABEL[expr].replace('Rada', nm), ANIM, _body(expr, ch)), SAGE if ch == 'saggio' else PAL)


ALL = {ch: {e: svg(e, 48, ch=ch) for e in EXPR} for ch in CHARS}

if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = os.path.join(root, 'img', 'rada'); os.makedirs(out, exist_ok=True)
    for e in EXPR:
        open(os.path.join(out, 'rada-%s.svg' % e), 'w', encoding='utf-8').write(standalone(e, 'fatina'))
        open(os.path.join(out, 'sapio-%s.svg' % e), 'w', encoding='utf-8').write(standalone(e, 'saggio'))
    print('ok', len(EXPR), 'espressioni x', len(CHARS), 'personaggi in img/rada/')
