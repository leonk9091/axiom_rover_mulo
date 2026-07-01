#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

namespace axiom {

static constexpr uint16_t kHeartbeatTimeoutMs = 500;
static constexpr uint16_t kCommandTimeoutMinMs = 50;
static constexpr uint16_t kCommandTimeoutMaxMs = 500;
static constexpr float kMaxLinearVelocityMs = 1.2f;
static constexpr float kMaxAngularVelocityRads = 1.5f;
static constexpr float kMaxCurrentA = 30.0f;

enum class SafetyState {
  Boot,
  SafeDisabled,
  Armed,
  Degraded,
  Estop,
  Fault,
};

struct SafetyCommandFrame {
  uint32_t seq = 0;
  uint32_t stamp_ms = 0;
  char mode[24] = "manual";
  float desired_linear_velocity_ms = 0.0f;
  float desired_angular_velocity_rads = 0.0f;
  uint16_t timeout_ms = 250;
  bool estop_request = false;
  bool enable_motors_request = false;
  float max_current_a = 0.0f;
  uint16_t crc16 = 0;
};

struct McuStatusFrame {
  uint32_t seq_ack = 0;
  uint32_t mcu_uptime_ms = 0;
  SafetyState safety_state = SafetyState::Boot;
  bool estop_active = false;
  bool motor_consent = false;
  const char* fault_code = "none";
  bool fault_latched = false;
  uint16_t heartbeat_age_ms = kHeartbeatTimeoutMs;
  uint32_t sensor_validity = 0;
  const char* degraded_mode = "none";
  float roll_rad = 0.0f;
  float pitch_rad = 0.0f;
  float battery_voltage_v = 0.0f;
  float motor_current_a = 0.0f;
  uint16_t crc16 = 0;
};

inline float clampFloat(float value, float low, float high) {
  if (value < low) return low;
  if (value > high) return high;
  return value;
}

inline uint16_t clampU16(uint32_t value, uint16_t low, uint16_t high) {
  if (value < low) return low;
  if (value > high) return high;
  return static_cast<uint16_t>(value);
}

inline const char* safetyStateName(SafetyState state) {
  switch (state) {
    case SafetyState::Boot: return "boot";
    case SafetyState::SafeDisabled: return "safe_disabled";
    case SafetyState::Armed: return "armed";
    case SafetyState::Degraded: return "degraded";
    case SafetyState::Estop: return "estop";
    case SafetyState::Fault: return "fault";
  }
  return "fault";
}

inline uint16_t crc16CcittFalse(const uint8_t* data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; ++i) {
    crc ^= static_cast<uint16_t>(data[i]) << 8;
    for (uint8_t bit = 0; bit < 8; ++bit) {
      crc = (crc & 0x8000) ? static_cast<uint16_t>((crc << 1) ^ 0x1021)
                           : static_cast<uint16_t>(crc << 1);
    }
  }
  return crc;
}

inline uint16_t crc16CcittFalse(const char* data) {
  return crc16CcittFalse(reinterpret_cast<const uint8_t*>(data), strlen(data));
}

inline void buildCommandCrcInput(const SafetyCommandFrame& frame, char* out, size_t out_len) {
  snprintf(
      out,
      out_len,
      "seq=%lu;stamp_ms=%lu;mode=%s;desired_linear_velocity_ms=%.3f;"
      "desired_angular_velocity_rads=%.3f;timeout_ms=%u;estop_request=%u;"
      "enable_motors_request=%u;max_current_a=%.3f",
      static_cast<unsigned long>(frame.seq),
      static_cast<unsigned long>(frame.stamp_ms),
      frame.mode,
      static_cast<double>(frame.desired_linear_velocity_ms),
      static_cast<double>(frame.desired_angular_velocity_rads),
      frame.timeout_ms,
      frame.estop_request ? 1 : 0,
      frame.enable_motors_request ? 1 : 0,
      static_cast<double>(frame.max_current_a));
}

inline bool parseSafetyCommandJson(const char* line, SafetyCommandFrame& out, const char*& error) {
  JsonDocument doc;
  DeserializationError json_error = deserializeJson(doc, line);
  if (json_error) {
    error = "json_parse_error";
    return false;
  }

  SafetyCommandFrame frame;
  frame.seq = doc["seq"] | 0U;
  frame.stamp_ms = doc["stamp_ms"] | 0U;
  const char* mode = doc["mode"] | "manual";
  strncpy(frame.mode, mode, sizeof(frame.mode) - 1);
  frame.mode[sizeof(frame.mode) - 1] = '\0';
  frame.desired_linear_velocity_ms = clampFloat(doc["desired_linear_velocity_ms"] | 0.0f,
                                                -kMaxLinearVelocityMs,
                                                kMaxLinearVelocityMs);
  frame.desired_angular_velocity_rads = clampFloat(doc["desired_angular_velocity_rads"] | 0.0f,
                                                   -kMaxAngularVelocityRads,
                                                   kMaxAngularVelocityRads);
  frame.timeout_ms = clampU16(doc["timeout_ms"] | 250U,
                              kCommandTimeoutMinMs,
                              kCommandTimeoutMaxMs);
  frame.estop_request = doc["estop_request"] | (doc["estop"] | false);
  frame.enable_motors_request = doc["enable_motors_request"] | false;
  frame.max_current_a = clampFloat(doc["max_current_a"] | 0.0f, 0.0f, kMaxCurrentA);
  frame.crc16 = doc["crc16"] | 0U;

  if (frame.crc16 == 0U) {
    error = "unsigned_command";
    return false;
  }

  char crc_input[256];
  buildCommandCrcInput(frame, crc_input, sizeof(crc_input));
  if (crc16CcittFalse(crc_input) != frame.crc16) {
    error = "crc_error";
    return false;
  }

  out = frame;
  error = "none";
  return true;
}

inline uint16_t computeStatusCrc(const McuStatusFrame& frame) {
  char payload[256];
  snprintf(
      payload,
      sizeof(payload),
      "seq_ack=%lu;mcu_uptime_ms=%lu;safety_state=%s;estop_active=%u;"
      "motor_consent=%u;fault_code=%s;fault_latched=%u;heartbeat_age_ms=%u;"
      "sensor_validity=%lu;degraded_mode=%s;roll_rad=%.3f;pitch_rad=%.3f;"
      "battery_voltage_v=%.3f;motor_current_a=%.3f",
      static_cast<unsigned long>(frame.seq_ack),
      static_cast<unsigned long>(frame.mcu_uptime_ms),
      safetyStateName(frame.safety_state),
      frame.estop_active ? 1 : 0,
      frame.motor_consent ? 1 : 0,
      frame.fault_code,
      frame.fault_latched ? 1 : 0,
      frame.heartbeat_age_ms,
      static_cast<unsigned long>(frame.sensor_validity),
      frame.degraded_mode,
      static_cast<double>(frame.roll_rad),
      static_cast<double>(frame.pitch_rad),
      static_cast<double>(frame.battery_voltage_v),
      static_cast<double>(frame.motor_current_a));
  return crc16CcittFalse(payload);
}

inline void writeStatusJson(Stream& stream, McuStatusFrame frame) {
  frame.crc16 = computeStatusCrc(frame);

  JsonDocument doc;
  doc["seq_ack"] = frame.seq_ack;
  doc["ack"] = frame.seq_ack;
  doc["mcu_uptime_ms"] = frame.mcu_uptime_ms;
  doc["safety_state"] = safetyStateName(frame.safety_state);
  doc["estop_active"] = frame.estop_active;
  doc["estop_hw"] = frame.estop_active;
  doc["motor_consent"] = frame.motor_consent;
  doc["fault_code"] = frame.fault_code;
  doc["fault_latched"] = frame.fault_latched;
  doc["heartbeat_age_ms"] = frame.heartbeat_age_ms;
  doc["sensor_validity"] = frame.sensor_validity;
  doc["degraded_mode"] = frame.degraded_mode;
  doc["roll_rad"] = frame.roll_rad;
  doc["pitch_rad"] = frame.pitch_rad;
  doc["battery_voltage_v"] = frame.battery_voltage_v;
  doc["motor_current_a"] = frame.motor_current_a;
  doc["crc16"] = frame.crc16;
  serializeJson(doc, stream);
  stream.println();
}

}  // namespace axiom
