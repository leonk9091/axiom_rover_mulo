/**
 * ESP32 Safety Firmware - Axiom Rover "Mulo"
 *
 * Funzioni:
 *   - Watchdog hardware: se heartbeat ROS manca per > 500ms → taglia motori (GPIO 14)
 *   - Lettura cella di carico HX711 (GPIO 18/19) → tensione cavo [N]
 *   - Lettura encoder verricello in quadratura (GPIO 32/33) → lunghezza cavo [m]
 *   - Pulsante E-Stop fisico (GPIO 14, interrupt) → E-Stop immediato
 *   - Relay SSR generatore ICE (GPIO 12)
 *   - Dump load (GPIO 27)
 *   - Comunicazione JSON su UART con Jetson (115200 bps)
 *   - LED status (GPIO 2): blink normale, fisso = E-Stop
 *
 * Pinout (da esp32_pinout.md):
 *   GPIO 12 → ICE SSR
 *   GPIO 14 → E-Stop input (interrupt) + Motor Kill relay output
 *   GPIO 18 → HX711 SCK
 *   GPIO 19 → HX711 DT
 *   GPIO 27 → Dump Load relay
 *   GPIO 32 → Encoder A
 *   GPIO 33 → Encoder B
 *   GPIO 2  → Status LED
 */

#include <Arduino.h>
#include <ArduinoJson.h>
#include "HX711.h"

// ---------------------------------------------------------------------------
// Pin definitions
// ---------------------------------------------------------------------------
#define PIN_ICE_SSR         12
#define PIN_ESTOP_BTN       14   // INPUT_PULLUP, active LOW
#define PIN_MOTOR_KILL      14   // stesso pin: se E-Stop → OUTPUT HIGH → relay taglia
#define PIN_HX711_SCK       18
#define PIN_HX711_DT        19
#define PIN_DUMP_LOAD       27
#define PIN_ENC_A           32
#define PIN_ENC_B           33
#define PIN_LED             2

// ---------------------------------------------------------------------------
// Costanti
// ---------------------------------------------------------------------------
#define HEARTBEAT_TIMEOUT_MS    500     // ms: timeout heartbeat ROS
#define BAUD_RATE               115200
#define LOAD_CELL_SCALE         420.0f  // fattore calibrazione HX711 (da calibrare)
#define ENCODER_PPR             1000    // impulsi per giro encoder
#define DRUM_CIRCUMFERENCE_M    0.314f  // m (diametro tamburo ~100mm → π*0.1)
#define CABLE_M_PER_PULSE       (DRUM_CIRCUMFERENCE_M / ENCODER_PPR)
#define JSON_TX_PERIOD_MS       50      // ms (20 Hz)
#define LED_BLINK_PERIOD_MS     500     // ms (blink normale)

// ---------------------------------------------------------------------------
// Stato globale
// ---------------------------------------------------------------------------
volatile bool     g_estop_active    = false;
volatile bool     g_estop_btn_press = false;
volatile int32_t  g_encoder_count   = 0;

unsigned long     g_last_heartbeat_ms = 0;
unsigned long     g_last_tx_ms        = 0;
unsigned long     g_last_led_ms       = 0;
bool              g_led_state         = false;
int               g_heartbeat_seq     = -1;
bool              g_ice_on            = false;
bool              g_dump_load_on      = false;

HX711 g_load_cell;

// ---------------------------------------------------------------------------
// ISR: pulsante E-Stop fisico
// ---------------------------------------------------------------------------
void IRAM_ATTR isr_estop_button() {
    g_estop_btn_press = true;
    g_estop_active    = true;
}

// ---------------------------------------------------------------------------
// ISR: encoder verricello (quadratura)
// ---------------------------------------------------------------------------
void IRAM_ATTR isr_encoder_a() {
    bool a = digitalRead(PIN_ENC_A);
    bool b = digitalRead(PIN_ENC_B);
    g_encoder_count += (a == b) ? +1 : -1;
}

// ---------------------------------------------------------------------------
// Funzioni safety
// ---------------------------------------------------------------------------
void trigger_motor_kill() {
    // Taglia alimentazione motori via relay hardware (indipendente da ROS)
    pinMode(PIN_MOTOR_KILL, OUTPUT);
    digitalWrite(PIN_MOTOR_KILL, HIGH);
    digitalWrite(PIN_LED, HIGH);  // LED fisso = E-Stop
    g_estop_active = true;
}

void reset_estop() {
    // Reset solo se pulsante fisico rilasciato E heartbeat ROS ripreso
    if (digitalRead(PIN_ESTOP_BTN) == HIGH &&
        (millis() - g_last_heartbeat_ms) < HEARTBEAT_TIMEOUT_MS) {
        g_estop_active    = false;
        g_estop_btn_press = false;
        pinMode(PIN_MOTOR_KILL, INPUT_PULLUP);  // rilascia relay
    }
}

// ---------------------------------------------------------------------------
// Parsing JSON in ingresso da Jetson
// ---------------------------------------------------------------------------
void parse_rx_json(const String& line) {
    StaticJsonDocument<128> doc;
    DeserializationError err = deserializeJson(doc, line);
    if (err) return;

    // Aggiorna timestamp heartbeat
    if (doc.containsKey("seq")) {
        g_last_heartbeat_ms = millis();
        g_heartbeat_seq     = doc["seq"].as<int>();
    }

    // Comandi
    bool ros_estop = doc["estop"] | false;
    if (ros_estop && !g_estop_active) {
        trigger_motor_kill();
    }

    // ICE generator
    bool ice_cmd = doc["ice_on"] | false;
    if (ice_cmd != g_ice_on) {
        g_ice_on = ice_cmd;
        digitalWrite(PIN_ICE_SSR, g_ice_on ? HIGH : LOW);
    }

    // Dump load
    bool dump_cmd = doc["dump_load"] | false;
    if (dump_cmd != g_dump_load_on) {
        g_dump_load_on = dump_cmd;
        digitalWrite(PIN_DUMP_LOAD, g_dump_load_on ? HIGH : LOW);
    }
}

// ---------------------------------------------------------------------------
// Trasmissione JSON verso Jetson
// ---------------------------------------------------------------------------
void send_tx_json(float tension_n, float cable_m) {
    StaticJsonDocument<128> doc;
    doc["ack"]       = g_heartbeat_seq;
    doc["estop_hw"]  = g_estop_active;
    doc["encoder"]   = cable_m;
    doc["tension"]   = tension_n;
    doc["ice_on"]    = g_ice_on;
    doc["dump_load"] = g_dump_load_on;
    serializeJson(doc, Serial);
    Serial.println();
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------
void setup() {
    Serial.begin(BAUD_RATE);

    // Pin setup
    pinMode(PIN_ICE_SSR,   OUTPUT); digitalWrite(PIN_ICE_SSR,   LOW);
    pinMode(PIN_DUMP_LOAD, OUTPUT); digitalWrite(PIN_DUMP_LOAD, LOW);
    pinMode(PIN_LED,       OUTPUT); digitalWrite(PIN_LED,       LOW);
    pinMode(PIN_ESTOP_BTN, INPUT_PULLUP);
    pinMode(PIN_ENC_A,     INPUT_PULLUP);
    pinMode(PIN_ENC_B,     INPUT_PULLUP);

    // Interrupt E-Stop (falling = pulsante premuto)
    attachInterrupt(digitalPinToInterrupt(PIN_ESTOP_BTN), isr_estop_button, FALLING);
    // Interrupt encoder (rising su fase A)
    attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), isr_encoder_a, RISING);

    // HX711 load cell
    g_load_cell.begin(PIN_HX711_DT, PIN_HX711_SCK);
    g_load_cell.set_scale(LOAD_CELL_SCALE);
    g_load_cell.tare();

    g_last_heartbeat_ms = millis();  // evita E-Stop immediato all'avvio

    Serial.println("{\"boot\":true,\"fw\":\"axiom_safety_v1.0\"}");
}

// ---------------------------------------------------------------------------
// Loop principale
// ---------------------------------------------------------------------------
void loop() {
    unsigned long now = millis();

    // 1. Leggi UART da Jetson
    if (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        if (line.length() > 0) {
            parse_rx_json(line);
        }
    }

    // 2. Watchdog hardware: timeout heartbeat ROS
    if (!g_estop_active && (now - g_last_heartbeat_ms) > HEARTBEAT_TIMEOUT_MS) {
        trigger_motor_kill();
        // Log su seriale (Jetson potrebbe non leggere, ma utile per debug)
        Serial.println("{\"fault\":\"heartbeat_timeout\",\"estop_hw\":true}");
    }

    // 3. Lettura cella di carico (non bloccante)
    float tension_n = 0.0f;
    if (g_load_cell.is_ready()) {
        tension_n = g_load_cell.get_units(1);
        tension_n = max(0.0f, tension_n);
    }

    // 4. Calcolo lunghezza cavo da encoder
    float cable_m = (float)g_encoder_count * CABLE_M_PER_PULSE;

    // 5. Trasmissione JSON (20 Hz)
    if ((now - g_last_tx_ms) >= JSON_TX_PERIOD_MS) {
        g_last_tx_ms = now;
        send_tx_json(tension_n, cable_m);
    }

    // 6. LED status
    if ((now - g_last_led_ms) >= LED_BLINK_PERIOD_MS) {
        g_last_led_ms = now;
        if (!g_estop_active) {
            g_led_state = !g_led_state;
            digitalWrite(PIN_LED, g_led_state ? HIGH : LOW);
        }
        // Se E-Stop: LED fisso (già impostato in trigger_motor_kill)
    }

    // 7. Protezione sovratensione cavo (hardware, indipendente da ROS)
    if (tension_n > 480.0f && !g_estop_active) {
        trigger_motor_kill();
        Serial.println("{\"fault\":\"cable_overtension\",\"estop_hw\":true}");
    }
}
