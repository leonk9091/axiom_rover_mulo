std_msgs/Header header

# GX50 range extender supervisory state.
# States are emitted by rover_power and consumed by the STM32 REX controller.
uint8 STATE_DISABLED=0
uint8 STATE_IDLE=1
uint8 STATE_SPOOL_UP=2
uint8 STATE_GENERATING=3
uint8 STATE_COOLDOWN=4
uint8 STATE_FAULT=5

uint16 FAULT_NONE=0
uint16 FAULT_DISABLED=1
uint16 FAULT_SOC_HIGH=2
uint16 FAULT_BUS_OVERVOLTAGE=3
uint16 FAULT_RPM_OVERSPEED=4
uint16 FAULT_DC_LINK_OVERVOLTAGE=5
uint16 FAULT_NO_CHARGE_CURRENT=6
uint16 FAULT_THERMAL_DERATE=7

uint8 state
uint16 fault_code
string state_label
string fault_label
string reason

bool engine_start_request
bool engine_kill_request
bool generation_enable
bool dump_load_request

float32 generator_power_target_w
float32 charge_current_target_a
float32 throttle_request

float32 measured_generator_power_w
float32 measured_charge_current_a
float32 rpm
float32 dc_link_voltage_v
float32 thermal_headroom
