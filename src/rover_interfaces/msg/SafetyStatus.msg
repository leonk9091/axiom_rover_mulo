std_msgs/Header header
bool    system_ok
bool    estop_active
bool    estop_hw_triggered   # pulsante fisico ESP32
string  estop_reason
string[] active_faults       # lista fault attivi (JSON serializzato)
bool[]  node_alive           # stato nodi: [winch, power, nav, vesc]
float32 watchdog_age_s       # s - età ultimo heartbeat ESP32
