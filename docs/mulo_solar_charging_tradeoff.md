# Studio di Convenienza: Ricarica Solare per Axiom Rover "Mulo"
## Analisi di Trade-Off ed Ingegnerizzazione del Sistema

Questo documento analizza la fattibilità tecnica, l'efficienza energetica e la convenienza pratica di integrare la ricarica tramite pannelli fotovoltaici sul Mulo MK0, confrontando l'installazione di **pannelli solari fissi a bordo** rispetto all'uso di **pannelli pieghevoli portatili**.

---

## 1. Modello Energetico del Trekking (Fabbisogno Giornaliero)

Per valutare la convenienza del solare, dobbiamo prima quantificare quanta energia consuma il rover in una tipica giornata di trekking montano:

*   **Capacità Batteria Mulo MK0:** `E_batt = 25.6 V * 100 Ah = 2560 Wh`
*   **Velocità di Crociera:** `v = 4.0 km/h`
*   **Tempo di Cammino Giornaliero Medio:** `t = 4 h` (pari a circa 16 km di percorso montano)
*   **Consumo Medio Trazione (Terreno sterrato/pendenza media 10-15%):** `P_trazione ≈ 150 W`
*   **Consumo Elettronica e Logica (ESP32, sensori, telemetria, LoRa):** `P_logica ≈ 25 W`
*   **Consumo Totale in Marcia:** `P_tot = P_trazione + P_logica = 175 W`
*   **Energia Consumata per la Trazione (Giornaliera):** `E_marcia = 175 W * 4 h = 700 Wh`
*   **Consumo Sentinella Notturna (10 Ore):** `E_sentinella ≈ 30 Wh`
*   **Fabbisogno Energetico Giornaliero Totale:** `E_richiesta ≈ 730 Wh` (pari al **28.5%** della batteria da 2.56 kWh)

---

## 2. Opzione A: Pannelli Solari Fissi Integrati a Bordo

Questa opzione prevede l'installazione di pannelli solari flessibili in silicio monocristallino incollati direttamente sul tettuccio protettivo del rover o integrati nella piastra superiore del vano di carico.

```
       +---------------------------------------------+
       |   PANNELLO FOTOVOLTAICO FISSO SUL ROVER     | -> Alzamento baricentro
       +---------------------------------------------+
                             |
                      [Esposizione] -> Orizzontale (non ottimale per ore di marcia)
                             |
                     [Ombre montane] -> Frequenti interruzioni (alberi, rocce)
                             |
                      [Rischio Urti] -> Elevato (rami, pietre, fango, ribaltamenti)
```

### Calcolo del Rendimento Reale A Bordo:
*   **Superficie Utile Massima Disponibile:** `S_pannello = 0.4 m²` (es. 80 cm x 50 cm)
*   **Potenza di Picco Teorica (STC 1000 W/m², efficienza celle 21%):**
    `P_picco = 1000 W/m² * 0.4 m² * 0.21 = 84 Wp`
*   **Perdite Reali Durante il Movimento su Sentiero:**
    *   *Effetto Coseno (Pannello parallelo al terreno, sole non perpendicolare):* `-30%` (efficienza di esposizione `0.70`)
    *   *Ombreggiamento Parziale (Passaggio sotto alberi, pareti rocciose, inclinazione del sentiero):* `-40%` (efficienza `0.60`)
    *   *Sporcizia, Polvere e Fango (Accumulati sulle ruote e depositati sul pannello):* `-10%` (efficienza `0.90`)
    *   *Perdite MPPT e Cablaggi:* `-5%` (efficienza `0.95`)
*   **Potenza Media Effettiva Generata durante la marcia:**
    `P_effettiva = 84 Wp * 0.70 * 0.60 * 0.90 * 0.95 ≈ 30.1 W`
*   **Energia Giornaliera Raccolta (Ipotizzando 6 ore di soleggiamento utile in estate):**
    `E_raccolta_fissa = 30.1 W * 6 h = 180.6 Wh`

### Valutazione Qualitativa Opzione A:
1. **Copertura del Fabbisogno Giornaliero:** `(180.6 Wh / 730 Wh) * 100 ≈ 24.7%` (il rover guadagna circa 1 ora di autonomia di marcia in più al giorno).
2. **Ricarica della Batteria Totale:** `(180.6 Wh / 2560 Wh) * 100 ≈ 7.05%` (richiederebbe ben **14 giorni di sole ininterrotto** per ricaricare da 0 a 100% il rover).
3. **Svantaggi Meccanici:** I pannelli solari montati in alto alzano il Centro di Massa (CoM), riducendo l'angolo di ribaltamento laterale. Inoltre, sono **estremamente esposti a graffi, urti con rami bassi, pietrisco sollevato, fango e acqua**, con un altissimo rischio di delaminazione o rottura parziale delle celle (che azzererebbe la produzione a causa del collegamento in serie).

---

## 3. Opzione B: Pannello Solare Portatile Pieghevole (Consigliato)

Questa opzione prevede l'uso di una "Solar Blanket" (es. **EcoFlow, Jackery o Dokio da 200W**) da tenere ripiegata al sicuro nel vano di carico del rover durante la marcia e da dispiegare esclusivamente durante le soste prolungate (pausa pranzo, campo base pomeridiano/serale).

```
   [Rover in Marcia]                   [Rover in Sosta (Pranzo / Campo)]
+-----------------------+              +-----------------------+
|  Pannello Piegato     |              |  Pannello Dispiegato  | -> Inclinazione ottimale (35°-45°)
|  Nel vano di carico   |              |  Orientato al Sole    | -> Zero ombreggiamento indotto
|  (Protetto al 100%)   |              |  Massima Efficienza   | -> Nessun rischio di urti in marcia
+-----------------------+              +-----------------------+
```

### Calcolo del Rendimento Reale in Sosta:
*   **Potenza Nominale del Pannello Pieghevole:** `P_picco = 200 Wp`
*   **Peso e Ingombro:** `~6.5 kg`, dimensioni piegato `50 x 50 x 5 cm` (facilmente alloggiabile nel pianale).
*   **Efficienza in Sosta (Posizionamento ottimale ad angolo corretto):**
    *   *Effetto Coseno (Inclinazione manuale ottimale verso il sole tramite cavalletti integrati):* `-5%` (efficienza `0.95`)
    *   *Ombreggiamento (Il campeggiatore sceglie attivamente una radura aperta priva di alberi):* `-10%` (velature o nubi passeggere, efficienza `0.90`)
    *   *Pulizia Superficie (Dispiegato pulito all'occorrenza):* `-0%`
    *   *Perdite MPPT e Cablaggi (Cavo da 5m AWG 12):* `-5%` (efficienza `0.95`)
*   **Potenza Media Effettiva Generata in sosta soleggiata:**
    `P_effettiva_pieghevole = 200 Wp * 0.95 * 0.90 * 0.95 ≈ 162.4 W`

### Scenari di Ricarica in Sosta:
*   **Scenario Sosta Pranzo (2 Ore di sole):**
    `E_pranzo = 162.4 W * 2 h = 324.8 Wh`
    *   Copre il **44.5%** del consumo giornaliero di marcia.
    *   Reintegra il **12.7%** della batteria complessiva.
*   **Scenario Campo Base Estivo (5 Ore di sole pomeridiano):**
    `E_campo = 162.4 W * 5 h = 812 Wh`
    *   Copre il **111.2%** del consumo giornaliero del rover (trazione + sentinella).
    *   Reintegra il **31.7%** della batteria complessiva.
    *   Consente l'**autonomia perpetua (Zero-Emission Off-Grid)**: il rover può viaggiare per 16 km ogni singolo giorno all'infinito senza mai toccare una presa di corrente o consumare benzina.

---

## 4. Analisi Comparativa di Convenienza (Trade-Off Matrix)

| Criterio | Pannello Fisso A Bordo (80W) | Pannello Pieghevole Portatile (200W) | Vincitore |
| :--- | :---: | :---: | :---: |
| **Produzione Energetica Reale** | Bassa (~180 Wh/giorno) | **Alta (~810 Wh/giorno)** | **Pieghevole** |
| **Autosufficienza (Off-Grid)** | No (Troppo lento a ricaricare) | **Sì (Autonomia perpetua estiva)** | **Pieghevole** |
| **Robustezza e Durata** | Molto Bassa (Esposto a rami/urti) | **Altissima (Chiuso e protetto in marcia)**| **Pieghevole** |
| **Impatto Meccanico/Stabilità** | Peggiora il CoM (peso in alto) | **Neutro (stivato in basso nel pianale)** | **Pieghevole** |
| **Costo Specifico (€/W)** | Alto (Pannelli custom flessibili) | **Basso (Standard di mercato)** | **Pieghevole** |
| **Sforzo Operatore** | Zero (Lavora da solo in marcia) | Richiede posizionamento manuale | **Fisso** |

---

## 5. Ingegnerizzazione dell'Integrazione Elettronica (Costo Zero)

Uno dei vantaggi straordinari dell'architettura elettrica già progettata per il Mulo MK0 è che **non occorre aggiungere alcun caricabatterie o regolatore solare dedicato**.

L'elettronica a bordo è già predisposta per supportare il solare grazie all'uso intelligente del regolatore **Victron SmartSolar MPPT 75/15 o 100/20** originariamente previsto per la ricarica dalle colonnine e-bike DC:

```
+------------------------------------+
| PANNELLO SOLARE PIEGHEVOLE (200W)   |
| (Tensione V_oc = 24V - 48V)        |
+------------------------------------+
                 |
                 v (Cavo 5 metri con connettori MC4)
+------------------------------------+
| CONNETTORE AUSILIARIO SOLAR (MC4)  | -> Sul pannello prese esterne del Mulo
+------------------------------------+
                 |
                 v (Fusibile 15A)
+------------------------------------+
| VICTRON SMARTSOLAR MPPT (75/15)    | -> Già a bordo per ricarica DC e-bike!
+------------------------------------+
                 |
                 v (29.2V Carica CC/CV)
+------------------------------------+
| BATTERIA LiFePO4 (24V 100Ah)       |
+------------------------------------+
```

### Caratteristiche dell'integrazione:
1. **Ingresso Condiviso/Commutato:** Il connettore di ricarica solare MC4 esterno è collegato in parallelo all'ingresso del regolatore MPPT Victron SmartSolar di bordo. Poiché non si caricherà mai contemporaneamente da una colonnina e-bike e da un pannello solare, l'ingresso viene condiviso in sicurezza (o commutato tramite un deviatore stagno).
2. **Algoritmo Victron Ultra-Fast MPPT:** In caso di passaggi di nuvole o ombreggiamenti parziali della foresta durante la sosta, il regolatore Victron adatta il punto di lavoro in meno di 1 secondo, massimizzando il recupero energetico del **10%** in più rispetto ad algoritmi MPPT tradizionali.
3. **Telemetria Bluetooth Integrata:** I campeggiatori possono monitorare l'efficienza della ricarica, la potenza istantanea prodotta (W) e lo storico solare giornaliero direttamente dall'app Victron Connect sul proprio smartphone o sul display del pager notturno via LoRa.

---

## 6. Verdetto Ingegneristico: Conviene il Solare?

### **Sì, ma solo con l'Opzione B (Pannello Pieghevole Portatile).**

*   **Il pannello fisso a bordo è sconsigliato:** Produce pochissima energia a causa dell'esposizione orizzontale errata e delle ombre dei sentieri, appesantisce il baricentro ed è destinato a distruggersi rapidamente contro rami e rocce durante la marcia off-road.
*   **Il pannello pieghevole portatile da 200W è eccezionale:** È protetto durante la marcia, produce oltre **4 volte** l'energia di un pannello fisso a parità di tempo grazie all'orientamento ottimale ed è in grado di garantire l'**indipendenza energetica totale e pulita (autonomia perpetua)** durante le spedizioni estive in montagna. Sfruttando l'elettronica MPPT Victron già a bordo, l'integrazione richiede solo l'aggiunta di una presa stagna MC4 esterna e ha un costo hardware aggiuntivo irrisorio.
