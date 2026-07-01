# Evidence Pack

Questa cartella raccoglie l'evidenza di validazione. Ogni test deve avere una
sottocartella con ID `VV-...`, manifest, log, report, foto o screenshot, commit
e firma/review.

## Struttura Minima

```text
reports/evidence/
  VV-P0-REX-001/
    run_manifest.json
    test_report.md
    data/
    figures/
    photos/
```

## Regola

Un requisito non e' chiuso se manca almeno uno tra log, report, configurazione,
commit, dataset o firma tecnica.
