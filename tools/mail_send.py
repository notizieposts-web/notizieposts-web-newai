"""Radar AI: invia l'email dell'edizione via SMTP di Gmail (usato dal workflow "Invio email").

Perche' non il connettore Gmail: send_message fa passare l'HTML dal filtro di Gmail, che riscrive i link
in https://www.google.com/url?q=... (chi apre vede "vuoi essere reindirizzato?") e toglie gli sfondi.
Via SMTP il messaggio parte identico a quello costruito da tools/mail_build.py.

Variabili d'ambiente (dai secret e dalle variabili del repository, mai nei file):
  GMAIL_APP_PASSWORD   password per le app di notizieposts@gmail.com (secret)
  MAIL_FROM            mittente (variabile; predefinito notizieposts@gmail.com)
  MAIL_DAILY           destinatari quotidiani, separati da virgola (secret)
  MAIL_ALTERNATE       destinatari a giorni alterni (secret)
  MAIL_ALTERNATE_START data di partenza dei giorni alterni, AAAA-MM-GG (variabile; predefinita 2026-10-19)
  MAIL_TEST            destinatario delle prove (secret)
  MODE                 "tutti" (predefinito) o "prova"
Gli indirizzi non vengono mai stampati: i log di un repository pubblico sono pubblici.
"""
import datetime, os, re, smtplib, ssl, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid, formatdate
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mail_build

def addrs(name):
    return [a.strip() for a in (os.environ.get(name) or '').split(',') if a.strip()]

def plain(u, html):
    n = int(u['n'])
    site = mail_build.SITE
    lines = ['Radar AI · %s' % u['titolo'], '', u['descrizione'], '',
             'Leggi l\'edizione: %sedizioni/%02d.html' % (site, n)]
    m = re.search(r'href="([^"]+radar-ai-%d\.mp3)"' % n, html)
    if m:
        lines.append('Ascolta l\'audio (MP3): ' + m.group(1))
    lines += ['Tutte le edizioni: ' + site, '', 'La domanda del giorno: ' + u['domanda']]
    return '\n'.join(lines) + '\n'

def message(sender, to, subject, html, text):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr(('Radar AI', sender))
    msg['To'] = to
    msg['Date'] = formatdate(localtime=False)
    msg['Message-ID'] = make_msgid(domain=sender.split('@')[1])
    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    return msg

def main():
    pwd = os.environ.get('GMAIL_APP_PASSWORD')
    if not pwd:
        raise SystemExit('::error::Manca il secret GMAIL_APP_PASSWORD')
    sender = os.environ.get('MAIL_FROM') or 'notizieposts@gmail.com'
    mode = (os.environ.get('MODE') or 'tutti').strip()
    tz = ZoneInfo('Europe/Rome')
    today = datetime.datetime.now(tz).date()
    html_std, u = mail_build.build('.')
    html_prev, _ = mail_build.build('.', precedente=True)
    if mode != 'prova' and u['data'] != today.isoformat():
        raise SystemExit('::error::tools/ultima.json e\' del %s, non di oggi: edizione non pronta' % u['data'])
    subject = '\U0001F4E1 Radar AI · ' + u['titolo']
    jobs = []
    if mode == 'prova':
        jobs = [(a, html_std) for a in addrs('MAIL_TEST')]
        subject += ' (prova)'
    else:
        jobs = [(a, html_std) for a in addrs('MAIL_DAILY')]
        start = datetime.date.fromisoformat(os.environ.get('MAIL_ALTERNATE_START') or '2026-10-19')
        if today >= start and (today - start).days % 2 == 0:
            jobs += [(a, html_prev) for a in addrs('MAIL_ALTERNATE')]
    if not jobs:
        raise SystemExit('::error::Nessun destinatario configurato')
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ctx, timeout=60) as s:
        s.login(sender, pwd)
        for i, (to, html) in enumerate(jobs, 1):
            s.sendmail(sender, [to], message(sender, to, subject, html, plain(u, html)).as_string())
            print('inviata %d/%d' % (i, len(jobs)))
    print('ok edizione', u['n'], 'audio', 'si' if 'radar-ai-%d.mp3' % int(u['n']) in html_std else 'no')

if __name__ == '__main__':
    main()
