std_msgs/Header header
float32 power_demand_w       # W - richiesta totale sistema
float32 power_battery_w      # W - quota batteria (pos=scarica, neg=ricarica)
float32 power_ice_w          # W - quota generatore ICE
float32 soc                  # [0,1] - State of Charge (EKF)
float32 soh                  # [0,1] - State of Health (EKF)
float32 voltage_v            # V - tensione bus
float32 current_a            # A - corrente batteria
float32 ecms_s_factor        # fattore equivalenza ECMS
float32 fuel_equivalent_gs   # g/s - consumo equivalente carburante
bool    ice_active
bool    dump_load_active
