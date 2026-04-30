std_msgs/Header header
string mode                  # passive | assisted | anchor
float32 tension_measured_n   # N - cella di carico
float32 tension_estimated_n  # N - modello Eulero-Lagrange
float32 tension_setpoint_n   # N - setpoint PID
float32 motor_duty           # [-1.0, +1.0]
float32 cable_length_m       # m - da encoder
float32 cable_velocity_ms    # m/s
float32 zmp_x                # m - ZMP longitudinale
float32 zmp_y                # m - ZMP laterale
float32 zmp_margin           # [0,1] - margine stabilità
bool    estop_active
