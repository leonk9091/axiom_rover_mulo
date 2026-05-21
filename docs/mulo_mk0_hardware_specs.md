# Specifiche Meccaniche e Strutturali: Axiom Rover "Mulo" - MK0

Questo documento raccoglie, analizza e integra tutti i dati relativi alla struttura, ai motori, ai riduttori e al drivetrain custom del rover da trekking **Axiom Rover "Mulo" - MK0**, giustificando le scelte ingegneristiche in ottica di affidabilità reale e manutenibilità.

Il modello MK0 non va inteso come configurazione "low cost": e' una piattaforma **value-engineered**, cioe' progettata per spendere dove il guadagno tecnico e' reale. Le priorita' sono inseguimento affidabile dell'operatore, carico utile, robustezza strutturale, dissipazione termica, frenata sicura e manutenzione semplice.

---

## 1. Schema Strutturale e Layout Meccanico

Il telaio è progettato secondo una filosofia **articolata 4WD**, composta da due semitelai (anteriore e posteriore) connessi da uno snodo di torsione centrale. Questa architettura garantisce che tutte e 4 le ruote rimangano sempre a contatto con il terreno accidentato, massimizzando la trazione.

```mermaid
classDiagram
    class Telaio_S235 {
        +Profilo: Tubolare 30x30x2 mm
        +Controventature: Piatto 20x3 mm
        +Snodo Central: Albero 20 mm
        +Cuscinetti Snodo: 2x UCP204
        +Carico Nominale: 130 kg
    }
    class Ponte_Corazzato {
        +Piastra di Rinforzo: Acciaio 6 mm
        +Cuscinetto Radiale: Flangiato UCF204
        +Albero Custom: Acciaio 42CrMo4
        +Isolamento Carico: 100% delle forze di taglio esterne
    }
    class Motorizzazione {
        +Motore: 4x Stepperonline Brushless 200W
        +Riduttore: Planetario Integrato 71.5:1
        +Albero Uscita: 19 mm con chiavetta (DIN 6885A)
        +Velocità Nominale: 42 RPM (4.03 km/h)
        +Coppia Nominale: 33 Nm per ruota
        +Coppia Totale: 132 Nm
    }
    class Drivetrain_Ruota {
        +Ruota: Cargo E-bike 20"
        +Mozzo: Standard 6 fori IS (33-36mm)
        +Freni Meccanici: 4x Pinze Avid BB7
        +Dischi Freno: 203 mm
    }

    Telaio_S235 --> Central_Joint : Connessione Articolata
    Telaio_S235 --> Ponte_Corazzato : Fissaggio Rigido
    Ponte_Corazzato --> Motorizzazione : Allineamento Albero
    Ponte_Corazzato --> Drivetrain_Ruota : Trasmissione Coppia
```

---

## 2. Analisi Comparativa del Materiale del Telaio: Acciaio S235 vs Alluminio 6061-T6

Per un vero veicolo da trekking off-road sottoposto a sollecitazioni cicliche gravose (urti contro rocce, vibrazioni costanti su pietrisco, carico statico di 130 kg + spinta del verricello), la scelta del materiale è critica.

| Proprietà Ingegneristica | Acciaio S235JR (Scelta Eletta) | Alluminio 6061-T6 | Impatto sul Rover |
| :--- | :--- | :--- | :--- |
| **Limite di Fatica** | **Definito.** Sotto una certa sollecitazione, resiste a infiniti cicli senza rompersi. | **Assente.** Si romperà inevitabilmente per fatica dopo un certo numero di cicli, anche a bassi carichi. | Le vibrazioni costanti del sentiero creano micro-cricche nell'alluminio. L'acciaio dura indefinitamente. |
| **Saldabilità in Officina** | **Eccellente.** Saldabile con elettrodo, MIG o TIG senza alcun pre/post riscaldamento. | **Complessa.** La saldatura riduce la resistenza della giunzione fino al 50% (diventa ricotto 6061-O). | L'alluminio saldato richiede un trattamento termico in un forno industriale a 170°C per recuperare le proprietà (T6), impossibile in un'officina comune. |
| **Riparabilità sul Campo** | **Massima.** Qualsiasi fabbro di montagna o officina di paese può riparare un giunto rotto in 5 minuti. | **Quasi nulla.** Richiede saldatrici AC-TIG specifiche e personale altamente specializzato. | Fondamentale durante trekking remoti. |
| **Modulo Elastico (Rigidezza)** | **~210 GPa.** Molto rigido, flessioni strutturali minime sotto carico. | **~70 GPa.** Tre volte più flessibile dell'acciaio. Richiede spessori maggiori. | L'alluminio tenderebbe a flettere sul giunto di torsione centrale, ovalizzando le sedi dei cuscinetti. |
| **Resistenza a Usura e Sforzo** | **Elevata.** Ideale per bullonatura diretta di cuscinetti pesanti (UCF204). | **Bassa.** I fori filettati tendono a spanarsi se sottoposti a vibrazioni alternate. | I cuscinetti UCP204 dello snodo centrale scaricano forze imponenti direttamente sulle pareti del telaio. |

**Verdetto Ingegneristico:** Il **tubolare d'acciaio S235 da 30x30x2 mm** è la scelta ottimale. L'alluminio comporterebbe rischi inaccettabili di cricche da fatica nelle giunzioni saldate e richiederebbe lavorazioni industriali post-saldatura estremamente costose.

---

## 3. Il "Ponte Corazzato": Dettaglio Tecnico e Drivetrain Custom

I motori elettrici ridotti soffrono enormemente i carichi radiali (il peso del rover che spinge perpendicolarmente sull'albero). Se calettassimo le ruote direttamente sull'albero da 14 mm del riduttore, i cuscinetti interni del motore si distruggerebbero in poche ore di cammino.

Per risolvere questo problema, l'MK0 adotta il **design a "Ponte Corazzato" (Sandwich Layout)**:

```
                  [ TELAIO INTERNO ]          [ TELAIO ESTERNO ]
                          |                           |
   [ Motore ]=======[Piastra Acciaio]==============[Cuscinetto]=======[ Ruota ]
   Stepperonline        da 6 mm                     UCF204            Cargo 20"
   (Supportato)           |                           |               (Carico)
                          |====== Albero Custom ======|
                                Acciaio 42CrMo4
```

### Componenti del Sandwich:
1.  **Motore (Interno):** Stepperonline 24V 200W con riduttore planetario 71.5:1. È imbullonato sul lato interno della piastra di rinforzo da 6 mm. L'albero motore non tocca la ruota direttamente.
2.  **Piastra di Rinforzo (Mezzeria):** Lastra di acciaio S235 da 6 mm di spessore, saldata e imbullonata direttamente al tubolare 30x30 del telaio. Funge da barriera strutturale.
3.  **Cuscinetto UCF204 (Esterno):** Cuscinetto flangiato autoallineante a 4 fori, imbullonato sul lato esterno della piastra da 6 mm. Sopporta il 100% delle forze radiali e flettenti esercitate dalla ruota.
4.  **Albero Custom di Prolunga (Materiale: Acciaio bonificato 42CrMo4):**
    *   *Lato Motore:* Foro cieco da 19 mm rettificato con cava chiavetta (DIN 6885A) per accoppiarsi all'uscita del riduttore.
    *   *Sezione Centrale:* Diametro 20 mm a tolleranza ristretta `h6` per alloggiare perfettamente nella pista interna del cuscinetto UCF204.
    *   *Lato Ruota:* Flangia circolare integrata per l'accoppiamento con il mozzo a 6 fori standard ISO della ruota Cargo da 20".

*Risultato:* Le forze d'urto del terreno vengono trasferite dalla ruota all'albero custom, da questo al cuscinetto UCF204, e infine scaricate direttamente sul telaio in acciaio. **Il riduttore del motore riceve solo e soltanto la coppia pura di torsione**, azzerando il rischio di rotture meccaniche interne.

*   **Manutenibilità e Sblocco d'Emergenza (Limp-Home meccanico):** Il principale capolavoro ingegneristico di questo layout risiede nella separazione fisica tra il supporto della ruota (esterno) e il motore (interno). Se un riduttore planetario dovesse subire un catastrofico blocco meccanico interno (es. rottura dei satelliti o grippaggio degli ingranaggi), nei sistemi tradizionali a calettamento diretto la ruota rimarrebbe completamente bloccata, rendendo impossibile il traino. Nel Mulo, è sufficiente svitare i 4 bulloni flangiati del motore dal lato *interno* del telaio e sfilare il motore verso l'interno dello chassis. L'albero motore si scollega dall'albero custom e la ruota, supportata autonomamente dal cuscinetto esterno UCF204, **rimane saldamente in sede e diventa istantaneamente folle al 100%**, permettendo al rover di essere trainato o di continuare la marcia su 3 ruote con attrito nullo.

### 3.1 Protocollo Operativo di Decoupling sul Campo (Limp-Home Manuale)

In caso di guasto meccanico irreversibile a uno dei motori o riduttori durante un trekking, l'operatore può eseguire l'isolamento fisico dell'asse danneggiato in meno di 2 minuti seguendo questa procedura:

1.  **Messa in Sicurezza ed E-Stop:** Arrestare il rover premendo il fungo di emergenza (E-stop) o spegnendo l'interruttore generale del bus DC per togliere tensione a tutti i driver VESC.
2.  **Isolamento Elettrico:** Scollegare il connettore rapido stagno IP68 (cavi di fase + sensori di Hall) del motore guasto. Questo protegge l'elettronica da eventuali correnti indotte (effetto dinamo) se il motore dovesse girare a vuoto durante il traino manuale prima dello smontaggio completo.
3.  **Rimozione Viti di Fissaggio:** Utilizzando una singola chiave esagonale maschio da 5 mm (inclusa nel kit attrezzi di bordo del Mulo), svitare le **4x viti a brugola M6** che flangiano la carcassa del riduttore planetario al lato interno della piastra in acciaio da 6 mm.
4.  **Sfilamento del Motore:** Tirare delicatamente il corpo motore verso l'interno dello chassis. L'albero di uscita da 14 mm del riduttore sfilerà agevolmente dalla sede femmina dell'albero custom in 42CrMo4, lasciando libera la chiavetta DIN 6885A.
5.  **Stoccaggio di Sicurezza:** Riporre il motore danneggiato nel vano bagagli centrale del rover o, se non è possibile, assicurarlo provvisoriamente al telaio tubolare tramite due fascette riutilizzabili in velcro ad alta resistenza per evitare che penda o si danneggi.
6.  **Ripristino Funzionalità:** Riattivare l'interruttore generale. Il firmware rileverà l'assenza del VESC escluso e passerà automaticamente alla modalità di guida degradata (3WD).

### 3.2 Gestione Software della Trazione Asimmetrica (3WD Degraded Mode)

La perdita di una ruota motrice introduce una forte asimmetria nella dinamica del veicolo. Se i tre motori superstiti continuassero a erogare coppia in modo simmetrico, il rover devierebbe inesorabilmente verso il lato della ruota folle (effetto imbardata parassita). Per compensare questo fenomeno, il firmware dell'ESP32-S3 implementa una logica di controllo dedicata:

```
                  [ RUOTA INTEGRATA ]          [ RUOTA INTEGRATA ]
                     (Trazione: 100%)             (Trazione: 100%)
                            \                             /
                             \                           /
                              +--- [ TELAIO ARTICOLATO ] +
                             /                           \
                            /                             \
                 [ RUOTA FOLLE (GUASTA) ]      [ RUOTA INTEGRATA ]
                     (Trazione: 0%)               (Trazione: Compensata)
```

1.  **Rilevamento e Diagnostica del Guasto:**
    *   Il VESC associato al motore guasto smette di comunicare sul bus CAN (generando un timeout) oppure invia un frame di fault persistente (es. `FAULT_CODE_DRV_8302`, `FAULT_CODE_OVER_CURRENT` o `FAULT_CODE_SENSORLESS_STALL`).
    *   L'ESP32-S3 transisce immediatamente lo stato globale a `DEGRADED`, limitando la velocità massima di avanzamento a **v_max = 1.5 km/h** (0.42 m/s) e la corrente massima erogabile dai motori al 50% del valore nominale per evitare surriscaldamenti.
2.  **Compensazione Attiva dell'Imbardata (Active Yaw Control):**
    *   Il firmware acquisisce ad alta frequenza (100 Hz) la velocità angolare di imbardata `ω_z` (yaw rate) dall'IMU di bordo (BNO085).
    *   Viene calcolato l'errore tra l'imbardata reale e quella richiesta dal comando di sterzo dell'operatore: `e_yaw = ω_z_target - ω_z_real`.
    *   Un regolatore PID dedicato genera un offset di coppia correttivo `ΔT`. Questa coppia di compensazione viene sommata al motore singolo sul lato "danneggiato" e sottratta (o invertita) sui due motori del lato "sano" per generare un momento contro-imbardata che stabilizza la traiettoria rettilinea.
    *   *Limitatore Anti-Slittamento:* Se la ruota singola superstite del lato danneggiato inizia a slittare a causa del sovraccarico, il controllo di trazione (TCS) riduce istantaneamente la coppia prima che si perda stabilità direzionale.
3.  **Comportamento in Curva:**
    *   La sterzata skid-steer con sole 3 ruote motrici è asimmetrica. Il raggio di curvatura minimo verso il lato danneggiato sarà maggiore rispetto a quello verso il lato sano. Il firmware adatta dinamicamente i coefficienti di miscelazione (mixing rate) tra sterzo e trazione per garantire una risposta fluida e prevedibile ai comandi dell'operatore.

---

## 4. Dati di Trazione e Calcoli Prestazionali

I dati raccolti sui motori **Stepperonline 24V 200W (con riduttore planetario 71.5:1)** rivelano prestazioni ideali per l'off-road pesante:

*   **Velocità Nominale all'albero ridotto:** **42 RPM**
*   **Velocità di Avanzamento:** Con ruote Fat-bike da 20" (diametro effettivo circa D = 0.51 m):
    
    v = RPM × π × D × (60 / 1000) ≈ 42 × 3.1416 × 0.51 × 0.06 ≈ 4.03 km/h
    
    Questa velocità coincide perfettamente con la **velocità naturale del passo umano** (trekking a piedi su sentiero).
*   **Coppia Nominale Continuativa:** **33 Nm** per singola ruota.
*   **Coppia Totale (4WD):** **132 Nm** totali scaricati a terra.
*   **Forza di Spinta Lineare Totale (Fs):**
    
    Fs = Coppia Totale / Raggio Ruota = 132 Nm / 0.255 m ≈ 517.6 N ≈ 53 kg di spinta netta.
    
    *Nota:* Una spinta lineare di oltre 500 N consente al rover di 130 kg di arrampicarsi su pendenze superiori al **35% (circa 20°)** su terreno a bassa aderenza, spingendosi ben oltre il requisito nominale del 15%.

---

## 5. Dimensionamento Termico e Dissipazione

La prestazione reale del rover non dipende solo dalla coppia nominale: in trekking il caso critico e' spesso **bassa velocita' + alta coppia + poca ventilazione**, oppure discesa lunga con rigenerazione limitata. Il dimensionamento MK0 deve quindi prevedere margine termico fin dall'inizio.

### Componenti da Sovradimensionare

1.  **Controller VESC:** scegliere modelli con corrente continua realmente compatibile con il carico, non solo corrente di picco. Montarli su dissipatore metallico collegato al telaio, con sensore temperatura e spazio per ventilazione protetta.
2.  **Motori e Riduttori:** verificare temperatura carcassa durante salita lenta a pieno carico. Se superano soglie conservative, introdurre derating automatico e rapporti/ruote coerenti con il passo umano.
3.  **Batteria e BMS:** il pacco batteria deve supportare corrente continua, picchi di trazione e rigenerazione. Il BMS deve misurare temperatura celle e poter interrompere il sistema in modo prevedibile.
4.  **Dump Load:** la resistenza di frenatura va montata su supporto dissipante, lontano da plastica, cablaggi e pacco batteria. Deve essere dimensionata per discese prolungate con batteria gia' carica.
5.  **Cablaggio di Potenza:** sezioni cavo, capicorda, fusibili e connettori devono essere scelti per corrente continua e vibrazioni, non per test statici da banco.

### Logica di Protezione Consigliata

- Derating progressivo sopra la temperatura nominale di VESC, motori o batteria.
- Arresto controllato su sovratemperatura critica, sovracorrente persistente o perdita comunicazione CAN.
- Logging di corrente, tensione, temperatura e fault VESC per manutenzione predittiva.
- Test termico obbligatorio con carico reale, salita lenta, discesa rigenerativa e stop-and-go su terreno irregolare.

---

## 6. Sistema Frenante di Sicurezza

Un rover pesante 130 kg operante in discesa di montagna non può affidarsi solo alla frenata elettrica. In caso di mancanza di alimentazione, il rover deve arrestarsi e bloccarsi autonomamente.

1.  **Frenata Elettrica Dinamica:** Gestita dai driver VESC tramite frenata rigenerativa. L'energia generata viene scaricata sulla batteria o dissipata in calore su una resistenza di frenatura (**Dump Load**) per evitare sovratensioni sui driver quando la batteria è carica al 100%.
2.  **Frenata Meccanica di Stazionamento e Sicurezza:**
    *   **Attuatori:** 4x Dischi freno da **203 mm** montati direttamente sulle flange degli alberi ruota custom.
    *   **Pinze:** Pinze meccaniche a doppio pistone **Avid BB7 MTN** (famose per l'affidabilità estrema in MTB e la facilità di regolazione senza attrezzi).
    *   **Controllo:** Sistema a cavo metallico (Bowden) collegato a leve manuali dotate di cricchetto di bloccaggio (pulsante di stazionamento, stile freno a mano motociclistico). Il rover può essere bloccato in sicurezza su qualsiasi pendenza, anche a batteria totalmente scarica.

---

## 7. Architettura Ibrida in Serie (Range Extender)

Per consentire trekking di lunga durata in scenari montani isolati, superando i limiti di peso e autonomia delle sole batterie al litio, l'Axiom MK0 integra un sistema **Range Extender ibrido in serie**.

### Specifiche Tecniche del Gruppo Elettrogeno
*   **Tipo:** Generatore compatto a benzina con tecnologia Inverter.
*   **Peso:** 12 kg (a secco).
*   **Potenza Costante:** 1000 W (alimentazione continua a 230V AC).
*   **Potenza di Picco:** 1200 W (durata massima 10 secondi).
*   **Rumorosità:** circa 52-58 dB a 7 metri (silenzioso, ideale per rispetto dell'ambiente naturale).

### Configurazione Elettrica in Parallelo (Bus DC)
Il generatore a benzina non muove meccanicamente il rover. L'intera propulsione rimane elettrica (4x motori brushless + VESC). Il generatore alimenta direttamente il sistema tramite un'architettura in parallelo con la batteria primaria (funzione "tampone"):

```
[ GENERATORE INVERTER 1000W ]
             |
          (230V AC)
             v
[ CARICABATTERIE CC/CV (600-800W) ]
             |
        (Corrente DC)
             v
 [ DIODO DI BLOCCO (IDEALE) ]
             |
             +--------------------> [ BUS DC PRINCIPALE ] <----> [ BATTERIA TAMPONE LIPO ]
                                             |
                                             v
                                  [ 4x DRIVER MOTOR VESC ]
```

*   **Caricabatterie CC/CV:** Collegato alla presa 230V AC del generatore, converte l'energia in corrente continua alla tensione nominale del pacco batteria (es. 24V o 48V).
*   **Diodo di Blocco (Diodo Ideale):** Posizionato sulla linea di ricarica in serie per impedire il riflusso di corrente dalla batteria verso il caricabatterie quando il generatore è spento.
*   **Ripartizione Dinamica dei Flussi di Potenza:**
    *   *Carico Basso (Avanzamento in piano / Stazionamento):* Il generatore produce 600W. Se i motori consumano solo 200W, i restanti 400W fluiscono automaticamente nella batteria per ricaricarla.
    *   *Carico Elevato (Salita / Ostacoli):* I motori richiedono picchi di 1500W. Il generatore fornisce i suoi 1000W costanti direttamente alla linea di potenza dei VESC, mentre la batteria tampone fornisce i restanti 500W scaricandosi lentamente.

### Integrazione Meccanica e Protezione dalle Vibrazioni
*   **Posizionamento:** Montato sul semitelaio posteriore. Il peso di 12 kg funge da contrappeso per l'assale anteriore (bilanciando il verricello e la suite ToF) e mantiene stabile l'assetto longitudinale.
*   **Antivibranti (Silent-Block):** Per evitare che le vibrazioni ad alta frequenza del motore a scoppio compromettano le letture dei sensori inerziali (IMU), il generatore è isolato tramite **4x piedini ammortizzanti in gomma morbida (durezza Shore A 45)**. La scatola dell'elettronica principale è a sua volta montata su boccole di isolamento in neoprene.

---

## 8. Analisi dei Pesi Reali e Soluzioni per il Trasporto

Per pianificare correttamente la logistica dell'Axiom Rover "Mulo", abbiamo effettuato un calcolo analitico preciso della massa dei singoli componenti strutturali, meccanici ed elettrici (basandoci sulle dimensioni dei tubolari S235, delle piastre da 6 mm, degli alberi in 42CrMo4 e dei componenti commerciali selezionati).

### 8.1 Distinta dei Pesi Reali (Weight Breakdown)

1.  **Carpenteria e Telaio S235:**
    *   Tubolari 30x30x2 mm (sviluppo totale 5.0 metri × 1.76 kg/m): **8.79 kg**
    *   Controventature diagonali (piatto 20x3 mm, 2.8 metri × 0.47 kg/m): **1.32 kg**
    *   Piastre di rinforzo da 6 mm (4x piastre ruote + 2x piastre snodo): **4.13 kg**
2.  **Organi di Trasmissione e Cuscinetti:**
    *   Cuscinetti commerciali (4x UCF204 flangiati + 2x UCP204 snodo centrale): **3.80 kg**
    *   Alberi custom in acciaio bonificato 42CrMo4 (4x mozzi ruota + albero snodo): **3.11 kg**
3.  **Propulsione ed Attuazione:**
    *   Motori e riduttori (4x Stepperonline M82B200-24P-30S/G82-71.5S1 da 4.93 kg cad.): **19.72 kg**
    *   Ruote Cargo 20" complete (4x cerchio, raggi, mozzo, camera e pneumatico 20x3.0"): **13.40 kg**
    *   Impianto frenante di si4.  **Alimentazione ed Elettronica (Comuni):**
    *   Cervello elettronico (Jetson, STM32, 4x VESC, box IP65, sensori e cablaggi): **5.30 kg**
    *   Verricello elettrico custom (`rover_winch` con cavo sintetico e relè): **2.20 kg**
5.  **Masse Risultanti Finali per Configurazione (Simmetria di Peso):**
    *   **Configurazione A: Ibrido Seriale (Range Extender a benzina)**
        *   Batteria LiFePO4 24V 30Ah (720 Wh) + Box + BMS: **8.70 kg**
        *   Sotto-sistema Range Extender (Generatore 1000W dry 12.00 kg + 2 litri carburante 1.48 kg + staffe/silent-blocks 1.20 kg): **14.68 kg**
        *   **MASSA TOTALE ROVER IBRIDO PRONTO ALL'USO:** **87.98 kg**
    *   **Configurazione B: 100% Elettrico (Batteria High-Capacity)**
        *   Batteria LiFePO4 24V 100Ah (2560 Wh) + Box rinforzato + BMS: **23.00 kg**
        *   Sotto-sistema Range Extender: **ASSENTE (0.00 kg)**
        *   **MASSA TOTALE ROVER 100% ELETTRICO PRONTO ALL'USO:** **87.60 kg**

*Nota di Simmetria Ingegneristica:* Le due configurazioni pesano virtualmente lo stesso (differenza di soli 0.38 kg), permettendo all'operatore di scegliere tra l'autonomia infinita a benzina o il silenzio assoluto del 100% elettrico senza alcuna variazione di peso sul telaio.

---

### 8.2 Valutazione Critica del Trasporto sul Tettuccio dell'Auto

L'idea di trasportare il Mulo sul tettuccio dell'auto tramite barre portatutto tradizionali presenta gravi criticità ingegneristiche, ergonomiche e di sicurezza:

1.  **Limiti di Carico Dinamico dell'Auto:** La stragrande maggioranza delle vetture stradali ha un limite massimo di carico dinamico sul tetto (dichiarato dal costruttore per le barre portatutto) compreso tra **50 kg e 75 kg**. Un carico di 87.98 kg (ibrido) o 87.60 kg (elettrico) supera ampiamente questo limite di sicurezza. Durante manovre d'emergenza (frenate brusche o bruschi cambi di direzione), le forze d'inerzia esercitate sul tetto potrebbero deformare i montanti dell'auto o strappare i piedi di fissaggio delle barre.
2.  **Rischi Ergonomici e di Infortunio:** Sollevare manualmente un blocco rigido e ingombrante da oltre 87 kg ad un'altezza superiore a 1.50 metri (sopra la testa) è proibitivo e pericoloso per la salute della schiena. Il rischio di infortuni muscolari, perdita di equilibrio o scivolamento del veicolo sulle lamiere dell'auto (danneggiando carrozzeria e sensori delicati come LiDAR e telecamere) è inaccettabilmente alto.

*   **Verdetto Ingegneristico:** **La soluzione del trasporto sul tettuccio dell'auto è completamente bocciata.** Il rover deve essere movimentato tramite il sistema smontabile Quick-Split, rampe con verricello o gancio traino.

---

### 8.3 Soluzioni Approvate per la Logistica e il Trasporto

Per risolvere in sicurezza il problema del trasporto, l'architettura del Mulo MK0 integra due funzionalità native e supporta un'opzione esterna standard:

#### 1. Soluzione A: Telaio a Sgancio Rapido "Quick-Split" (Smontabilità in 2 Minuti)
Lo snodo di torsione centrale è progettato per consentire la rapida separazione fisica dei due semitelai (anteriore e posteriore):
*   **Meccanica:** L'albero di torsione da 20 mm che unisce i due semitelai è bloccato in sede da un perno passante di sicurezza con **coppiglia a scatto rapido (pull-pin)**. Rimuovendo la coppiglia, l'albero sfila agevolmente dai cuscinetti UCP204.
*   **Elettronica:** Il cablaggio passante tra i due semitelai (alimentazione del bus DC principale e bus CAN per i segnali) è interrotto da due connettori rapidi stagni **IP68 a baionetta di derivazione militare (es. serie Amphenol o connettori Anderson di potenza)**.
*   **Pesi risultanti:** Il rover viene diviso in due moduli indipendenti:
    *   *Modulo Anteriore:* **36.4 kg** (comprensivo di ruote anteriori, piastre, verricello, sterzo e suite sensori).
    *   *Modulo Posteriore:* **36.9 kg** (senza Range Extender, con batteria 30Ah) o **51.6 kg** (con Range Extender montato e batteria 30Ah). Nel caso di configurazione 100% elettrica con batteria da 100Ah, il modulo posteriore pesa **51.2 kg** (con la batteria montata nel suo alloggiamento).
    Un peso di circa 36 kg per modulo è movimentabile in sicurezza da una singola persona per caricarlo nel bagagliaio dell'auto, eliminando la necessità di sforzi eccessivi.

#### 2. Soluzione B: Auto-Caricamento con Rampe e Verricello (Zero Sforzo Fisico)
Se si desidera trasportare il rover intero all'interno di un SUV, Station Wagon o furgone senza smontarlo:
*   **Attrezzatura:** Si utilizzano **2x rampe pieghevoli leggere in alluminio** (stile rampa per moto/ATV, dal peso complessivo di 4 kg e lunghezza 1.8 metri, facilmente riponibili a lato del bagagliaio).
*   **Procedura:**
    1.  Si posizionano le rampe sul bordo del paraurti posteriore dell'auto.
    2.  Si aggancia il cavo del verricello elettrico anteriore (`rover_winch`) ad un anello di traino fisso all'interno del bagagliaio.
    3.  L'operatore, tramite radiocomando o pulsantiera, aziona il verricello. Il rover **si tira da solo su per le rampe** entrando dolcemente nel bagagliaio.
*   **Sforzo fisico richiesto:** **Zero.** Il lavoro meccanico di sollevamento è interamente svolto dal verricello a 12V alimentato dalla batteria del rover.

#### 3. Soluzione C: Porta-Moto da Gancio Traino (Trasporto Esterno Professionale)
Per chi dispone di un gancio di traino omologato sull'automobile:
*   **Struttura:** Si adotta un porta-moto leggero da gancio traino (omologato per carichi verticali fino a 120-150 kg).
*   **Vantaggi:** Il rover viene caricato intero sul supporto esterno a soli 30-40 cm da terra (sforzo di sollevamento minimo o agevolato da una piccola rampa laterale). Il bagagliaio rimane libero per l'attrezzatura da trekking e non c'è rischio di sporcare l'abitacolo con fango o residui di terra raccolti dalle ruote Fat del Mulo durante le escursioni.

---

## 9. Sistema di Alimentazione Avanzato (LiFePO4 100Ah) e Sotto-sistema di Ricarica AC/DC

Per massimizzare l'autonomia silenziosa del rover da trekking "Mulo" (Configurazione B), viene integrato un pacco batteria LiFePO4 ad alta capacità accoppiato a una suite di ricarica flessibile ed efficiente in grado di operare sia in rifugio (220V AC) sia presso le colonnine di ricarica e-bike montane.

### 9.1 La Batteria: LiFePO4 24V 100Ah
La batteria selezionata è un pacco commerciale LiFePO4 da **24V nominali (25.6V effettivi, architettura 8S)** con capacità di **100Ah (2560 Wh / 2.56 kWh)**.

#### Specifiche Principali e Analisi Costi (Mercato 2026):
*   **Capacità Energetica:** 2.56 kWh.
*   **Dimensioni Tipiche:** circa 520 × 240 × 220 mm (Layout compatto, alloggiabile nel pianale posteriore).
*   **Peso:** 20.0 kg (celle + BMS interno) + 3.0 kg (case metallico protettivo stagno IP67 con guide di fissaggio antivibranti).
*   **BMS Integrato:** Corrente di scarica continuativa di **100A** (potenza continuativa gestibile: 2560W, ideale per coprire i picchi di stallo dei 4 motori da 200W, pari a max ~1500W complessivi).
*   **Fasce di Costo sul Mercato:**
    *   *Fascia Budget (es. Eco-Worthy, Redodo, LiTime base):* **350 € – 450 €**. Celle prismatiche Grade A, molto affidabili dal punto di vista elettromeccanico, ma prive di connettività e riscaldamento.
    *   *Fascia Media "Smart" (Consigliata - es. LiTime Smart con Bluetooth e Auto-Riscaldamento):* **450 € – 650 €**. Include:
        - **Modulo Bluetooth + App Mobile:** Consente di monitorare in tempo reale lo stato di carica (SoC), la tensione delle singole celle e la temperatura della batteria direttamente dallo smartphone o integrando un dongle sulla Jetson.
        - **Auto-riscaldamento integrato:** In ambiente montano, la temperatura può scendere sotto i 0°C. Caricare una batteria al litio sotto il punto di congelamento distrugge permanentemente le celle per deposizione di litio metallico. Il sistema di riscaldamento interno consuma una frazione dell'energia di ricarica per portare le celle sopra i 5°C prima di avviare la ricarica reale.
    *   *Fascia Premium (es. Victron Energy Smart, Mastervolt):* **900 € – 1500 €+**. Massima robustezza industriale, connettività bus nativa (VE.Can / RS485) per telemetria integrata diretta in ROS 2, ma economicamente meno sostenibile.

### 9.2 Architettura di Ricarica Duale (AC 220V & DC Colonnine E-bike)
Il rover deve potersi ricaricare rapidamente in qualsiasi scenario montano. L'architettura prevede due ingressi di ricarica indipendenti collegati in parallelo sul Bus DC della batteria tramite diodi di blocco (diodi ideali):

```
                                          +---------------------------------------+
                                          |            ROVER "MULO"               |
                                          |                                       |
  [ PRESA 220V AC (RIFUGIO) ] ----------> [ CARICATORE AC-DC (Mean Well NPB-750) ] |
  (Presa Neutrik powerCON TRUE1)          |   (24V 22.5A / ~650W)                 |
                                          |          |                            |
                                          |    [ Diodo Ideale 1 ]                 |
                                          |          v                            |
  [ COLONNINA E-BIKE (PORTA DC) ] ------> [ CARICATORE DC-DC (MPPT SmartSolar)   ] | ---> [ BUS DC / BATTERIA 24V 100Ah ]
  (36V/48V DC, Rosenberger RoPD)          |   (Ingresso 30-60V -> Uscita 29.2V)   |
                                          |          |                            |
                                          |    [ Diodo Ideale 2 ]                 |
                                          |          v                            |
                                          +---------------------------------------+
```

```text
       SCHEMA DI CABLAGGIO DETTAGLIATO - SOTTO-SISTEMA DI RICARICA DUALE
       =================================================================

   [ PRESA ESTERNA AC IP68 ] (Neutrik powerCON TRUE1 TOP)
   PIN L (Linea)   --------> [ Cavo Marrone 3x1.5mm² ] -------> Ingresso AC (L) [ Mean Well NPB-750-24 ]
   PIN N (Neutro)  --------> [ Cavo Blu 3x1.5mm² ] ----------> Ingresso AC (N) [ (Caricatore AC-DC) ]
   PIN PE (Terra)  --------> [ Cavo Giallo/Verde 1.5mm² ] ----> Ingresso AC (PE)
                                    |
            [ PRESA ESTERNA DC IP69K ] (Rosenberger RoPD Magnetico - Colonnine E-bike)
    PIN + (Positivo) -------> [ Cavo AWG 10 Rosso (Silicone) ] -+
    PIN - (Negativo) -------> [ Cavo AWG 10 Nero (Silicone) ]  -+--> [ INGRESSO PV (+) ] [ Victron SmartSolar ]
                                                                |--> [ INGRESSO PV (-) ] [ MPPT 75/15 ]
    [ PRESA ESTERNA SOLAR ] (MC4 Stagna IP68 - Pannello Solare) |
    PIN + (Positivo) -------> [ Cavo AWG 10 Rosso (Silicone) ] -+
    PIN - (Negativo) -------> [ Cavo AWG 10 Nero (Silicone) ]  -+
    
    PIN Data/CAN (Opt.) ----> [ Cavo 4 poli schermato ] --------> Interfaccia VE.Direct -> [ Optoisolatore 6N137 ]
                                                                                                 |
                                                                                                 v
                                                                                            [ ESP32-S3 RX/TX ]

   [ CONNESSIONI DI POTENZA DC VERSO BATTERIA (AWG 10 SILICONE) ]
   
   Mean Well (+) --------> [ Fusibile Stagno 30A ] -------> Ingresso IN (+)  [ Diodo Ideale 1 ]
   Mean Well (-) -----------------------------------------> Ingresso GND (-) [ (MOSFET 80V 50A) ]
                                                                   |
                                                                   v
                                                             Uscita OUT (+) ----+
                                                                                |
   Victron OUT (+) ------> [ Fusibile Stagno 30A ] -------> Ingresso IN (+)     | ---> [ BARRA COLLETTRICE DC (+) ]
   Victron OUT (-) ---------------------------------------> Ingresso GND (-)    |            |
                                                                   |            |            v
                                                                   v            |      [ BMS BATTERIA (+) ]
                                                             Uscita OUT (+) ----+
   
   Mean Well (-) --------------------------------------------------------------------> [ BARRA COLLETTRICE DC (-) ]
   Victron OUT (-) ------------------------------------------------------------------>            |
                                                                                                  v
                                                                                       [ BMS BATTERIA (P-) ]
```


#### 1. Ricarica da Presa 220V AC (Rifugi e Baita)
*   **Hardware Eletto:** Alimentatore/Caricabatterie intelligente **Mean Well NPB-750-24** (750W nominali, programmabile).
*   **Caratteristiche & Dissipazione:**
    - Il Mean Well NPB-750 è programmabile tramite protocollo CAN, è fanless (convezione robusta naturale) ed eroga fino a **22.5A** di corrente a 29.2V (tensione di fine carica per LiFePO4 8S).
    - Consente di ripristinare il **65% della carica in sole 3 ore** (ideale per una pausa pranzo lunga in rifugio) o il **100% in circa 4.5 ore** durante il pernottamento.
    - *Alloggiamento e Protezione:* Il caricabatterie è alloggiato stabilmente sul fondo del telaio posteriore, all'interno di un carter di alluminio con pad termoconduttivo interposto per scaricare il calore direttamente sulla struttura metallica del rover. Il carter è isolato da vibrazioni tramite **4x silent-block in gomma Shore A 45 da 15 mm**.
*   **Connettore di Ingresso AC IP68:**
    - Per l'ingresso AC di bordo viene installato una presa da pannello flangiata **Neutrik powerCON TRUE1 TOP (NAC3MPX-WOT-TOP)**, certificata IP65/IP67 e resistente ai raggi UV.
    - Questo connettore consente il collegamento e lo scollegamento sotto carico e in presenza di forte umidità o pioggia battente. Un apposito tappo in gomma impermeabile protegge i contatti quando il rover è in movimento.

#### 2. Ricarica da Colonnine E-bike Montane (Standard E-bike DC)
Le colonnine per e-bike installate sui sentieri montani presentano due modalità di connessione:
*   **Modalità A (Prese standard 230V AC - Schuko):** Moltissime colonnine dispongono semplicemente di normali prese Schuko protette da sportelli stagni. In questo caso, l'operatore apre lo sportello, collega la spina 220V (cavo di transizione da powerCON a Schuko) del caricabatterie di bordo del Mulo e si ricarica normalmente. **Questa è la via più universale e priva di problemi di compatibilità.**
*   **Modalità B (Cavi DC diretti con connettori proprietari/universali):** Le colonnine erogano direttamente corrente continua (DC) a tensioni adatte a batterie e-bike da 36V nominali (circa 42V max) o 48V nominali (circa 54.6V max).
    - *Il Problema dei Connettori Proprietari (Bosch, Shimano):* Questi connettori effettuano un handshake digitale (CAN bus o resistivo proprietario) con il BMS originale della bici. Senza questo segnale, la colonnina non eroga tensione. Ricaricare da questi cavi è impraticabile.
    - *La Soluzione per Standard Aperti (Rosenberger / bike-energy):* Lo standard open-source diffuso in Europa (*bike-energy*) adotta connettori magnetici standard Rosenberger RoPD che erogano una tensione DC fissa (tipicamente 36V o 48V) senza necessità di protocolli chiusi.
    - *L'Integrazione Ingegneristica (Trick del Regolatore MPPT):* Per convertire in sicurezza la tensione di uscita delle colonnine (36V-54V DC) alla tensione di ricarica corretta del nostro pacco 24V (29.2V max), integriamo a bordo un **Regolatore di Carica Solare MPPT (es. Victron SmartSolar MPPT 75/15 o 100/20)**.
      I regolatori solari MPPT sono eccellenti convertitori DC-DC Buck programmabili a bassissima perdita. Collegando l'ingresso della colonnina e-bike (36V/48V) all'ingresso "PV" (pannello solare) del regolatore MPPT, questo rileva la sorgente CC stabile e la converte con efficienza superiore al 98% in una ricarica CC/CV perfetta a 29.2V per la batteria 24V del Mulo, erogando fino a 15A/20A di ricarica continua (~450W - 580W).
*   **Connettori di Ingresso DC IP68/IP69K:**
    - **Presa Colonnine E-Bike:** Viene flangiata una spina da pannello **Rosenberger RoPD flangiata IP69K** con accoppiamento magnetico a sgancio rapido.
      *Vantaggio Safety:* In caso di strattone accidentale al cavo della colonnina, il connettore Rosenberger si scollega istantaneamente per attrazione magnetica senza causare danni meccanici al rover o far cadere il mezzo da un eventuale cavalletto.
    - **Presa Solare Ausiliaria:** Viene installata una coppia di connettori **MC4 da pannello stagni IP68** protetti da tappi ermetici. Questa presa è collegata in parallelo all'ingresso PV del regolatore Victron SmartSolar MPPT, consentendo il collegamento diretto di un pannello fotovoltaico portatile durante le soste.

#### 3. Ricarica Solare da Pannello Pieghevole Portatile
Per trekking plurigiornalieri in totale autonomia ed isolamento elettrico off-grid, il rover sfrutta lo stesso regolatore **Victron SmartSolar MPPT 75/15 o 100/20** a costo zero collegando all'ingresso ausiliario MC4 un **pannello solare pieghevole portatile da 200W (Solar Blanket)**.
*   **Strategia Operativa:** Il pannello pieghevole (peso ~6.5 kg) viene stivato in sicurezza nel vano di carico protetto del rover durante la marcia (evitando graffi, fango e rotture causati da rami ed ostacoli sui sentieri). Viene dispiegato a terra o appoggiato sul rover solo durante le soste (es. pausa pranzo o campo base pomeridiano), orientandolo manualmente con l'angolazione ottimale verso il sole.
*   **Prestazioni:** Genera una potenza reale di circa **162W** netti (considerando le perdite atmosferiche e l'efficienza MPPT). Durante una sosta di 2 ore a pranzo, recupera **~325 Wh** (~12.7% di batteria); con 5 ore di esposizione al campo pomeridiano recupera **~812 Wh** (~31.7% di batteria), coprendo interamente il fabbisogno energetico giornaliero del trekking (trazione + sentinella notturna) e garantendo l'**autonomia perpetua a zero emissioni**.
*   **Efficienza MPPT Ultra-Fast:** L'algoritmo MPPT di Victron ottimizza costantemente il punto di massima potenza anche in caso di nubi passeggere o ombre parziali, incrementando la resa del 10% rispetto a regolatori tradizionali.

### 9.3 Specifiche Cablaggio e Sezioni Rame
Per minimizzare le cadute di tensione sulla linea di potenza ed evitare surriscaldamenti all'interno del telaio, i cablaggi di ricarica seguono questi rigorosi standard:
*   **Sezione Conduttori (Cavi di Potenza Ricarica):**
    - Utilizzo esclusivo di cavi con conduttori in rame rosso ultra-flessibile isolati in **silicone ad alta temperatura (soglia 200°C)**.
    - **Sezione di 6.0 mm² (pari a AWG 10)** per le tratte principali dal caricatore AC e dal MPPT fino alla batteria. A 22.5A, la densità di corrente è pari a circa 3.75 A/mm², ampiamente inferiore al limite conservativo di 5.0 A/mm² per vani non ventilati. La perdita di tensione per metro di cavo è inferiore a 0.05V.
*   **Isolamento e Canalizzazione:**
    - I cablaggi di ricarica sono inseriti in una guaina corrugata isolante in **poliammide PA12 autoestinguente**, resistente a benzina, oli e sollecitazioni meccaniche continue da schiacciamento e abrasione su roccia.

### 9.4 Sicurezza, Protezioni e Telemetria seriale
1.  **Diodi Ideali di Blocco (MOSFET 80V 50A):**
    - Per evitare correnti di ricircolo tra i due caricabatterie (AC-DC e DC-DC) e prevenire che la batteria scarichi energia verso le porte di ingresso esterne quando scollegate, ogni linea è protetta da un **Diodo Ideale** basato su MOSFET a bassissima caduta di tensione (tipicamente < 0.03V).
    - Rispetto a un diodo Schottky tradizionale che a 22A dissiperebbe oltre 17W (generando calore concentrato distruttivo), il diodo ideale dissipa meno di **0.65W**, garantendo un circuito freddo e sicuro.
2.  **Protezione Termica BMS e Riscaldamento:**
    - Se la temperatura della batteria supera i 45°C durante la ricarica rapida, il BMS interrompe autonomamente il circuito.
    - In caso di temperatura inferiore a 0°C, la logica di bordo devia la corrente di carica verso gli elementi riscaldanti resistivi (heating blanket) della batteria, attivando la ricarica reale solo al superamento della soglia di sicurezza di +5°C.
3.  **Fusibili di Linea:**
    - Ciascun ingresso di ricarica è protetto da un fusibile a lama automobilistico stagno IP67 da **30A**, alloggiato immediatamente a monte del punto di giunzione sul Bus DC principale della batteria per isolare cortocircuiti localizzati.
4.  **Telemetria Seriale VE.Direct (Opzionale):**
    - La seriale del Victron MPPT (linea VE.Direct) viene interfacciata all'ESP32-S3 tramite un optoisolatore ad alta velocità (es. **6N137**) per mantenere il totale isolamento galvanico tra la logica di controllo e le masse esterne della ricarica. Questo consente al firmware dell'ESP32-S3 di loggare continuamente su SD la tensione in ingresso della colonnina, la potenza assorbita e lo stato di carica (SoC), inviando segnali di diagnostica tempestivi.

