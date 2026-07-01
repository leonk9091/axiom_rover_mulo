# Toolchain Manifest - MULO Assembly Readiness

Data baseline: 2026-06-14

Questo manifesto registra gli strumenti open-source disponibili sulla macchina
di sviluppo usata per generare il pacchetto di assemblaggio. Le versioni sotto
sono l'evidenza locale da usare per ripetere gli export.

## Tool Installati/Verificati

| Area | Tool | Versione verificata | Percorso/Comando |
| :--- | :--- | :--- | :--- |
| EDA | KiCad CLI | 10.0.3 | `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe` |
| EDA fallback | KiCad CLI | 9.0.7 | `C:\Program Files\KiCad\9.0\bin\kicad-cli.exe` |
| CAD parametrico | FreeCADCmd | 1.1.1 | `C:\Users\jessi\AppData\Local\Programs\FreeCAD 1.1\bin\freecadcmd.exe` |
| CAD fallback | FreeCADCmd | 1.0.2 | `C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe` |
| Geometrie scriptabili | OpenSCAD | 2021.01 | `C:\Program Files\OpenSCAD\openscad.exe` |
| Harness | WireViz | 0.4.1 | `wireviz` |
| Grafi | Graphviz DOT | installato | `dot` |
| Vettoriale | Inkscape | 1.4.4 | installato via `winget` |
| Firmware | PlatformIO | disponibile | `platformio` / `pio` |
| Report dati | Python + pandas/matplotlib | disponibile | `python` |

## Comando Di Rigenerazione

Da root repository:

```powershell
powershell -ExecutionPolicy Bypass -File .\axiom_rover_ws\scripts\generate_assembly_artifacts.ps1
```

Lo script produce:

- export KiCad SVG/PDF/ERC;
- diagrammi Graphviz PNG/SVG/PDF;
- harness WireViz HTML/PNG/SVG/TSV/GV;
- geometria OpenSCAD STL/DXF/PNG;
- modello FreeCAD FCStd/STEP/STL quando `freecadcmd` e' disponibile.

## Regola Enterprise

Gli output generati non sono certificazione: sono evidence di baseline tecnica.
Prima di ordinare pezzi o cablaggi ad alta energia servono review firmata,
misure reali, rating finali e aggiornamento della matrice `REQ -> design -> test`.
