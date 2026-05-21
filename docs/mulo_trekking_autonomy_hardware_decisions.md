# Decisioni Hardware per Autonomia Trekking - Mulo X-1

Questo documento formalizza le decisioni progettuali emerse per rendere `Mulo` una piattaforma da trekking semi-autonoma, economica ma robusta, capace di seguire l'operatore, evitare ostacoli, riconoscere persone, stimare rischi di caduta/pendenza e attivare routine SOS quando resta bloccata.

La decisione centrale e': **non affidare la sicurezza a una singola AI visiva**. Il rover deve usare una architettura a livelli, dove i sensori geometrici e il microcontrollore fermano il veicolo anche se Linux, ROS 2 o la rete neurale falliscono.

---

## 1. Requisiti Operativi

Il sistema deve supportare:

- inseguimento dell'operatore senza controllo visivo continuo;
- avanzamento assistito su traccia o comando operatore;
- evitamento ostacoli statici e dinamici;
- riconoscimento persone e comportamento prudente quando attraversano il percorso;
- stima di traversabilita' di ostacoli, terreno e pendenze;
- rilevamento di vuoti, gradini, bordi sentiero e rischio ribaltamento;
- gestione energetica e comunicazione dello stato batteria residua;
- rilevamento blocco meccanico tramite encoder/corrente motori;
- routine SOS: buzzer/speaker, beacon radio/4G/LoRa, telemetria e log.

Il requisito pratico piu' importante e': **non fermarsi ogni pochi secondi per incertezza sensoriale**. La policy deve distinguere tra pericolo reale, incertezza temporanea e ostacolo aggirabile.

---

## 2. Decisione Architetturale

### Scelta approvata

```text
Jetson Orin Nano Super / futuro Orin NX
    ROS 2, AI visiva, Nav2, sensor fusion, mission logic

STM32
    controllo real-time, safety, watchdog, stop indipendente

LiDAR 2D DToF + camera RGB + ToF multizona
    geometria locale, pseudo-3D economico, edge detection

Encoder + corrente motori + IMU
    propriocezione, stallo, pendenza, ribaltamento
```

### Motivazione

- **Jetson** e' scelta come cervello cognitivo perche' offre CUDA/TensorRT/Isaac ROS e permette di sperimentare modelli di visione con meno vincoli rispetto a un acceleratore AI dedicato.
- **STM32** resta obbligatorio come sistema nervoso autonomo: deve fermare il rover anche se Jetson si blocca.
- **Camera depth costosa non e' obbligatoria nella prima base hardware**. Si puo' ottenere una stima spaziale utile fondendo camera RGB economica e LiDAR 2D.
- **LiDAR/ToF/IMU sono safety-first**: servono a non sbattere, non cadere e non ribaltarsi. La camera RGB serve a capire meglio il contesto, non a garantire da sola la sicurezza.

---

## 3. Alternative Valutate

| Alternativa | Esito | Motivo |
| :--- | :--- | :--- |
| ESP32-S3 come cervello unico | Scartata per X-1 | Troppo limitato per ROS 2, visione, AI e navigazione complessa. |
| Telefono usato come cervello | Solo supporto/telemetria | Buono per camera, 4G e UI, ma non affidabile per real-time e I/O fisici. |
| Mini PC Ryzen/Intel + STM32 | Valido per ROS 2 classico | Ottimo rapporto prezzo/prestazioni, ma senza GPU/acceleratore non e' ideale per AI visiva real-time. |
| Mini PC + Hailo-8 | Valido ma piu' vincolato | Efficiente su modelli supportati, meno flessibile di Jetson per sviluppo robotics/AI. |
| Jetson Orin Nano Super + STM32 | Scelta di partenza | Miglior equilibrio tra costo, AI, ROS 2, consumi e scalabilita'. |
| Jetson Orin NX 16GB + STM32 | Upgrade consigliato | Maggior margine per piu' modelli, segmentazione terreno e autonomia piu' fluida. |
| RTX + mini PC | Non consigliata per trekking | Potenza bruta alta, ma consumi, volume, calore e alimentazione sono poco adatti al rover. |

---

## 4. Topologia di Controllo

### Livello 0 - Potenza e Attuazione

Responsabilita':

- alimentazione batteria/BMS;
- fusibili, sezionatore, TVS, DC-DC separati;
- VESC/ODrive/controller motori;
- freni meccanici e dump load se presente;
- encoder ruota/motore;
- misura corrente motori.

Nota: CAN bus e' preferito per i controller motori. Dove possibile usare transceiver protetti o isolati, cavo twistato, terminazioni corrette e connettori bloccabili.

### Livello 1 - Safety Real-Time

Responsabilita' STM32:

- leggere ToF anti-caduta e ToF frontali bassi;
- leggere IMU e calcolare roll/pitch/yaw-rate;
- leggere encoder e corrente motori;
- monitorare E-stop fisico;
- monitorare heartbeat Jetson;
- attuare stop indipendente;
- generare stato safety verso ROS 2.

Lo STM32 **non deve dipendere da coordinate globali**. Deve ragionare su stato locale e pericolo immediato:

```text
wheel_speed_l/r
motor_current_l/r
roll, pitch, yaw_rate
tof_danger_mask
battery_voltage/current
estop_state
jetson_heartbeat_age
```

Policy minima:

- vuoto/gradino rilevato -> stop immediato;
- roll/pitch oltre soglia -> stop o derating;
- corrente alta + encoder fermi -> stallo;
- heartbeat Jetson assente per circa 500 ms -> stop controllato;
- E-stop fisico -> taglio comando motori indipendente.

### Livello 2 - Cognizione e Navigazione

Responsabilita' Jetson:

- ROS 2;
- Nav2 e costmap;
- acquisizione LiDAR 2D;
- acquisizione camera RGB;
- YOLO/TensorRT per persone, animali, ostacoli e segnali rilevanti;
- fusione camera-LiDAR;
- stima posizione locale/globale con `robot_localization`;
- mission logic: follow-me, avanza su traccia, aggiramento ostacoli;
- logging diagnostico;
- invio comandi velocita'/sterzo allo STM32.

La Jetson decide traiettorie e contesto, ma non deve essere l'ultimo garante della sicurezza.

### Livello 3 - Comunicazioni e Missione

Responsabilita':

- 4G/LTE per telemetria e SOS;
- LoRa o beacon dedicato per fallback a bassa banda;
- buzzer/speaker per richiesta di aiuto locale;
- dashboard remota;
- log eventi: stop safety, stallo, batteria bassa, perdita sensori, perdita link.

---

## 5. Sensor Fusion Economica: Camera RGB + LiDAR 2D

La base economica evita una camera depth costosa usando una fusione pseudo-3D:

1. La camera RGB rileva una bounding box, ad esempio `person`.
2. La calibrazione estrinseca camera-LiDAR converte la bounding box in un settore angolare.
3. Il LiDAR 2D rileva un cluster nello stesso settore angolare.
4. Il sistema associa classe visiva e distanza LiDAR.

Risultato:

```text
persona rilevata a rho = 2.5 m, theta = -12 deg
ostacolo dinamico -> rallenta, lascia passare o aggira
```

Questa tecnica fornisce una posizione utile per avoidance e tracking. Non va trattata come misura metrologica: distorsione lente, rolling shutter, sincronizzazione temporale e calibrazione introducono errore.

---

## 6. Sensori Scelti e Criteri

### LiDAR 2D

Scelta raccomandata per base economica:

```text
LDROBOT LD19 o equivalente LiDAR 2D DToF
```

Motivo:

- preferire DToF rispetto a triangolazione per uso outdoor;
- montaggio orizzontale per mantenere una occupancy grid pulita;
- usare schermatura meccanica contro sole diretto.

Nota critica: LiDAR economici dichiarati outdoor possono degradare sotto sole di montagna. Servono tettuccio/paraluce, montaggio protetto e filtri software su outlier e cluster instabili.

### Camera RGB

Scelta raccomandata:

```text
camera USB RGB decente, lente non estrema, preferibilmente global shutter se budget lo permette
```

Ruolo:

- rilevare persone/animali/oggetti;
- migliorare la semantica della costmap;
- supportare teleoperazione e diagnostica.

Non e' un sensore safety primario.

### ToF multizona

Scelta raccomandata:

```text
ST VL53L5CX per mini depth-map 8x8
VL53L1X dove basta un singolo raggio economico
```

Ruolo:

- edge detection;
- gradini/vuoti sotto e davanti al rover;
- ostacoli bassi immediatamente davanti alle ruote;
- riduzione delle zone cieche del LiDAR 2D.

Per piu' moduli I2C prevedere:

- multiplexer TCA9548A oppure bus separati;
- gestione indirizzi/reset `LPn`;
- rate safety conservativo;
- logica a zone invece di interpretare ogni cella come verita' assoluta.

### IMU

Scelta consigliata per prototipo:

```text
BNO085/BNO086
```

Motivo: orientamento gia' fuso e integrazione rapida. Piu' avanti si puo' passare a IMU industriale se vibrazioni, temperatura o deriva lo richiedono.

---

## 7. Layout Sensori Proposto

```text
               Fronte rover

          [Camera RGB]
              |
        [LD19 orizzontale]

  [ToF front-low L]      [ToF front-low R]
       \ 30 deg down    30 deg down /

  [ToF down/edge L]      [ToF down/edge R]

               Retro rover
```

Indicazioni:

- LiDAR 2D quasi orizzontale: ostacoli e cluster dinamici.
- ToF frontali bassi inclinati: zona cieca davanti alle ruote.
- ToF sotto chassis: vuoto, bordo sentiero, gradino improvviso.
- IMU vicino al baricentro del rover.
- Camera RGB rigidamente fissata rispetto al LiDAR per mantenere calibrazione.

---

## 8. Policy Comportamentali

### Oggetto statico

```text
LiDAR/ToF rilevano ostacolo stabile
-> rallenta
-> cerca varco
-> se nessun varco, stop e richiesta intervento
```

### Oggetto dinamico o persona

```text
YOLO classifica person/dog oppure LiDAR vede cluster mobile
-> crea zona di costo dinamica
-> rallenta o si scansa
-> riparte quando la traiettoria e' libera
```

### Vuoto o bordo sentiero

```text
ToF down/front rileva salto distanza anomalo
-> STM32 stop immediato
-> Jetson marca evento safety
```

### Pendenza e ribaltamento

```text
IMU rileva roll/pitch oltre soglia warning
-> derating velocita'/coppia

IMU rileva roll/pitch oltre soglia critica
-> stop safety
```

### Rover bloccato

```text
cmd_vel > 0
encoder quasi fermi
corrente alta
-> tentativo breve di recovery
-> se fallisce: stop, buzzer, beacon SOS, telemetria
```

---

## 9. Scelte di Acquisto Consigliate

### Base minima intelligente

```text
Jetson Orin Nano Super Developer Kit 8GB
STM32 Nucleo/H7 o scheda equivalente
LDROBOT LD19 o LiDAR 2D DToF equivalente
camera RGB USB
2-4 ToF ST VL53L5CX / VL53L1X
BNO085/BNO086
encoder + misura corrente motori
4G/LTE o LoRa per SOS
```

### Upgrade quando il software cresce

```text
Jetson Orin NX 16GB
camera migliore o depth camera outdoor-oriented
LiDAR piu' robusto
IMU industriale
GNSS migliore
```

### Da evitare come base primaria

- LiDAR 2D a triangolazione economici spacciati per outdoor;
- sola camera RGB senza sensori geometrici;
- sola camera depth economica come sensore safety;
- Jetson/mini PC senza STM32 watchdog;
- alimentazioni condivise rumorose tra motori e logica;
- connettori USB non bloccati in zone soggette a vibrazione.

---

## 10. Implicazioni Software ROS 2

Pacchetti coinvolti:

- `rover_control`: comandi motori e bridge con controller/VESC.
- `rover_safety`: watchdog, stop, stability margin, stato E-stop.
- `rover_navigation`: follow-me, shared autonomy, terrain assessor, costmap.
- `rover_power`: energia residua e budget missione.
- `rover_system`: state estimation e hardware bridge.
- `rover_interfaces`: contratti pubblici per stati, fault, terrain cost e safety.

Topic/contratti da prevedere o consolidare:

```text
/safety/status
/safety/faults
/hardware/state
/power/energy_budget
/terrain/cost
/mission/cmd_vel
/perception/dynamic_obstacles
/perception/classified_clusters
```

Il comando operativo verso STM32 deve restare semplice:

```text
desired_linear_velocity
desired_angular_velocity
mode
timeout_ms
```

Se il comando scade, STM32 ferma il rover.

---

## 11. Rischi Residui

- Sole diretto e riflessi possono degradare LiDAR/ToF economici.
- Erba alta, fango, rami sottili e superfici nere possono generare misure instabili.
- Camera RGB + LiDAR richiede calibrazione meccanica stabile.
- 4 moduli ToF multizona richiedono progettazione I2C ordinata.
- YOLO leggero puo' sbagliare classi in ombra, controluce o pioggia.
- ROS 2/Jetson non deve mai essere safety-critical da solo.
- Vibrazioni e cablaggio possono causare guasti intermittenti piu' subdoli del bug software.

Mitigazioni:

- soglie conservative lato STM32;
- filtri temporali e hysteresis;
- paraluce e montaggio sensori incassato;
- logging continuo dei fault;
- test outdoor progressivi;
- E-stop fisico e freni meccanici.

---

## 12. Piano di Validazione

1. Banco elettrico: alimentazioni, CAN, heartbeat Jetson-STM32, E-stop.
2. Banco sensori: ToF, IMU, LiDAR, camera, logging ROS bag.
3. Test indoor lento: ostacoli statici, cluster dinamici, stop su heartbeat assente.
4. Test outdoor controllato: sole, ombra, ghiaia, erba, pendenze basse.
5. Calibrazione camera-LiDAR: associazione bounding box/cluster.
6. Test safety edge: gradino simulato, vuoto controllato, bumper/stop.
7. Test stallo: ruote bloccate con limite corrente e recovery.
8. Test missione: follow-me, pausa, avanza, aggiramento, SOS.
9. Test endurance: vibrazioni, temperatura, batteria, log fault.

Ogni test deve produrre log ripetibili: ROS bag lato Jetson e log compatto lato STM32.

---

## 13. Stima Costi

Le cifre sono stime indicative per acquisto 2026 in Europa/AliExpress, IVA inclusa dove applicabile. Non includono utensili di officina, saldatura professionale, lavorazioni impreviste o componenti gia' disponibili a magazzino.

### Elettronica di Bordo e Percezione

| Voce | Stima economica | Stima robusta | Nota |
| :--- | ---: | ---: | :--- |
| Jetson Orin Nano Super Developer Kit 8GB | 280 EUR | 330 EUR | Sotto 320 EUR e' un buon prezzo. |
| NVMe SSD, case, ventola, cablaggi Jetson | 50 EUR | 120 EUR | Storage e montaggio antivibrazione. |
| STM32 Nucleo/H7 o equivalente | 20 EUR | 70 EUR | H7 preferibile se cresce la safety. |
| CAN, level shifting, I2C mux, PCB/proto board | 40 EUR | 150 EUR | Include transceiver e cablaggio logica. |
| LiDAR 2D DToF LD19 o equivalente | 60 EUR | 110 EUR | Da schermare meccanicamente. |
| Camera RGB USB | 20 EUR | 150 EUR | Global shutter solo se budget lo permette. |
| ToF ST VL53L5CX/VL53L1X, 2-4 moduli | 40 EUR | 160 EUR | Mix multizona/singolo raggio. |
| IMU BNO085/BNO086 | 20 EUR | 50 EUR | Prototipo rapido. |
| 4G/LTE, LoRa, buzzer/speaker SOS | 60 EUR | 180 EUR | Dipende dal modem e antenna. |

Totale elettronica/percezione:

```text
economica: 590-750 EUR
robusta:   1.000-1.320 EUR
```

### Powertrain, Batteria e Meccanica

| Voce | Stima economica | Stima robusta | Nota |
| :--- | ---: | ---: | :--- |
| 4x motori brushless/ridotti 24V 200W | 480 EUR | 800 EUR | Dipende da spedizione e dazio. |
| 4x controller/VESC o driver equivalenti | 240 EUR | 700 EUR | Economici tipo Makerbase vs VESC piu' seri. |
| Batteria LiFePO4 24V 30Ah o 100Ah | 200 EUR | 650 EUR | 30Ah (~200€) per Ibrido, 100Ah Smart con Bluetooth/Riscaldamento (~550€) per Elettrico. |
| Caricatori di bordo (AC-DC & DC-DC MPPT) | 120 EUR | 350 EUR | Caricatore AC Mean Well NPB-750 + Regolatore MPPT per colonnine e-bike. |
| Ruote cargo 20", 4 pezzi | 160 EUR | 360 EUR | Mozzo disco 6 fori. |
| Freni meccanici, dischi 203mm, cavi | 180 EUR | 450 EUR | BB7/TRP o equivalenti. |
| Cuscinetti UCF/UCP, bulloneria, supporti | 80 EUR | 220 EUR | Include ricambi e fissaggi buoni. |
| Acciaio, piastre, staffe, verniciatura | 150 EUR | 500 EUR | Variabile con officina e recupero materiali. |
| Alberi custom 42CrMo4 e lavorazioni | 250 EUR | 800 EUR | Una delle voci piu' incerte. |
| Cablaggi potenza, connettori, scatole IP | 150 EUR | 500 EUR | Spesso sottostimata. |

Totale powertrain/meccanica:

```text
economica: 2.140-2.500 EUR
robusta:   4.500-5.200 EUR
```

### Totale Sistema

| Configurazione | Stima |
| :--- | ---: |
| Base economica funzionante, con scelte attente | 2.800-3.300 EUR |
| Base trekking seria, senza esagerare | 4.000-5.500 EUR |
| Versione robusta con componenti migliori e margine | 6.000-7.500 EUR |
| Upgrade Orin NX 16GB al posto della Nano | +350-800 EUR |
| Batteria 24V 50-100Ah invece di 30Ah | +200-700 EUR |
| LiDAR/depth camera piu' robusti | +300-1.500 EUR |

### Lettura Pratica

La parte Jetson/sensori non e' il costo dominante. Il costo vero del rover sta in:

- motori e controller;
- batteria sicura;
- freni e dump load;
- alberi custom;
- cablaggi e protezioni;
- scatole IP e montaggio antivibrazione;
- lavorazioni meccaniche.

Per una prima versione da test, il target realistico e':

```text
circa 3.000 EUR se si compra bene e si autocostruisce molto
circa 4.500 EUR se si vuole gia' una base trekking credibile
```

---

## 14. Decisione Finale

La base hardware approvata per `Mulo X-1` e':

```text
Jetson Orin Nano Super 8GB
+ STM32 safety/control
+ LiDAR 2D DToF schermato
+ camera RGB economica ma stabile
+ ToF multizona/singoli per vuoti e zone cieche
+ IMU
+ encoder e sensori corrente
+ comunicazione SOS 4G/LoRa
```

L'upgrade naturale, se la percezione AI diventa il collo di bottiglia, e':

```text
Jetson Orin NX 16GB
```

Questa architettura mantiene il costo sotto controllo senza sacrificare il principio fondamentale: **il rover deve potersi fermare in modo sicuro anche quando il cervello cognitivo fallisce**.
