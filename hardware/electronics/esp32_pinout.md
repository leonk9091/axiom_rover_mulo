# Schema Pinout ESP32 - Axiom Rover "Mulo"

L'ESP32 funge da interfaccia tra il computer di bordo (Jetson) e l'hardware di telemetria/potenza.

## 1. Connessioni Alimentazione
- **Vin:** 5V (regolati dalla batteria 24V).
- **GND:** Massa comune con Jetson e VESC.

## 2. Pinout GPIO

| Funzione | Pin ESP32 | Tipo | Note |
| :--- | :--- | :--- | :--- |
| **ICE Start (Relè SSR)** | GPIO 12 | Output | Segnale per avvio motore a scoppio |
| **Winch Load Cell (SCK)** | GPIO 18 | Output | Clock per HX711 |
| **Winch Load Cell (DT)** | GPIO 19 | Input | Dati per HX711 |
| **Winch Encoder A** | GPIO 32 | Input (Pull-up) | Fase A encoder tamburo |
| **Winch Encoder B** | GPIO 33 | Input (Pull-up) | Fase B encoder tamburo |
| **Freno Emergenza (E-Stop)** | GPIO 14 | Input (Interr.) | Pulsante fisico a fungo |
| **Motor Kill / Consenso Motori** | GPIO 26 | Output | Uscita separata active-high verso relay/opto consenso motori |
| **Status LED (Progetto)** | GPIO 2 | Output | LED di bordo (Blink = OK) |

## 3. Comunicazione con Jetson
- **USB-Serial:** Connessione diretta alla porta USB della Jetson Orin.
- **Baud Rate:** 115200 bps.
- **Protocollo:** ROS 2 Micro-ROS o seriale personalizzata (JSON).

## 4. Note Hardware
- **Isolamento:** Si consiglia di utilizzare un optoisolatore tra GPIO 12 e l'SSR del generatore per evitare disturbi elettromagnetici.
- **Resistenze:** Aggiungere resistenze di pull-up esterne da 4.7kΩ sui pin dell'encoder per maggiore immunità ai disturbi sui lunghi cavi.
