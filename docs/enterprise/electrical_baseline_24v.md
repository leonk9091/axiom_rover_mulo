# Baseline Elettrica 24 V - Mulo

## Decisione

La baseline approvata per MK0/X-1 e' **24 V nominali LiFePO4**. Ogni riferimento a 48 V in immagini, bozze o simulazioni e' da trattare come non conforme finche' non esiste una decisione tecnica firmata che migri batteria, VESC, DC-DC, carica, dump load, fusibili, cavi e parametri.

## Schema Potenza Minimo

```text
Battery 24 V LiFePO4
  -> main fuse near battery
  -> manual service disconnect
  -> protected DC bus
      -> branch fuse -> VESC traction
      -> branch fuse -> VESC winch
      -> branch fuse -> DC-DC logic 24->12/5 V
      -> branch fuse -> charger / charge port
      -> branch fuse -> range extender charge input
      -> branch fuse -> dump load controller/resistor
```

## Regole Cablaggio

| Area | Regola |
| :--- | :--- |
| Potenza batteria/VESC | Sezione dimensionata su corrente continua, non picco pubblicitario. |
| Motore fase | Preferire AWG10 o equivalente se test termici superano margine su AWG12. |
| CAN | Coppia twistata, terminazioni 120 ohm agli estremi, percorso lontano da fasi motore. |
| Segnali safety | E-stop NC, pull fisici fail-safe, connettori bloccabili. |
| Masse | Potenza e logica collegate con strategia definita; evitare loop e ground rumorosi sui sensori. |
| Box | Potenza e logica separati; pressacavi IP, scarico condensa, accesso fusibili. |

## Protezioni Minime

- Fusibile principale entro distanza minima pratica dalla batteria.
- Sezionatore manuale accessibile senza utensili speciali.
- Fusibili separati per trazione, verricello, carica, DC-DC, servizi e dump load.
- Dump load in carter termico con distanza da plastica/cavi.
- Misura tensione/corrente almeno lato bus o batteria.
- Ramo range extender con fusibile dedicato, buck CC/CV, diodo ideale o contattore anti-backfeed e interfaccia BMS charge inhibit.
- Condensatori DC link REX con margine coerente con fault a 70 V; baseline minima 100 V finche' non esiste calcolo di derating firmato.

## Gate

Non ordinare batteria, VESC, caricatori, DC-DC o connettori finche' questo file, la wire list e la BOM candidate shortlist non sono coerenti.
