# al-documentazione

Documentazione onboarding dei progetti. Un dossier HTML per progetto, stesso
formato ovunque: cosa è, com'è fatto, come funziona, come spiegarlo a un
collaboratore nuovo e al cliente.

## Struttura

- `index.html` - home con due aree: **Progetti AI** e **Servizi AL Consultant**.
- `progetti-ai.html` - elenco dei dossier Progetti AI.
- `servizi-al-consultant.html` - elenco dei dossier Servizi AL Consultant.
- gli altri `.html` - i singoli dossier.
- `_genera.py` - generatore: rigenera tutte le pagine con `python3 _genera.py`.

Il look (CSS) vive in `architettura-strumenti.html` ed è la fonte unica dello
stile: `_genera.py` lo legge da lì.
