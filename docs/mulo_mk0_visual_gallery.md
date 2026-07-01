# Gallery Visuale Tecnica - Axiom MK0

Questa gallery raccoglie formati diversi per visualizzare e comunicare l'architettura MK0. Serve a scegliere lo strumento giusto a seconda del pubblico: officina, firmware, documentazione, revisione tecnica o presentazione.

## Tavole SVG

- [Layout dall'alto](diagrams/mk0_top_layout.svg)
- [Geometria UWB](diagrams/mk0_uwb_geometry.svg)
- [ToF e ostacoli in vista laterale](diagrams/mk0_side_tof_obstacle.svg)
- [Controllo e cablaggio logico](diagrams/mk0_control_wiring.svg)
- [Vista esplosa ponte corazzato](diagrams/mk0_exploded_drivetrain.svg)

## Modelli 3D e Disegni Meccanici CAD (SolidWorks & PNG)

Questi file contengono la modellazione tridimensionale originale e i disegni costruttivi del Mulo MK0, utili per l'officina, il tornitore e la verifica ingegneristica:

*   **Esploso 3D del Ponte Corazzato:**
    *   File Disegno: [ponte_corazzato_exploded_view.png](../hardware/cad/ponte_corazzato_exploded_view.png)
    *   *Descrizione:* Vista assonometrica esplosa in stile tavola tecnica che mostra l'asse coassiale di accoppiamento tra il motore, la piastra da 6 mm, il cuscinetto UCF204, l'albero custom e la ruota Cargo da 20".
*   **Tavola Costruttiva Snodo Centrale Articolato (Quick-Split):**
    *   File Blueprint: [blueprint_chassis_articulation.png](../hardware/cad/blueprint_chassis_articulation.png)
    *   *Descrizione:* Dettaglio ingegneristico dello snodo di torsione a sgancio rapido con accoppiamento cuscinetti ritti UCP204, albero di torsione da 20 mm e spina con coppiglia elastica.
*   **Tavola Ingegneristica del Verricello Meccanico (Winch):**
    *   File Blueprint: [blueprint_winch_assembly.png](../hardware/cad/blueprint_winch_assembly.png)
    *   *Descrizione:* Vista tecnica quotata dell'ancoraggio del verricello sul semitelaio anteriore, passacavo a rulli e allineamento di tiro per l'auto-soccorso.
*   **Dettaglio Esploso Assonometrico Ingegneristico:**
    *   File Blueprint: [blueprint_drivetrain_exploded.png](../hardware/cad/blueprint_drivetrain_exploded.png)
    *   *Descrizione:* Spaccato tecnico alternativo della catena cinematica coassiale (motore-piastra-flangia-ruota) in stile manuale d'officina.
*   **Layout CAD 3D Vano di Potenza e Ricarica (Power Box):**
    *   File CAD: [cad_power_box_assembly.png](../hardware/cad/cad_power_box_assembly.png)
    *   *Descrizione:* Modello 3D che illustra l'alloggiamento stagno IP68 del Mean Well NPB-750-24 e del regolatore MPPT Victron, con flangia Rosenberger RoPD e passacavi AWG 10.
*   **Modello dell'Albero Custom in SolidWorks (Tornitura):**
    *   File CAD: [albero_custom.SLDPRT](../hardware/cad/albero_custom.SLDPRT)
    *   *Descrizione:* Il file SolidWorks 3D originale del mozzo/albero custom in **42CrMo4** con la flangia a 6 fori integrata e il foro cieco da 14 mm per l'albero motore.
*   **Assieme Ruota e Mozzo:**
    *   File Disegno: [wheel_assembly.png](../hardware/cad/wheel_assembly.png)
    *   *Descrizione:* Dettaglio dell'accoppiamento tra la ruota da 20", il freno a disco da 203 mm e la flangia dell'albero di trasmissione.
*   **Struttura e Rinforzi del Telaio (SolidWorks & Layout):**
    *   File Telaio: [Parte3.SLDPRT](../../Parte3.SLDPRT) e [Parte4.SLDPRT](../../Parte4.SLDPRT) (nella root del progetto)
    *   Disegni Layout: [chassis_layout.png](../hardware/cad/chassis_layout.png) e [chassis_bracing.png](../hardware/cad/chassis_bracing.png)
    *   *Descrizione:* Modelli e render per la saldatura dei tubolari S235 da 30x30 mm e delle controventature diagonali del semitelaio.

## Grafici Ingegneristici e Curve di Funzionamento (PNG)

Questi grafici analizzano e validano le performance fisiche ed elettriche dei sistemi di bordo, fondamentali per lo sviluppo del firmware e il dimensionamento della batteria:

*   **Curva di Coppia e Efficienza del Motore (Torque vs Speed):**
    *   File Grafico: [plot_motor_torque_speed.png](diagrams/plot_motor_torque_speed.png)
    *   *Descrizione:* Profilo di funzionamento della coppia erogata dal motore a 24V gestito da VESC in funzione del regime di giri (RPM) e della curva di efficienza energetica associata.
*   **Curva di Scarica e Autonomia LiFePO4 (SoC %):**
    *   File Grafico: [plot_battery_discharge_soc.png](diagrams/plot_battery_discharge_soc.png)
    *   *Descrizione:* Andamento della tensione delle celle della batteria LiFePO4 in funzione dello Stato di Carica (State of Charge) per differenti correnti di scarica costanti (0.2C, 0.5C, 1C).
*   **Errore Angolare UWB vs Distanza (Trilaterazione):**
    *   File Grafico: [plot_uwb_trilateration_error.png](diagrams/plot_uwb_trilateration_error.png)
    *   *Descrizione:* Analisi sperimentale della precisione di stima angolare del follow-me basato su due ancore UWB distanziate da 0.60 m (baseline).
*   **Forza di Trazione Verricello vs Pendenza del Terreno:**
    *   File Grafico: [plot_winch_tension_slope.png](diagrams/plot_winch_tension_slope.png)
    *   *Descrizione:* Tensione richiesta sul cavo verricello (N) per differenti carichi trasportati (50 kg, 75 kg, 100 kg) in salita in funzione del grado di pendenza del terreno (0-45°).

## Rendering d'Ambiente e Studio Tecnico (PNG)

Questi rendering presentano il Mulo MK0 nel suo design finito ed operativo, utili per scopi di presentazione e validazione d'impatto visivo:

*   **Render Studio Premium (Officina Dark):**
    *   File Render: [render_mulo_studio_dark.png](diagrams/render_mulo_studio_dark.png)
    *   *Descrizione:* Vista da studio fotografico professionale che mette in evidenza la finitura nero opaco del telaio tubolare in acciaio, le grandi ruote Cargo da 20" e lo snodo centrale in un'ambientazione officina pulita.
*   **Render Operativo (Trekking Alpino):**
    *   File Render: [render_mulo_trekking_alpine.png](diagrams/render_mulo_trekking_alpine.png)
    *   *Descrizione:* Il rover Mulo ripreso in azione su un sentiero montano roccioso, mentre segue in modalità follow-me l'escursionista a distanza di sicurezza, portando in modo stabile i bagagli di trekking.

## Linguaggi per schemi

### Mermaid

File: [mk0_firmware_state_machine.mmd](diagrams/mk0_firmware_state_machine.mmd)

```mermaid
stateDiagram-v2
    [*] --> INIT
    INIT --> IDLE: sensori OK
    IDLE --> FOLLOW: comando avvio / UWB valido
    FOLLOW --> DEGRADED: misura incerta
    FOLLOW --> STOP: perdita UWB / fault CAN / pendenza critica
    DEGRADED --> FOLLOW: misure stabili
    DEGRADED --> STOP: timeout degrado
    STOP --> IDLE: reset manuale
    ESTOP --> IDLE: rilascio E-stop + reset
```

### PlantUML

File: [mk0_fault_sequence.puml](diagrams/mk0_fault_sequence.puml)

Utile per rappresentare sequenze temporali: perdita UWB, fault CAN, stop conservativo, reset operatore e logging.

### Graphviz DOT

File: [mk0_signal_graph.dot](diagrams/mk0_signal_graph.dot)

Utile per grafi di dipendenza, priorita' dei segnali, relazioni tra sensori, MCU, VESC, potenza e safety.

## Dashboard HTML

File: [mk0_visual_dashboard.html](diagrams/mk0_visual_dashboard.html)

Pagina autonoma HTML/CSS per presentare il progetto senza strumenti esterni. Puo' essere aperta direttamente nel browser e usata come mini-tavola tecnica interattiva.

## Indice visuale cliccabile

File: [mk0_visual_index.html](diagrams/mk0_visual_index.html)

Indice locale con preview cliccabili delle tavole SVG, della dashboard e dei sorgenti Mermaid/PlantUML/Graphviz.

## Prompt per immagini fotorealistiche

Questi prompt sono pronti per un generatore bitmap quando serve un render visuale piu' realistico.

### Render prodotto

```text
Fotorealistic engineering product render of a compact four-wheel articulated trekking rover named Axiom MK0, steel square-tube chassis, four 20-inch cargo bicycle wheels, visible external flanged bearings, rugged mechanical disc brakes, front UWB anchors and small ToF sensors, sealed electronics boxes, matte industrial finish, realistic workshop lighting, clean technical background, no people, no logos, no text, high detail.
```

### Vista esplosa

```text
Technical exploded view of a rugged rover wheel drivetrain assembly: geared 24V motor, 6 mm steel mounting plate, custom 42CrMo4 extension shaft, external UCF204 flanged bearing, 203 mm brake disc, 20 inch cargo wheel hub, aligned on a common axis, clean white background, engineering manual style, realistic metal materials, no text labels.
```

### Scenario trekking

```text
Realistic outdoor scene of a compact autonomous follow-me trekking cargo rover on a mountain trail, four large 20-inch wheels, steel articulated chassis, carrying hiking equipment, following an operator at walking pace from behind, natural daylight, readable mechanical details, safe distance, no futuristic styling, no military appearance, no text.
```
