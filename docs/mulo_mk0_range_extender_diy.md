# Range Extender DIY per Mulo MK0 — Documento Tecnico

**Versione:** 1.0  
**Stato:** Progettazione Preliminare  
**Riferimento:** `hardware/bom.md` § 3 — Alimentazione e Controllo

---

## 1. Concept Generale e Filosofia Progettuale

### Perché un Range Extender DIY e non un generatore commerciale

I generatori commerciali da 1 kW (es. Honda EU10i, Yamaha EF1000iS) sono macchine ottimizzate per l'uso domestico stazionario. Impongono vincoli incompatibili con la robotica mobile:

- **Elettronica proprietaria chiusa:** impossibile integrare la ricarica nel BMS/ECMS del rover
- **Orientamento fisso:** non sopportano inclinazioni >15° senza perdita di lubrificazione o fuoriuscita di carburante
- **Peso excessivo:** 13-21 kg per 1 kW — quasi il doppio di una soluzione custom
- **Ingombro fisso:** coperture e forme non adattabili al telaio del rover
- **Nessun controllo remoto:** impossibile spegnere/accendere via ROS2

La strada DIY — già adottata nella robotica industriale a lungo raggio e nei droni pesanti — consiste nell'**accoppiare un motore termico industriale a membrana con un motore brushless usato come alternatore**. Non si costruisce il motore da zero: si integrano due componenti già ottimizzati.

### 1.1 Vantaggi della Batteria LiFePO4 24V

La scelta della chimica LiFePO4 a 24V (8 celle in serie) non è casuale. È il risultato di un trade-off ingegneristico tra densità energetica, sicurezza, durata e compatibilità con l'impianto elettrico esistente.

| Vantaggio | Descrizione | Impatto sul Rover |
|:---|:---|:---|
| **Sicurezza intrinseca** | La chimica LiFePO4 è la più sicura tra le batterie al litio. Non va in thermal runaway, non prende fuoco, non esplode. | Ideale per veicolo off-road esposto a urti, vibrazioni e temperature estreme. |
| **Cicli di vita elevati** | 2000-5000 cicli all'80% DoD vs 300-500 cicli per Li-ion NMC/NCA. | Una LiFePO4 100Ah dura 5-10 anni di uso intensivo senza sostituzione. |
| **Curva di scarica piatta** | Mantiene ~3.2V/cella per l'80% della scarica. | Il rover ha potenza costante per quasi tutta la durata della batteria, senza cali di prestazione visibili. |
| **Tolleranza termica** | Funziona da -20°C a +60°C. | In montagna d'inverno la LiFePO4 resiste meglio del Li-ion tradizionale, che perde capacità sotto 0°C. |
| **Efficienza di ricarica** | Può essere ricaricata a rate elevati (1C) senza degradazione significativa. | Il range extender può caricare rapidamente la batteria senza danneggiarla. |
| **Nessun effetto memoria** | Può essere ricaricata parzialmente senza ridurre la capacità residua. | Ideale per ricariche brevi dal range extender o dal pannello solare. |
| **Compatibilità con l'impianto** | Il sistema 24V è già progettato per il rover (motori, VESC, elettronica, fusibili). | Nessuna modifica all'impianto elettrico esistente. |

**Perché 24V e non 48V?**

| Criterio | 24V | 48V |
|:---|:---:|:---:|
| Corrente per 1 kW | ~42A | ~21A |
| Spessore cavi | AWG10 (più pesante) | AWG14 (più leggero) |
| Sicurezza (soglia shock) | <60V DC (extra-bassa tensione) | <120V DC (bassa tensione) |
| Compatibilità motori | ✅ Motori esistenti 24V | ❌ Serve nuovo set motori+VESC |
| Range extender | Buck 50V→24V (più semplice) | Buck 50V→48V (più semplice) |
| Costo complessivo | ✅ Più basso | ❌ Più alto (nuovi componenti) |

> **Conclusione:** Il 24V è il compromesso ottimale per il Mulo MK0. La corrente più alta (~42A), gestibile con cavi AWG10 e connettori XT90/Anderson. Il passaggio a 48V sarebbe giustificato solo con un rover significativamente più potente (>3 kW di trazione).

---

## 2. Architettura del Sistema

```
╔══════════════════════════════════════════════════════════════════╗
║              RANGE EXTENDER DIY — BLOCCHI FUNZIONALI            ║
╚══════════════════════════════════════════════════════════════════╝

  ┌─────────────────────┐      ┌───────────────────────┐
  │  Motore Termico     │      │  Motore VEVOR 48V     │
  │  (63cc 2T / GX50)   │      │  1800W Brushless DC   │
  │  ~2.0 kW @6500 RPM  │      │  (Kv ~94 RPM/V)       │
  └──────────┬──────────┘      └───────────┬───────────┘
             │                             ▲
             │ Puleggia 1:1                │ Puleggia 1:1
             │ (Ø8mm + spina)              │ (Ø12mm + chiavetta)
             └────────── Cinghia ──────────┘
                        HTD 5M 15mm
                                           │
                                           │ AC Trifase (~50V-60V AC RMS)
                                           ▼
                               ┌───────────────────────┐
                               │  Ponte Raddrizzatore  │
                               │  SQL100A Trifase      │
                               └───────────┬───────────┘
                                           │ DC grezza pulsante (~70-85V DC)
                                           ▼
                               ┌───────────────────────┐
                               │  Banco Condensatori   │
                               │  Elettrolitici        │
                               │  100V ~4700µF         │
                               └───────────┬───────────┘
                                           │ DC stabile
                                           ▼
                               ┌───────────────────────┐
                               │  Regolatore Buck      │
                               │  Step-Down 1500W      │
                               └───────────┬───────────┘
                               │ 28.8V DC regolata (CC/CV)
                               ▼
                               ┌───────────────────────┐
                               │ Modulo Diodo Ideale   │
                               │ 50A / 80V             │
                               └───────────┬───────────┘
                                           │
                                           ▼
                               ┌───────────────────────┐
                               │ Pacco Batteria LiFePO4│
                               │ 24V, >30 Ah           │
                               └───────────────────────┘
```

Il flusso è sequenziale e **unidirezionale**: il termico genera coppia meccanica → il BLDC la converte in AC trifase → il raddrizzatore + condensatori la convertono in DC → il regolatore la adatta alla tensione di ricarica della batteria.

---

## 3. Selezione Componenti

### 3.1 Core Termico: Honda GX50 (raccomandato)

| Parametro | GX35 | **GX50** | Note |
|---|---|---|---|
| Cilindrata | 35.8 cc | **49.4 cc** | Più coppia a bassi giri |
| Potenza max | 1.0 kW @7000 RPM | **1.47 kW @7000 RPM** | +47% potenza netta |
| Coppia max | ~1.5 Nm @5000 RPM | **~2.0 Nm @5000 RPM** | Più adatta al generatore |
| Peso | 1.3 kg | **1.5 kg** | Differenza trascurabile |
| Lubrificazione | Membrana (360°) | **Membrana (360°)** | Funziona inclinato/ribaltato |
| Carburatore | Walbro a membrana | **Walbro a membrana** | Nessun problema di erogazione in salita |
| Avviamento | Strappo | **Strappo** | Vedi §7 per avviamento elettrico |

> **Perché GX50 e non GX35:** Il margine di potenza extra (+0.47 kW) permette di caricare la batteria mentre il rover è in movimento leggero, e non solo in sosta. Il peso aggiuntivo (200g) è irrilevante.

**Alternativa europea al GX50:** Briggs & Stratton 550 Series (127cc — sovradimensionato ma più coppia a bassi giri) oppure Zenoah/Husqvarna motori 4T industriali 50cc — ricambi più reperibili in Italia.

### 3.2 Alternatore: Motore VEVOR 48V 1800W Brushless DC

In questa configurazione aggiornata, utilizziamo un motore industriale **VEVOR 48V 1800W BLDC** come generatore. Essendo progettato per operare a 4500 RPM nominali a 48V, il suo Kv stimato è circa `4500 / 48 = ~93.75 RPM/V`.

| Parametro | Specifica VEVOR | Note |
|---|---|---|
| Potenza Nominale | 1800W | Abbondante per caricare a ~1.4kW continui |
| Tensione Nominale| 48V | Genera ~48V a 4500 RPM |
| RPM Nominale | 4500 RPM | Ottimale se accoppiato a pulegge 1:1 o 1.5:1 |
| Albero | 12 mm | Perfetto per puleggia HTD 5M foro 12mm |
| Peso | 5.3 kg (11.68 lbs)| Contribuisce ad abbassare il baricentro del rover |

**Rapporto di trasmissione:** Se accoppiato 1:1 al motore termico a 6500 RPM, il VEVOR genererà circa `6500 / 94 = ~69V DC` (che possono superare gli 80V di picco a vuoto) dopo il raddrizzatore. Questo richiede un Buck Converter step-down capace di gestire ingressi elevati (almeno 80V-100V).

> **Nota chiave sul Controller:** Il kit VEVOR include un controller di velocità per uso trazione. **Questo controller non va utilizzato**. Il motore funzionerà esclusivamente come generatore passivo: le tre fasi escono libere e si collegano direttamente al ponte raddrizzatore a diodi. Nessun firmware aggiuntivo richiesto.

### 3.3 Ponte Raddrizzatore Trifase

- **Tipo:** Ponte trifase a 6 diodi Schottky (configurazione a ponte di Graetz trifase)
- **Diodi consigliati:** MBR40250 o MBR60200 (60A, 200V, bassa Vf)
- **Dissipazione:** Montare su dissipatore alluminio con pasta termica — i diodi dissipano ~2-3W totali a piena corrente
- **Capacità di condensatori:** 2x 4700μF / 63V elettrolitici in parallelo (livellamento tensione)

### 3.4 Regolatore DC-DC Programmabile

| Parametro | Requisito |
|---|---|
| Topologia | Buck (step-down) |
| Tensione ingresso | **30-90V DC** (Il VEVOR a 6500 RPM genera ~70-85V) |
| Tensione uscita | 28.8V (ricarica LiFePO4 24V a 8S) |
| Corrente max uscita | 40-50A continui |
| Modalità ricarica | CC/CV programmabile (Constant Current / Constant Voltage) |

**Candidati:** Moduli buck industriali 100V->24V, o regolatori **MPPT solari** (molti MPPT accettano fino a 100V-150V in ingresso e sono perfetti per caricare batterie LiFePO4 24V da sorgenti a tensione variabile).

---

## 4. Risoluzione della Trasmissione e Allineamento

Nelle prime fasi di progettazione si era considerata una trasmissione diretta (direct drive) coassiale tramite giunto Lovejoy. Tuttavia, a causa dei vincoli di accoppiamento degli alberi del motore Honda GX50 (che esce con frizione centrifuga da 76mm ad innesto a ~4400 RPM) e per prevenire carichi flettenti distruttivi sulle bronzine/cuscinetti dell'albero motore, si è optato per una **trasmissione a cinghia dentata HTD 5M (larghezza 15mm, rapporto 1:1)**.

Questa scelta garantisce l'assorbimento delle sollecitazioni e permette di posizionare i motori parallelamente su una singola piastra comune.

### 4.1 La Presa di Forza (PTO): Il Metodo della Spinatura Supportata (Opzione DIY)

Per convertire l'alloggiamento frizione standard (quello femmina a 9 denti, montato sul carter motore Honda) in un asse di uscita robusto e dritto senza ricorrere a costosi ricambi importati, si adotta il trucco del **KP08 supportato**:

1. **Albero Millerighe Modificato:** Si acquista un'asta rigida di ricambio per decespugliatore (diametro esterno 8mm liscio con terminale scanalato a 9 denti 9T) e se ne taglia uno spezzone di circa 15 cm tramite smerigliatrice angolare. L'estremità scanalata 9T viene infilata nella campana frizione.
2. **Supporto Esterno (Cuscinetto KP08):** L'albero da 8mm sporge verso l'esterno. Per evitare che il tiro laterale della cinghia deformi o sforzi la campana o i cuscinetti del motore Honda, l'asse liscio da 8mm viene alloggiato in un supporto flangiato **KP08** imbullonato direttamente alla piastra di base. I grani a brugola interni del KP08 stringono l'asse impedendo scorrimenti assiali.
3. **Fissaggio Puleggia (Roll Pin):** La puleggia HTD 5M (foro 8mm) viene infilata sull'asse liscio. Si esegue un foro passante radiale utilizzando un trapano a colonna e si pianta a martellate una spina elastica in acciaio (roll pin) da 3mm o 4mm per bloccare solidamente la puleggia contro torsioni e vibrazioni.

### 4.2 Tolleranze e Incollaggio Coassiale

* **Allineamento Tollerante:** Non è richiesta accuratezza micrometrica durante la foratura manuale della piastra di base per allineare il cuscinetto. Il supporto KP08 è autoallineante: la sede interna sferica bascula compensando angoli imperfetti e assicurando che l'asse giri senza attriti.
* **Incollaggio coassiale anti-fretting:** Per prevenire l'usura (fretting) dovuta ai picchi alternati di coppia del motore termico monocilindrico, l'innesto millerighe 9T va incollato rigidamente nella frizione femmina.
* **Colla Anaerobica Professionale:** È obbligatorio usare un vero bloccante coassiale anaerobico ad alta resistenza (Loctite 638/648, Loxeal 83-21, o Arexons PRO 52A43). Scartare resine clone cinesi (es. "LOCTTLF") che cederebbero sotto carico termico e vibratorio.

### 4.3 Regimi di Rotazione e Rapporto Pulegge

Il motore brushless prescelto (Outrunner taglia 80100, Kv ~170) riporta spesso sulle schede dei venditori un limite di "4080 RPM", che indica semplicemente il regime calcolato a vuoto a 24V di alimentazione elettrica. Meccanicamente, il rotore e i cuscinetti possono reggere tranquillamente velocità comprese tra 8.000 e 10.000 RPM.
Entrambi i motori gireranno con rapporto pulegge 1:1 a circa **6500 RPM** (punto di massima efficienza o "Sweet Spot" del motore Honda GX50). A questo regime, l'alternatore brushless genererà circa ~35V AC RMS trifase, raddrizzati in ~50V DC stabili in ingresso al Buck Step-Down.

---

## 5. Circuito di Rettifica e Regolazione — Schema Completo

```
                    BLDC OUTRUNNER (Alternatore)
                    ┌─────┐   ┌─────┐   ┌─────┐
                    │  U  │   │  V  │   │  W  │
                    └──┬──┘   └──┬──┘   └──┬──┘
                       │         │         │
                 ┌─────▼─────────▼─────────▼─────┐
                 │   Ponte Raddrizzatore Trifase   │
                 │   6x Diodi Schottky MBR40250   │
                 └──────────────┬────────────────-┘
                                │ DC pulsante (0-65V)
                 ┌──────────────▼─────────────────┐
                 │  Condensatori 2x 4700μF / 63V   │
                 │  in parallelo (livellamento)     │
                 └──────────────┬─────────────────┘
                                │ DC stabilizzata
                 ┌──────────────▼─────────────────┐
                 │  Regolatore Buck Programmabile   │
                 │  CC/CV → 28.8V / 40A max        │
                 │  (+ shunt INA226 monitoring)     │
                 └──────────────┬─────────────────┘
                                │ 28.8V DC / ≤40A
                 ┌──────────────▼─────────────────┐
                 │   BMS LiFePO4 24V (8S)          │
                 │   Protezione overcharge/OVP      │
                 └──────────────┬─────────────────┘
                                │
                 ┌──────────────▼─────────────────┐
                 │   Pacco Batteria LiFePO4         │
                 │   24V / >30 Ah                   │
                 └────────────────────────────────-┘
```

### Monitoraggio remoto (integrazione ROS2)

Aggiungere un **INA226** (shunt I2C) tra regolatore e BMS permette di misurare in tempo reale:
- Corrente di ricarica (A)
- Tensione di ricarica (V)
- Potenza istantanea (W)

Il dato viene pubblicato su topic ROS2 `/power/range_extender` dal nodo nel package `rover_power`, implementando così la strategia ECMS descritta in `engineering_recommendations.md` §3.

---

## 6. Integrazione Fisica sul Rover Mulo MK0

### Concetto di layout verticale

```
      VISTA LATERALE MULO MK0 — LAYOUT ENERGETICO
      
      ────────────────────────────────────── 100cm (CoG carico)
      
      ╔══════════════════════════════════╗
      ║  GABBIA ZAINI (Alluminio 6061)   ║  ← 55-90cm
      ║  Zaini / Materiale Trekking      ║
      ╚══════════════════════════════════╝
      ════════════════════════════════════  ← 55cm  (Pianale S235)
      ╔══════════════════════════════════╗
      ║  VANO BATTERIA + ELETTRONICA     ║  ← 30-55cm
      ║  LiFePO4 24V / Jetson / VESC    ║
      ║  (Vano chiuso IP54, antiurto)    ║
      ╚══════════════════════════════════╝
      ════════════════════════════════════  ← 30cm  (Traversa telaio)
      
      ╔══════════════════════════════════╗
      ║  GABBIA RANGE EXTENDER           ║  ← 0-30cm sotto traversa
      ║  (Aperta, ventilata)             ║
      ║  [ GX50 ] ─── [ BLDC ] ─ [ ∿ ] ║
      ║  [Raddrizzatore] [Buck] [Cond.]  ║
      ╚══════════════════════════════════╝
      ════════════════════════════════════  ← 0cm   (suolo)
```

### Perché il generatore sta SOTTO

1. **Baricentro basso:** il gruppo GX50+BLDC pesa ~6.5 kg posizionati sotto l'asse delle ruote — migliora la stabilità al ribaltamento
2. **Ventilazione naturale:** la posizione sotto-telaio garantisce flusso d'aria continuo anche in sosta
3. **Isolamento termico/acustico:** la traversa di acciaio S235 + vano batteria fanno da barriera tra il calore/vibrazioni del termico e l'elettronica sopra
4. **Accesso manutenzione:** il tiraggio della corda di avviamento e il rifornimento carburante avvengono dal fianco, senza toccare il resto del rover
5. **Scarico orientabile:** il tubo di scarico può uscire lateralmente o posteriormente, lontano da qualsiasi sensore

---

## 7. Gabbia Sotto-Telaio per Range Extender

### 7.1 Funzione e Requisiti

| Requisito | Motivazione |
|---|---|
| Struttura aperta (ventilata) | Il GX50 produce calore e fumi — la chiusura causerebbe surriscaldamento e accumulo CO |
| Protezione da urti e sassi | Il rover opera off-road: proteggere il BLDC e il circuito elettronico da proiettili |
| Smontabile in <5 minuti | Manutenzione in campo: rifornimento benzina, controllo olio, pulizia filtro aria |
| Orientamento fisso del GX50 | L'albero di uscita deve essere allineato con l'asse del BLDC |
| Isolamento vibrazioni | Nessuna vibrazione trasmessa al telaio principale → protegge Jetson, IMU, LiDAR |

### 7.2 Struttura della Gabbia

**Materiale:** Acciaio S235 - Tubolare 25×25×2 mm (stesso dell'acciaio del telaio principale — saldatura omogenea possibile)

> Perché acciaio e non alluminio? La gabbia è sotto il rover, esposizione massima a urti, sassi, rocce. L'acciaio S235 assorbe meglio l'energia d'impatto. Peso leggermente superiore ma posizione bassa (vantaggio CoG).

### 7.2 Struttura della Gabbia e Layout Meccanico

**Materiale:** Acciaio S235 - Tubolare 25×25×2 mm.

```
      VISTA FRONTALE LAYOUT TRASMISSIONE (CINGHIA HTD 5M)

              Puleggia                 Cinghia              Puleggia
              Motore                  HTD 5M 1:1           Brushless
             ┌────────┐         ========================   ┌────────┐
             │ Pulle  │════════════════════════════════════│ Pulle  │
             └────────┘                                    └────────┘
                 │                                             │
             ┌───▼────┐                                    ┌───▼────┐
             │ Albero │                                    │ Albero │
             │ 8mm 9T │                                    │  12mm  │
             └────────┘                                    └────────┘
                 │                                             │
             [Tamburo]                                     [Motore  ]
             [Frizione]                                    [VEVOR   ]
                 │                                             │
             [Supporto]                                    [Base    ]
             [  KP08  ]                                    [Motore  ]
                 │                                             │
      =======════╧═════════════════════════════════════════════╧═════════
      PIASTRA MONOLITICA D'ACCIAIO (Spessore 5-6mm)
      ===================================================================

      VISTA LATERALE GABBIA RANGE EXTENDER (PIASTRA UNICA)
      
      ┌──────────────────────────────────────────────┐ ← Aggancio al telaio
      │  ●────────────────────────────────────────●  │   (Silent Block)
      │  │                                        │  │
      │  │      [HONDA GX50]                      │  │
      │  │      (rialzato con                     │  │
      │  │      4 distanziali)      [ VEVOR   ]   │  │
      │  │           │              [ 1800W   ]   │  │
      │  │     ┌─────▼─────┐       ┌────▼────┐    │  │
      │  │     │   Puleg   │======═│  Puleg  │    │  │ (HTD 5M 1:1)
      │  │     └───────────┘       └─────────┘    │  │
      │  │   ══════════════════════════════════   │  │
      │  │   PIASTRA UNICA D'ACCIAIO (5-6mm)      │  │
      │  │   ──────────────────────────────────   │  │
      │  │   [ 4x Silent Block agli angoli ]      │  │
      │  │                                        │  │
      │  │   ┌────────────────────────────────┐   │  │
      │  │   │ Piastra Alluminio Elettronica  │   │  │ (Dissipatore)
      │  │   │ (SQL100A, Buck, Condensatori)  │   │  │
      │  │   └────────────────────────────────┘   │  │
      │  ●────────────────────────────────────────●  │
      └──────────────────────────────────────────────┘
```

### 7.3 Dimensioni Gabbia

| Parametro | Valore | Note |
|---|---|---|
| Larghezza | 55 cm | Filo esterno telaio S235 |
| Profondità | 40 cm | GX50 (25cm) + flangia (5cm) + BLDC (10cm) |
| Altezza | 22-25 cm | Sotto la traversa principale (ground clearance rover: 30cm) |
| Spazio sottocassa residuo | ~5-8 cm | Dipende dal terreno — verificare in campo |

> **Attenzione ground clearance:** Il rover Mulo MK0 ha ruote cargo e-bike 20" → raggio ~255mm → altezza mozzo ~255mm. La traversa inferiore del telaio è a circa 30-35cm da terra. La gabbia da 22-25cm lascia ~5-10cm di clearance — sufficiente per sentiero compatto, limite su rocce alte.

### 7.4 Fissaggio Strutturale e Isolamento Vibrazioni

Un errore critico in fase di progettazione consiste nell'utilizzare supporti antivibranti (silent-block) separati per il motore termico e l'alternatore brushless. Sotto la trazione della cinghia dentata HTD, i motori fletterebbero l'uno rispetto all'altro, causando la rottura precoce della cinghia o il disallineamento delle pulegge.

* **Sotto-telaio Monolitico (La Piastra Unica):** Per scongiurare questo problema, il motore Honda GX50 e la staffa a L del motore Brushless sono imbullonati rigidamente alla stessa massiccia piastra d'acciaio da 5-6mm.
* **Distanziali del Carter Termico:** Il GX50 si fissa sulla piastra sfruttando i 4 fori filettati inferiori, ma viene rialzato tramite 4 colonnine/distanziali metallici per proteggere il serbatoio in plastica inferiore dallo schiacciamento contro la piastra stessa.
* **Sospensione a Silent-Block:** L'isolamento vibratorio a salvaguardia delle schede logiche e dei sensori del Mulo (Jetson, LiDAR, IMU BNO086) si ottiene montando l'intera piastra (con tutto il gruppo solidale montato sopra) al telaio principale mediante **4 Silent-Block in gomma** (40-50 Shore) posizionati esclusivamente ai quattro angoli della piastra.

### 7.5 Protezione Elettronica (Piastra Derivata)

L'elettronica di potenza (ponte raddrizzatore, condensatori, regolatore Buck) non va posizionata sul corpo del GX50 ma su una **piastra alluminio separata**, montata nella metà posteriore della gabbia, lontano dal calore del motore termico.

- Materiale piastra: Alluminio 3mm (dissipatore passivo)
- Separazione dal GX50: minimo 15 cm + schermo termico in acciaio inox 0.5mm
- Connessione alla batteria: cavo AWG10 (carica 40A) con connettore XT90 o Anderson SB50

---

## 8. Sistema di Avviamento

### Opzione A: Strappo Manuale (MK0 — Default)

La corda di strappo del GX50 rimane accessibile dal fianco del rover. L'operatore la tira prima della sessione di ricarica. Semplice, affidabile, nessuna elettronica aggiuntiva.

- **Pro:** zero complessità, massima affidabilità
- **Contro:** richiede presenza fisica dell'operatore

### Opzione B: Avviamento Elettrico (MK1 — Upgrade)

Il BLDC outrunner usato **temporaneamente come motore** per avviare il GX50. Richiede:

1. Un ESC bidirezionale capace di pilotare il BLDC in modalità "motor" (attingendo dalla batteria)
2. Un sensore di posizione albero (encoder Hall già integrato nella maggior parte dei BLDC)
3. Firmware ROS2 che gestisce la sequenza: avvio ESC → coppia avviamento → rilevamento combustione → switch a modalità generatore

```python
# rover_power: nodo range_extender_manager.py
# Sequenza avviamento elettrico (pseudocodice)

def avvia_range_extender():
    self.esc.set_mode('motor')
    self.esc.set_rpm(1200)          # RPM avviamento GX50
    time.sleep(3.0)                  # Attende combustione
    if self.rpm_sensor.get() > 800:  # GX50 avviato
        self.esc.set_mode('generator_passthrough')
        self.buck.enable()
        self.get_logger().info('Range extender attivo')
    else:
        self.esc.disable()
        self.get_logger().error('Avviamento fallito — riprovare')
```

> La funzione Stator-Starter complica il firmware ma elimina la necessità dell'operatore fisico. Ideale per operazioni autonome prolungate.

### Opzione C: Avviamento Elettrico a Pulsante (MK0.5 — Compromesso Consigliato)

Questa opzione è il compromesso ideale tra semplicità e comodità. Usa un **motore di avvio elettrico separato** con pulsante sul pannello operatore, senza modificare il firmware del BLDC o aggiungere un ESC bidirezionale. È la scelta consigliata per la prima versione del range extender.

**Principio di funzionamento:**

Il Honda GX50 (e la maggior parte dei motori industriali 4T) può essere dotato di un **kit di avviamento elettrico** opzionale. Il kit include:
1. Un piccolo **motore di avvio 12V** (motorino DC brush) che si ingranca sul volano del GX50 tramite un pinioncino a frizione centrifuga
2. Un **solenoide di avvio** (relay 12V 80-100A) che collega il motorino alla batteria
3. Un **pulsante di avvio** sul pannello operatore

Il GX50 ha già integrato il sistema di accensione **CDI (Capacitor Discharge Ignition)** — ovvero i "condensatori e candela" — che genera la scintilla per accendere la miscela aria/carburante. Non serve nulla di aggiuntivo per l'accensione: il CDI è già nel motore.

**Schema di funzionamento:**

```
  [Pulsante START] ──► [Solenoide 12V] ──► [Motore Avvio 12V]
                                                   │
                                              [Ingrana volano GX50]
                                                   │
                                              [GX50 parte]
                                                   │
                                              [CDI integra: condensatori + candela]
                                                   │
                                              [Motore gira autonomamente]
                                                   │
                                              [Pinioncino si disengage]
                                                   │
                                              [BLDC inizia a generare AC]
```

**Alimentazione del motore di avvio:**
- Il motore di avvio è tipicamente a 12V
- Alimentato dalla batteria LiFePO4 24V del rover tramite un **convertitore DC-DC step-down 24V→12V** (10A continuo, 20A picco)
- Alternativa premium: un **supercondensatore da 500F/2.7V × 6 in serie** (16.2V) come buffer di avviamento. Il supercondensatore eroga picchi >200A senza stressare la batteria principale, e si ricarica in pochi secondi dopo ogni avviamento.

**Vantaggi rispetto all'Opzione B (BLDC come starter):**
- ✅ Nessuna modifica firmware del BLDC
- ✅ Nessun ESC bidirezionale necessario
- ✅ Costo inferiore (~70-90€ vs ~150-200€)
- ✅ Affidabilità meccanica superiore (motore di avvio dedicato)
- ✅ Il BLDC resta permanentemente in modalità generatore (più semplice)
- ✅ Il CDI è già integrato nel GX50 — "condensatori e candela" già inclusi

**Svantaggi:**
- ❌ Richiede ancora presenza fisica dell'operatore (deve premere il pulsante)
- ❌ Aggiunge un componente meccanico (motore di avvio) con usura
- ❌ Consuma ~200-300Wh dalla batteria ad ogni avviamento (trascurabile)

**Costo stimato:**

| Componente | Costo |
|:---|---:|
| Kit avviamento elettrico GX50 (motore + solenoide + ingranaggio) | ~30-50€ |
| Convertitore DC-DC 24V→12V 20A (o supercondensatore) | ~25-40€ |
| Pulsante + cablaggio + relay | ~15€ |
| **TOTALE** | **~70-90€** |

> **Raccomandazione per MK0:** L'Opzione C (avviamento elettrico a pulsante) è la scelta consigliata per la prima versione del range extender. Offre il 90% del comfort dell'avviamento remoto al 30% del costo e complessità. L'operatore preme un pulsante, il GX50 parte (CDI già integrato), e la ricarica inizia. Nessuna corda da tirare, nessun firmware da modificare.

---

## 9. Silenziatore Aggiuntivo

Il GX50 esce di fabbrica con un silenziatore minimo. Per uso in montagna (trekking, rifugi, zone protette) il livello sonoro originale (~85 dB a 1m) è inaccettabile.

### Soluzione: Risuonatore a espansione in camera singola

```
  [GX50 Scarico] ──► [Tubo flessibile acciaio inox Ø22mm] ──► [Camera espansione]
                                                                   │
                                               Volume: ~500 cc     │
                                               Materiale: inox     │
                                               304L spess. 1.5mm   │
                                                                   ▼
                                                              [Uscita Ø16mm]
                                                              orientata verso
                                                              il basso/posteriore
```

- **Attenuazione stimata:** -15 dB (da ~85 dB a ~70 dB a 1 m)  
- **Peso aggiunto:** ~0.4 kg  
- **Materiale:** Acciaio inox 304L (temperatura scarico GX50: ~200-300°C)  
- **Posizione:** All'interno della gabbia, lato posteriore, con uscita fumi verso il basso e verso il retro del rover

---

## 10. Bilancio Energetico nell'Architettura Mulo MK0

### Scenari operativi

| Scenario | Batteria | Range Extender | Consumo rover | Bilancio |
|---|---|---|---|---|
| **Trekking piatto** | 24V, 30Ah = 720 Wh | OFF | ~200-300W | 2.4-3.6 ore autonomia pura |
| **Salita ripida** | 24V, 30Ah = 720 Wh | OFF | ~600-800W | 0.9-1.2 ore |
| **Sosta ricarica** | LiFePO4 24V | ON: ~1000W netti | 0W | +30 Ah in ~45 min |
| **Marcia + ricarica** | LiFePO4 24V | ON: ~1000W | ~300W | **+700W bilancio positivo** |
| **Salita + ricarica** | LiFePO4 24V | ON: ~1000W | ~700W | **+300W bilancio positivo** |

> In **tutti gli scenari con Range Extender attivo**, il rover accumula più energia di quanta ne consuma. L'autonomia diventa teoricamente **illimitata** finché c'è carburante.

### Consumo carburante GX50 a piena potenza

- Consumo specifico Honda GX50: ~370 g/kWh (benzina)
- A 1.47 kW → ~543 g/ora → ~0.73 L/ora (densità benzina 0.745 kg/L)
- Serbatoio GX50: 0.58 L → ~48 minuti a piena potenza
- **Tank aggiuntivo esterno da 1L (HDPE, montato in gabbia):** +82 minuti → totale ~2 ore di generazione continua per rifornimento

---

## 11. Peso Totale e Budget

### Pesi Range Extender

| Componente | Peso |
|---|---|
| Honda GX50 (con serbatoio pieno) | ~2.2 kg |
| BLDC Outrunner 80100 | ~2.5 kg |
| Alloggiamento Frizione + Asse + Cuscinetto KP08 | ~0.6 kg |
| Pulegge HTD 5M 20T (x2) + Cinghia 15mm | ~0.2 kg |
| Ponte Raddrizzatore SQL100A + Condensatore 4700µF | ~0.4 kg |
| Regolatore Buck Step-Down 1500W | ~0.4 kg |
| Silenziatore aggiuntivo | ~0.4 kg |
| Tank carburante HDPE 1L (vuoto) | ~0.2 kg |
| **TOTALE RANGE EXTENDER** | **~6.9 kg** |

### Pesi Gabbia Sotto-Telaio

| Componente | Peso |
|---|---|
| Profilo S235 25×25×2mm (perimetro gabbia ~2m) | ~2.3 kg |
| Piastra Unica Acciaio 5mm (Supporto Motori) | ~1.8 kg |
| Staffa a L Alluminio (Tensionamento Brushless) | ~0.4 kg |
| Piastra alluminio elettronica 3mm | ~0.4 kg |
| Schermo termico inox 0.5mm | ~0.3 kg |
| 4x Silent-block + Distanziali metallici | ~0.4 kg |
| Bulloneria varia (M10, M8, M6) | ~0.4 kg |
| **TOTALE GABBIA + PIASTRE** | **~6.0 kg** |

**Peso totale sistema = 12.9 kg** — A fronte di una maggiore robustezza strutturale e di un allineamento garantito dalla piastra unica di acciaio.

### Budget Stimato

| Componente | Costo |
|---|---|
| Honda GX50 (motore solo, no frizione) | ~200-250 € |
| BLDC Outrunner 80100 Kv170 | ~80-120 € |
| Alloggiamento frizione stazionaria + asse 9T + KP08 | ~35 € |
| Kit pulegge HTD 5M 20T (foro 8mm e 12mm) + Cinghia | ~25 € |
| Bloccante coassiale Loctite 638 o Loxeal 83-21 | ~15 € |
| Staffa a L + Distanziali metallici | ~15 € |
| Piastra unica d'acciaio 5mm + Piastre alluminio | ~35 € |
| Ponte raddrizzatore SQL100A + condensatori 100V | ~20 € |
| Regolatore Buck programmabile 1500W | ~45 € |
| Modulo diodo ideale 50A + Sensore Hall ACS758 | ~20 € |
| Silenziatore custom inox (officina) | ~50-80 € |
| Tank HDPE 1L + fitting | ~15 € |
| Tubolare S235 gabbia + bulloneria | ~40 € |
| Silent-block x4 | ~15 € |
| Cavi AWG10, connettori XT90/Anderson | ~20 € |
| **TOTALE STIMATO** | **~615-815 €** |

---

## 12. Integrazione con rover_power (ROS2)

Il Range Extender viene gestito dal package `rover_power` tramite un nodo dedicato:

```
rover_power/
├── range_extender_manager.py     # Nodo principale
├── range_extender_monitor.py     # Telemetria INA226 → topic ROS2
└── config/
    └── range_extender_params.yaml
```

**Topic pubblicati:**
- `/power/range_extender/state` (`std_msgs/String`): IDLE | STARTING | RUNNING | FAULT
- `/power/range_extender/power_w` (`std_msgs/Float32`): Potenza generata istantanea (W)
- `/power/range_extender/charge_current_a` (`std_msgs/Float32`): Corrente di ricarica (A)

**Servizi:**
- `/power/range_extender/start` — avvia sequenza accensione (Opzione B)
- `/power/range_extender/stop` — spegne carburante via solenoid valve

**Integrazione ECMS:** Il nodo legge `/power/battery_soc` e attiva/disattiva il generatore secondo la strategia di gestione energetica definita in `engineering_recommendations.md` §3.

---

## 13. Note di Sicurezza

> [!WARNING]
> Il GX50 produce monossido di carbonio (CO). Non avviare mai in ambienti chiusi. In campo aperto orientare sempre lo scarico sottovento rispetto all'operatore.

> [!CAUTION]
> La benzina è infiammabile. Il serbatoio HDPE aggiuntivo deve essere montato a **minimo 20 cm** dall'uscita dello scarico del GX50, su piastra di supporto con bacinella di contenimento anti-sversamento.

> [!IMPORTANT]
> Prima di avviare il GX50, verificare sempre:
> 1. Livello olio nel carter (dipstick) — l'olio si consuma lentamente
> 2. Assenza perdite di carburante dal raccordo tank
> 3. Che nessun cavo elettrico passi vicino al tubo di scarico (temperatura: 200-300°C)
> 4. Che la gabbia ventilata non sia ostruita da fango o vegetazione

---

## 14. Prossimi Passi (TODO)

- [ ] Sourcing dei componenti meccanici ed elettronici (Loctite 638/648, cuscinetto KP08, albero 9T, pulegge HTD 5M).
- [ ] Foratura della piastra di supporto in acciaio da 5mm per il motore Honda e le asole di scorrimento della staffa a L del brushless.
- [ ] Taglio e preparazione dell'asse decespugliatore da 8mm con terminale 9T.
- [ ] Incollaggio coassiale dell'asse 9T nel tamburo frizione con bloccante anaerobico.
- [ ] Foratura radiale al trapano a colonna per inserire la spina elastica (roll pin) sulla puleggia da 8mm.
- [ ] Costruzione e installazione della staffa a L per l'alternatore Brushless 80100.
- [ ] Configurazione della centralina STM32 e programmazione del controllo di ricarica tramite loop PID (modulazione servo del gas basata sul sensore di corrente ACS758).
- [ ] Prova a banco del circuito di rettifica SQL100A e della taratura del Buck Step-Down.
- [ ] Test di avviamento e verifica termica del generatore sotto carico continuo a 6500 RPM.
- [ ] Installazione e cablaggio finale sul telaio del Mulo con silent-block agli angoli della piastra.

---

*Documento generato il 2026-06-13. Riferimenti: `hardware/bom.md`, `engineering_recommendations.md` §3 e §7, `docs/mulo_mk0_gabbia_alluminio.md`.*
