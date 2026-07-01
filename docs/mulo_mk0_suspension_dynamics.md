# Analisi Dinamica e Strategia Sospensiva (Mulo MK0)

Questo documento traccia i calcoli e le decisioni architetturali per garantire la stabilità del rover "Mulo" nei sentieri alpini, definendo il compromesso ottimale tra altezza del carico (ergonomia) e resistenza al ribaltamento, e stabilendo la strategia di smorzamento delle vibrazioni.

## 1. Il Compromesso Altezza vs Stabilità (Obiettivo: 55 cm)

La richiesta ergonomica principale è di alzare il pianale di carico per agevolare l'operatore durante il trekking. Tuttavia, l'ambiente montano impone vincoli dinamici severi:
- **Carreggiata Massima (W)**: 0.60 m (limite fisico dei sentieri stretti).
- **Massa Totale ($M_{tot}$)**: ~130 kg (65 kg telaio/motori, 35 kg elettronica/batterie pesanti, 30 kg payload).
- **Limite di Ribaltamento Laterale Minimo ($\alpha_{static}$)**: $38^\circ - 40^\circ$.

### Calcolo del Baricentro Massimo ($y_{CoG}$)
Per garantire una resistenza statica al ribaltamento di $40^\circ$, l'altezza del baricentro globale non deve superare i 35.7 cm:
$y_{CoG_{max}} = \frac{W/2}{\tan(40^\circ)} = \frac{0.30}{0.839} = 0.357\text{ m}$

Posizionando i componenti pesanti (motori a 25 cm, batterie incassate a 20 cm) e spostando il carico utile di 30 kg in alto, i calcoli dei momenti fisici dimostrano che **l'altezza massima del pianale di carico ammissibile è di 55 cm**. 
A questa quota ($h = 0.55\text{ m}$), il baricentro globale si attesta a circa $0.378\text{ m}$, garantendo un angolo di ribaltamento statico eccezionale di **$38^\circ$**.

> [!IMPORTANT] 
> Oltre i 55 cm, il rischio di ribaltamento laterale su terreni sconnessi (effetto pendolo dinamico) diventerebbe critico senza un sistema attivo di "Zavorra Mobile" (slittamento laterale del pacco batteria) o senza allargare la carreggiata a 0.70 m.

---

## 2. La Scelta Sospensiva a 4 km/h

Il "Mulo" procede a velocità di camminata (circa 4 km/h). A questa velocità, le sospensioni a braccio oscillante (Trailing Arm) con ammortizzatori indipendenti introducono complicanze costruttive eccessive, potenziale instabilità per rollio (body-roll verso valle) e punti di rottura non necessari, senza aggiungere reale valore alla trazione.

Il compito primario di mantenere le ruote a contatto con il terreno accidentato è già svolto in modo superbo dallo **Snodo Centrale di Torsione (Quick-Split) su cuscinetti UCP204**. 

Tuttavia, un telaio metallico rigido trasmetterebbe vibrazioni distruttive ad alta frequenza ai sensori (IMU, LiDAR, Telecamere) e all'elettronica di bordo (Jetson/ESP32).

---

## 3. Implementazione: La Micro-Sospensione "Semirigida"

La strategia ingegneristica definitiva per il Mulo MK0 combina l'indistruttibilità del telaio rigido con lo smorzamento attivo delle vibrazioni, tramite l'utilizzo strategico di polimeri (Silent-Blocks):

### A. Piastre Ruota Disaccoppiate
Le piastre in acciaio da 6 mm che ospitano il motore brushless e il cuscinetto radiale (UCF204) non sono imbullonate rigidamente al telaio principale. Vengono interposti **4x Silent-Block antivibranti (es. M10)** tra la piastra e il telaio.
- *Beneficio*: La ruota ottiene una micro-escursione elastica di 5-8 mm in tutte le direzioni. Questa corsa infinitesimale assorbe il picco G dell'impatto contro le rocce a 4 km/h, annullando le vibrazioni per l'elettronica superiore senza le complicazioni cinematiche di un braccio oscillante.

### B. Snodo Centrale Smorzato
Lo snodo centrale a torsione libera viene equipaggiato con **tamponi di finecorsa in poliuretano** e **boccole elastiche** per limitare la torsione massima a $\pm 15^\circ$.
- *Beneficio*: Limita il rollio estremo del semitelaio posteriore in forte pendenza, offrendo un ritorno elastico automatico verso la posizione orizzontale ed evitando cedimenti strutturali sulle rocce alte.

### C. Smorzamento Pneumatico (Gomme a bassa pressione)
Le quattro ruote Cargo da 20 pollici vengono gonfiate a una pressione estremamente bassa (**1.0 - 1.2 bar**).
- *Beneficio*: Il grande volume d'aria dello pneumatico funge da sospensione primaria naturale, copiando le asperità minori (ghiaia, radici) e lavorando in perfetta sinergia con i silent-block.

---

## 4. Sintesi degli Studi di Simulazione e Stabilità Dinamica

Per validare le scelte geometriche e sospensive del Mulo MK0, sono stati condotti studi di simulazione dinamica multicorpo (sviluppati in MATLAB R2025b ed esportati nei grafici di progetto). I risultati stabiliscono i limiti operativi fisici e le strategie di superamento degli ostacoli sui sentieri alpini.

### A. Limiti del Telaio Monolitico (Worst-Case)
Se il telaio fosse un corpo unico completamente rigido privo di snodo centrale, con una carreggiata stretta di 60 cm ed il baricentro a 37.8 cm:
- **Impatto a 4 km/h su pietra da 15 cm**: Il trasferimento istantaneo dell'energia cinetica dell'urto provoca un rollio transitorio che supera la soglia limite statica (38.4°), portando il rover al ribaltamento completo.
- **Soluzione per Telaio Rigido**: Richiederebbe l'allargamento della carreggiata a W = 70 cm (soglia limite statica a 42.8°) ed un addolcimento delle sospensioni (k_susp = 12000 N/m, c_susp = 350 N*s/m) per limitare il rollio massimo transitorio a 38.7°, mantenendo il veicolo stabile.

### B. Il Ruolo Salvifico dello Snodo Centrale UCP204 (Carreggiata fissa a 60 cm)
Modellando il Mulo come un **veicolo articolato a due corpi** (semitelaio anteriore e semitelaio posteriore connessi dallo snodo torsionale con finecorsa a 15°), il comportamento dinamico a 60 cm di carreggiata diventa estremamente sicuro:
- **Torsione Geometrica Richiesta**: Salire su una pietra da 15 cm con una ruota dell'assale da 60 cm richiede una torsione geometrica pari a:
  theta_geometrico = arcsin(0.15 / 0.60) = arcsin(0.25) = 14.48°
- **Comportamento Transitorio a 4 km/h**: 
  - La torsione geometrica rientra quasi interamente nei 15° di rotazione libera dello snodo centrale. 
  - Il semitelaio anteriore subisce un rollio transitorio di **26.31°** (ben al di sotto del limite di ribaltamento).
  - Lo snodo si torce di **15.69°**, comprimendo leggermente i tamponi di finecorsa in poliuretano che smorzano il moto.
  - Il semitelaio posteriore (dove risiedono batteria, generatore e carico utile principale) rimane quasi piatto, registrando un rollio massimo di soli **11.13°**.
  - La ruota posteriore a valle rimane incollata al suolo esercitando una forza normale di ben **278.9 N**, fungendo da ancora attiva contro il ribaltamento.
- **STATO**: **Stabilità dinamica assoluta mantenuta**. Il rover supera agevolmente l'ostacolo senza alcun rischio di ribaltamento.

### C. Superamento dell'Ostacolo Limite di Emergenza (20 cm)
Salire su un masso da 20 cm rappresenta il limite fisico assoluto per la carreggiata da 60 cm:
- **Torsione Geometrica Richiesta**: 
  theta_geometrico = arcsin(0.20 / 0.60) = arcsin(0.333) = 19.47°
- **Risposta del Sistema**: Poiché l'angolo supera i 15° di rotazione libera, lo snodo si torce di **16.14°**, comprimendo fortemente i finecorsa rigidi in poliuretano e trasferendo la coppia stabilizzante al posteriore.
- **Margini di Sicurezza**: Il semitelaio posteriore rolla fino a **30.73°** (ancorato con 272.9 N sulla ruota posteriore sinistra). Il semitelaio anteriore picca a **41.40°**, sfiorando per soli 0.87° la soglia di ribaltamento locale del singolo assale (fissata a 42.27° per baricentro ottimizzato a 33 cm).
- **STATO**: **Stabilità limite mantenuta**. Il rover supera l'ostacolo rimanendo in piedi, ma si trova in condizioni critiche e non ripetibili in sicurezza su terreno reale.

### D. Ostacoli Superiori a 20 cm (Strategia di Auto-Soccorso con Verricello)
Per qualsiasi dislivello, gradone o ostacolo superiore a 20 cm, si esclude la marcia per trazione e si adotta la modalità di **auto-soccorso con il verricello anteriore (`rover_winch`)**:
1. **Punto di Tiro Basso**: Il verricello deve essere montato allineato all'altezza dei mozzi (circa 25 cm da terra) per minimizzare il braccio di leva rispetto al CoG ed evitare il rischio di ribaltamento all'indietro (Pitch-up o Back-flip).
2. **Controllo Attivo del Momento di Tiro**: Il nodo software ROS 2 `winch_manager.py` acquisisce la tensione del cavo tramite la cella di carico (HX711) e l'inclinazione reale dall'IMU (BNO085), calcolando in tempo reale il bilancio tra il momento ribaltante del tiro e quello stabilizzante della gravità:
   M_ribaltante = Tensione * (h_winch - h_CoG)
   M_stabilizzante = (Massa * g * cos(pitch)) * (Wheelbase / 2)
   In caso di superamento dell'80% del limite di sicurezza, la trazione viene automaticamente arrestata o ridotta per mantenere le ruote anteriori a contatto con il suolo.

