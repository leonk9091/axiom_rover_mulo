#include <Arduino.h>
#include "rex_protocol.hpp"

using axiom_rex::RexCommandFrame;
using axiom_rex::RexFault;
using axiom_rex::RexMeasurements;
using axiom_rex::RexState;

// Logical Nucleo pinout. Confirm on the final carrier before wiring fuel/ignition.
static constexpr uint8_t PIN_SAFETY_KILL_IN = D2;       // Active LOW from safety MCU/E-stop chain.
static constexpr uint8_t PIN_RPM_HALL = D3;             // Interrupt input, one pulse per rev target.
static constexpr uint8_t PIN_KILL_IGNITION = D7;        // HIGH = kill GX50 ignition via opto/relay.
static constexpr uint8_t PIN_THROTTLE_PWM = D9;         // PWM command to external servo driver.
static constexpr uint8_t PIN_DUMP_LOAD = D8;            // HIGH = dump/load request.
static constexpr uint8_t PIN_STATUS_LED = LED_BUILTIN;

static constexpr uint8_t PIN_VDC_RAW = A0;
static constexpr uint8_t PIN_ICHARGE = A1;
static constexpr uint8_t PIN_RECTIFIER_TEMP = A2;
static constexpr uint8_t PIN_BUCK_TEMP = A3;
static constexpr uint8_t PIN_EXHAUST_TEMP = A4;

static constexpr uint32_t kStatusPeriodMs = 100;        // 10 Hz toward ROS/logging.
static constexpr size_t kLineBufferSize = 512;
static constexpr float kAdcRefV = 3.3f;
static constexpr float kAdcMax = 1023.0f;
static constexpr float kVdcScale = 25.0f;               // 3.3 V ADC -> 82.5 V via divider.
static constexpr float kAcsZeroV = 2.5f;                // ACS758-style centered output.
static constexpr float kAcsSensitivityVA = 0.040f;      // 40 mV/A placeholder; calibrate.

RexCommandFrame g_last_command;
RexState g_state = RexState::Disabled;
RexFault g_fault = RexFault::Disabled;
const char* g_reason = "boot disabled";

uint32_t g_last_command_ms = 0;
uint32_t g_last_status_ms = 0;
uint32_t g_no_charge_start_ms = 0;
volatile uint32_t g_rpm_pulses = 0;
uint32_t g_last_rpm_sample_ms = 0;
uint32_t g_last_rpm_pulses = 0;
float g_rpm = 0.0f;

char g_line[kLineBufferSize];
size_t g_line_len = 0;

void onRpmPulse() {
  g_rpm_pulses++;
}

float readAdcVoltage(uint8_t pin) {
  return (analogRead(pin) * kAdcRefV) / kAdcMax;
}

float readTemperaturePlaceholder(uint8_t pin) {
  // Placeholder NTC transfer: calibrate before bench evidence.
  return readAdcVoltage(pin) * 30.0f;
}

RexMeasurements readMeasurements(uint32_t now_ms) {
  if (g_last_rpm_sample_ms == 0) {
    g_last_rpm_sample_ms = now_ms;
    g_last_rpm_pulses = g_rpm_pulses;
  } else if (now_ms - g_last_rpm_sample_ms >= 250) {
    const uint32_t pulses = g_rpm_pulses;
    const uint32_t delta_pulses = pulses - g_last_rpm_pulses;
    const uint32_t delta_ms = now_ms - g_last_rpm_sample_ms;
    g_rpm = (60000.0f * static_cast<float>(delta_pulses)) / static_cast<float>(delta_ms);
    g_last_rpm_pulses = pulses;
    g_last_rpm_sample_ms = now_ms;
  }

  RexMeasurements m;
  m.rpm = g_rpm;
  m.dc_link_voltage_v = readAdcVoltage(PIN_VDC_RAW) * kVdcScale;
  const float charge_sensor_v = readAdcVoltage(PIN_ICHARGE);
  m.charge_current_a = max(0.0f, (charge_sensor_v - kAcsZeroV) / kAcsSensitivityVA);
  m.rectifier_temp_c = readTemperaturePlaceholder(PIN_RECTIFIER_TEMP);
  m.buck_temp_c = readTemperaturePlaceholder(PIN_BUCK_TEMP);
  m.exhaust_zone_temp_c = readTemperaturePlaceholder(PIN_EXHAUST_TEMP);
  return m;
}

bool safetyKillActive() {
  return digitalRead(PIN_SAFETY_KILL_IN) == LOW;
}

bool commandTimedOut(uint32_t now_ms) {
  return (now_ms - g_last_command_ms) > axiom_rex::kCommandTimeoutMs;
}

void setKillIgnition(bool kill) {
  digitalWrite(PIN_KILL_IGNITION, kill ? HIGH : LOW);
}

void setThrottle(float request) {
  const float clamped = axiom_rex::clampFloat(request, 0.0f, 1.0f);
  const int duty = static_cast<int>(clamped * 255.0f);
  analogWrite(PIN_THROTTLE_PWM, duty);
}

void forceSafeOutputs() {
  setThrottle(0.0f);
  digitalWrite(PIN_DUMP_LOAD, LOW);
  setKillIgnition(true);
}

void latchFault(RexFault fault, const char* reason) {
  g_fault = fault;
  g_state = RexState::Fault;
  g_reason = reason;
  forceSafeOutputs();
}

void applyRexPolicy(uint32_t now_ms, const RexMeasurements& m) {
  if (safetyKillActive() || g_last_command.ice_kill) {
    latchFault(RexFault::EstopOrSafetyKill, "safety kill input or ice_kill command active");
    return;
  }
  if (commandTimedOut(now_ms)) {
    latchFault(RexFault::CommandTimeout, "rex command timeout");
    return;
  }
  if (m.rpm > axiom_rex::kMaxRpm) {
    latchFault(RexFault::RpmOverspeed, "rpm above gx50/rex limit");
    return;
  }
  if (m.dc_link_voltage_v > axiom_rex::kMaxDcLinkV) {
    latchFault(RexFault::DcLinkOvervoltage, "dc link above limit");
    return;
  }

  const bool generation_requested = g_last_command.ice_on && g_last_command.charge_current_a > 0.1f;
  if (!generation_requested) {
    g_state = RexState::Idle;
    g_fault = RexFault::None;
    g_reason = "idle, generation not requested";
    setThrottle(0.0f);
    setKillIgnition(false);
    digitalWrite(PIN_DUMP_LOAD, g_last_command.dump_load ? HIGH : LOW);
    g_no_charge_start_ms = 0;
    return;
  }

  const bool clutch_should_charge = m.rpm >= axiom_rex::kClutchEngageRpm;
  if (clutch_should_charge && m.charge_current_a < axiom_rex::kNoChargeCurrentA) {
    if (g_no_charge_start_ms == 0) {
      g_no_charge_start_ms = now_ms;
    } else if (now_ms - g_no_charge_start_ms > axiom_rex::kNoChargeTimeoutMs) {
      latchFault(RexFault::NoChargeCurrent, "no charge current with clutch engaged");
      return;
    }
  } else {
    g_no_charge_start_ms = 0;
  }

  g_state = clutch_should_charge ? RexState::Generating : RexState::SpoolUp;
  g_fault = RexFault::None;
  g_reason = clutch_should_charge ? "closed-loop generation active" : "spooling to clutch engage rpm";
  setKillIgnition(false);
  setThrottle(g_last_command.throttle_request);
  digitalWrite(PIN_DUMP_LOAD, g_last_command.dump_load ? HIGH : LOW);
}

void handleCommandLine(const char* line) {
  RexCommandFrame parsed;
  RexFault fault = RexFault::None;
  if (!axiom_rex::parseRexCommandJson(line, parsed, fault)) {
    latchFault(fault, "invalid rex auxiliary command");
    return;
  }
  g_last_command = parsed;
  g_last_command_ms = millis();
  if (g_state == RexState::Disabled && !parsed.ice_on) {
    g_fault = RexFault::None;
    g_reason = "valid command received, waiting idle";
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
      latchFault(RexFault::CrcError, "serial line overflow");
    }
  }
}

void publishStatus(const RexMeasurements& measurements) {
  const bool faulted = g_state == RexState::Fault || g_state == RexState::Disabled;
  const bool generation_enable = g_state == RexState::SpoolUp || g_state == RexState::Generating;
  axiom_rex::writeRexStatusJson(
      Serial,
      g_last_command,
      g_state,
      g_fault,
      measurements,
      generation_enable && !faulted,
      faulted,
      generation_enable && !faulted,
      g_last_command.dump_load,
      generation_enable && !faulted ? g_last_command.throttle_request : 0.0f,
      g_reason);
}

void setup() {
  pinMode(PIN_SAFETY_KILL_IN, INPUT_PULLUP);
  pinMode(PIN_RPM_HALL, INPUT_PULLUP);
  pinMode(PIN_KILL_IGNITION, OUTPUT);
  pinMode(PIN_THROTTLE_PWM, OUTPUT);
  pinMode(PIN_DUMP_LOAD, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);

  forceSafeOutputs();
  attachInterrupt(digitalPinToInterrupt(PIN_RPM_HALL), onRpmPulse, RISING);

  Serial.begin(115200);
  g_last_command_ms = millis();
  Serial.println("{\"boot\":true,\"fw\":\"axiom_stm32_rex_controller_v0.1\"}");
}

void loop() {
  const uint32_t now_ms = millis();
  pollSerial();
  RexMeasurements measurements = readMeasurements(now_ms);
  applyRexPolicy(now_ms, measurements);

  digitalWrite(PIN_STATUS_LED, g_state == RexState::Generating ? HIGH : LOW);

  if (now_ms - g_last_status_ms >= kStatusPeriodMs) {
    g_last_status_ms = now_ms;
    publishStatus(measurements);
  }
}
