# KiCad Implementation Notes - MULO-REX Controller

KiCad CLI 10.0.3 e' disponibile sulla macchina di sviluppo. La cartella
`kicad/mulo_rex_controller` contiene una baseline funzionale esportabile in
PDF/SVG/ERC. Per arrivare al PCB finale, sostituire i blocchi grafici con
simboli reali usando questi passi.

## Fogli Schema

1. `01_power_input`
   - 24 V input protetto;
   - buck 5 V logic;
   - buck 6 V servo;
   - TVS/fusibili;
   - punti misura.

2. `02_stm32_rex`
   - NUCLEO-F446RE/F103RB headers;
   - mapping pin da `rex_controller_harness.csv`;
   - pull-up/down fail-safe;
   - USB/serial bringup.

3. `03_sensing`
   - RPM Hall;
   - Vdc divider 100 V rated + TVS + RC;
   - current sensor front-end;
   - temperature front-end.

4. `04_actuation`
   - ignition kill opto/relay;
   - throttle servo driver;
   - dump-load request output;
   - safety kill input isolation.

## ERC Gate

- Nessun power input senza fusibile o protezione upstream.
- Nessun pin MCU collegato direttamente a DC link o ignition primary.
- `SAFETY_KILL_N` ha pull fisico e stato fail-safe documentato.
- `KILL_IGNITION` resta nello stato sicuro durante reset MCU.
- Grounds di sensori, servo, potenza e chassis hanno strategia esplicita.
- Ogni connettore ha pin 1 e orientamento.

## DRC/PCB Gate

- Clearance coerenti con 70 V DC link e ambiente sporco/umido.
- Tracce analogiche lontane da servo, ignition e fasi BLDC.
- Connettori su bordo con strain relief.
- Fori di fissaggio e keepout per Nucleo/carrier.
- Test point per GND, 5 V, 6 V, Vdc scaled, Icharge, RPM, kill.

## Import Manuale

Usare:

- `rex_controller_netlist.csv` per creare label e net classes;
- `rex_controller_harness.csv` per connettori;
- `rex_controller_bom.csv` per footprint/rating candidati;
- `rex_controller_schematic.mmd` come review visiva prima dello schema elettrico.
- `wireviz/rex_controller_harness.yml` per controllare connettori, fili e colori.
- `generated/kicad/*` come output di review, non come certificazione PCB.
