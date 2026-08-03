#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore vademecum PROGETTI AI.
Il look sta tutto in assets/styles.css (fonte unica): ogni pagina lo linka,
niente piu' CSS duplicato. Scrive la home in root, i dossier in progetti-ai/,
le pagine servizi (in chiaro) in _sorgenti-servizi/ da cifrare.
Rilancia con:  python3 _genera.py
"""
import re
import pathlib

BASE = pathlib.Path(__file__).parent
# Cartelle del repo. Ora ENTRAMBE le aree sono protette: il testo in chiaro
# vive solo nelle cartelle sorgente (GITIGNORED, mai sul repo); online vanno
# solo i file cifrati da cifra.sh. La home resta pubblica in root.
#  - _sorgenti-progetti/ pagine Progetti AI in chiaro  -> cifrate in progetti-ai/
#  - _sorgenti-servizi/  pagine Servizi in chiaro      -> cifrate in servizi-al-consultant/
#  - assets/             styles.css condiviso (pubblico, non e' segreto)
# SRCDIR: dato lo slug categoria, dice in quale cartella sorgente scrivere.
SRC_PUB = BASE / "_sorgenti-progetti"
SRC_PROT = BASE / "_sorgenti-servizi"
ASSETS = BASE / "assets"
SRCDIR = {"progetti-ai": SRC_PUB, "servizi-al-consultant": SRC_PROT}
for _d in (SRC_PUB, SRC_PROT, ASSETS):
    _d.mkdir(exist_ok=True)


def stylesheet(prefix=""):
    # prefix="" per la home in root, "../" per le pagine dentro una cartella.
    return '<link rel="stylesheet" href="' + prefix + 'assets/styles.css">\n'

# --- 2. sezioni fisse ---
SECHEADS = {
    1: ("In una frase, e a chi serve", "Orientarsi in 30 secondi."),
    2: ("Stack e strumenti", "Con cosa e costruito, e perche."),
    3: ("Come funziona - il flusso", "Il pattern del progetto, passo per passo."),
    4: ("Onboarding collaboratore + spiegazione cliente", "Allineare chi arriva, e raccontarlo a chi non e tecnico."),
    5: ("Paletti, limiti e stato", "Cosa e vero oggi, cosa manca."),
}
SEC_IDS = {1: "intro", 2: "stack", 3: "flusso", 4: "onboarding", 5: "paletti"}

NAV = ('<a href="#intro" class="active"><span class="n">01</span> In una frase</a>\n'
       '        <a href="#stack"><span class="n">02</span> Stack e strumenti</a>\n'
       '        <a href="#flusso"><span class="n">03</span> Come funziona + passo passo</a>\n'
       '        <a href="#onboarding"><span class="n">04</span> Onboarding + cliente</a>\n'
       '        <a href="#paletti"><span class="n">05</span> Paletti e stato</a>')

SCRIPT = ('<script>\n'
          '  const links=[...document.querySelectorAll("#toc a")];\n'
          '  const map=new Map(links.map(a=>[a.getAttribute("href").slice(1),a]));\n'
          '  const obs=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.remove("active"));map.get(e.target.id)&&map.get(e.target.id).classList.add("active");}});},{rootMargin:"-45% 0px -50% 0px"});\n'
          '  document.querySelectorAll("section,#intro").forEach(s=>obs.observe(s));\n'
          '</script>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">\n')


def chips(items):
    out = []
    for i, (label, value) in enumerate(items):
        cls = "chip state" if i == 0 else "chip"
        out.append('<span class="' + cls + '"><span class="dot"></span>' + label + ": <b>" + value + "</b></span>")
    return "\n        ".join(out)


def section(n, body):
    t, sub = SECHEADS[n]
    num = "%02d" % n
    return ('\n    <section id="' + SEC_IDS[n] + '">\n'
            '      <div class="sechead"><span class="secnum">' + num + '</span><div><h2>' + t +
            '</h2><div class="sub">' + sub + '</div></div></div>\n' + body + '\n    </section>')


def sec1(paras, serve):
    left = "".join("<p>" + x + "</p>\n          " for x in paras).rstrip()
    items = "".join("<li><b>" + r + "</b>" + d + "</li>\n            " for r, d in serve).rstrip()
    return ('      <div class="grid2">\n        <div>\n          ' + left +
            '\n        </div>\n        <div class="callout">\n          <div class="lbl">A chi serve</div>\n          <ul>\n            ' +
            items + '\n          </ul>\n        </div>\n      </div>')


def flow(steps):
    out = '      <div class="flow">\n'
    for num, tit, txt, cmd, man in steps:
        cls = "step manual" if man else "step"
        out += ('        <div class="' + cls + '"><div class="sn">' + num + '</div><h4>' + tit +
                '</h4><p>' + txt + '</p><span class="cmd">' + cmd + '</span></div>\n')
    return out + "      </div>"


def howto(titolo, intro, steps):
    # Blocco "Passo-passo" per chi opera per la prima volta: ogni clic in ordine.
    # steps: lista di (titolo_passo, corpo_html). Il corpo puo contenere span
    # inline gia pronti: <span class="path">campo</span>, <span class="who">a mano
    # dal team</span>, <span class="who sys">lo fa il sistema</span>.
    lis = ""
    for t, c in steps:
        lis += '        <li><span class="ht-t"><span class="ht-b">' + t + "</span>" + c + "</span></li>\n"
    return (h3("Passo-passo: " + titolo) + '\n      <p class="muted">' + intro + "</p>\n"
            '      <ol class="howto">\n' + lis + "      </ol>")


def table(head, rows):
    thead = ""
    if head:
        thead = "<thead><tr>" + "".join("<th>" + c + "</th>" for c in head) + "</tr></thead>\n        "
    body = ""
    for r in rows:
        body += "          <tr>" + "".join("<td>" + c + "</td>" for c in r) + "</tr>\n"
    return '      <table class="tbl">\n        ' + thead + "<tbody>\n" + body + "        </tbody>\n      </table>"


def note(txt):
    return '      <div class="note">' + txt + "</div>"


def h3(txt):
    return "      <h3>" + txt + "</h3>"


def kv(rows):
    out = '          <div class="kv">\n'
    for k, v in rows:
        out += '            <div class="row"><span class="k">' + k + '</span><span class="v">' + v + "</span></div>\n"
    return out + "          </div>"


def cards(c1, c2):
    ol = "".join("<li>" + x + "</li>\n            " for x in c1[2]).rstrip()
    return ('      <div class="cards">\n'
            '        <div class="ocard">\n          <div class="lbl">' + c1[0] + '</div>\n          <h4>' + c1[1] + '</h4>\n          <ol>\n            ' + ol + "\n          </ol>\n        </div>\n"
            '        <div class="ocard">\n          <div class="lbl">' + c2[0] + '</div>\n          <h4>' + c2[1] + '</h4>\n          <p>' + c2[2] + '</p>\n          <p style="margin-top:10px"><b>Regola d\'oro:</b> ' + c2[3] + "</p>\n        </div>\n      </div>")


def pitch(paras):
    ps = "".join("<p>" + x + "</p>\n        " for x in paras).rstrip()
    return '      <div class="pitch">\n        <div class="lbl">Come lo spieghi al cliente (non tecnico)</div>\n        ' + ps + "\n      </div>"


def warn(items):
    lis = "".join("<li>" + x + "</li>\n          " for x in items).rstrip()
    return '      <div class="warn">\n        <div class="lbl">Paletti da spiegare subito</div>\n        <ul>\n          ' + lis + "\n        </ul>\n      </div>"


def sec5(dafare, stato):
    return ('      <div class="grid2">\n        <div>\n          <h3>Da fare piu avanti</h3>\n' +
            table([], dafare) + '\n        </div>\n        <div class="callout">\n          <div class="lbl">Stato reale (onesto)</div>\n' +
            kv(stato) + "\n        </div>\n      </div>")


def page(p):
    s = []
    s.append('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n')
    s.append('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    s.append("<title>Vademecum - " + p["name"] + "</title>\n")
    s.append(FONTS)
    s.append(stylesheet("../") + '</head>\n<body>\n<div class="wrap">\n')
    s.append('  <aside class="side">\n    <div>\n      <div class="brandmark">Vade<span>mecum</span></div>\n')
    s.append('      <div style="font-size:11.5px;color:var(--ink-3);margin-top:6px;font-family:\'Montserrat\',sans-serif"><a href="index.html" style="text-decoration:none;color:inherit">&larr; tutti i progetti</a></div>\n    </div>\n')
    s.append('    <div>\n      <div class="kicker">Sezioni</div>\n      <nav class="toc" id="toc">\n        ' + NAV + "\n      </nav>\n    </div>\n")
    s.append('    <div class="foot">\n      <b>' + p["name"] + "</b><br>\n      Ultimo aggiornamento: 30 lug 2026<br>\n      Owner: Tomas &middot; " + p["fonte"] + "\n    </div>\n  </aside>\n")
    s.append('  <main>\n    <header class="hero" id="top">\n      <div class="eyebrow">Vademecum &middot; Onboarding collaboratori</div>\n')
    s.append("      <h1>" + p["h1"] + '</h1>\n      <p class="lede">' + p["lede"] + "</p>\n")
    s.append('      <div class="chips">\n        ' + chips(p["chips"]) + "\n      </div>\n    </header>\n")
    for n in (1, 2, 3, 4, 5):
        s.append(section(n, p["sec"][n]))
    s.append('\n\n    <footer class="pgfoot">\n      <span>Vademecum &middot; ' + p["name"] + '</span>\n      <span class="mono">v1.0 &middot; 2026-07-30</span>\n    </footer>\n  </main>\n</div>\n')
    s.append(SCRIPT + "\n</body>\n</html>\n")
    return "".join(s)


# --- accenti: parole intere + frasi non ambigue (l'apostrofo ASCII rompe le
#     stringhe Python, gli accenti no, ma li applico qui per tenerli in un posto solo) ---
_WORD = {
    r"\bperche\b": "perché", r"\bPerche\b": "Perché", r"\bfinche\b": "finché",
    r"\bcosi\b": "così", r"\bgia\b": "già", r"\bpiu\b": "più", r"\bpuo\b": "può",
    r"\bqualita\b": "qualità", r"\bquantita\b": "quantità",
    r"\bvelocita\b": "velocità", r"\battivita\b": "attività",
}
_PHRASE = [
    ("Con cosa e costruito", "Con cosa è costruito"),
    ("chi non e tecnico", "chi non è tecnico"),
    ("Cosa e vero oggi", "Cosa è vero oggi"),
    ("Cos&rsquo;e.", "Cos&rsquo;è."),
    ("e lento, ma l&rsquo;invio automatico e rischioso", "è lento, ma l&rsquo;invio automatico è rischioso"),
    ("Perché e fatto così.", "Perché è fatto così."),
    ("ed e idempotente", "ed è idempotente"),
    ("non e esposto", "non è esposto"),
    ("Installa, da le credenziali", "Installa, dà le credenziali"),
    ("a mano e disordinato", "a mano è disordinato"),
    ("e la puntata, così", "è la puntata, così"),
    ("qual e l&rsquo;ultima", "qual è l&rsquo;ultima"),
    ("da zero e lento e incoerente", "da zero è lento e incoerente"),
    ("Il primo caso e Food Lab", "Il primo caso è Food Lab"),
    ("la proposta e una pagina", "la proposta è una pagina"),
    ("non rompe la UI ne il catalogo", "non rompe la UI né il catalogo"),
    ("non cambia la UI ne il catalogo", "non cambia la UI né il catalogo"),
    ("JSON e fisso", "JSON è fisso"),
    ("catalogo. E anche", "catalogo. È anche"),
    ("qui e documentato", "qui è documentato"),
    ("e li la logica", "è lì la logica"),
    ("&laquo;E&rsquo; un assistente", "&laquo;È un assistente"),
    ("l&rsquo;invio e sempre a mano", "l&rsquo;invio è sempre a mano"),
    ("E una demo: la versione completa", "È una demo: la versione completa"),
    ("<b>E una demo.</b>", "<b>È una demo.</b>"),
    ("puntata e numerata", "puntata è numerata"),
    ("La home e generata", "La home è generata"),
    ("framework ne build", "framework né build"),
    ("e da li che arriva", "è da lì che arriva"),
    ("non e un foglio prezzi: e una pagina", "non è un foglio prezzi: è una pagina"),
    ("La formula e su misura", "La formula è su misura"),
    ("La formula e specifica", "La formula è specifica"),
    ("Il deck e una proposta", "Il deck è una proposta"),
    ("Si (processed.json)", "Sì (processed.json)"),
    ("cosa e, com&rsquo;e fatto", "cosa è, com&rsquo;è fatto"),
]


# Entita HTML tipografiche -> carattere reale "pulito" (rende identico nel
# browser, ma tiene i sorgenti leggibili). NON tocco quelle che DEVONO restare
# codificate: &lt; &gt; &amp; (letterali dentro <code>), &nbsp; (spazio unificatore
# anti-orfane) e &larr; (freccia back della sidebar, come nei dossier a mano).
_ENT = {
    "&rsquo;": "’", "&lsquo;": "‘",
    "&ldquo;": "“", "&rdquo;": "”",
    "&laquo;": "«", "&raquo;": "»",
    "&middot;": "·", "&rarr;": "→",
    "&euro;": "€", "&ge;": "≥", "&le;": "≤",
}


def fix(html):
    for pat, rep in _WORD.items():
        html = re.sub(pat, rep, html)
    for a, b in _PHRASE:
        html = html.replace(a, b)
    for ent, ch in _ENT.items():
        html = html.replace(ent, ch)
    return html


# ============================ DATI PROGETTI ============================
P = []

# ---- MAIL AUTOMATION ----
P.append(dict(
    name="Mail Automation", slug="mail-automation", fonte="Fonte: repo MAIL AUTOMATION",
    h1="Mail<br>Automation",
    lede="Un agente che legge le mail non lette, impara il tuo stile dalle inviate e prepara bozze di risposta in Gmail. Non manda niente: le bozze le controlli e le invii tu.",
    chips=[("Stato", "in uso"), ("Tipo", "agente locale"), ("Accesso", "Gmail API"), ("Costo", "nessuna API key")],
    sec={
        1: sec1(
            ["<b>Cos&rsquo;e.</b> Uno script Python locale che usa Claude Code headless (<code>claude -p</code>) per scrivere le risposte, salvate direttamente in Gmail come bozze.",
             "<b>Il problema che risolve.</b> Rispondere alle mail ripetitive e lento, ma l&rsquo;invio automatico e rischioso. Qui l&rsquo;AI prepara e tu invii: la velocita senza il rischio.",
             "<b>Perche e fatto cosi.</b> Gira in locale sull&rsquo;abbonamento (zero costo extra, niente API key). OAuth perche lo script lavora fuori dalla chat, ed e idempotente: salva gli id gia lavorati."],
            [("Tomas", "Svuota la posta piu in fretta: apre Gmail e trova le bozze gia pronte da rivedere."),
             ("Collaboratore tecnico", "Installa, da le credenziali Google una volta sola e lancia lo script quando serve."),
             ("Uso interno", "Strumento interno: non e esposto a clienti, aiuta solo chi risponde alle mail.")]),
        2: (table(["Strumento", "Ruolo nel progetto", "Perche scelto"], [
                ['Claude Code headless <span class="tag">motore</span>', "Scrive la bozza leggendo la mail e lo stile appreso.", "Usa l&rsquo;abbonamento: nessuna API key."],
                ['Gmail API + OAuth <span class="tag n">accesso</span>', "Legge le non lette e salva le bozze in Gmail.", "Serve perche lo script gira da solo."],
                ['Python + venv <span class="tag n">runtime</span>', "Orchestrazione: <code>run.py</code>, <code>learn_style.py</code>.", "Locale, dipendenze isolate."],
                ['<code>data/processed.json</code> <span class="tag n">stato</span>', "Traccia gli id gia lavorati.", "Idempotenza: niente bozze doppie."],
                ['<code>secrets/credentials.json</code> <span class="tag n">segreti</span>', "Credenziali Google OAuth, solo locale.", "Mai nel repo."],
            ]) + "\n" + h3("Comandi") + "\n" + table(["Comando", "Quando", "Cosa fa"], [
                ["<code>python learn_style.py</code>", "Una volta, e per aggiornare", "Impara lo stile dalle inviate &rarr; <code>data/style_profile.md</code>."],
                ["<code>python run.py</code>", "Quando vuoi", "Prepara le bozze per le non lette (salta le automatiche)."],
            ])),
        3: ('      <p class="muted">Un giro dello script, da mail non letta a bozza pronta. L&rsquo;ultimo passo, l&rsquo;invio, resta a te.</p>\n' +
            flow([("01", "Login", "OAuth Google la prima volta, il token resta salvato in locale.", "OAuth", False),
                  ("02", "Impara stile", "Legge le mail inviate e crea lo <code>style_profile.md</code>.", "learn_style.py", False),
                  ("03", "Leggi non lette", "Prende le mail non lette e salta quelle automatiche.", "Gmail API", False),
                  ("04", "Scrivi bozza", "Claude scrive la risposta nel tuo stile e la salva in Gmail.", "claude -p", False),
                  ("05", "Invia", "Apri Gmail &gt; Bozze, controlli e invii a mano.", "manuale", True)]) + "\n" +
            note("<b>Regola chiave.</b> Idempotenza: gli id gia lavorati stanno in <code>processed.json</code>, quindi rilanciare <code>run.py</code> non crea bozze doppie.") + "\n" +
            howto("preparare le bozze del giorno", "Per chi non l&rsquo;ha mai fatto: dal terminale alle bozze pronte in Gmail. Il primo blocco si fa una volta sola; dal punto 4 in poi e la routine di ogni volta.", [
                ("Ambiente, una volta sola", "Apri il terminale nella cartella del progetto. Crea l&rsquo;ambiente e installa: <code>python -m venv .venv</code>, attivalo, poi <code>pip install -r requirements.txt</code>."),
                ("Credenziali Google, una volta sola", "Su Google Cloud abilita la <b>Gmail API</b> e scarica il file <code>credentials.json</code>. Mettilo nella cartella <span class=\"path\">secrets/</span>: resta solo sul tuo computer, mai nel repo."),
                ("Impara il tuo stile", "Lancia <code>python learn_style.py</code>. Si apre il browser per il login Google (una volta): dai il consenso. Lo script legge le tue mail inviate e scrive <span class=\"path\">data/style_profile.md</span>. <span class=\"who sys\">lo fa lo script</span>"),
                ("Prepara le bozze", "Lancia <code>python run.py</code>. Legge le mail non lette (salta newsletter e notifiche) e per ognuna scrive una bozza di risposta nel tuo stile, salvandola dentro Gmail. <span class=\"who sys\">lo fa lo script</span>"),
                ("Apri Gmail e vai in Bozze", "Apri Gmail e clicca <span class=\"path\">Bozze</span> nella barra a sinistra: trovi le risposte gia scritte, una per mail."),
                ("Rileggi e invia tu", "Apri ogni bozza, correggi se serve e premi <b>Invia</b>. Niente parte da solo: l&rsquo;invio e sempre un tuo clic. <span class=\"who\">a mano</span>"),
            ]) + "\n" +
            h3("Dove finiscono le cose") + "\n" + table(["Cartella / file", "Contenuto"], [
                ["<code>core/</code>", "La logica dello script."],
                ["<code>data/</code>", "<code>style_profile.md</code> + <code>processed.json</code>."],
                ["<code>secrets/</code>", "<code>credentials.json</code> (OAuth), mai nel repo."],
                ["<code>run.py</code> &middot; <code>learn_style.py</code>", "Uso quotidiano &middot; apprendimento dello stile."],
            ])),
        4: (cards(
                ("Collaboratore - primi passi", "Da zero a produttivo",
                 ["Crea il venv e <code>pip install -r requirements.txt</code>.",
                  "Su Google Cloud abilita la Gmail API e scarica <code>credentials.json</code> in <code>secrets/</code>.",
                  "Lancia <code>python learn_style.py</code> (login browser una volta).",
                  "Lancia <code>python run.py</code>, poi controlla Gmail &gt; Bozze."]),
                ("Collaboratore - cosa deve saper fare", "Le competenze minime",
                 "Python di base e terminale, piu saper creare credenziali OAuth su Google Cloud. Nient&rsquo;altro: il testo lo scrive Claude.",
                 "mai committare <code>secrets/credentials.json</code> o i token. Restano solo in locale.")) + "\n" +
            pitch(["&laquo;E&rsquo; un assistente che ti pre-scrive le risposte alle mail nel tuo tono. Tu apri, dai un&rsquo;occhiata e invii: risparmi tempo senza perdere la tua voce.&raquo;",
                   "Nessuna mail parte senza che tu l&rsquo;abbia letta e approvata."]) + "\n" +
            warn(["<b>Non invia nulla.</b> Prepara soltanto bozze, l&rsquo;invio e sempre a mano.",
                  "<b>Segreti in locale.</b> Credenziali e token solo in <code>secrets/</code>, mai nel repo.",
                  "<b>Salta le automatiche.</b> Newsletter e notifiche vengono ignorate, niente bozze inutili."])),
        5: sec5([
                ["Pianificazione", "Lanciarlo a orari fissi (cron) resta da valutare."],
                ["Filtri", "Affinare quali mail saltare."],
            ], [
                ("Invio", "Manuale (solo bozze)"), ("Esecuzione", "Locale, a mano"),
                ("Costo API", "Nessuno (abbonamento)"), ("Idempotenza", "Si (processed.json)")]),
    }))

# ---- CONFIGURATORE VERNICI ----
P.append(dict(
    name="Configuratore Vernici", slug="configuratore-vernici", fonte="Fonte: repo CONFIGURATORI AI/tool-vernici",
    h1="Configuratore<br>Vernici",
    lede="Il cliente scrive a parole cosa deve fare; il tool compone in pochi secondi un carrello con prodotti e quantita, spiegando il perche di ogni riga.",
    chips=[("Stato", "demo"), ("Tipo", "tool web"), ("Motore", "deterministico offline"), ("Test", "18")],
    sec={
        1: sec1(
            ["<b>Cos&rsquo;e.</b> Una demo web (HTML/JS, nessun build) che interpreta una richiesta a parole e calcola un carrello di vernici con quantita e motivazione.",
             "<b>Il problema che risolve.</b> Il cliente non sa quali e quanti prodotti servono. Qui descrive il lavoro (&laquo;bagno, 3x4, termosifoni&raquo;) e ottiene una proposta chiara.",
             "<b>Perche e fatto cosi.</b> Motore deterministico e offline per la demo (prevedibile e testabile). L&rsquo;upsell verso il prodotto vero: sostituire l&rsquo;interprete con Claude API che ritorna lo stesso JSON, senza toccare UI e catalogo."],
            [("Tomas", "Mostra al cliente una demo che vende: dal linguaggio naturale al carrello pronto."),
             ("Collaboratore tecnico", "Estende catalogo e motore, o collega Claude API per capire qualsiasi frase."),
             ("Cliente rivenditore", "Fa provare ai suoi clienti un configuratore che riduce gli errori d&rsquo;ordine.")]),
        2: (table(["Strumento", "Ruolo nel progetto", "Perche scelto"], [
                ['HTML/JS classico <span class="tag">frontend</span>', "La UI del configuratore, gira anche da GitHub Pages.", "Semplice, nessuna toolchain."],
                ['<code>src/motore.js</code> <span class="tag n">logica</span>', "Interpreta il testo e calcola. Niente DOM qui.", "Deterministico, testabile a parte."],
                ['<code>src/catalogo.js</code> <span class="tag n">dati</span>', "Prodotti, prezzi e rese (di esempio).", "Separato dalla logica."],
                ['<code>src/app.js</code> <span class="tag n">collante</span>', "Aggancia UI e motore, disegna il carrello.", "Un solo punto per la UI."],
                ['<code>node --test</code> <span class="tag n">test</span>', "18 test su catalogo + motore.", "Regressioni sotto controllo."],
                ['Claude API <span class="tag n">futuro</span>', "Rimpiazzerebbe l&rsquo;interprete per capire QUALSIASI frase.", "Stesso JSON in uscita, UI invariata."],
            ]) + "\n" + h3("Il contratto JSON (non cambia mai)") + "\n" + table(["Output di motore o API", "Perche conta"], [
                ["<code>{ righe:[{prodotto, qty, perche}], totale, note:[] }</code>", "Formato fisso: cambiare il motore non rompe la UI ne il catalogo."],
            ])),
        3: ('      <p class="muted">Dalla frase del cliente al carrello, in pochi secondi e offline.</p>\n' +
            flow([("01", "Scrivi", "Il cliente descrive a parole il lavoro da fare.", "testo", False),
                  ("02", "Interpreta", "<code>motore.js</code> estrae misure, usi e prodotti nominati.", "motore.js", False),
                  ("03", "Calcola", "Quantita e rese in base al catalogo.", "catalogo.js", False),
                  ("04", "Carrello", "<code>app.js</code> mostra le righe con il perche di ognuna.", "app.js", False),
                  ("05", "Ordine", "Il carrello va rivisto e confermato da una persona.", "manuale", True)]) + "\n" +
            note("<b>Regola chiave.</b> Il contratto JSON e fisso: passare dal motore offline a Claude API non cambia la UI ne il catalogo. E anche l&rsquo;upsell verso il cliente.") + "\n" +
            howto("avviare e provare la demo", "Per chi non l&rsquo;ha mai fatto: la demo gira in locale con un mini-server (i browser bloccano l&rsquo;apertura diretta del file). Ogni passo in ordine.", [
                ("Apri il terminale nella cartella", "Vai nella cartella del tool: <code>cd tool-vernici</code>."),
                ("Avvia il mini-server", "Lancia <code>python3 -m http.server 8770</code>. Lascia questa finestra aperta: e il server che serve la pagina."),
                ("Apri la pagina nel browser", "Vai su <span class=\"path\">localhost:8770</span>. Si apre il configuratore."),
                ("Scrivi la richiesta a parole", "Nel campo di testo descrivi il lavoro come farebbe un cliente, es. <span class=\"path\">bagno 3x4, due mani, termosifoni</span>."),
                ("Leggi il carrello", "Il tool mostra le righe con prodotto, quantita e il <b>perche</b> di ognuna. <span class=\"who sys\">lo fa il motore</span>"),
                ("Confermato da una persona", "Il carrello e una proposta: va sempre riletto e confermato prima di trasformarlo in un ordine vero. <span class=\"who\">a mano</span>"),
            ]) + "\n" +
            h3("Dove finiscono le cose") + "\n" + table(["Cartella", "Contenuto"], [
                ["<code>src/</code>", "catalogo, motore, app."],
                ["<code>test/</code>", "18 test (node --test)."],
                ["<code>docs/</code> &middot; <code>mockups/</code> &middot; <code>assets/</code>", "documentazione, mockup, risorse."],
            ])),
        4: (cards(
                ("Collaboratore - primi passi", "Da zero a produttivo",
                 ["<code>cd tool-vernici; python3 -m http.server 8770</code>, poi apri <code>localhost:8770</code>.",
                  "<code>node --test test/*.test.js</code> per la logica.",
                  "Leggi <code>src/motore.js</code>: e li la logica, senza DOM.",
                  "Per il prodotto vero: sostituisci <code>interpretaRichiesta()</code> con Claude API (stesso JSON)."]),
                ("Collaboratore - cosa deve saper fare", "Le competenze minime",
                 "JavaScript di base e saper leggere i test Node. Per l&rsquo;upsell: chiamare Claude API e mappare l&rsquo;output nel JSON del contratto.",
                 "prezzi e rese nel catalogo sono di ESEMPIO: prima del prodotto vero vanno sostituiti con quelli reali.")) + "\n" +
            pitch(["&laquo;Il tuo cliente scrive cosa deve verniciare e ottiene subito una lista di prodotti e quantita, con la spiegazione del perche. Meno errori d&rsquo;ordine, piu fiducia.&raquo;",
                   "E una demo: la versione completa capisce qualsiasi frase, con la stessa interfaccia."]) + "\n" +
            warn(["<b>Dati di esempio.</b> Prezzi e rese non sono reali finche non li sostituisci.",
                  "<b>Serve un mini-server.</b> I browser bloccano <code>file://</code>: aprila via <code>http.server</code>.",
                  "<b>E una demo.</b> L&rsquo;interprete capisce i casi comuni, non ancora qualsiasi frase."])),
        5: sec5([
                ["Claude API", "Interprete che capisce qualsiasi richiesta."],
                ["Catalogo reale", "Sostituire prezzi e rese di esempio."],
                ["Checkout", "Collegare a un vero flusso d&rsquo;ordine."],
            ], [
                ("Stato", "Demo"), ("Motore", "Deterministico, offline"),
                ("Test", "18 (node --test)"), ("Dati", "Di esempio")]),
    }))

# ---- STORYTELLING ----
P.append(dict(
    name="Storytelling - l'altra parte", slug="storytelling-altra-parte", fonte="Fonte: repo STORYTELLING/sito",
    h1="Storytelling<br>l&rsquo;altra parte",
    lede="Il sito e il blog &laquo;l&rsquo;altra parte&raquo; per AL: articoli di storytelling e le immagini social, generati da script che tengono in ordine cartelle e home.",
    chips=[("Stato", "in uso"), ("Tipo", "sito + blog"), ("Build", "script Python"), ("Hosting", "statico")],
    sec={
        1: sec1(
            ["<b>Cos&rsquo;e.</b> Un repo con due cose separate: il blog &laquo;l&rsquo;altra parte&raquo; (articoli di storytelling) e le immagini social usate da Notion e Instagram. La lista articoli in home la genera uno script.",
             "<b>Il problema che risolve.</b> Pubblicare articoli a mano e disordinato. Qui uno script impagina l&rsquo;articolo e aggiorna la home; le cartelle numerate (<code>NN-slug</code>) restano in ordine cronologico da sole.",
             "<b>Perche e fatto cosi.</b> Sito statico, semplice da ospitare. Il numero <code>NN</code> e la puntata, cosi si sa sempre qual e l&rsquo;ultima. I link alle immagini social sono usati da fuori: non si spostano."],
            [("Tomas", "Pubblica un articolo con un comando, senza impaginare niente a mano."),
             ("Collaboratore", "Aggiunge articoli seguendo il formato .md piu lo script di build."),
             ("Lettore (AL)", "Legge un blog curato e coerente, puntata dopo puntata.")]),
        2: (table(["Strumento", "Ruolo nel progetto", "Perche scelto"], [
                ['HTML statico <span class="tag">sito</span>', "<code>index.html</code> + un <code>index.html</code> per articolo.", "Facile da ospitare (GitHub Pages)."],
                ['<code>tools/*.py</code> <span class="tag n">build</span>', "Impagina l&rsquo;articolo e rigenera la home.", "Un comando, niente lavoro manuale."],
                ['<code>meta.json</code> <span class="tag n">dati</span>', "Dati dell&rsquo;articolo per rigenerare la home.", "Fonte unica per la lista."],
                ['Cartelle <code>NN-slug</code> <span class="tag n">ordine</span>', "Un numero di puntata per cartella.", "Ordine cronologico automatico."],
                ['<code>social/&lt;cliente&gt;/</code> <span class="tag n">immagini</span>', "Slide 1080x1350 usate da Notion/IG.", "Link stabili, da non spostare."],
            ]) + "\n" + h3("Regola delle cartelle") + "\n" + table(["Percorso", "Contenuto"], [
                ["<code>blog/NN-slug/</code>", "<code>index.html</code> + <code>copertina.jpg</code> + <code>meta.json</code>."],
                ["<code>social/&lt;cliente&gt;/NN-slug/</code>", "<code>slide1.png</code> ... (1080x1350)."],
            ])),
        3: ('      <p class="muted">Aggiungere un articolo: dal testo .md alla pagina pubblicata.</p>\n' +
            flow([("01", "Scrivi", "Il testo in un <code>.md</code> con l&rsquo;intestazione.", "bozza.md", False),
                  ("02", "Genera", "Lo script crea <code>blog/NN-slug/</code> impaginato.", "nuovo-articolo.py", False),
                  ("03", "Home", "La lista articoli si aggiorna da <code>meta.json</code>.", "auto", False),
                  ("04", "Copertina", "Sostituisci la copertina segnaposto con la foto vera.", "manuale", True),
                  ("05", "Pubblica", "Commit e deploy del sito statico.", "manuale", True)]) + "\n" +
            note("<b>Regola chiave.</b> Non spostare le cartelle gia pubblicate in <code>social/</code>: i link diretti sono usati da Notion e Instagram, spostarli li rompe.") + "\n" +
            howto("pubblicare un nuovo articolo", "Per chi non l&rsquo;ha mai fatto: dal testo alla puntata online. Lo script fa il lavoro pesante (impagina e aggiorna la home); a te restano testo, copertina e pubblicazione.", [
                ("Scrivi il testo in un file .md", "Crea un file <code>bozza.md</code> con l&rsquo;intestazione richiesta (trovi un esempio dentro <code>tools/nuovo-articolo.py</code>). Scrivi li l&rsquo;articolo."),
                ("Lancia lo script", "Dal terminale: <code>python3 tools/nuovo-articolo.py bozza.md</code>. Crea la cartella <span class=\"path\">blog/NN-slug/</span> gia impaginata. <span class=\"who sys\">lo fa lo script</span>"),
                ("Controlla la home", "La lista degli articoli in home si aggiorna da sola leggendo i <code>meta.json</code>: apri la home e verifica che la nuova puntata sia in cima. <span class=\"who sys\">lo fa lo script</span>"),
                ("Metti la copertina vera", "Nella cartella dell&rsquo;articolo sostituisci <code>copertina.jpg</code> segnaposto con la foto definitiva. <span class=\"who\">a mano</span>"),
                ("Pubblica", "Fai <code>commit</code> e <code>deploy</code> del sito statico. Da questo momento la puntata e online. <span class=\"who\">a mano</span>"),
            ]) + "\n" +
            h3("Dove finiscono le cose") + "\n" + table(["Cartella", "Contenuto"], [
                ["<code>index.html</code>", "La home (generata dagli script)."],
                ["<code>blog/</code>", "Un articolo per cartella <code>NN-slug</code>."],
                ["<code>social/</code>", "Immagini per cliente e per post."],
                ["<code>tools/</code>", "Script e template."],
            ])),
        4: (cards(
                ("Collaboratore - primi passi", "Da zero a produttivo",
                 ["Leggi il README: come sono separati <code>blog/</code> e <code>social/</code>.",
                  "Scrivi <code>bozza.md</code> con l&rsquo;intestazione (esempio in <code>tools/nuovo-articolo.py</code>).",
                  "Lancia <code>python3 tools/nuovo-articolo.py bozza.md</code>.",
                  "Sostituisci <code>copertina.jpg</code>, poi commit e deploy."]),
                ("Collaboratore - cosa deve saper fare", "Le competenze minime",
                 "Markdown per scrivere, Python di base per lanciare lo script e Git per pubblicare. Nessun framework.",
                 "non rinominare o spostare le cartelle <code>social/</code> gia pubblicate: rompi i link usati da Notion e Instagram.")) + "\n" +
            pitch(["&laquo;Il tuo blog racconta l&rsquo;altra parte con un&rsquo;impaginazione curata e coerente, articolo dopo articolo. Le stesse immagini alimentano anche Instagram.&raquo;",
                   "Ogni puntata e numerata: la storia si legge sempre in ordine."]) + "\n" +
            warn(["<b>Non spostare</b> le cartelle <code>social/</code> pubblicate: hanno link esterni attivi.",
                  "<b>La home e generata:</b> si modifica via <code>meta.json</code> e script, non a mano.",
                  "<b>Copertine segnaposto:</b> vanno sostituite con la foto vera."])),
        5: sec5([
                ["Automazioni", "Collegare la pubblicazione al flusso social."],
                ["SEO", "Meta e anteprime social per ogni articolo."],
            ], [
                ("Tipo", "Sito statico + blog"), ("Build", "Script Python"),
                ("Immagini social", "Link stabili (Notion/IG)"), ("Pubblicazione", "Commit/deploy manuale")]),
    }))

# ---- SITI WEB EVOLUTION ----
P.append(dict(
    name="Siti Web Evolution", slug="siti-web-evolution", fonte="Fonte: repo SITI WEB EVOLUTION",
    h1="Siti Web<br>Evolution",
    lede="Landing page per i clienti costruite da un motore di temi: parti da un tema pronto, lo adatti al cliente e ottieni una pagina coerente e veloce.",
    chips=[("Stato", "in uso"), ("Tipo", "landing clienti"), ("Motore", "temi"), ("Target", "mobile-first")],
    sec={
        1: sec1(
            ["<b>Cos&rsquo;e.</b> Un sistema per fare landing ai clienti: un <code>_motore-landing</code> con temi pronti (ottone, minimale, chiaro) e una cartella per cliente con la pagina finale.",
             "<b>Il problema che risolve.</b> Rifare ogni landing da zero e lento e incoerente. Qui si parte da un tema e si personalizza: stessa qualita, tempi molto ridotti.",
             "<b>Perche e fatto cosi.</b> HTML statico e mobile-first, facile da ospitare. Temi separati dai clienti: aggiornare un tema non tocca le pagine gia consegnate."],
            [("Tomas", "Sforna landing per i clienti partendo da una base gia solida."),
             ("Collaboratore", "Crea un cliente nuovo copiando un tema e cambiando i contenuti."),
             ("Cliente (attivita)", "Ottiene una landing veloce e curata, perfetta da telefono.")]),
        2: (table(["Strumento", "Ruolo nel progetto", "Perche scelto"], [
                ['HTML/CSS statico <span class="tag">frontend</span>', "Le landing, una per cliente.", "Mobile-first, hosting semplice."],
                ['<code>_motore-landing/temi/</code> <span class="tag n">temi</span>', "tema-ottone, tema-minimale, tema-chiaro.", "Basi riusabili e coerenti."],
                ['<code>anteprima-temi.html</code> <span class="tag n">preview</span>', "Confronta i temi in un colpo.", "Scelta rapida col cliente."],
                ['<code>clienti/&lt;Nome&gt;/</code> <span class="tag n">output</span>', "<code>index.html</code> + assets del cliente.", "Pagine separate dai temi."],
            ]) + "\n" + h3("Temi disponibili") + "\n" + table(["Tema", "Mood"], [
                ["<code>tema-ottone</code>", "Caldo, premium."],
                ["<code>tema-minimale</code>", "Essenziale."],
                ["<code>tema-chiaro</code>", "Pulito, luminoso."],
            ])),
        3: ('      <p class="muted">Da tema scelto a landing online, cliente per cliente.</p>\n' +
            flow([("01", "Scegli tema", "Apri <code>anteprima-temi.html</code> col cliente.", "anteprima", False),
                  ("02", "Crea cliente", "Copia il tema in <code>clienti/&lt;Nome&gt;/</code>.", "copia", False),
                  ("03", "Personalizza", "Testi, immagini e colori del cliente.", "index.html", False),
                  ("04", "Verifica", "Mobile-first, niente overflow, stati.", "QA", False),
                  ("05", "Pubblica", "Deploy statico (es. GitHub Pages).", "manuale", True)]) + "\n" +
            note("<b>Regola chiave.</b> Aggiornare un tema non modifica le landing gia consegnate: ogni cliente ha la sua copia del tema.") + "\n" +
            howto("creare la landing di un cliente", "Per chi non l&rsquo;ha mai fatto: da tema scelto a pagina online. L&rsquo;idea chiave: ogni cliente parte da una <b>copia</b> del tema, cosi resta indipendente.", [
                ("Scegli il tema col cliente", "Apri <code>_motore-landing/anteprima-temi.html</code>: mostra i temi affiancati (ottone, minimale, chiaro). Decidete insieme quale."),
                ("Copia il tema per il cliente", "Copia la cartella del tema scelto dentro <span class=\"path\">clienti/&lt;Nome&gt;/</span>. Questa e la landing di quel cliente, staccata dagli altri."),
                ("Personalizza i contenuti", "Nell&rsquo;<code>index.html</code> del cliente cambia testi, immagini e colori con quelli suoi. <span class=\"who\">a mano</span>"),
                ("Verifica da telefono", "Controlla il <b>mobile-first</b>: niente scroll orizzontale, tap target grandi, tutto leggibile su schermo piccolo. <span class=\"who\">a mano</span>"),
                ("Pubblica", "Deploy statico (es. GitHub Pages): la landing va online. <span class=\"who\">a mano</span>"),
            ]) + "\n" +
            h3("Dove finiscono le cose") + "\n" + table(["Cartella / file", "Contenuto"], [
                ["<code>_motore-landing/temi/</code>", "I temi base."],
                ["<code>_motore-landing/anteprima-temi.html</code>", "Confronto dei temi."],
                ["<code>clienti/&lt;Nome&gt;/</code>", "La landing del cliente."],
            ])),
        4: (cards(
                ("Collaboratore - primi passi", "Da zero a produttivo",
                 ["Apri <code>_motore-landing/anteprima-temi.html</code> per vedere i temi.",
                  "Copia il tema scelto in <code>clienti/&lt;Nome&gt;/</code>.",
                  "Cambia testi e immagini nell&rsquo;<code>index.html</code> del cliente.",
                  "Controlla il mobile-first, poi pubblica."]),
                ("Collaboratore - cosa deve saper fare", "Le competenze minime",
                 "HTML/CSS e occhio al mobile-first (tap target &ge;44px). Nessun framework ne build.",
                 "ogni cliente ha la SUA copia del tema: non collegare piu clienti allo stesso file, o una modifica li tocca tutti.")) + "\n" +
            pitch(["&laquo;La tua landing nasce da una base gia curata e collaudata, poi la vestiamo sui tuoi contenuti. Veloce da mettere online e perfetta da telefono.&raquo;",
                   "Mobile-first: la maggior parte dei visitatori arriva da smartphone."]) + "\n" +
            warn(["<b>Mobile-first sempre:</b> e da li che arriva la maggior parte dei clienti.",
                  "<b>Una copia per cliente:</b> niente file di tema condiviso tra piu clienti.",
                  "<b>Niente overflow orizzontale:</b> i contenuti larghi scrollano nel loro box."])),
        5: sec5([
                ["Nuovi temi", "Ampliare la libreria dei temi."],
                ["Form / lead", "Collegare i contatti a un backend."],
            ], [
                ("Tipo", "Landing clienti"), ("Temi", "ottone &middot; minimale &middot; chiaro"),
                ("Target", "Mobile-first"), ("Clienti attivi", "Business AL &middot; Ai Do Mori")]),
    }))

# ---- PREVENTIVI AI / FOOD LAB ----
P.append(dict(
    name="Preventivi AI - Food Lab", slug="preventivi-foodlab", fonte="Fonte: repo PREVENTIVI AI/Food Lab Experience",
    h1="Preventivi AI<br>Food Lab",
    lede="Deck e preventivi con prezzi per le proposte ai clienti. Il caso Food Lab Experience: una proposta con formula ibrida di pricing, presentata come pagina sfogliabile.",
    chips=[("Stato", "in uso"), ("Tipo", "deck/preventivo"), ("Formato", "HTML"), ("Prezzi", "inclusi")],
    sec={
        1: sec1(
            ["<b>Cos&rsquo;e.</b> Proposte commerciali (deck/preventivo) costruite come pagina HTML da presentare al cliente. Il primo caso e Food Lab Experience, con prezzi e formula ibrida.",
             "<b>Il problema che risolve.</b> Un preventivo in PDF piatto convince poco. Qui la proposta e una pagina curata che racconta valore e prezzo insieme.",
             "<b>Perche e fatto cosi.</b> HTML sfogliabile = controllo pieno sulla presentazione, si manda con un link e si aggiorna in fretta."],
            [("Tomas", "Presenta al cliente una proposta che vende, non un semplice foglio prezzi."),
             ("Collaboratore", "Duplica il formato per un nuovo preventivo cambiando contenuti e cifre."),
             ("Cliente", "Legge una proposta chiara: cosa riceve e quanto costa.")]),
        2: (table(["Strumento", "Ruolo nel progetto", "Perche scelto"], [
                ['HTML/CSS <span class="tag">formato</span>', "La proposta come pagina sfogliabile.", "Controllo totale, condivisibile con un link."],
                ['Script Proposta (.rtf) <span class="tag n">fonte</span>', "Il testo e l&rsquo;argomentario della proposta.", "Base del contenuto."],
                ['Formula pricing <span class="tag n">modello</span>', "Ibrida: fisso + mensile + percentuali.", "Decisa insieme al cliente."],
            ]) + "\n" + h3("Formula Food Lab") + "\n" + table(["Voce", "Valore"], [
                ["Setup iniziale", "1.200 &euro;"],
                ["Canone mensile", "790 &euro;/mese"],
                ["Quota su risultati", "10%"],
                ["Quota aggiuntiva", "8%"],
            ]) + "\n" + note("Il dettaglio esatto delle voci percentuali e nel deck: qui la formula e riassunta.")),
        3: ('      <p class="muted">Da brief del cliente a proposta presentata.</p>\n' +
            flow([("01", "Brief", "Cosa vuole il cliente, budget e obiettivi.", "brief", False),
                  ("02", "Bozza", "Claude aiuta a strutturare proposta e testi.", "claude", False),
                  ("03", "Prezzi", "Applica la formula ibrida concordata.", "pricing", False),
                  ("04", "Deck", "Impagina in HTML sfogliabile.", "index.html", False),
                  ("05", "Presenta", "Invii il link e presenti al cliente.", "manuale", True)]) + "\n" +
            note("<b>Regola chiave.</b> I prezzi si decidono con il cliente: qui e documentato il caso Food Lab, non un listino fisso.") + "\n" +
            howto("preparare una nuova proposta", "Per chi non l&rsquo;ha mai fatto: si parte da un deck gia fatto (Food Lab) e lo si adatta al nuovo cliente. Le cifre non si inventano: si confermano prima di mandare.", [
                ("Apri il deck di esempio", "Apri <code>Food Lab Experience/index.html</code> nel browser: e il formato sfogliabile da cui partire."),
                ("Leggi l&rsquo;argomentario", "Apri lo <span class=\"path\">Script Proposta (.rtf)</span>: spiega come e strutturata la proposta e il tono da tenere."),
                ("Duplica la cartella", "Copia l&rsquo;intera cartella e rinominala per il nuovo cliente: cosi il caso Food Lab resta intatto."),
                ("Cambia testi e cifre", "Nell&rsquo;<code>index.html</code> aggiorna i contenuti e applica la formula concordata (fisso + canone + quote). <span class=\"who\">a mano</span>"),
                ("Conferma i prezzi col cliente", "Prima di inviare, fatti confermare le cifre: un preventivo con numeri sbagliati e un problema. <span class=\"who\">a mano</span>"),
                ("Manda il link e presenta", "Invii il link della pagina e la presenti: e una proposta, non un contratto. <span class=\"who\">a mano</span>"),
            ]) + "\n" +
            h3("Dove finiscono le cose") + "\n" + table(["File", "Contenuto"], [
                ["<code>Food Lab Experience/index.html</code>", "Il deck sfogliabile."],
                ["<code>Food Lab Experience/Script Proposta ....rtf</code>", "Il testo della proposta."],
            ])),
        4: (cards(
                ("Collaboratore - primi passi", "Da zero a produttivo",
                 ["Apri <code>Food Lab Experience/index.html</code> per vedere il formato.",
                  "Leggi lo Script Proposta per capire l&rsquo;argomentario.",
                  "Duplica la cartella per un nuovo preventivo.",
                  "Cambia testi e cifre, poi manda il link."]),
                ("Collaboratore - cosa deve saper fare", "Le competenze minime",
                 "HTML/CSS di base per adattare il deck e chiarezza sui numeri della formula. Il testo si costruisce con Claude.",
                 "mai numeri inventati: le cifre di un preventivo vanno confermate col cliente prima di mandarle.")) + "\n" +
            pitch(["&laquo;La tua proposta non e un foglio prezzi: e una pagina che racconta cosa ottieni e quanto costa, chiara e sfogliabile.&raquo;",
                   "La formula e su misura: una parte fissa, un canone e una quota sui risultati."]) + "\n" +
            warn(["<b>Prezzi da confermare</b> col cliente prima dell&rsquo;invio.",
                  "<b>La formula e specifica</b> di Food Lab, non un listino generale.",
                  "<b>Il deck e una proposta,</b> non un contratto."])),
        5: sec5([
                ["Template", "Rendere il deck riusabile per altri clienti."],
                ["Generatore", "Da brief a bozza di deck con Claude."],
            ], [
                ("Tipo", "Deck/preventivo"), ("Caso", "Food Lab Experience"),
                ("Formula", "1.200 + 790/mese + 10% + 8%"), ("Prezzi", "Nel deck")]),
    }))

# ---- COME USIAMO GITHUB ----
P.append(dict(
    name="Come usiamo GitHub", slug="come-usiamo-github", fonte="Fonte: org al-consultant",
    h1="Come usiamo<br>GitHub",
    lede="GitHub è dove vivono il codice e i siti dei progetti: una copia online con tutta la storia delle modifiche, condivisa tra chi lavora. Non è l&rsquo;hosting: i siti vanno online sul nostro server. Qui c&rsquo;è come lo usiamo noi, senza fronzoli.",
    chips=[("Stato", "riferimento"), ("Tipo", "guida di metodo"), ("Org", "al-consultant"), ("Flusso", "commit su main")],
    sec={
        1: sec1(
            ["<b>Cos&rsquo;è.</b> GitHub è una copia online dei progetti con la loro storia. Sotto c&rsquo;è <b>git</b>, che sul tuo computer tiene traccia di ogni modifica; GitHub la mette online e la fa condividere. Un progetto = un <b>repository</b> (repo): es. <code>alblog</code>, <code>al-documentazione</code>.",
             "<b>Il problema che risolve.</b> Lavorare in due sugli stessi file senza sovrascriversi, e poter <b>tornare indietro</b> se qualcosa si rompe. Ogni salvataggio (<b>commit</b>) è un punto nella storia a cui puoi tornare.",
             "<b>Perche è fatto cosi da noi.</b> GitHub è la fonte unica e il posto della collaborazione, <b>non</b> l&rsquo;hosting. I repo stanno sotto l&rsquo;organizzazione <code>al-consultant</code>; siamo in due, quindi si committa dritto sul ramo <code>main</code>, senza giri."],
            [("Tomas", "Tiene tutto in un posto solo, con la storia completa, e condivide il lavoro col collaboratore."),
             ("Collaboratore", "Scarica il repo, lavora sul suo computer e ricarica: senza mandarsi file per mail."),
             ("Uso interno", "È il metodo comune a tutti i repo dell&rsquo;org, non un progetto a sé.")]),
        2: (table(["Concetto", "Cos&rsquo;è", "Perche conta"], [
                ['Repository (repo) <span class="tag">base</span>', "La cartella del progetto con tutta la sua storia.", "Un repo per progetto."],
                ['Commit <span class="tag n">salvataggio</span>', "Un salvataggio con un messaggio che dice cosa hai cambiato.", "È il punto a cui puoi tornare."],
                ['Ramo <code>main</code> <span class="tag n">linea</span>', "La linea principale del progetto.", "Da noi si lavora qui direttamente."],
                ['Push / Pull <span class="tag n">sincronia</span>', "Push manda i tuoi commit su GitHub, pull scarica quelli degli altri.", "Tiene allineate le due copie."],
                ['<code>.gitignore</code> <span class="tag n">filtro</span>', "La lista di file da NON caricare mai.", "Ci tiene fuori segreti e roba locale."],
                ['Org <code>al-consultant</code> <span class="tag n">proprietario</span>', "L&rsquo;account che possiede i repo, con i suoi membri.", "I repo stanno sotto l&rsquo;org, non sotto una persona."],
            ]) + "\n" + h3("Strumenti che usiamo") + "\n" + table(["Strumento", "Ruolo", "Perche"], [
                ["git (terminale)", "I comandi veri: clone, add, commit, push, pull.", "È come lavora Claude Code."],
                ["GitHub Desktop", "App grafica: gli stessi comandi coi bottoni.", "Per chi non ama il terminale."],
                ["github.com", "Il sito: vedi repo e storia, gestisci membri e permessi.", "Il pannello di controllo."],
            ]) + "\n" + h3("Comandi di ogni giorno") + "\n" + table(["Comando", "Quando", "Cosa fa"], [
                ["<code>git clone &lt;url&gt;</code>", "Una volta sola", "Scarica il repo sul tuo computer."],
                ["<code>git pull</code>", "Prima di iniziare", "Scarica le ultime modifiche degli altri."],
                ["<code>git add -A</code>", "Fatto un pezzo", "Prepara i file cambiati per il salvataggio."],
                ["<code>git commit -m \"messaggio\"</code>", "Dopo add", "Salva un punto nella storia, col messaggio."],
                ["<code>git push</code>", "Dopo commit", "Manda i tuoi salvataggi su GitHub."],
            ]) + "\n" + h3("Il nostro caso: repo pubblico ma protetto") + "\n" + table(["Cosa", "Come"], [
                ["<code>al-documentazione</code> è pubblico", "Il codice è visibile a tutti su github.com."],
                ["I testi sensibili non si vedono", "<code>cifra.sh</code> li cifra con staticrypt: online va solo la versione cifrata, aperta con password."],
                ["I sorgenti in chiaro restano fuori", "Vivono in <code>_sorgenti-*</code>, che <code>.gitignore</code> tiene fuori dal repo: sul pubblico non arrivano mai."],
            ])),
        3: ('      <p class="muted">Il giro di ogni giorno: dal tuo computer a GitHub. Il deploy del sito è un passo a parte, sul nostro server.</p>\n' +
            flow([("01", "Pull", "Scarichi le ultime modifiche prima di iniziare.", "git pull", False),
                  ("02", "Lavori", "Modifichi i file sul tuo computer, nell&rsquo;editor.", "editor", False),
                  ("03", "Commit", "Salvi un punto con un messaggio chiaro.", "git commit", False),
                  ("04", "Push", "Mandi i commit su GitHub, li vede anche l&rsquo;altro.", "git push", False),
                  ("05", "Deploy", "Il sito va online sul nostro server (passo a parte).", "server", True)]) + "\n" +
            note("<b>Regola chiave.</b> Si committa dritto su <code>main</code> perche siamo in due. Quando sarete di piu, si passa a un <b>branch</b> per persona e a una <b>Pull Request</b> per rivedere prima di unire.") + "\n" +
            howto("clonare un repo e fare la prima modifica", "Per chi non l&rsquo;ha mai fatto: da zero fino alla prima modifica online su GitHub. I primi due passi si fanno una volta sola.", [
                ("Installa git, una volta sola", "Su Mac di solito c&rsquo;è già (controlla con <code>git --version</code>). Su Windows scarica <b>Git for Windows</b>, oppure installa <b>GitHub Desktop</b> che se lo porta dietro."),
                ("Fatti aggiungere all&rsquo;org", "Chiedi a Tomas di invitarti in <code>al-consultant</code> su github.com. Accetti l&rsquo;invito dalla mail. <span class=\"who\">a mano</span>"),
                ("Clona il repo", "Sul repo, bottone verde <span class=\"path\">Code</span> &gt; copia l&rsquo;URL. In terminale: <code>git clone &lt;URL&gt;</code>. Con Desktop: <span class=\"path\">File &gt; Clone repository</span>. Ti crea la cartella in locale."),
                ("Prima di lavorare, aggiorna", "Lancia <code>git pull</code>: prende le ultime modifiche degli altri, cosi non parti da una copia vecchia. <span class=\"who\">a mano</span>"),
                ("Modifica e salva un punto", "Cambi i file, poi <code>git add -A</code> e <code>git commit -m \"cosa hai fatto\"</code>. Il messaggio serve a chi legge la storia dopo. <span class=\"who\">a mano</span>"),
                ("Manda online su GitHub", "Lancia <code>git push</code>. Ora le tue modifiche sono su GitHub e le vede anche Tomas. Il sito online è un altro passo (deploy sul server). <span class=\"who\">a mano</span>"),
            ]) + "\n" +
            h3("Dove finiscono le cose") + "\n" + table(["Posto", "Contenuto"], [
                ["github.com/al-consultant", "Tutti i repo dell&rsquo;org, i membri e i permessi."],
                ["Repo in locale", "La tua copia di lavoro, dove modifichi i file."],
                ["<code>.git/</code> (nascosta)", "La storia dei commit. Non si tocca a mano."],
                ["<code>.gitignore</code>", "La lista di cosa non caricare (segreti, file locali)."],
            ])),
        4: (cards(
                ("Collaboratore - primi passi", "Da zero a produttivo",
                 ["Fatti invitare nell&rsquo;org <code>al-consultant</code> e accetta l&rsquo;invito.",
                  "Installa git o GitHub Desktop, poi imposta nome e mail: <code>git config --global user.name</code> e <code>user.email</code>.",
                  "<code>git clone &lt;URL&gt;</code> del repo su cui devi lavorare.",
                  "Il giro: <code>git pull</code> &rarr; modifichi &rarr; <code>git add -A</code> &rarr; <code>git commit -m \"...\"</code> &rarr; <code>git push</code>."]),
                ("Collaboratore - cosa deve saper fare", "Le competenze minime",
                 "Sapere clone, pull, commit e push, col terminale o con GitHub Desktop. Nient&rsquo;altro: niente branch complicati finche lavoriamo su <code>main</code>.",
                 "mai committare segreti (<code>.env</code>, token, credenziali, i file dentro <code>secrets/</code>). Controlla che siano in <code>.gitignore</code> PRIMA del primo commit.")) + "\n" +
            pitch(["&laquo;GitHub è come un Google Drive per il codice, ma con la storia completa: ogni salvataggio resta, si può tornare indietro e più persone lavorano sugli stessi file senza pestarsi i piedi.&raquo;",
                   "Il sito non è ospitato qui: GitHub tiene il codice, il sito va online sul nostro server."]) + "\n" +
            warn(["<b>Mai segreti nel repo.</b> <code>.env</code>, token, chiavi, credenziali: sempre fuori, in <code>.gitignore</code>.",
                  "<b><code>al-documentazione</code> è pubblico.</b> Chiunque legge il codice: per questo le pagine sensibili sono cifrate e i sorgenti in chiaro sono gitignorati.",
                  "<b>Si committa su <code>main</code>.</b> Niente PR per ora: un commit sbagliato lo vedono tutti subito. Messaggi chiari e <code>git pull</code> prima di <code>git push</code>."])),
        5: sec5([
                ["Branch + PR", "Quando saremo di piu: un branch per persona e revisione prima di unire."],
                ["Automazioni", "GitHub Actions per build e deploy automatici (ora il deploy è a mano)."],
                ["Protezione main", "Regole sul ramo main quando arriveranno le Pull Request."],
            ], [
                ("Org", "al-consultant (2 membri)"),
                ("Flusso", "Commit diretto su main"),
                ("Hosting", "Server nostro (non GitHub Pages)"),
                ("Pagine sensibili", "Cifrate, sorgenti gitignorati")]),
    }))

# ============================ SERVIZI AL CONSULTANT ============================
# Dati RISERVATI: NON stanno qui (finirebbero sul repo pubblico in chiaro).
# Vivono in _sorgenti-servizi/_dati-servizi.py, GITIGNORED, caricato solo se
# presente (in locale). Su un clone pubblico il file manca: la sezione resta
# "in preparazione" e nessun contenuto riservato viene esposto.
SERVIZI_ITEMS = []
_dati_srv = SRC_PROT / "_dati-servizi.py"
if _dati_srv.exists():
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("_dati_servizi", _dati_srv)
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)  # se il file c'e' ma e' rotto l'errore esce forte
    _svc, SERVIZI_ITEMS = _mod.build(globals())
    P.extend(_svc)
    print("caricati", len(_svc), "dossier servizi (riservati, solo locale)")
else:
    print("nessun dato servizi in locale: sezione Servizi in preparazione")


# ---- scrivi i file ----
# Tutti i dossier vanno in una cartella sorgente GITIGNORED e verranno cifrati.
# p["protected"]=True identifica i servizi (area riservata AL); gli altri sono
# Progetti AI. Entrambe le aree finiscono cifrate, solo in cartelle diverse.
for p in P:
    dest = SRC_PROT if p.get("protected") else SRC_PUB
    (dest / (p["slug"] + ".html")).write_text(fix(page(p)), encoding="utf-8")
    print("scritto", dest.name + "/" + p["slug"] + ".html")

# ---- HUB A DUE LIVELLI ----
# Home = 2 card categoria. Ogni categoria ha una pagina sua con i suoi dossier.
# Categoria: (nome, slug, descrizione, [progetti], protected).
#   protected=True -> pagina + dossier vanno in _sorgenti-servizi/ e poi cifrati.
# Lista vuota = "in arrivo".
CATS = [
    ("Progetti AI", "progetti-ai", "Gli strumenti e le automazioni AI: motore comune, tool interni e lavori per i clienti.", [
        ("architettura-strumenti.html", "Architettura strumenti", "Come si incastrano tutti gli strumenti AI: motore, principi, cartelle.", "meta"),
        ("automazione-social-al.html", "Automazione Social AL", "Motore social multi-cliente: crea e ricicla contenuti nel tono giusto.", "in uso"),
        ("mail-automation.html", "Mail Automation", "Bozze di risposta in Gmail nel tuo stile. Non invia: prepara.", "in uso"),
        ("preventivi-foodlab.html", "Preventivi AI - Food Lab", "Deck e preventivi con prezzi come pagina sfogliabile.", "in uso"),
        ("configuratore-vernici.html", "Configuratore Vernici", "Dal linguaggio naturale a un carrello di prodotti, col perche.", "demo"),
        ("siti-web-evolution.html", "Siti Web Evolution", "Landing per clienti da un motore di temi, mobile-first.", "in uso"),
        ("storytelling-altra-parte.html", "Storytelling - l'altra parte", "Sito e blog l'altra parte per AL, con build da script.", "in uso"),
        ("come-usiamo-github.html", "Come usiamo GitHub", "Repo, collaborazione e gestione: come lavoriamo su GitHub, coi nostri repo.", "meta"),
    ], True),
    # Gli item servizi arrivano da _dati-servizi.py (gitignored). Se non c'e',
    # SERVIZI_ITEMS resta [] e la categoria appare "in preparazione".
    ("Servizi AL Consultant", "servizi-al-consultant", "Le procedure operative interne: come si fanno i lavori per i clienti, strumento per strumento. Area riservata.", SERVIZI_ITEMS, True),
]

def _head(title, prefix=""):
    return ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>" + title + "</title>\n" + FONTS + stylesheet(prefix) + "</head>\n<body>\n")


def _cat_cards(items):
    if not items:
        return ('        <div class="pcard empty">\n'
                '          <span class="pchip"><span class="dot"></span>in arrivo</span>\n'
                '          <p>I primi servizi dedicati ad A.L.&nbsp;Consultant. In preparazione.</p>\n'
                '        </div>\n')
    out = ""
    for href, name, tag, stato in items:
        st = "state" if stato == "in uso" else ""
        out += ('        <a class="pcard" href="' + href + '">\n'
                '          <div class="pcard-top"><span class="pchip ' + st + '"><span class="dot"></span>' + stato + '</span><span class="arrow">&rarr;</span></div>\n'
                "          <h3>" + name + "</h3>\n          <p>" + tag + "</p>\n        </a>\n")
    return out


def home_page():
    cards = ""
    for name, slug, desc, items, prot in CATS:
        count = (str(len(items)) + " progetti") if items else "in arrivo"
        if items and prot:
            # Categoria riservata: niente nomi in chiaro sulla home pubblica.
            pills = '<span class="pill">contenuto riservato</span>'
        elif items:
            pills = "".join('<span class="pill">' + n + "</span>" for _, n, _, _ in items)
        else:
            pills = '<span class="pill empty">in preparazione</span>'
        lock = '<span class="pchip lock"><span class="dot"></span>riservata</span>' if prot else ""
        cards += ('      <a class="homecard" href="' + slug + '/index.html">\n'
                  '        <div class="homecard-top"><span class="tags">' + lock + '<span class="pchip"><span class="dot"></span>' + count + '</span></span><span class="arrow">&rarr;</span></div>\n'
                  "        <h2>" + name + '</h2>\n        <p class="cdesc">' + desc + '</p>\n'
                  '        <div class="preview">' + pills + "</div>\n      </a>\n")
    s = [_head("Documentazione progetti - PROGETTI AI")]
    s.append('  <main class="hub">\n    <header class="hubhero">\n      <div class="eyebrow">Vademecum &middot; Documentazione interna</div>\n')
    s.append('      <h1>Documentazione progetti</h1>\n      <p class="lede">Ogni progetto in un dossier: cosa e, com&rsquo;e fatto, come funziona e come spiegarlo a chi arriva. Scegli l&rsquo;area.</p>\n    </header>\n')
    s.append('      <div class="homegrid">\n' + cards + "      </div>\n")
    tot = sum(len(c[3]) for c in CATS)
    s.append('    <div class="hubfoot"><span>PROGETTI AI &middot; documentazione onboarding</span><span class="mono">' + str(tot) + " progetti &middot; 2026-07-30</span></div>\n  </main>\n</body>\n</html>\n")
    return "".join(s)


def subpage(name, slug, desc, items):
    s = [_head("Documentazione - " + name, "../")]
    s.append('  <main class="hub">\n    <header class="hubhero">\n      <a class="backlink" href="../index.html">&larr; Documentazione progetti</a>\n      <div class="eyebrow">Vademecum &middot; ' + name + '</div>\n')
    s.append("      <h1>" + name + '</h1>\n      <p class="lede">' + desc + "</p>\n    </header>\n")
    s.append('      <div class="pgrid">\n' + _cat_cards(items) + "      </div>\n")
    s.append('    <div class="hubfoot"><span>PROGETTI AI &middot; ' + name + '</span><span class="mono">' + str(len(items)) + " progetti &middot; 2026-07-30</span></div>\n  </main>\n</body>\n</html>\n")
    return "".join(s)


(BASE / "index.html").write_text(fix(home_page()), encoding="utf-8")
print("scritto index.html (home) con", len(CATS), "categorie")
# L'elenco di ogni categoria e' l'index.html dentro la sua cartella sorgente
# (GITIGNORED). Verra' cifrato da cifra.sh nella cartella pubblica omonima.
for name, slug, desc, items, prot in CATS:
    dest = SRCDIR[slug]
    (dest / "index.html").write_text(fix(subpage(name, slug, desc, items)), encoding="utf-8")
    print("scritto", dest.name + "/index.html (da cifrare) -", len(items), "progetti")
