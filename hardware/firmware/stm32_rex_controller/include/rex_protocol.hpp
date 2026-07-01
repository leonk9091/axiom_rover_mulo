#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

namespace axiom_rex {

static constexpr uint16_t kCommandTimeoutMs = 500;
static constexpr float kMaxChargeCurrentA = 24.0f;
static constexpr float kMaxThrottle = 1.0f;
static constexpr float kMaxDcLinkV = 70.0f;
static constexpr float kMaxRpm = 7500.0f;
static constexpr float kClutchEngageRpm = 4400.0f;
static constexpr float kNoChargeCurrentA = 0.5f;
static constexpr uint32_t kNoChargeTimeoutMs = 2000;

enum class RexState : uint8_t {
  Disabled = 0,
  Idle = 1,
  SpoolUp = 2,
  Generating = 3,
  Cooldown = 4,
  Fault = 5,
};

enum class RexFault : uint16_t {
  None = 0,
  Disabled = 1,
  SocHigh = 2,
  BusOvervoltage = 3,
  RpmOverspeed = 4,
  DcLinkOvervoltage = 5,
  NoChargeCurrent = 6,
  ThermalDerate = 7,
  CommandTimeout = 8,
  CrcError = 9,
  EstopOrSafetyKill = 10,
};

struct RexCommandFrame {
  uint32_t seq = 0;
  bool ice_on = false;
  bool ice_kill = false;
  bool dump_load = false;
  float charge_current_a = 0.0f;
  float throttle_request = 0.0f;
  uint16_t aux_crc16 = 0;
};

struct RexMeasurements {
  float rpm = 0.0f;
  float dc_link_voltage_v = 0.0f;
  float charge_current_a = 0.0f;
  float rectifier_temp_c = 0.0f;
  float buck_temp_c = 0.0f;
  float exhaust_zone_temp_c = 0.0f;
};

inline float clampFloat(float value, float low, float high) {
  if (value < low) return low;
  if (value > high) return high;
  return value;
}

inline const char* stateLabel(RexState state) {
  switch (state) {
    case RexState::Disabled: return "DISABLED";
    case RexState::Idle: return "IDLE";
    case RexState::SpoolUp: return "SPOOL_UP";
    case RexState::Generating: return "GENERATING";
    case RexState::Cooldown: return "COOLDOWN";
    case RexState::Fault: return "FAULT";
  }
  return "FAULT";
}

inline const char* faultLabel(RexFault fault) {
  switch (fault) {
    case RexFault::None: return "NONE";
    case RexFault::Disabled: return "DISABLED";
    case RexFault::SocHigh: return "SOC_HIGH";
    case RexFault::BusOvervoltage: return "BUS_OVERVOLTAGE";
    case RexFault::RpmOverspeed: return "RPM_OVERSPEED";
    case RexFault::DcLinkOvervoltage: return "DC_LINK_OVERVOLTAGE";
    case RexFault::NoChargeCurrent: return "NO_CHARGE_CURRENT";
    case RexFault::ThermalDerate: return "THERMAL_DERATE";
    case RexFault::CommandTimeout: return "COMMAND_TIMEOUT";
    case RexFault::CrcError: return "CRC_ERROR";
    case RexFault::EstopOrSafetyKill: return "ESTOP_OR_SAFETY_KILL";
  }
  return "UNKNOWN";
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

inline void buildAuxCommandCrcInput(const RexCommandFrame& frame, char* out, size_t out_len) {
  snprintf(
      out,
      out_len,
      "seq=%lu;ice_on=%u;ice_kill=%u;dump_load=%u;"
      "rex_charge_current_a=%.3f;rex_throttle_request=%.3f",
      static_cast<unsigned long>(frame.seq),
      frame.ice_on ? 1 : 0,
      frame.ice_kill ? 1 : 0,
      frame.dump_load ? 1 : 0,
      static_cast<double>(frame.charge_current_a),
      static_cast<double>(frame.throttle_request));
}

inline bool parseRexCommandJson(const char* line, RexCommandFrame& out, RexFault& fault) {
  JsonDocument doc;
  DeserializationError json_error = deserializeJson(doc, line);
  if (json_error) {
    fault = RexFault::CrcError;
    return false;
  }

  RexCommandFrame frame;
  frame.seq = doc["seq"] | 0U;
  frame.ice_on = doc["ice_on"] | false;
  frame.ice_kill = doc["ice_kill"] | false;
  frame.dump_load = doc["dump_load"] | false;
  frame.charge_current_a = clampFloat(doc["rex_charge_current_a"] | 0.0f, 0.0f, kMaxChargeCurrentA);
  frame.throttle_request = clampFloat(doc["rex_throttle_request"] | 0.0f, 0.0f, kMaxThrottle);
  frame.aux_crc16 = doc["aux_crc16"] | 0U;

  if (frame.aux_crc16 == 0U) {
    fault = RexFault::CrcError;
    return false;
  }

  char crc_input[192];
  buildAuxCommandCrcInput(frame, crc_input, sizeof(crc_input));
  if (crc16CcittFalse(crc_input) != frame.aux_crc16) {
    fault = RexFault::CrcError;
    return false;
  }

  out = frame;
  fault = RexFault::None;
  return true;
}

inline void writeRexStatusJson(
    Stream& stream,
    const RexCommandFrame& command,
    RexState state,
    RexFault fault,
    const RexMeasurements& measurements,
    bool engine_start_request,
    bool engine_kill_request,
    bool generation_enable,
    bool dump_load_request,
    float throttle_request,
    const char* reason) {
  JsonDocument doc;
  doc["seq_ack"] = command.seq;
  doc["state"] = static_cast<uint8_t>(state);
  doc["state_label"] = stateLabel(state);
  doc["fault_code"] = static_cast<uint16_t>(fault);
  doc["fault_label"] = faultLabel(fault);
  doc["reason"] = reason;
  doc["engine_start_request"] = engine_start_request;
  doc["engine_kill_request"] = engine_kill_request;
  doc["generation_enable"] = generation_enable;
  doc["dump_load_request"] = dump_load_request;
  doc["charge_current_target_a"] = command.charge_current_a;
  doc["throttle_request"] = throttle_request;
  doc["rpm"] = measurements.rpm;
  doc["dc_link_voltage_v"] = measurements.dc_link_voltage_v;
  doc["charge_current_a"] = measurements.charge_current_a;
  doc["rectifier_temp_c"] = measurements.rectifier_temp_c;
  doc["buck_temp_c"] = measurements.buck_temp_c;
  doc["exhaust_zone_temp_c"] = measurements.exhaust_zone_temp_c;
  serializeJson(doc, stream);
  stream.println();
}

}  // namespace axiom_rex
