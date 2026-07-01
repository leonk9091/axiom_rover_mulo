# Manuale di Lettura — Grafici Showcase Mulo MK0

Guida completa alla lettura dei 4 grafici professionali generati da `scripts/rover_simulation_showcase.py`. Ogni sezione spiega un sottografico: cosa rappresenta, come interpretarlo, e quali numeri sono importanti per il Mulo.

---

## Indice

1. [Grafico 1: PID Control](#1-pid-control)
2. [Grafico 2: Dinamica Longitudinale](#2-dinamica-longitudinale)
3. [Grafico 3: Rollio Laterale](#3-rollio-laterale)
4. [Grafico 4: NMPC CasADi](#4-nmpc-casadi)

---

## 1. PID Control

**File:** `showcase_01_pid_control.png`
**Libreria:** `python-control` (equivalente Control System Toolbox di MATLAB)
**Modello:** Motore Stepperonline 24V 200W + Riduttore Planetario 71.5:1

### 1A — Risposta al Gradino (in alto a sinistra)

**Cosa mostra:** Come risponde la velocita' del motore quando gli chiedi di passare istantaneamente da 0 a 42 RPM.

**Come leggerla:**
- **Linea rossa** = risposta in anello aperto (senza controllo). Il motore accelera lentamente e raggiunge il valore finale in ~0.8 s senza overshoot.
- **Linea verde** = risposta in anello chiuso con PID. Il motore raggiunge il target molto piu' velocemente (~0.03 s) ma con un picco iniziale (overshoot del ~27%).
- **Linee tratteggiate arancioni** = banda di tolleranza +/-10% attorno al valore target.
- **Zona verde chiara** = intervallo accettabile. Se la linea verde entra in questa zona e ci resta, il controllo funziona.

**Numeri chiave per il Mulo:**
| Parametro | Valore | Significato |
|---|---|---|
| Tempo di salita (10%-90%) | 0.030 s | Quanto tempo ci mette a raggiungere la velocita' target |
| Overshoot | 26.7% | Quanto supera il target (26.7% = arriva a ~53 RPM prima di stabilizzarsi) |
| Tempo di assestamento (2%) | 0.277 s | Quando la velocita' si stabilizza definitivamente |
| Errore a regime | 0% | L'azione integrale (Ki) garantisce errore zero |

**Interpretazione pratica:** L'overshoot del 27% significa che quando chiedi 42 RPM, il motore arriva momentaneamente a ~53 RPM. Questo e' accettabile per un motore brushless (ha margine di coppia), ma se fosse troppo alto andrebbe ridotto diminuendo Kp.

### 1B — Diagramma di Bode (in alto a destra)

**Cosa mostra:** Come il sistema in anello chiuso risponde a segnali sinusoidali di diverse frequenze. In pratica, ti dice a quali frequenze il motore riesce a "seguire" il comando e a quali no.

**Come leggerla:**
- **Asse X (logaritmico)** = frequenza del segnale di ingresso (rad/s)
- **Asse Y** = magnitudine in decibel (dB). 0 dB = il motore segue perfettamente il comando. Valori negativi = il motore non riesce a stare dietro.
- **Linea verde** = curva di risposta in frequenza del sistema chiuso
- **Linea rossa tratteggiata** = soglia -3 dB (dove la risposta cala al 70.7%)
- **Freccia arancione** = punto in cui la curva incrocia i -3 dB = **banda passante**

**Cos'e' la banda passante:** E' la massima frequenza a cui il motore riesce a seguire un comando variabile. Per il Mulo e' ~11.7 Hz, il che significa che il motore riesce a reagire a variazioni di comando fino a 11.7 volte al secondo. Oltre questa frequenza, il motore "filtra" il comando (non riesce a stare dietro).

**Perche' conta:** A 4 km/h su sentiero, le variazioni di carico (sassi, pendenze) hanno frequenze tipiche di 1-5 Hz. Con una banda di 11.7 Hz, il PID ha margine ampio per reagire in tempo reale.

### 1C — Mappa Poli-Zeri (in basso a sinistra)

**Cosa mostra:** La posizione dei poli e degli zeri del sistema nel piano complesso. E' lo strumento piu' potente per valutare la stabilita' con un colpo d'occhio.

**Come leggerla:**
- **Asse X** = parte reale del numero complesso
- **Asse Y** = parte immaginaria
- **X rosse** = posizione dei **poli** (3 poli per il sistema PID + motore)
- **O blu vuoti** = posizione degli **zeri** (2 zeri introdotti dal PID)
- **Zona verde** (semipiano sinistro) = regione di stabilita'
- **Linea verticale grigia** = asse immaginario (confine stabilita'/instabilita')

**Regola fondamentale:**
> Un sistema e' stabile se e solo se TUTTI i poli sono nel semipiano sinistro (parte reale negativa).

**Poli del Mulo in anello chiuso:**
```
Polo 1: -17.98 + 47.50j  (coppia complessa → oscillazione smorzata veloce)
Polo 2: -17.98 - 47.50j  (coniugato del Polo 1)
Polo 3:  -4.91 +  0.00j  (polo reale → smorzamento lento senza oscillazione)
```

**Cosa significa ogni polo:**
- **Parte reale** (numero negativo): indica quanto velocemente si smorza. -17.98 significa smorzamento rapido. -4.91 significa smorzamento lento (e' il polo "dominante").
- **Parte immaginaria** (+/- 47.50): indica oscillazione. La coppia complessa significa che il motore oscilla a ~47.5 rad/s (= ~7.6 Hz) durante la risposta transitoria.
- **Polo reale** (-4.91): e' una componente lenta che non oscilla. Determina il "coda" finale della risposta.

**In pratica:** I poli sono tutti a sinistra dell'asse Y → sistema stabile. I due poli complessi (-17.98 +/- 47.50j) causano l'overshoot del 27% visto nel grafico 1A. Il polo reale (-4.91) causa la coda lenta di assestamento.

### 1D — Inseguimento Profilo di Velocita' (in basso a destra)

**Cosa mostra:** Come il motore segue un profilo di velocita' realistico con accelerazioni, rallentamenti e fermate — simulando quello che succede in un trekking reale.

**Come leggerla:**
- **Linea gialla tratteggiata** = riferimento (cosa chiedi al motore)
- **Linea verde** = velocita' reale del motore
- **Zona rossa** = overshoot (il motore va piu' veloce del richiesto)
- **Zona blu** = undershoot (il motore va piu' lento del richiesto)

**Scenario simulato:**
1. **0-0.3 s:** fermo (0 RPM)
2. **0.3-2.0 s:** accelerazione a 42 RPM (velocita' massima)
3. **2.0-3.5 s:** rallentamento a 21 RPM (ostacolo/pendenza)
4. **3.5-5.0 s:** ritorno a 42 RPM
5. **5.0-6.0 s:** decelerazione a 0 (stop)

**Interpretazione:** Le zone colorate mostrano l'errore di inseguimento. Zone piccole = buon controllo. Zone grandi = il motore fatica a stare dietro al comando. Per il Mulo, questo grafico dimostra che il PID riesce a gestire transizioni rapide di velocita' senza perdere il controllo.

---

## 2. Dinamica Longitudinale

**File:** `showcase_02_longitudinal_dynamics.png`
**Libreria:** `scipy.integrate.solve_ivp` (equivalente ode45 di MATLAB)
**Modello:** Sistema massa-molla-smorzatore a 2 gradi di liberta' (2 DOF)

### 2A — Profilo del Sentiero (in alto a sinistra)

**Cosa mostra:** L'altezza del terreno lungo il percorso del rover. Il modello combina 3 componenti per simulare un sentiero alpino realistico.

**Come leggerla:**
- **Asse X** = distanza percorsa in metri
- **Asse Y** = altezza del terreno in millimetri
- **Zona marrone** = profilo del sentiero

**Le 3 componenti del sentiero:**

| Componente | Ampiezza | Lunghezza d'onda | Cosa simula |
|---|---|---|---|
| Ghiaia fine | 20 mm | 10 cm | Pietrisco e ghiaia sciolta |
| Sassi medi | 50 mm | 40 cm | Radici, sassi sporgenti |
| Ondulazione | 80 mm | 200 cm | Avvallamenti e dossi del terreno |

**Interpretazione:** Il profilo non e' casuale — e' una sovrapposizione di sinusoidi a diverse frequenze. Questo permette di analizzare quali frequenze vengono filtrate dalla sospensione (silent-block + pneumatico) e quali arrivano ai sensori.

### 2B — Risposta Verticale (in alto a destra)

**Cosa mostra:** Come si muovono verticalmente la strada, la ruota e il telaio mentre il rover percorre il sentiero. Mostra l'effetto filtro della sospensione.

**Come leggerla:**
- **Linea marrone** = altezza della strada (stesso profilo del grafico 2A)
- **Linea arancione** = posizione della ruota (massa non sospesa)
- **Linea blu** = posizione del telaio (massa sospesa — dove sono i sensori)
- **Zona blu chiara** = differenza tra telaio e strada

**Cosa osservare:**
- La ruota (arancione) segue da vicino il profilo strada (marrone) — perche' il pneumatico a 1.2 bar e' molto morbido
- Il telaio (blu) ha un movimento molto piu' liscio — il silent-block M10 filtra le vibrazioni
- La distanza tra le due linee (zona blu) e' la compressione/estensione del silent-block

**Interpretazione pratica:** Se la linea blu fosse identica alla marrone, la sospensione non funzionerebbe. Il fatto che sia molto piu' "piatta" dimostra che il sistema gomma + silent-block assorbe efficacemente le asperita'.

### 2C — Accelerazioni sui Sensori (in basso a sinistra)

**Cosa mostra:** Le accelerazioni verticali (in unita' G) trasmesse al telaio — cioe' quelle che subiscono Jetson, IMU, LiDAR e telecamere.

**Come leggerla:**
- **Linea verde** = accelerazione istantanea
- **Linea rossa tratteggiata** = valore RMS (Root Mean Square — energia media delle vibrazioni)
- **Linea arancione tratteggiata** = picco massimo
- **Zona verde chiara** = intervallo di sicurezza (< 0.5 G)

**Numeri chiave:**
| Parametro | Valore | Implicazione |
|---|---|---|
| RMS | ~3.4 G | Le vibrazioni medie sono elevate — servono sensori robusti |
| Max | ~8.7 G | I picchi sono molto alti — il silent-block potrebbe essere troppo rigido |

**Attenzione:** Questi valori sono alti per sensori delicati. Nella pratica:
- L'IMU BNO085 e il LiDAR hanno specifiche di resistenza alle vibrazioni tipicamente > 10 G
- La Jetson e' robusta ma va montata su supporti antivibranti
- Se i valori fossero troppo alti, bisognerebbe ammorbidire il silent-block o aggiungere un secondo stadio di isolamento

### 2D — Deformazione Silent-Block (in basso a destra)

**Cosa mostra:** Quanto si comprime/estende il silent-block M10 durante la marcia. E' la differenza di posizione tra il telaio e la ruota.

**Come leggerla:**
- **Linea viola** = deformazione in millimetri
- **Zona verde** = compressione (il silent-block si schiaccia)
- **Zona rossa** = estensione (il silent-block si allunga)
- **Linee arancioni tratteggiate** = limite consigliato (+/- 3 mm)

**Interpretazione:**
- Se la deformazione resta entro +/- 3 mm, il silent-block lavora nel suo range lineare (comportamento prevedibile)
- Se supera i 3 mm, entra in non-linearita' (la gomma si irrigidisce) e il filtraggio peggiora
- Deformazioni > 5 mm indicano che il silent-block e' sottodimensionato per quel terreno

**Per il Mulo:** Con k_silent = 200 kN/m (rigidezza tipica di un silent-block M10 in gomma dura), le deformazioni sono contenute — il che conferma che il silent-block e' adeguato per la micro-sospensione.

---

## 3. Rollio Laterale

**File:** `showcase_03_roll_dynamics.png`
**Libreria:** `scipy.integrate.odeint` (equivalente ode45 di MATLAB)
**Modello:** Dinamica del rollio con snodo centrale articolato non lineare

### 3A — Pendenza Terreno vs Rollio Telaio (in alto a sinistra)

**Cosa mostra:** Come si inclina il rover quando percorre una traversa con pendenza crescente da 0° a 25°.

**Come leggerla:**
- **Linea marrone** = pendenza del terreno (cresce linearmente da 0° a 25° in 10 secondi, poi resta costante)
- **Linea blu** = angolo di rollio effettivo del telaio
- **Linea rossa tratteggiata** = angolo limite di ribaltamento (38.4° per il Mulo con CoG a 37.8 cm e carreggiata 60 cm)
- **Zona rossa** = zona di ribaltamento (oltre il limite)

**Cosa osservare:**
- Il telaio (blu) si inclina MENO del terreno (marrone) — lo snodo centrale articolato permette ai due semitelai di adattarsi alla pendenza senza inclinare tutto il telaio
- Il rollio massimo raggiunto e' ~12.3° anche con pendenza terreno di 25° — c'e' un ampio margine di sicurezza
- La differenza tra le due curve e' il "vantaggio" dello snodo centrale

**Numeri chiave:**
| Parametro | Valore | Significato |
|---|---|---|
| Pendenza massima terreno | 25° | Scenario di traversa ripida |
| Rollio massimo telaio | 12.3° | Inclinazione reale del telaio |
| Angolo limite ribaltamento | 38.4° | Limite teorico (W=60cm, CoG=37.8cm) |
| Margine di sicurezza | 38.4° - 12.3° = 26.1° | Quanto margine resta prima del ribaltamento |

### 3B — Margine di Stabilita' (in alto a destra)

**Cosa mostra:** La distanza orizzontale tra il baricentro (CoG) e la ruota a valle. Quando questa distanza arriva a zero, il rover si ribalta.

**Come leggerla:**
- **Linea verde** = distanza CoG-ruota in millimetri
- **Linea rossa continua** = soglia di ribaltamento (d=0)
- **Linea grigia tratteggiata** = posizione dell'asse centrale (d = W/2 = 300 mm)
- **Zona verde** = rover stabile (CoG sopra il poligono di appoggio)
- **Zona rossa** = rover ribaltato (CoG fuori dal poligono)

**Formula:** `d = W/2 - h_CoG * tan(theta)` dove theta e' l'angolo di rollio.

**Interpretazione:**
- d = 300 mm → rover perfettamente orizzontale (CoG centrato)
- d = 0 mm → il CoG e' esattamente sopra la ruota a valle (istante prima del ribaltamento)
- d < 0 mm → il CoG e' oltre la ruota → ribaltamento

**Per il Mulo:** Il margine minimo durante la traversa a 25° resta positivo → il rover non si ribalta.

### 3C — Coppia di Richiamo Snodo Centrale (in basso a sinistra)

**Cosa mostra:** La coppia esercitata dallo snodo centrale articolato per contrastare il rollio. Lo snodo funziona come una molla torsionale che si oppone alla rotazione tra i due semitelai.

**Come leggerla:**
- **Linea arancione** = coppia dello snodo in N*m
- **Linee rosa** = punto di saturazione (+/- 15°)
- **Zona verde** = coppia positiva (contrasta il rollio)
- **Zona rossa** = coppia negativa (amplifica il rollio — da evitare)

**Comportamento dello snodo:**
1. **Fino a 15°** di torsione: lo snodo si comporta come una molla (tau = -k_snodo * theta)
2. **Oltre 15°**: va in battuta meccanica (la coppia aumenta 10x) — questo e' il limite fisico dei tamponi in poliuretano

**Interpretazione:** Lo snodo "aiuta" a limitare il rollio assorbendo energia torsionale. Se la coppia supera il limite di battuta, il sistema diventa piu' rigido e il rollio si trasferisce integralmente al telaio.

### 3D — Ritratto di Fase (in basso a destra)

**Cosa mostra:** L'evoluzione del sistema nel piano angolo-velocita'. E' uno strumento matematico avanzato che mostra la "traiettoria" del sistema nello spazio degli stati.

**Come leggerla:**
- **Asse X** = angolo di rollio (gradi)
- **Asse Y** = velocita' angolare di rollio (gradi/s)
- **Linea viola** = traiettoria del sistema nel tempo
- **Cerchio verde** = stato iniziale (angolo=0, velocita'=0)
- **Quadrato rosso** = stato finale

**Come interpretarlo:**
- Se la traiettoria forma una **spirale che converge verso un punto** → il sistema e' stabile e si assesta
- Se la traiettoria **si allontana dal centro** → il sistema diverge (instabile)
- Se la traiettoria forma un **cerchio chiuso** → oscillazione perpetua (marginalmente stabile)

**Per il Mulo:** La spirale converge verso un punto fisso → il rover si stabilizza sulla traversa e non oscilla indefinitamente. Questo e' il comportamento desiderato.

---

## 4. NMPC CasADi

**File:** `showcase_04_nmpc_casadi.png`
**Libreria:** `CasADi` con risolutore `IPOPT`
**Modello:** Controllo Predittivo Non Lineare (NMPC) con modello cinematico del veicolo

### Cos'e' l'NMPC?

L'NMPC (Nonlinear Model Predictive Control) e' un algoritmo di controllo avanzato che:
1. Prevede il comportamento futuro del rover per i prossimi N step (orizzonte di predizione)
2. Calcola la sequenza ottimale di coppie per ogni ruota
3. Applica solo il primo controllo, poi ricalcola
4. Ripete ad ogni step (controllo a orizzonte scorrevole)

E' il tipo di controllo suggerito nelle engineering recommendations del Mulo per sostituire il PID semplice.

### 4A — Traiettoria X-Y (in alto a sinistra)

**Cosa mostra:** Il percorso del rover nel piano orizzontale. Dove va effettivamente vs dove dovrebbe andare.

**Come leggerla:**
- **Linea rossa tratteggiata** = traiettoria di riferimento (il percorso ideale)
- **Linea verde** = traiettoria effettiva calcolata dall'NMPC
- **Punti gialli** = posizioni del rover a intervalli regolari

**Scenario:**
1. **Dritto** (primi 4 secondi): il rover avanza in linea retta
2. **Curva a destra** (4-8 secondi): il rover curva dolcemente
3. **Dritto** (8-12 secondi): il rover riprende la marcia rettilinea

**Interpretazione:**
- Se la linea verde segue da vicino la rossa → l'NMPC funziona bene
- Deviazioni grandi → il controllore non riesce a compensare i vincoli
- La distanza tra le due linee e' l'**errore di inseguimento**

### 4B — Velocita' Longitudinale (in alto a destra)

**Cosa mostra:** La velocita' del rover nel tempo, confrontata con il limite imposto.

**Come leggerla:**
- **Linea verde** = velocita' effettiva (km/h)
- **Linea rossa tratteggiata** = limite massimo (4.0 km/h = velocita' del passo umano)
- **Zona verde chiara** = area sotto la curva (energia cinetica)

**Cosa osservare:**
- L'NMPC mantiene la velocita' entro il limite anche durante le transizioni
- Le piccole oscillazioni sono normali — l'NMPC fa "micro-correzioni" ad ogni step
- Se la velocita' scende sotto il target, significa che il controllore sta dando priorita' al seguire la traiettoria piuttosto che mantenere la velocita'

### 4C — Coppia Motori 4WD (in basso a sinistra)

**Cosa mostra:** La coppia erogata da ciascuno dei 4 motori nel tempo. E' il risultato piu' importante dell'NMPC.

**Come leggerla:**
- **4 linee colorate** = coppia di ogni ruota (FL, FR, RL, RR)
- **Linee rosse tratteggiate** = limiti fisici (+/- 33 Nm per motore)
- **Zona grigia** = intervallo di lavoro accettabile

**Cosa osservare:**
- **In rettilineo**: tutte e 4 le ruote erogano circa la stessa coppia (trazione simmetrica)
- **In curva**: le ruote interne ed esterne erogano coppie diverse — il differenziale di coppia genera la sterzata (skid-steer)
- Se qualche linea tocca il limite rosso → quel motore e' saturato (non puo' dare di piu')

**Per il Mulo:** L'NMPC distribuisce la coppia in modo da:
1. Minimizzare l'errore di traiettoria
2. Minimizzare il consumo energetico
3. Rispettare i limiti di 33 Nm per motore

### 4D — Orientamento Rover (in basso a destra)

**Cosa mostra:** L'angolo di heading del rover — cioe' in che direzione punta il muso del rover.

**Come leggerla:**
- **Linea viola** = angolo di orientamento (gradi)
- **Zona verde** = curva a destra (angolo positivo)
- **Zona rossa** = curva a sinistra (angolo negativo)
- **Linea grigia** = riferimento zero (marcia rettilinea)

**Interpretazione:**
- In rettilineo: l'angolo resta vicino a 0°
- Durante la curva (4-8 s): l'angolo cresce gradualmente mentre il rover sterza
- Dopo la curva: l'angolo si stabilizza al nuovo valore

**Perche' conta:** L'angolo di heading e' fondamentale per la navigazione. Se l'NMPC non controllasse bene l'orientamento, il rover devierebbe dalla traiettoria anche con la velocita' giusta.

---

## Legenda Colori (Comune a Tutti i Grafici)

| Colore | Significato |
|---|---|
| 🟢 Verde | Valore positivo, zona sicura, riferimento |
| 🔵 Blu | Dato principale, traiettoria, misura |
| 🔴 Rosso | Limite, pericolo, errore, zona critica |
| 🟠 Arancione | Avviso, soglia, banda passante |
| 🟡 Giallo | Annotazioni, riferimenti secondari |
| 🟣 Viola | Dati derivati, fase, coppia |
| ⬜ Grigio | Assi, griglie, riferimento zero |

---

## Come Rigenerare i Grafici

```bash
set PYTHONIOENCODING=utf-8 && python scripts/rover_simulation_showcase.py
```

I 4 file PNG vengono salvati nella root del progetto:
- `showcase_01_pid_control.png`
- `showcase_02_longitudinal_dynamics.png`
- `showcase_03_roll_dynamics.png`
- `showcase_04_nmpc_casadi.png`

---

## Dipendenze Richieste

```bash
pip install numpy scipy matplotlib control casadi sympy jupyter
```

Tutte installate tramite `scripts/requirements_simulation.txt`.