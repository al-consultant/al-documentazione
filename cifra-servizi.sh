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
    --template-color-primary "#b4331f" \
    --template-color-secondary "#f4efe6" >/dev/null
  echo "     cifrato: $(basename "$f")"
done

unset STATICRYPT_PASSWORD
echo
echo "Fatto. In root ci sono le versioni cifrate."
echo "Ora pubblica:  git add -A && git commit -m \"feat: cifra sezione servizi\" && git push"
