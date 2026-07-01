# STM32 REX Controller Pinout - Honda GX50

Target consigliato: `NUCLEO-F446RE`. Target minimo verificabile: `NUCLEO-F103RB`.

## Confini

La safety MCU STM32 Nucleo resta responsabile di E-stop e consenso motori. Il
REX controller riceve un ingresso kill fisico dalla safety chain e deve portare
il GX50 in stato sicuro anche se ROS smette di inviare comandi.

## Pinout Logico Bringup

| Funzione | Pin logico | Direzione | Fail-safe | Note |
| :--- | :--- | :--- | :--- | :--- |
| Safety kill input | D2 | Input pull-up | LOW = kill GX50 | Da safety MCU/E-stop chain, non solo ROS. |
| RPM Hall | D3 | Input interrupt | Stale/no pulse = no generation | 1 impulso/giro target; schermare cavo. |
| Kill ignition | D7 | Output | HIGH = kill | Pilota opto/relay verso primario accensione Honda. |
| Dump load request | D8 | Output | LOW = off | Solo richiesta locale; dump finale va validato su potenza. |
| Throttle PWM | D9 | Output PWM | 0 = minimo | Pilotare servo driver; molla ritorno minimo obbligatoria. |
| Vdc raw | A0 | Analog input | Fault > 70 V | Partitore calibrato, isolamento e TVS. |
| Charge current | A1 | Analog input | Fault se 0 con frizione innestata | ACS758/INA226 o equivalente calibrato. |
| Rectifier temp | A2 | Analog input | Derate/fault | NTC/termocoppia tramite front-end. |
| Buck temp | A3 | Analog input | Derate/fault | NTC/termocoppia tramite front-end. |
| Exhaust-zone temp | A4 | Analog input | Derate/fault | Vicino schermatura, non sul collettore nudo. |

## Cablaggi Obbligatori

- Kill ignition su relay/opto normalmente in stato sicuro documentato.
- Servo throttle con molla meccanica di ritorno al minimo.
- Cavi Hall/ACS schermati o twistati, lontani da fasi BLDC e candela.
- DC link con partitore dimensionato, fusibile/TVS e riferimento massa definito.
- Tutti i segnali REX devono essere distinguibili dalla safety trazione.

## Gate Banco

Il firmware puo' essere acceso via USB prima del banco termico. Il GX50 non puo'
essere acceso finche':

- `PIN_KILL_IGNITION` e' verificato con multimetro;
- throttle torna a zero rimuovendo alimentazione servo;
- RPM Hall produce letture coerenti;
- Vdc e corrente sono calibrate su sorgente/carico noto;
- guardie cinghia/pulegge/frizione sono installate.
