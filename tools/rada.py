"""Rada, il pupazzo degli aiuti: un solo disegno, nove espressioni, animato.
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
THEME = {'V': 'var(--violet)', 'T': 'var(--teal)', 'I': 'var(--ink)', 'F': 'var(--bg)', 'P': 'var(--red)', 'Y': '#FFC94D', 'W': 'var(--surface)', 'L': 'var(--line)'}
FIXED = {'V': '#4B4BF5', 'T': '#0A9BB5', 'I': '#121A2B', 'F': '#FFFFFF', 'P': '#F27BA8', 'Y': '#FFC94D', 'W': '#FFFFFF', 'L': '#D3D9E6'}

# animazioni: valgono per l'SVG nella pagina (rada.CSS) e, identiche, dentro i file
ANIM = '''.rd-all{animation:rd-float 3.2s ease-in-out infinite}
.rd-eyes,.rd-mouth-t,.rd-wave,.rd-bulb,.rd-ping,.rd-spark,.rd-dot,.rd-drop,.rd-sym,.rd-armL,.rd-armR,.rd-q{transform-box:fill-box;transform-origin:center}
.rd-eyes{animation:rd-blink 4.6s infinite}
.rd-ping{animation:rd-ping 2.4s ease-out infinite;transform-origin:50% 100%}
.rd-ping.b{animation-delay:.5s}
.rd-wave{transform-origin:0% 100%;animation:rd-wave .9s ease-in-out infinite alternate}
.rd-mouth-t{animation:rd-talk .24s ease-in-out infinite alternate}
.rd-snd{animation:rd-fade 1s ease-in-out infinite}.rd-snd.b{animation-delay:.3s}
.rd-bulb{animation:rd-pop 1.4s ease-in-out infinite alternate}
.rd-dot{animation:rd-fade 1.6s ease-in-out infinite}.rd-dot.b{animation-delay:.25s}.rd-dot.c{animation-delay:.5s}
.rd-spark{animation:rd-twinkle 1.1s ease-in-out infinite alternate}.rd-spark.b{animation-delay:.35s}.rd-spark.c{animation-delay:.7s}
.rd-jump{animation:rd-jump .7s ease-in-out infinite alternate}
.rd-drop{animation:rd-drop 1.8s ease-in infinite}
.rd-sym{animation:rd-bob 1.8s ease-in-out infinite alternate}.rd-sym.b{animation-delay:.4s}.rd-sym.c{animation-delay:.8s}
.rd-q{animation:rd-tilt 1.6s ease-in-out infinite alternate}
.rd-point{transform-box:fill-box;transform-origin:0% 100%;animation:rd-point 1.2s ease-in-out infinite alternate}
.rd-fist{transform-box:fill-box;transform-origin:100% 100%;animation:rd-fist .8s ease-in-out infinite alternate}
@keyframes rd-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-2.5px)}}
@keyframes rd-blink{0%,93%,100%{transform:scaleY(1)}96.5%{transform:scaleY(.08)}}
@keyframes rd-ping{0%{opacity:.9;transform:scale(.5)}100%{opacity:0;transform:scale(1.25)}}
@keyframes rd-wave{from{transform:rotate(-10deg)}to{transform:rotate(16deg)}}
@keyframes rd-talk{from{transform:scaleY(.45)}to{transform:scaleY(1.25)}}
@keyframes rd-fade{0%,100%{opacity:.15}50%{opacity:1}}
@keyframes rd-pop{from{transform:scale(.9)}to{transform:scale(1.12)}}
@keyframes rd-twinkle{from{transform:scale(.4) rotate(0deg);opacity:.3}to{transform:scale(1.1) rotate(25deg);opacity:1}}
@keyframes rd-jump{from{transform:translateY(0)}to{transform:translateY(-6px)}}
@keyframes rd-drop{0%{transform:translateY(-3px);opacity:0}25%{opacity:1}100%{transform:translateY(9px);opacity:0}}
@keyframes rd-bob{from{transform:translateY(2px)}to{transform:translateY(-3px)}}
@keyframes rd-tilt{from{transform:rotate(-8deg)}to{transform:rotate(10deg)}}
@keyframes rd-point{from{transform:rotate(0deg)}to{transform:rotate(-9deg)}}
@keyframes rd-fist{from{transform:rotate(0deg)}to{transform:rotate(10deg)}}
@media (prefers-reduced-motion:reduce){.rd-all,.rd-all *{animation:none!important}}'''

CSS = '<style id="rada-css">.rd{flex:none;overflow:visible;vertical-align:middle}\n' + ANIM + '\n.rd-row{display:flex;gap:.7rem;align-items:center}.rd-row>:last-child{flex:1;min-width:0}</style>'


def _eyes(kind):
    hl = '<circle cx="{x}" cy="{y}" r="1.7" fill="{F}"/>'
    def dot(x, y, r=5.2, dx=1.6, dy=-1.8): return '<circle cx="%s" cy="%s" r="%s" fill="{I}"/>' % (x, y, r) + hl.replace('{x}', str(x + dx)).replace('{y}', str(y + dy))
    arc = lambda x: '<path d="M%s 62 Q%s 53 %s 62" fill="none" stroke="{I}" stroke-width="3.6" stroke-linecap="round"/>' % (x - 6, x, x + 6)
    if kind == 'happy': return arc(47) + arc(73)
    if kind == 'up': return dot(49, 57, 5, 1.8, -2) + dot(75, 57, 5, 1.8, -2)
    if kind == 'soft': return (dot(47, 61, 4.8) + dot(73, 61, 4.8) +
                               '<path d="M40 52 L52 49 M80 52 L68 49" stroke="{I}" stroke-width="2.6" stroke-linecap="round"/>')
    if kind == 'curious': return dot(47, 61, 4.4) + dot(73, 59, 6.8, 2.2, -2.4) + '<path d="M66 47 Q74 43 81 48" fill="none" stroke="{I}" stroke-width="2.6" stroke-linecap="round"/>'
    if kind == 'wide': return dot(47, 59, 5.6) + dot(73, 59, 5.6) + '<path d="M40 48 Q47 44 53 48 M67 48 Q73 44 80 48" fill="none" stroke="{I}" stroke-width="2.4" stroke-linecap="round"/>'
    if kind == 'focus': return dot(47, 61, 4.6, 1.2, -1.4) + dot(73, 61, 4.6, 1.2, -1.4) + '<path d="M41 52 L53 53 M79 52 L67 53" stroke="{I}" stroke-width="2.6" stroke-linecap="round"/>'
    return dot(47, 60) + dot(73, 60)


def _mouth(kind):
    if kind == 'open': return '<path d="M50 72 Q60 87 70 72 Z" fill="{I}"/><ellipse cx="60" cy="79.5" rx="4.2" ry="2.4" fill="{P}"/>'
    if kind == 'talk': return '<ellipse class="rd-mouth-t" cx="60" cy="76" rx="5.5" ry="4.6" fill="{I}"/>'
    if kind == 'o': return '<ellipse cx="62" cy="76" rx="3.4" ry="3.8" fill="{I}"/>'
    if kind == 'flat': return '<path d="M53 76 Q60 78.5 67 74.5" fill="none" stroke="{I}" stroke-width="3.2" stroke-linecap="round"/>'
    if kind == 'small': return '<path d="M53 75 Q60 80.5 67 75" fill="none" stroke="{I}" stroke-width="3.2" stroke-linecap="round"/>'
    return '<path d="M50 73 Q60 83 70 73" fill="none" stroke="{I}" stroke-width="3.4" stroke-linecap="round"/>'


def _arm(d, hx, hy, cls=''):
    return '<g%s><path d="%s" fill="none" stroke="{V}" stroke-width="7.5" stroke-linecap="round"/><circle cx="%s" cy="%s" r="5.4" fill="{V}"/></g>' % (
        (' class="%s"' % cls) if cls else '', d, hx, hy)

L_DOWN = _arm('M23 72 Q12 82 16 93', 16, 93)
R_DOWN = _arm('M97 72 Q108 82 104 93', 104, 93)
SPARK = '<path class="rd-spark %s" d="M%s %s l2.2 5 l5 2.2 l-5 2.2 l-2.2 5 l-2.2 -5 l-5 -2.2 l5 -2.2 z" fill="%s"/>'

POSE = {
    'ciao': dict(eyes='normal', mouth='smile', arms=L_DOWN + _arm('M97 68 Q112 58 109 40', 109, 40, 'rd-wave'), extra=''),
    'parla': dict(eyes='normal', mouth='talk', arms=L_DOWN + _arm('M97 70 Q110 70 110 56', 110, 56, 'rd-point'),
                  extra='<path class="rd-snd" d="M10 60 Q6 68 10 76" fill="none" stroke="{T}" stroke-width="2.6" stroke-linecap="round"/><path class="rd-snd b" d="M4 55 Q-3 68 4 81" fill="none" stroke="{T}" stroke-width="2.6" stroke-linecap="round"/>'),
    'idea': dict(eyes='wide', mouth='open', arms=L_DOWN + _arm('M97 68 Q110 60 104 44', 104, 44, 'rd-point'),
                 extra='<g class="rd-bulb"><path d="M103 6 v-5 M90 11 l-4 -4 M116 11 l4 -4 M86 22 h-5 M120 22 h5" stroke="{Y}" stroke-width="2.6" stroke-linecap="round"/><circle cx="103" cy="21" r="9" fill="{Y}"/><rect x="99" y="29" width="8" height="5.5" rx="1.6" fill="{I}"/></g>'),
    'pensa': dict(eyes='up', mouth='flat', arms=L_DOWN, front=_arm('M98 84 Q97 99 79 91', 75, 87).replace('r="5.4" fill="{V}"', 'r="5.4" fill="{V}" stroke="{F}" stroke-width="2"'),
                  extra='<circle class="rd-dot" cx="96" cy="34" r="2.6" fill="{T}"/><circle class="rd-dot b" cx="104" cy="25" r="3.8" fill="{T}"/><circle class="rd-dot c" cx="112" cy="13" r="5.4" fill="{T}"/>'),
    'spiega': dict(eyes='normal', mouth='open', arms=L_DOWN + _arm('M97 68 Q108 62 106 50', 106, 50, 'rd-point'),
                   extra='<g><rect x="92" y="6" width="27" height="33" rx="4" fill="{W}" stroke="{I}" stroke-width="2.2"/><path d="M97 15 h3 M97 22.5 h3 M97 30 h3" stroke="{T}" stroke-width="3" stroke-linecap="round"/><path d="M104 15 h10 M104 22.5 h10 M104 30 h7" stroke="{I}" stroke-width="2.2" stroke-linecap="round"/></g>'),
    'felice': dict(eyes='happy', mouth='open', arms=_arm('M23 64 Q8 50 14 34', 14, 34, 'rd-fist') + _arm('M97 64 Q112 50 106 34', 106, 34, 'rd-wave'),
                   extra=(SPARK % ('', 24, 8, '{Y}')) + (SPARK % ('b', 98, 6, '{Y}')) + (SPARK % ('c', 112, 52, '{T}')) + (SPARK % ('b', 6, 56, '{P}')), jump=True),
    'coraggio': dict(eyes='soft', mouth='small', arms=_arm('M23 66 Q10 56 15 42', 15, 42, 'rd-fist') + R_DOWN,
                     extra='<path class="rd-drop" d="M88 36 q4 6 0 9 q-4 -3 0 -9 z" fill="{T}"/><path d="M6 30 l5 3 M4 40 h6 M8 51 l5 -3" stroke="{Y}" stroke-width="2.6" stroke-linecap="round"/>'),
    'curiosa': dict(eyes='curious', mouth='o', arms=L_DOWN, front=_arm('M98 84 Q98 100 80 93', 76, 89).replace('r="5.4" fill="{V}"', 'r="5.4" fill="{V}" stroke="{F}" stroke-width="2"'),
                    extra='<g class="rd-q"><path d="M96 22 q0 -9 8 -9 q8 0 8 7.5 q0 5 -5.5 7.5 q-2.5 1.2 -2.5 5" fill="none" stroke="{T}" stroke-width="3.6" stroke-linecap="round"/><circle cx="104" cy="40" r="2.4" fill="{T}"/></g>'),
    'conta': dict(eyes='focus', mouth='small', arms=_arm('M23 70 Q10 66 12 52', 12, 52, 'rd-fist') + _arm('M97 70 Q110 66 108 52', 108, 52, 'rd-point'),
                  extra='<path class="rd-sym" d="M6 22 h12 M12 16 v12" stroke="{T}" stroke-width="3.4" stroke-linecap="round"/><path class="rd-sym b" d="M100 16 l10 10 M110 16 l-10 10" stroke="{Y}" stroke-width="3.4" stroke-linecap="round"/><path class="rd-sym c" d="M104 36 h12 M104 42 h12" stroke="{P}" stroke-width="3.2" stroke-linecap="round"/>'),
}


def _body(expr):
    p = POSE[expr]
    inner = ('<ellipse cx="60" cy="112" rx="30" ry="3.2" fill="{I}" opacity=".12"/>'
             '<g class="rd-all"><g%s>' % (' class="rd-jump"' if p.get('jump') else '') +
             '<path d="M60 28 V15" stroke="{V}" stroke-width="3.6" stroke-linecap="round"/>'
             '<path class="rd-ping" d="M51 9 Q60 0 69 9" fill="none" stroke="{T}" stroke-width="2.2" stroke-linecap="round"/>'
             '<path class="rd-ping b" d="M46 6 Q60 -8 74 6" fill="none" stroke="{T}" stroke-width="2.2" stroke-linecap="round"/>'
             '<circle cx="60" cy="13" r="4.6" fill="{T}"/>'
             '<ellipse cx="46" cy="104" rx="9" ry="5" fill="{V}"/><ellipse cx="74" cy="104" rx="9" ry="5" fill="{V}"/>'
             + p['arms'] +
             '<ellipse cx="60" cy="66" rx="40" ry="39" fill="{V}"/>'
             '<ellipse cx="60" cy="65" rx="30.5" ry="27" fill="{F}"/>'
             '<circle cx="37.5" cy="71" r="4.4" fill="{P}" opacity=".45"/><circle cx="82.5" cy="71" r="4.4" fill="{P}" opacity=".45"/>'
             '<g class="rd-eyes">' + _eyes(p['eyes']) + '</g>' + _mouth(p['mouth']) + p.get('front', '') + p['extra'] + '</g></g>')
    return inner


def _fill(s, pal):
    for k, v in pal.items(): s = s.replace('{' + k + '}', v)
    return s


def svg(expr='ciao', px=48, cls=''):
    """SVG decorativo per la pagina: usa i colori del tema e le animazioni di rada.CSS."""
    return _fill('<svg class="rd%s" data-rd="%s" viewBox="-6 -10 136 128" width="%d" height="%d" aria-hidden="true" focusable="false">%s</svg>' % (
        (' ' + cls) if cls else '', expr, px, round(px * 128 / 136), _body(expr)), THEME)


def standalone(expr):
    return _fill('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -10 136 128" width="272" height="256" role="img" aria-labelledby="t"><title id="t">%s</title><style>%s</style>%s</svg>\n' % (
        LABEL[expr], ANIM, _body(expr)), FIXED)


ALL = {e: svg(e, 48) for e in EXPR}

if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = os.path.join(root, 'img', 'rada'); os.makedirs(out, exist_ok=True)
    for e in EXPR:
        open(os.path.join(out, 'rada-%s.svg' % e), 'w', encoding='utf-8').write(standalone(e))
    print('ok rada', len(EXPR), 'svg in img/rada/')
