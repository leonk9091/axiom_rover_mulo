# Analisi Motori Axiom Rover: Stepperonline vs Hub Motor

## Opzione 1: Stepperonline 24V 200W (71.5:1) - IL VINCITORE
Questo motore è ideale per il trekking pesante con ruote da 20".

### Specifiche Tecniche
- **Velocità:** 42 RPM (4.03 km/h con ruote da 20"). Perfetto per il passo umano.
- **Coppia:** 33 Nm per motore (132 Nm totali).
- **Spinta Lineare:** ~528 Newton (54 kg di spinta).
- **Meccanica:** Albero da 14mm con chiavetta. Richiede accoppiatore a flangia.
- **Elettronica:** Richiede Dual VESC o ODrive (supporto sensori di Hall obbligatorio).

---

## Opzione 2: Wheelchair Brushless Hub Motor (200W 24V)
Motore integrato nel mozzo, solitamente usato per sedie a rotelle.

### Specifiche Tecniche
- **Modello:** MY1012L4/L5.
- **Velocità:** 100-120 RPM (~10-12 km/h con ruote da 20"). Troppo veloce per il trekking a piedi senza riduzione.
- **Coppia:** 20 Nm.
- **Vantaggio:** Freno integrato, montaggio semplificato.
- **Svantaggio:** Meno coppia rispetto alla combinazione ridotta planetaria dello Stepperonline.

---

## Conclusioni Ingegneristiche
L'**Opzione 1 (Stepperonline)** è superiore per:
1. **Coppia Brutale:** Fondamentale per superare ostacoli e pendenze del 45%.
2. **Matching di Velocità:** Lavora al massimo dell'efficienza alla velocità di camminata.
3. **Modularità:** Il riduttore planetario protegge il motore dagli impatti diretti.
