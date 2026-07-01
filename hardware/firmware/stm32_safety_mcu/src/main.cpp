#include <Arduino.h>
#include "safety_protocol.hpp"

using axiom::McuStatusFrame;
using axiom::SafetyCommandFrame;
using axiom::SafetyState;

// Logical pinout for STM32 Nucleo safety bringup.
// Adjust these aliases after selecting the final Nucleo carrier board.
static constexpr uint8_t PIN_ESTOP_NC = D2;        // Input pull-up, active LOW/open.
static constexpr uint8_t PIN_MOTOR_CONSENT = D7;   // Output, HIGH enables external consent.
static constexpr uint8_t PIN_DUMP_LOAD = D8;       // Output, HIGH requests dump load.
static constexpr uint8_t PIN_STATUS_LED = LED_BUILTIN;

static constexpr uint32_t kStatusPeriodMs = 50;    // 20 Hz.
static constexpr size_t kLineBufferSize = 512;

SafetyCommandFrame g_last_command;
uint32_t g_last_command_ms = 0;
uint32_t g_last_status_ms = 0;
bool g_fault_latched = false;
const char* g_fault_code = "none";
char g_line[kLineBufferSize];
size_t g_line_len = 0;

void setMotorConsent(bool enabled) {
  digitalWrite(PIN_MOTOR_CONSENT, enabled ? HIGH : LOW);
}

bool estopPressed() {
  return digitalRead(PIN_ESTOP_NC) == LOW;
}

void latchFault(const char* code) {
  g_fault_latched = true;
  g_fault_code = code;
  setMotorConsent(false);
}

bool commandTimedOut(uint32_t now_ms) {
  const uint32_t age_ms = now_ms - g_last_command_ms;
  const uint16_t timeout_ms = g_last_command.timeout_ms > 0
                                  ? g_last_command.timeout_ms
                                  : axiom::kHeartbeatTimeoutMs;
  return age_ms > timeout_ms || age_ms > axiom::kHeartbeatTimeoutMs;
}

SafetyState currentSafetyState(uint32_t now_ms) {
  if (estopPressed()) {
    return SafetyState::Estop;
  }
  if (g_fault_latched) {
    return SafetyState::Fault;
  }
  if (commandTimedOut(now_ms)) {
    return SafetyState::SafeDisabled;
  }
  if (g_last_command.enable_motors_request) {
    return SafetyState::Armed;
  }
  return SafetyState::SafeDisabled;
}

void applySafetyPolicy(uint32_t now_ms) {
  if (estopPressed()) {
    latchFault("estop_physical");
  }
  if (g_last_command.estop_request) {
    latchFault("estop_software");
  }
  if (commandTimedOut(now_ms) && !g_fault_latched) {
    g_fault_code = "heartbeat_timeout";
    setMotorConsent(false);
    return;
  }

  const bool may_enable = !g_fault_latched &&
                          !estopPressed() &&
                          !commandTimedOut(now_ms) &&
                          g_last_command.enable_motors_request;
  setMotorConsent(may_enable);
}

void handleCommandLine(const char* line) {
  SafetyCommandFrame parsed;
  const char* error = "none";
  if (!axiom::parseSafetyCommandJson(line, parsed, error)) {
    g_fault_code = error;
    return;
  }

  g_last_command = parsed;
  g_last_command_ms = millis();
  if (parsed.estop_request) {
    latchFault("estop_software");
  } else if (!g_fault_latched) {
    g_fault_code = "none";
  }
}

void pollSerial() {
  while (Serial.available() > 0) {
    const char c = static_cast<char>(Serial.read());
    if (c == '\r') {
      continue;
    }
    if (c == '\n') {
      g_line[g_line_len] = '\0';
      if (g_line_len > 0) {
        handleCommandLine(g_line);
      }
      g_line_len = 0;
      continue;
    }
    if (g_line_len + 1 < kLineBufferSize) {
      g_line[g_line_len++] = c;
    } else {
      g_line_len = 0;
      latchFault("serial_line_overflow");
    }
  }
}

void publishStatus(uint32_t now_ms) {
  McuStatusFrame status;
  status.seq_ack = g_last_command.seq;
  status.mcu_uptime_ms = now_ms;
  status.safety_state = currentSafetyState(now_ms);
  status.estop_active = estopPressed() || g_fault_latched;
  status.motor_consent = digitalRead(PIN_MOTOR_CONSENT) == HIGH;
  status.fault_code = g_fault_code;
  status.fault_latched = g_fault_latched;
  const uint32_t age_ms = now_ms - g_last_command_ms;
  status.heartbeat_age_ms = static_cast<uint16_t>(age_ms > 65535U ? 65535U : age_ms);
  status.sensor_validity = 0U;  // IMU/ToF/VESC bits will be enabled during HIL bringup.
  status.degraded_mode = commandTimedOut(now_ms) ? "link_loss_hold" : "none";
  status.roll_rad = 0.0f;
  status.pitch_rad = 0.0f;
  status.battery_voltage_v = 0.0f;
  status.motor_current_a = 0.0f;
  axiom::writeStatusJson(Serial, status);
}

void setup() {
  pinMode(PIN_ESTOP_NC, INPUT_PULLUP);
  pinMode(PIN_MOTOR_CONSENT, OUTPUT);
  pinMode(PIN_DUMP_LOAD, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);

  setMotorConsent(false);
  digitalWrite(PIN_DUMP_LOAD, LOW);
  digitalWrite(PIN_STATUS_LED, LOW);

  Serial.begin(115200);
  g_last_command_ms = millis();
  Serial.println("{\"boot\":true,\"fw\":\"axiom_stm32_safety_mcu_v0.1\"}");
}

void loop() {
  const uint32_t now_ms = millis();
  pollSerial();
  applySafetyPolicy(now_ms);

  digitalWrite(PIN_STATUS_LED, digitalRead(PIN_MOTOR_CONSENT) == HIGH ? HIGH : LOW);

  if (now_ms - g_last_status_ms >= kStatusPeriodMs) {
    g_last_status_ms = now_ms;
    publishStatus(now_ms);
  }
}
