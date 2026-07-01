# KiCad Sources - MULO-REX Controller

Questa cartella contiene la baseline KiCad generabile per il controller STM32
del range extender Honda GX50.

## Stato

Il file `mulo_rex_controller/mulo_rex_controller.kicad_sch` e' uno schema
funzionale di architettura, utile per review e PDF/SVG. Non sostituisce ancora
lo schematic capture dettagliato con simboli, footprint, netclass e PCB.

## Export

Da root repository:

```powershell
powershell -ExecutionPolicy Bypass -File .\axiom_rover_ws\scripts\generate_assembly_artifacts.ps1
```

Output attesi:

- `hardware/electronics/rex_controller/generated/kicad/mulo_rex_controller.svg`
- `hardware/electronics/rex_controller/generated/kicad/mulo_rex_controller.pdf`
- `hardware/electronics/rex_controller/generated/kicad/mulo_rex_controller_erc.rpt`

## Gate Per PCB Finale

- Sostituire i blocchi grafici con simboli reali.
- Assegnare footprint e connettori scelti.
- Chiudere ERC senza errori.
- Chiudere DRC PCB con clearances coerenti con 70 V DC link e ambiente umido.
- Allegare PDF schematico, PDF PCB, BOM, pick/place, gerber e report DRC.
