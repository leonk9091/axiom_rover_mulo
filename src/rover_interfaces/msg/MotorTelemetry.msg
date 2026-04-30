std_msgs/Header header
int32[]   motor_ids          # [1,2,3,4]
float32[] rpm                # RPM per motore
float32[] current_a          # Ampere per motore
float32[] duty_cycle         # [-1,+1] per motore
float32[] temp_motor_c       # °C temperatura motore
float32[] temp_esc_c         # °C temperatura ESC
float32[] voltage_input_v    # V tensione ingresso per ESC
float32[] fault_codes        # codice fault VESC (0=OK)
