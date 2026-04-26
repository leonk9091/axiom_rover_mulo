# Analisi Prestazionale e Sicurezza Axiom Rover

## 📐 Dinamica in Salita (15° / 27%)
Con ruote Fat-bike da 20" (R=0.254m) e 4 motori Stepperonline (33Nm ciascuno):

- **Spinta Totale:** 520 Newton.
- **Massa Max (Salita):** ~131 kg (incluso peso rover).
- **Velocità:** 4.0 km/h (Passo trekking ideale).
- **Margine:** Con un rover da 80kg, il sistema lavora con il **60% di riserva di potenza**, garantendo temperature basse e alta affidabilità.

## 🛑 Frenata Rigenerativa e Sicurezza
Il sistema si affida ai controller VESC per la gestione della discesa.

### Funzionamento
- **Modalità Rigenerativa:** Il VESC trasforma i motori in generatori durante la discesa.
- **Capacità Frenante:** Fino a 205 kg di massa controllata su pendenza 15°.
- **Potenza Dissipata:** ~92W per motore in discesa (ampiamente entro il limite dei 200W).

### ⚠️ Vincoli di Sicurezza Critici
1.  **Stazionamento:** I motori brushless NON bloccano il rover quando spenti. 
    -   *Soluzione:* Obbligatorio aggiungere **freni meccanici a disco** (6-fori standard sulle ruote Fat-bike) con pinza comandata da cavo o attuatore per lo stazionamento.
2.  **Batteria Carica:** Se la batteria è al 100%, la rigenerazione viene tagliata dal VESC per evitare sovratensioni.
    -   *Soluzione:* Implementare un **Dump Load** (resistenza di frenatura) attivata dal VESC o mantenere la batteria < 95% all'inizio delle discese.

## 🔗 Accoppiamento Meccanico (L'interfaccia 6-fori)
Le ruote Fat-bike scelte hanno il mozzo standard a 6 fori (ISO 44mm).
- **Metodo:** La flangia d'acciaio da 14mm viene imbullonata direttamente al posto del disco freno (o insieme ad esso se si usa un distanziale) sul mozzo della ruota.
- **Stabilità:** Questo elimina giochi meccanici e permette di trasmettere tutti i 33Nm di coppia senza rischio di slittamento sull'albero.
