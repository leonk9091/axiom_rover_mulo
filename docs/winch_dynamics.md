# Simulazione Dinamica Verricello e Stabilità (Antiribaltamento)

## ⚠️ Il Problema del "Back-Flip"
Quando il verricello tira dal punto alto (solitamente sopra il baricentro), crea un momento torcente che tende a sollevare le ruote anteriori, rischiando il ribaltamento all'indietro (Pitch-up).

## Parametri di Calcolo
- **Interasse (Wheelbase):** 0.8m
- **Altezza Baricentro (CoG Height):** 0.2m
- **Altezza Punto di Tiro (Winch Height):** 0.35m
- **Pendenza:** 15°

## Strategia di Controllo ROS 2 (Winch Node)
Per evitare il ribaltamento, il nodo `winch_manager.py` deve implementare questa logica:

```python
def check_stability(tension, pitch_angle):
    # Calcolo momento ribaltante (Winch) vs Momento stabilizzante (Gravità)
    overturning_moment = tension * winch_height_relative_to_cog
    stabilizing_moment = (mass * g * cos(pitch_angle)) * (wheelbase / 2)
    
    if overturning_moment > stabilizing_moment * safety_factor:
        # Riduci immediatamente la forza del verricello
        apply_winch_brake_or_release()
```

## Checklist Meccanica per Stabilità
1.  **Punto di Tiro Basso:** Fissare il verricello il più vicino possibile al piano dei mozzi ruota per ridurre il braccio di leva.
2.  **Contrappeso:** Batteria LiFePO4 posizionata il più avanti e in basso possibile nel modulo anteriore.
3.  **Monitoraggio Inclinazione:** IMU obbligatoria per leggere il `pitch` in tempo reale.
