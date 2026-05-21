# Proposta Tecnica: Axiom Rover "Mulo" MK0 Operativo ESP32-S3

Questo documento propone la linea **Axiom MK0** come prototipo operativo implementabile subito, basato su architettura embedded **ESP32-S3**, inseguimento **UWB**, sensori **ToF**, controllo motori via **VESC/CAN**, logging locale e safety conservativa.

La proposta non sostituisce l'architettura **Mulo X-1** basata su ROS 2, Jetson e sensor fusion avanzata. Il ruolo corretto dell'MK0 e' costruire una **milestone fisica robusta**: un banco reale per validare telaio, powertrain, freni, batteria, cablaggi, UWB e procedure di test prima di aggiungere autonomia cognitiva piu' complessa.

---

## 1. Verdetto Ingegneristico

L'MK0 e' realmente implementabile, ma deve essere definito con precisione:

```text
Rover follow-me embedded, lento, deterministico e supervisionato.
```

Non deve essere presentato come rover autonomo completo. La versione implementabile nel breve periodo e' una piattaforma che segue l'operatore tramite UWB, mantiene una distanza target, si ferma in modo conservativo quando la misura diventa incoerente e registra log utili per diagnosi e miglioramento.

Il punto di forza dell'MK0 e' la riduzione della complessita' software:

- niente Linux nel loop critico;
- boot rapido;
- consumi ridotti;
- comportamento piu' prevedibile rispetto a una pipeline AI/ROS ancora sperimentale;
- integrazione diretta con sensori locali, CAN bus e logica di arresto.

Il limite strutturale e' altrettanto chiaro: senza LiDAR, camera, ROS 2 e pianificazione globale, l'MK0 non puo' interpretare un sentiero complesso, classificare ostacoli o costruire una mappa affidabile. Deve quindi muoversi a bassa velocita' e privilegiare sempre stop, derating e intervento dell'operatore rispetto a manovre autonome aggressive.

---

## 2. Perimetro Funzionale v1

La prima versione operativa deve essere volutamente stretta. L'obiettivo e' ottenere un rover che si muove poco, lentamente e in modo ripetibile, non un sistema che tenta di risolvere ogni scenario outdoor.

Funzioni incluse nella v1:

- **Follow-me UWB:** calcolo di distanza e angolo relativo dell'operatore tramite due anchor UWB montate sul rover e tag mobile sull'operatore.
- **Controllo distanza:** mantenimento di una distanza target, ad esempio 1,5 m, con arresto se l'operatore e' troppo vicino.
- **Comando pausa/stop:** pulsante o telecomando semplice, sempre prioritario rispetto al follow-me.
- **Stop sicuro su incoerenza:** arresto se UWB e' assente, instabile, fuori range o geometricamente non valido.
- **Derating base:** riduzione velocita'/coppia su pendenza, temperatura elevata, sovracorrente persistente o errore CAN.
- **Ostacoli semplici:** uso dei ToF frontali per rallentare, fermare o marcare un ostacolo come attraversabile solo in condizioni molto conservative.
- **Logging su SD:** salvataggio di distanze UWB, target calcolato, comandi motore, fault, tensione, corrente, temperatura, pendenza e stato GPS.

Funzioni escluse dalla v1:

- navigazione autonoma su mappa;
- riconoscimento persone tramite visione;
- evitamento ostacoli complesso;
- scelta autonoma di traiettorie alternative su sentiero;
- affidamento al GPS come sensore primario di inseguimento;
- safety basata solo su firmware applicativo.

La modalita' "Avanza sul Percorso" puo' essere mantenuta come funzione sperimentale successiva, ma non deve bloccare la validazione della v1 follow-me.

---

## 3. Architettura Minima

L'architettura minima consigliata per MK0 e' la seguente:

```text
ESP32-S3
    firmware deterministico, state machine, logging, CAN command

2x Anchor UWB frontali
    misura distanza dal tag operatore

Tag UWB operatore
    riferimento principale del follow-me locale

4x ToF frontali
    due bassi e due alti per filtro ostacoli semplice

IMU
    roll, pitch, vibrazioni e stop/derating su assetto critico

GNSS
    traccia, geofence semplice e recupero posizione; non follow-me primario

VESC su CAN
    attuazione motori e lettura fault/correnti/temperature

Gruppo Elettrogeno (1000W / 1200W)
    Range Extender ibrido in serie per ricarica batteria e supporto VESC

Micro-SD
    log diagnostici e prove di campo
```

Per l'IMU e' preferibile una soluzione piu' stabile del solo MPU6050, ad esempio **BNO085/BNO086** o equivalente, per ridurre il lavoro firmware sulla fusione assetto e ottenere misure piu' sfruttabili durante i test iniziali.

I contratti logici minimi da usare nel firmware sono:

| Campo | Significato |
| :--- | :--- |
| `target_distance` | Distanza stimata operatore-rover in metri. |
| `target_angle` | Angolo relativo rispetto alla mezzeria del rover. |
| `safety_state` | Stato sintetico: `OK`, `DEGRADED`, `STOP`, `ESTOP`, `CHARGING`. |
| `drive_command` | Comando calcolato verso VESC: velocita', sterzo differenziale e limite corrente. |
| `generator_current` | Corrente istantanea misurata in uscita dal caricabatterie (Ampere). |
| `fault_code` | Codice fault persistente o ultimo evento diagnostico. |

Questi campi non introducono nuove API ROS 2: sono un vocabolario firmware/documentale per rendere i test ripetibili e facilitare una futura integrazione con X-1.

### Geometria UWB

Con due anchor distanziate di larghezza nota `W`, ad esempio 0,60 m, e distanze misurate `d1` e `d2`, la stima relativa e':

```text
x = (d1^2 - d2^2) / (2W)
y = sqrt(d1^2 - (x + W/2)^2)
theta = atan2(x, y)
```

Questa geometria e' sufficiente per un prototipo follow-me, ma non va trattata come misura assoluta precisa. Quando l'operatore e' lontano rispetto alla baseline, piccoli errori sulle distanze producono errori angolari visibili. Il firmware deve quindi filtrare, limitare la velocita' e fermarsi se il target salta o diventa incoerente.

---

## 4. Rischi Tecnici Reali

### UWB a Due Anchor

La trilaterazione a due anchor e' implementabile, ma il margine angolare dipende dalla baseline e dalla qualita' delle misure. Con `W = 0,60 m`, a distanze di alcuni metri il segnale di sterzo puo' diventare rumoroso. Sono necessari:

- filtro temporale o Kalman semplice;
- limite massimo di variazione di `target_angle`;
- timeout corto su misura assente;
- stop se il radicando geometrico e' negativo o se le distanze cambiano in modo fisicamente impossibile;
- test con l'operatore davanti, laterale, parzialmente schermato dal corpo e in movimento.

Una terza anchor o moduli UWB con AoA migliorerebbero la robustezza, ma non sono obbligatori per la prima validazione se il comportamento resta lento e conservativo.

### ToF Outdoor

I sensori ToF economici possono degradare con sole diretto, superfici nere, fango, erba, pioggia e angoli sfavorevoli. La logica basso/alto e' utile, ma non deve essere l'unico garante della safety.

Per la v1 i ToF devono servire soprattutto a:

- rallentare davanti a ostacoli vicini;
- fermare il rover se piu' sensori confermano un ostacolo alto;
- produrre log per capire falsi positivi e falsi negativi;
- evitare decisioni brusche basate su una singola lettura.

### Ostacoli da 15 cm

Lo scavalcamento di ostacoli fino a 15 cm e' plausibile con ruote da 20" e coppia adeguata, ma non e' garantibile solo dai calcoli statici. Dipende da forma dell'ostacolo, aderenza, peso, baricentro, pressione gomme, velocita' e approccio.

La policy corretta e':

```text
prima test controllati, poi aumento graduale della soglia attraversabile.
```

Fino a validazione fisica, il firmware deve trattare l'ostacolo basso come condizione di rallentamento e attenzione, non come permesso automatico a spingere con coppia elevata.

### Safety

La safety non deve dipendere dal solo loop applicativo ESP32. Anche nella versione MK0 servono protezioni hardware e comportamenti fail-safe:

- E-stop fisico;
- sezionatore e fusibili corretti;
- watchdog;
- perdita CAN -> comando motori nullo;
- perdita UWB -> stop;
- pendenza critica -> stop;
- sovracorrente o temperatura persistente -> derating o stop;
- freni meccanici indipendenti per stazionamento e recupero.

---

## 5. Piano di Implementazione

### Fase 1 - Banco Elettronico

- Assemblare ESP32-S3, UWB, IMU, SD, CAN transceiver e alimentazione logica separata.
- Verificare boot, watchdog, scrittura SD e lettura sensori senza motori collegati.
- Integrare il sensore di corrente Hall (ACS758) per la linea del generatore ed eseguire letture analogico-digitali di calibrazione.
- **Integrazione Telemetria Caricatori:** Cablare l'accoppiatore ottico veloce (6N137) sulla seriale dell'ESP32-S3 per il link VE.Direct dal regolatore Victron. Verificare la decodifica dei pacchetti dati (tensione e corrente di carica) senza interferenze logiche.
- Produrre log CSV o JSONL con timestamp, UWB grezzo, IMU, stato firmware, corrente generatore, parametri di carica seriale e fault.

### Fase 2 - Firmware Base

- Implementare state machine minima: `INIT`, `IDLE`, `FOLLOW`, `DEGRADED`, `STOP`, `ESTOP`.
- Implementare calcolo `target_distance` e `target_angle`.
- Applicare filtro temporale, soglie di plausibilita' e timeout UWB.
- Generare `drive_command` limitato in velocita' e corrente.
- Registrare ogni transizione di stato con `fault_code`.

### Fase 3 - Test UWB a Terra

- Testare tag fermo a 1 m, 1,5 m, 2 m, 3 m e 4 m.
- Testare movimento laterale lento dell'operatore.
- Misurare jitter di distanza e angolo.
- Definire soglie reali di filtro e timeout dai log, non da ipotesi.

### Fase 4 - Motori su Cavalletto

- Collegare VESC via CAN senza carico a terra.
- Verificare comando velocita' nullo su `STOP`, `ESTOP`, perdita UWB e perdita CAN.
- Verificare limits di corrente e risposta a fault VESC.
- **Validazione Elettrica del Sotto-sistema di Ricarica (Duale e Solare):**
  - Eseguire il test di isolamento a 500V DC tramite megaohmmetro tra la terra/fase/neutro dell'ingresso AC e lo chassis metallico del rover, confermando una resistenza superiore a **100 MΩ** per scongiurare rischi di folgorazione.
  - Verificare il funzionamento elettrico del parallelo generatore-caricatore-batteria e la tenuta del diodo di blocco.
  - Verificare il parallelo dell'ingresso ausiliario MC4 solare con l'ingresso Rosenberger e la stabilità delle due linee di ricarica (AC-DC Mean Well e DC-DC Victron MPPT) sotto carico, assicurandosi che i diodi ideali prevengano qualsiasi reflusso di corrente con cadute di tensione < 0.03V.
- Confirmare che il loop firmware resta stabile alla frequenza target.

### Fase 5 - Test Lento Indoor

- Rover su pavimento libero, velocita' molto bassa.
- Operatore davanti al rover con tag UWB.
- Verificare partenza, inseguimento, stop sotto soglia di distanza, pausa manuale e perdita tag.
- Introdurre ostacoli semplici e validare solo rallentamento/stop, non aggiramento autonomo.

### Fase 6 - Test Outdoor Controllato

- Terreno piano, poi ghiaia leggera, poi pendenza moderata.
- Testare sole/ombra e schermature del corpo sull'UWB.
- Eseguire prove con carico crescente.
- Eseguire prove termiche brevi su salita lenta e stop-and-go.
- Testare l'efficacia del Range Extender a benzina: eseguire un trekking continuo di 2 ore monitorando le temperature del generatore, l'efficacia dei supporti silent-block (rumore IMU) e lo stato di carica (SoC) della batteria.
- **Validazione Termica ed Ambientale della Ricarica (Duale e Solare):**
  - Eseguire una ricarica rapida completa a **22.5A** costanti da rete AC 220V e monitorare con termocamera la dissipazione termica del Mean Well NPB-750 all'interno del vano di alloggiamento posteriore, assicurando stabilità termica sotto i **65°C**.
  - Testare il comportamento a basse temperature: raffreddare il rover a meno di 0°C e collegare il caricatore di bordo, verificando il corretto inibimento della carica da parte del BMS e l'attivazione automatica della resistenza scaldante integrata per preriscaldare le celle sopra i +5°C.
  - **Test Ricarica Solare in Sosta:** Dispiegare il pannello solare pieghevole portatile da 200W durante una sosta all'aperto esposta al sole, collegarlo alla presa ausiliaria MC4 e verificare il corretto aggancio dell'algoritmo MPPT Victron SmartSolar. Misurare la potenza reale erogata, verificando l'efficienza di conversione (>98%) e la corretta trasmissione della telemetria via seriale VE.Direct all'ESP32-S3 e via Bluetooth all'app di controllo.
- Salvare log per ogni run e annotare manualmente condizioni, carico, terreno e fault.

---

## 6. Criteri di Successo

La v1 MK0 e' considerata riuscita se soddisfa questi criteri:

- segue l'operatore a passo umano lento in area controllata;
- mantiene una distanza target senza oscillazioni pericolose;
- si arresta se l'operatore entra sotto la distanza minima;
- si arresta su perdita o incoerenza UWB;
- non usa il GPS per il follow-me ravvicinato;
- riduce o annulla il comando su pendenza critica;
- registra log leggibili e correlabili agli eventi reali;
- non tenta manovre autonome complesse quando i sensori sono incerti;
- conserva spazio architetturale per evolvere verso X-1.

Il successo dell'MK0 non si misura dalla quantita' di autonomia, ma dalla qualita' della base fisica e diagnostica che rende possibile sviluppare il rover senza rischiare subito la complessita' dell'intero stack ROS 2/AI.

La roadmap consigliata e':

```text
MK0 operativo
    validazione meccanica, elettrica, UWB, powertrain, safety, logging

MK0+
    miglioramento sensori, terza anchor/AoA, ToF piu' robusti, procedure campo

Mulo X-1
    Jetson + STM32, ROS 2, LiDAR/camera, Nav2, sensor fusion e autonomia avanzata
```
