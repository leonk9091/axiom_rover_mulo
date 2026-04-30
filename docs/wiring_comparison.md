# Confronto Sistemi di Cablaggio: Fritzing vs WireViz

Per il "Mulo" ho preparato due visualizzazioni diverse dei collegamenti per aiutarti a capire sia l'aspetto fisico che la logica di connessione.

## 1. Visualizzazione "Fritzing" (Fisica)
Utile per capire come posizionare i componenti e come appaiono visivamente i fili.

![Fritzing Wiring](file:///A:/progetto%20rover/axiom_rover_ws/hardware/electronics/fritzing_wiring.png)

- **Pro:** Immediato, colori dei cavi realistici.
- **Utilizzo:** Montaggio rapido a banco (prototipazione).

## 2. Visualizzazione "WireViz" (Logica Industriale)
Questa è la visualizzazione "a codice". È uno schema tecnico che si concentra sui pin, sui connettori e sulla tipologia di cavi.

![WireViz Diagram](file:///A:/progetto%20rover/axiom_rover_ws/hardware/electronics/wireviz_diagram.png)

- **Pro:** Estremamente preciso, ideale per documentazione tecnica e manutenzione.
- **Utilizzo:** Cablaggio finale definitivo e debugging.

## Codice Sorgente WireViz (.yaml)
Puoi modificare questo codice per rigenerare il diagramma se aggiungi sensori:

```yaml
# A:\progetto rover\axiom_rover_ws\hardware\electronics\mulo_wiring.yaml
connectors:
  Jetson_Orin: { pincount: 40 }
  ESP32: { pincount: 30 }
  Dual_VESC_1: { pincount: 12 }
  Dual_VESC_2: { pincount: 12 }
  Battery_24V: { pincount: 2 }

cables:
  CAN_Bus: { wirecount: 2, color: [blue, white], label: CAN }
  Power_Main: { wirecount: 2, color: [red, black], gauge: 10AWG }

connections:
  - [Jetson_Orin: 1, ESP32: 1] # Esempio Power
  - [Dual_VESC_1: 1, Dual_VESC_2: 1, label: CAN_Loop]
```
