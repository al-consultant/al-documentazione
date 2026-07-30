# al-documentazione

Documentazione onboarding dei progetti. Un dossier HTML per progetto, stesso
formato ovunque: cosa è, com'è fatto, come funziona, come spiegarlo a un
collaboratore nuovo e al cliente.

## Struttura

```
index.html                 home con le due aree
assets/styles.css          il look, un file solo (tutte le pagine lo linkano)
progetti-ai/               <- documenti Progetti AI
  index.html               elenco dei dossier
  *.html                   i singoli dossier
servizi-al-consultant/     <- documenti Servizi AL Consultant (cifrati)
  index.html               elenco (protetto da password)
_genera.py                 generatore
cifra-servizi.sh           cifra la sezione servizi (staticrypt)
```

## Come si aggiorna

1. Modifica i dati in `_genera.py` (o lo stile in `assets/styles.css`).
2. `python3 _genera.py` rigenera home, elenchi e dossier.
3. Per la sezione servizi: `./cifra-servizi.sh` (chiede la password e cifra).
4. `git add -A && git commit -m "..." && git push`.

## Sezione servizi (password)

Le pagine servizi in chiaro stanno in `_sorgenti-servizi/`, che è **gitignored**:
non finiscono mai sul repo. `cifra-servizi.sh` le cifra con
[staticrypt](https://github.com/robinmoisson/staticrypt) e scrive in
`servizi-al-consultant/` solo la versione cifrata. Chi apre la pagina deve
inserire la password per vederne il contenuto. La sicurezza vale quanto la
password: sceglierla lunga e non banale.
