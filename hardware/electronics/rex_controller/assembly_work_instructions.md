# MULO-REX Controller Assembly Work Instructions

Data baseline: 2026-06-14

Queste istruzioni valgono per il banco REX con STM32 Nucleo, Honda GX50 e
controller separato. Non autorizzano test con motore acceso: servono come
sequenza di cablaggio e controllo prima della prima energizzazione.

## Prerequisiti

- `range_extender_enabled: false` in tutti i profili software.
- E-stop fisico verificato a bassa energia.
- Safety MCU STM32 alimentata e fail-closed.
- Nessun collegamento batteria/DC link ad alta energia durante i controlli logici.
- CO monitor, estintore e guardie meccaniche disponibili per le fasi successive.

## Sequenza Di Assemblaggio Logico

1. Montare STM32 REX su piastra carrier isolata.
2. Collegare `J_SAFE` e verificare che `SAFETY_KILL_N=LOW` forzi kill.
3. Collegare USB service e verificare boot firmware senza carichi esterni.
4. Collegare `J_IGN` solo a motore spento e verificare continuita' del circuito kill.
5. Collegare servo throttle con alimentazione 6 V separata e testare ritorno meccanico a idle.
6. Collegare RPM Hall e verificare impulsi simulati prima del montaggio su GX50.
7. Collegare Vdc sense tramite partitore/front-end, mai direttamente a MCU.
8. Collegare Icharge sense e calibrare zero/scala con corrente nota.
9. Collegare sonde temperatura e verificare range plausibili.
10. Collegare `J_DUMP` come richiesta logica verso controller dump-load esterno.

## Controlli Pass/Fail

| Controllo | Metodo | Pass |
| :--- | :--- | :--- |
| Continuita' GND logica | multimetro | resistenza coerente, nessun loop shield indesiderato |
| Isolamento ignition | multimetro + schema | nessun pin MCU diretto su primaria accensione |
| Stato reset MCU | power cycle | kill attivo, throttle idle, generation disabled |
| Perdita USB/seriale | scollegamento host | kill attivo entro timeout firmware |
| `SAFETY_KILL_N` basso | jumper/uscita safety | kill attivo e nessuna richiesta carica |
| Vdc alta simulata | alimentatore limitato/front-end | fault overvoltage + kill |
| RPM alta simulata | generatore impulsi | fault overspeed + kill |
| No charge con throttle | simulazione sensore | fault no-charge-current |

## Blocco Ordini

Non ordinare cablaggi finali finche' in `rex_controller_bom.csv` restano
rating `TBD` per fusibili, connettori, servo stall current o sezioni cavo.
