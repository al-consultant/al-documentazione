#!/usr/bin/env bash
# Rigenera tutte le pagine e cifra la sezione "Servizi AL Consultant".
#
# Cosa fa, passo per passo:
#  1) lancia _genera.py: le pagine protette finiscono in _sorgenti-servizi/ (in chiaro, mai sul repo);
#  2) chiede la password QUI (non viene stampata, non viene salvata da nessuna parte);
#  3) staticrypt cifra ogni pagina protetta e scrive in root SOLO la versione cifrata.
#
# Dopo, commit e push mettono online solo il file cifrato. Chi apre la pagina
# deve inserire la password per vederne il contenuto.
#
# Uso:  ./cifra-servizi.sh     (poi digiti la password quando te la chiede)

set -euo pipefail
cd "$(dirname "$0")"

echo "1/3  Rigenero le pagine..."
python3 _genera.py >/dev/null
echo "     ok."

shopt -s nullglob
files=(_sorgenti-servizi/*.html)
if [ ${#files[@]} -eq 0 ]; then
  echo "Nessuna pagina servizi da cifrare. Niente da fare."
  exit 0
fi

echo "2/3  Password per la sezione Servizi (non verra mostrata):"
read -rs -p "     Password: " STATICRYPT_PASSWORD; echo
if [ -z "$STATICRYPT_PASSWORD" ]; then
  echo "Password vuota: annullo, non cifro niente." >&2
  exit 1
fi
export STATICRYPT_PASSWORD

echo "3/3  Cifro ${#files[@]} pagina/e in servizi-al-consultant/..."
mkdir -p servizi-al-consultant
for f in "${files[@]}"; do
  npx --yes staticrypt "$f" -d servizi-al-consultant -c false --short \
    --template-title "Servizi AL Consultant - Area riservata" \
    --template-instructions "Inserisci la password per accedere ai servizi." \
    --template-button "Entra" \
    --template-placeholder "Password" \
    --template-error "Password errata" \
    --template-color-primary "#111111" \
    --template-color-secondary "#ffffff" >/dev/null
  echo "     cifrato: $(basename "$f")"
done

# StatiCrypt non ha flag per font/maiuscolo: li re-iniettiamo qui, cosi ogni
# ri-cifratura mantiene il look (Montserrat, titolo maiuscolo su due righe,
# bottone nero). Sono override in fondo al <head>, indipendenti dallo spazio.
echo "     rifinisco il look del pop-up (Montserrat, maiuscolo, bottone nero)..."
python3 - <<'PY'
import glob, re
MARK = "<!-- al-look -->"
STYLE = MARK + """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
.staticrypt-content,.staticrypt-form,.staticrypt-form input,.staticrypt-form .staticrypt-decrypt-button,.staticrypt-title{font-family:"Montserrat",sans-serif !important;}
.staticrypt-content{background:#ffffff !important;}
.staticrypt-title{font-weight:800;text-transform:uppercase;letter-spacing:.01em;line-height:1.1;}
.staticrypt-form .staticrypt-decrypt-button,.staticrypt-form .staticrypt-decrypt-button:hover,.staticrypt-form .staticrypt-decrypt-button:active,.staticrypt-form .staticrypt-decrypt-button:focus{background:#111111 !important;}
</style>
"""
for path in glob.glob("servizi-al-consultant/*.html"):
    html = open(path, encoding="utf-8").read()
    if MARK not in html:
        html = html.replace("</head>", STYLE + "</head>", 1)
    # titolo del pop-up: tolgo il "-" e vado a capo (solo nel <p>, non nel <title>)
    html = html.replace(
        'staticrypt-title">Servizi AL Consultant - Area riservata',
        'staticrypt-title">Servizi AL Consultant<br>Area riservata',
    )
    open(path, "w", encoding="utf-8").write(html)
    print("     rifinito:", path)
PY

unset STATICRYPT_PASSWORD
echo
echo "Fatto. In root ci sono le versioni cifrate."
echo "Ora pubblica:  git add -A && git commit -m \"feat: cifra sezione servizi\" && git push"
