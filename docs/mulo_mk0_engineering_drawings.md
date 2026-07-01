# Disegni Ingegneristici Concettuali - Axiom Rover MK0

Queste tavole servono a visualizzare l'architettura MK0 proposta. Non sono disegni costruttivi quotati: le dimensioni non esplicitate nei documenti tecnici vanno confermate su CAD, distinta componenti e misure reali.

## 1. Layout dall'alto

![Layout dall'alto MK0](diagrams/mk0_top_layout.svg)

La vista top mostra la separazione funzionale tra telaio articolato, ponte corazzato, ruote da 20", elettronica centrale, VESC e sensori frontali. La quota certa evidenziata e' la baseline UWB da 0,60 m, usata dal firmware per stimare l'angolo dell'operatore.

## 2. Geometria UWB

![Geometria UWB MK0](diagrams/mk0_uwb_geometry.svg)

La trilaterazione a due anchor e' sufficiente per una prima versione follow-me lenta e conservativa. Il disegno evidenzia anche il punto debole: quando il tag e' lontano rispetto alla baseline, piccoli errori sulle distanze `d1` e `d2` diventano errore angolare.

## 3. Vista laterale ToF e ostacoli

![Vista laterale ToF MK0](diagrams/mk0_side_tof_obstacle.svg)

La logica basso/alto dei ToF va trattata come filtro pratico, non come garanzia assoluta. Gli ostacoli bassi intorno a 15 cm devono essere validati con test fisici progressivi prima di autorizzare boost di coppia o attraversamento automatico.

## 4. Controllo e cablaggio logico

![Architettura controllo MK0](diagrams/mk0_control_wiring.svg)

Lo schema separa sensori, safety MCU STM32 Nucleo, VESC/CAN, potenza, safety fisica e logging. Il principio chiave e' che `STOP` ed `ESTOP` restano prioritari rispetto al follow-me e che la perdita di misura o comando porta sempre a comando motori nullo. Le tavole storiche con etichetta ESP32-S3 restano da considerare prototipo/legacy, non baseline safety finale.

## 5. Nuovi Blueprint Meccanici di Dettaglio

Di seguito vengono riportati i nuovi blueprint e prospetti di dettaglio ingegneristico che completano le tavole concettuali superiori, integrando le specifiche costruttive del Mulo MK0:

### A. Snodo di Torsione Centrale Articolato (Quick-Split Joint)
![Blueprint Snodo Centrale](../hardware/cad/blueprint_chassis_articulation.png)
*Rappresentazione tecnica dello snodo di torsione con i supporti ritti UCP204, l'albero passante e le spine di sicurezza per lo sfilamento rapido dei semitelai.*

### B. Gruppo Verricello Anteriore (Winch Assembly)
![Blueprint Verricello Anteriore](../hardware/cad/blueprint_winch_assembly.png)
*Vista blueprint dell'installazione del verricello sul muso dell'Axiom Rover, con allineamento ottimizzato del cavo di trazione parallelo all'asse longitudinale.*

### C. Spaccato Esploso della Trasmissione Coassiale (Exploded Drivetrain)
![Blueprint Esploso Trasmissione](../hardware/cad/blueprint_drivetrain_exploded.png)
*Dettaglio assonometrico esploso in stile manuale d'officina dell'asse della ruota da 20", cuscinetto flangiato UCF204, freno a disco da 203 mm e mozzo custom.*

### D. Layout vano di potenza e ricarica (Power Box CAD)
![CAD Vano Ricarica](../hardware/cad/cad_power_box_assembly.png)
*Modello CAD tridimensionale del vano posteriore stagno IP68 contenente il caricabatterie Mean Well NPB-750-24, il Victron MPPT e le porte di ricarica stagne.*

---

## 6. Curve e Grafici Prestazionali di Funzionamento

Per guidare lo sviluppo degli algoritmi di controllo del firmware e validare il dimensionamento elettromeccanico di bordo, sono stati integrati i seguenti grafici prestazionali di riferimento:

### A. Caratteristica di Coppia-Velocità del Motore (VESC Brushless)
![Grafico Coppia Velocità](diagrams/plot_motor_torque_speed.png)
*Curva di coppia (Nm) ed efficienza energetica (%) del motore brushless da 24V gestito in corrente da VESC in funzione del regime di giri (RPM).*

### B. Curva di Scarica della Batteria LiFePO4 (Voltage vs State of Charge)
![Grafico Scarica Batteria](diagrams/plot_battery_discharge_soc.png)
*Andamento della tensione di cella (V) in funzione dello stato di carica (SoC %) per diverse correnti di esercizio (0.2C nominale, 0.5C di lavoro, 1C picco).*

### C. Errore Angolare di Trilaterazione UWB vs Distanza
![Grafico Errore UWB](diagrams/plot_uwb_trilateration_error.png)
*Analisi teorico-sperimentale dell'errore di stima dell'angolo (gradi) del tag rispetto al rover in funzione della distanza per una baseline tra le ancore di 0.60 m.*

### D. Tensione Cavo Verricello vs Pendenza del Sentiero
![Grafico Forza Verricello](diagrams/plot_winch_tension_slope.png)
*Tensione di tiro richiesta (N) al variare dell'inclinazione del terreno (0-45°) per diversi carichi utili di trasporto (50 kg, 75 kg, 100 kg).*

---

## 7. Checklist di Aggiornamento Disegni CAD (Modifiche Strutturali)

Per implementare le soluzioni di trasporto e il Range Extender senza compromettere l'integrità strutturale del rover, i disegni costruttivi tridimensionali (CAD) dovranno essere aggiornati integrando i seguenti dettagli meccanici ed elettrici:

1.  **Assieme Snodo Centrale (Quick-Split Joint):**
    *   *Disegno Albero di Torsione:* Modificare l'albero cilindrico da 20 mm `h6` inserendo un foro trasversale passante da 6 mm alle estremità per l'alloggiamento del perno a sgancio rapido con coppiglia elastica a scatto (safety pull-pin).
    *   *Quote Sedi Cuscinetti UCP204:* Prevedere una tolleranza geometrica di allineamento coassiale inferiore a **0.05 mm** tra i due supporti ritti sul semitelaio per scongiurare grippaggi durante le operazioni di sfilamento manuale.
2.  **Punti di Ancoraggio e Traino (Winch Anchors):**
    *   *Golfari Strutturali Anteriori e Posteriori:* Inserire a disegno 4x golfari femmina M10 in acciaio ad alta resistenza (classe 8.8) avvitati direttamente su boccole filettate saldate sui nodi principali del telaio tubolare 30x30.
    *   *Posizione Piastra Verricello:* Modificare il posizionamento del verricello (`rover_winch`) sul semitelaio anteriore in modo che la linea di tiro del cavo sintetico sia perfettamente parallela all'asse longitudinale del rover, massimizzando l'efficienza di trazione durante l'auto-caricamento sulle rampe.
3.  **Layout Passacavi e Connettori IP68 (Snodo Centrale):**
    *   *Staffe Supporto Connettori:* Disegnare una staffa metallica a "L" sul semitelaio posteriore e anteriore, adiacente allo snodo centrale, per il montaggio flangiato di connettori rapidi IP68 stagni a baionetta (es. Amphenol serie Eco|mate o Anderson Powerpole stagni) che collegano la logica tra i due moduli.
    *   *Canaline Passacavo:* Integrare a disegno canaline protettive in PVC flessibile corrugato o treccia metallica per proteggere il cablaggio da sforzi di trazione, torsione e contatti accidentali con rocce o vegetazione.
4.  **Vano Alloggiamento Caricatori (Power Box Posteriore):**
    *   *Scatola Stagna Porta-Caricatori:* Disegnare una scatola stagna in alluminio spessore 2.5 mm, con guarnizione in neoprene sul coperchio imbullonato (IP65/IP66), da posizionarsi sotto il pianale di carico posteriore.
    *   *Quote e Tolleranze Fissaggi:* Integrare i fori per **4x silent-block M5** per l'NPB-750-24 e **4x fori M4** per il Victron MPPT. Assicurare una distanza minima di isolamento termico di 15 mm dalle pareti laterali della scatola per favorire i moti convettivi d'aria interna.
    *   *Dettaglio Dissipazione di Bordo:* Prevedere a disegno l'accoppiamento tra il fondo piatto del Mean Well NPB-750 e la scatola tramite pad termoconduttivo flessibile da 2.0 mm (conduzione calore verso lo chassis tubolare esterno).
5.  **Pannello di Ricarica Esterno (Charging Port Panel):**
    *   *Piastra di Flangiatura Connettori:* Disegnare una piastra custom in alluminio anticorodal anodizzato spessore 3 mm per alloggiare la presa **powerCON TRUE1 TOP (Neutrik)** e la flangia magnetica **Rosenberger RoPD**.
    *   *Archetto di Protezione Meccanica:* Integrare a disegno un archetto protettivo a gabbia in tubolare tondo d'acciaio diametro 16 mm, saldato direttamente al telaio principale e sporgente di 35 mm rispetto al pannello, per proteggere i connettori da urti contro alberi, spigoli di roccia o cadute accidentali del rover sul fianco sinistro.
    *   *Canalizzazione AWG 10 silicone:* Inserire a modello il percorso protetto per i cavi AWG 10 in silicone dal pannello di ricarica fino ai fusibili da 30A e alla scatola di potenza principale della batteria.
