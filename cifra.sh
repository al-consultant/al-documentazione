#!/usr/bin/env bash
# Rigenera tutte le pagine e cifra ENTRAMBE le aree riservate:
#   Progetti AI  e  Servizi AL Consultant.
#
# Perche' una password sola per tutto:
#   staticrypt cifra ogni file singolarmente, ma usa un SALT (una specie di
#   "impronta" pubblica, non e' segreta). Se tutte le pagine hanno lo STESSO
#   salt e tu spunti "Ricordami", il browser sblocca da solo tutte le altre
#   pagine dello stesso sito senza richiederti di nuovo la password. Per questo
#   qui fissiamo un SALT unico: cosi' digiti la password una volta, spunti
#   "Ricordami", e giri libero in Progetti AI e Servizi senza reinserirla ad
#   ogni progetto. Se NON spunti "Ricordami", te la richiede pagina per pagina.
#
# Cosa fa, passo per passo:
#   1) lancia _genera.py: le pagine in chiaro finiscono nelle cartelle sorgente
#      _sorgenti-progetti/ e _sorgenti-servizi/ (GITIGNORED, mai sul repo);
#   2) chiede la password QUI una sola volta (non viene stampata ne' salvata);
#   3) staticrypt cifra ogni pagina e scrive in progetti-ai/ e
#      servizi-al-consultant/ SOLO la versione cifrata, tutte con lo stesso salt.
#
# Dopo, commit e push mettono online solo i file cifrati. La home resta pubblica.
#
# Uso:  ./cifra.sh     (poi digiti la password quando te la chiede)

set -euo pipefail
cd "$(dirname "$0")"

# Salt condiviso da TUTTE le pagine: non e' un segreto (staticrypt lo scrive
# comunque dentro ogni file). Deve solo restare COSTANTE: e' cio' che fa
# funzionare "Ricordami" tra una pagina e l'altra. Non cambiarlo alla leggera:
# se lo cambi, chi aveva gia' sbloccato dovra' reinserire la password.
SALT="2949551c3ad0be36e626aa29b7d78fc9"

echo "1/3  Rigenero le pagine..."
python3 _genera.py >/dev/null
echo "     ok."

echo "2/3  Password per le aree riservate (non verra' mostrata):"
read -rs -p "     Password: " STATICRYPT_PASSWORD; echo
if [ -z "$STATICRYPT_PASSWORD" ]; then
  echo "Password vuota: annullo, non cifro niente." >&2
  exit 1
fi
export STATICRYPT_PASSWORD

# Cifra tutti gli *.html di una cartella sorgente nella cartella pubblica.
# $1 = cartella sorgente   $2 = cartella pubblica di output   $3 = titolo pop-up
cifra_area() {
  local src="$1" out="$2" titolo="$3"
  shopt -s nullglob
  local files=("$src"/*.html)
  if [ ${#files[@]} -eq 0 ]; then
    echo "     (nessuna pagina in $src, salto)"
    return 0
  fi
  mkdir -p "$out"
  echo "     cifro ${#files[@]} pagina/e da $src in $out/ ..."
  for f in "${files[@]}"; do
    npx --yes staticrypt "$f" -d "$out" -c false --short --salt "$SALT" \
      --template-title "$titolo" \
      --template-instructions "Inserisci la password per accedere." \
      --template-button "Entra" \
      --template-placeholder "Password" \
      --template-error "Password errata" \
      --template-color-primary "#111111" \
      --template-color-secondary "#ffffff" >/dev/null
    echo "       cifrato: $(basename "$f")"
  done
}

echo "3/3  Cifro le due aree (stesso salt = una password per tutto)..."
cifra_area "_sorgenti-progetti" "progetti-ai"            "Progetti AI - Area riservata"
cifra_area "_sorgenti-servizi"  "servizi-al-consultant"  "Servizi AL Consultant - Area riservata"

# StatiCrypt non ha flag per font/maiuscolo: li re-iniettiamo qui, cosi' ogni
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
/* Niente spunta "ricordami": lo sblocco lo gestiamo noi per sessione. */
#staticrypt-remember-label,.staticrypt-remember{display:none !important;}
</style>
"""
# titolo del pop-up: tolgo il "-" e vado a capo (solo nel <p>, non nel <title>)
TITOLI = {
    "Progetti AI - Area riservata": "Progetti AI<br>Area riservata",
    "Servizi AL Consultant - Area riservata": "Servizi AL Consultant<br>Area riservata",
}
for path in glob.glob("progetti-ai/*.html") + glob.glob("servizi-al-consultant/*.html"):
    html = open(path, encoding="utf-8").read()
    if MARK not in html:
        html = html.replace("</head>", STYLE + "</head>", 1)
    for src, dst in TITOLI.items():
        html = html.replace('staticrypt-title">' + src, 'staticrypt-title">' + dst)
    # Sblocco PER SESSIONE (non "ricordami" permanente):
    #  1) memorizza sempre lo sblocco (come se "ricordami" fosse spuntato),
    #     cosi' entri una volta e giri libero tra i progetti senza reinserirla;
    #  2) usa sessionStorage al posto di localStorage: alla chiusura del browser
    #     lo sblocco si azzera e alla riapertura ti richiede di nuovo la password.
    html = html.replace(
        'isRememberChecked = document.getElementById("staticrypt-remember").checked;',
        'isRememberChecked = true;',
    )
    html = html.replace("localStorage", "sessionStorage")
    open(path, "w", encoding="utf-8").write(html)
    print("     rifinito:", path)
PY

unset STATICRYPT_PASSWORD
echo
echo "Fatto. In progetti-ai/ e servizi-al-consultant/ ci sono le versioni cifrate."
echo "Ora pubblica:  git add -A && git commit -m \"feat: cifra Progetti AI + Servizi con password unica\" && git push"
