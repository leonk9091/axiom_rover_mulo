#!/usr/bin/env python3
"""
VESC Driver Node - Axiom Rover "Mulo"
Implementa:
  - Comunicazione CAN bus con 4x Dual VESC (pyvesc + python-can)
  - Cinematica differenziale 4WD: Twist → RPM per ruota
  - Frenata rigenerativa: rilevamento decelerazione → brake_current
  - Gestione fault VESC (over-temp, over-current, DRV fault)
  - Telemetria completa (RPM, Amp, Temp, Duty, Voltage) a 20Hz
  - E-Stop hardware: duty 0 immediato su tutti i motori
  - Integrazione con rover_interfaces/MotorTelemetry

Architettura CAN (da wiring_walkthrough.md):
  - Dual VESC 1: CAN ID 1 (FL) + CAN ID 2 (RL)
  - Dual VESC 2: CAN ID 3 (FR) + CAN ID 4 (RR)
  - VESC 3:      CAN ID 5 (Verricello)
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Float32
import math
import time
import threading

# pyvesc + python-can (pip install pyvesc python-can)
try:
    import can
    import pyvesc
    from pyvesc.VESC.messages import SetDutyCycle, SetRPM, SetCurrentBrake
    from pyvesc.VESC.messages import GetValues
    CAN_AVAILABLE = True
except ImportError:
    CAN_AVAILABLE = False

# rover_interfaces (disponibili dopo colcon build)
try:
    from rover_interfaces.msg import MotorTelemetry, RoverState, StabilityMargin
    INTERFACES_AVAILABLE = True
except ImportError:
    from std_msgs.msg import Float64MultiArray
    INTERFACES_AVAILABLE = False

# ---------------------------------------------------------------------------
# Parametri fisici rover (da mulo_specs.md e motor_selection.md)
# ---------------------------------------------------------------------------
WHEEL_RADIUS_M      = 0.254         # m  (ruota cargo 20" → r = 10" = 0.254m)
WHEELBASE_M         = 0.8           # m  (interasse)
TRACK_WIDTH_M       = 0.6           # m  (carreggiata)
GEAR_RATIO          = 71.5          # riduzione planetaria Stepperonline
MOTOR_POLE_PAIRS    = 7             # coppie polari motore brushless (tipico)
# RPM_meccanici = RPM_elettrici / POLE_PAIRS / GEAR_RATIO
# Velocità lineare [m/s] = RPM_meccanici * 2π * WHEEL_RADIUS / 60

MAX_RPM_MOTOR       = 3000          # RPM elettrici massimi (limite sicurezza)
MAX_CURRENT_A       = 30.0          # A  (limite corrente per motore)
MAX_BRAKE_CURRENT_A = 20.0          # A  (limite corrente frenata rigenerativa)
MAX_DUTY            = 0.85          # duty massimo (85% per margine termico)

# Soglie frenata rigenerativa
REGEN_DECEL_THRESHOLD = 0.05        # m/s² - decelerazione minima per attivare regen
REGEN_DECEL_WINDOW_S  = 0.1         # s  - finestra temporale per calcolo decelerazione

# CAN
CAN_INTERFACE       = 'can0'
CAN_BITRATE         = 500000        # 500 kbps (standard VESC)
CAN_TIMEOUT_S       = 0.05          # s  (timeout risposta VESC)

# CAN ID motori (da wiring_walkthrough.md)
MOTOR_FL_ID         = 1             # Front Left
MOTOR_RL_ID         = 2             # Rear Left
MOTOR_FR_ID         = 3             # Front Right
MOTOR_RR_ID         = 4             # Rear Right
MOTOR_IDS           = [MOTOR_FL_ID, MOTOR_RL_ID, MOTOR_FR_ID, MOTOR_RR_ID]

# Segno RPM per orientamento motori (FL/RL invertiti rispetto FR/RR)
MOTOR_SIGN          = {
    MOTOR_FL_ID: +1,
    MOTOR_RL_ID: +1,
    MOTOR_FR_ID: -1,
    MOTOR_RR_ID: -1,
}

# Soglie fault
TEMP_MOTOR_WARN_C   = 80.0
TEMP_MOTOR_FAULT_C  = 100.0
TEMP_ESC_WARN_C     = 70.0
TEMP_ESC_FAULT_C    = 85.0
VOLTAGE_MIN_V       = 20.0          # V  (batteria LiFePO4 24V quasi scarica)
VOLTAGE_MAX_V       = 29.4          # V  (batteria LiFePO4 24V carica)

TELEMETRY_HZ        = 20
CONTROL_HZ          = 50


def rpm_to_ms(rpm_electrical: float) -> float:
    """Converte RPM elettrici in velocità lineare ruota [m/s]."""
    rpm_mech = rpm_electrical / (MOTOR_POLE_PAIRS * GEAR_RATIO)
    return rpm_mech * 2.0 * math.pi * WHEEL_RADIUS_M / 60.0


def ms_to_rpm(v_ms: float) -> float:
    """Converte velocità lineare [m/s] in RPM elettrici."""
    rpm_mech = v_ms * 60.0 / (2.0 * math.pi * WHEEL_RADIUS_M)
    return rpm_mech * MOTOR_POLE_PAIRS * GEAR_RATIO


class VESCCANInterface:
    """
    Interfaccia CAN per comunicazione con VESC tramite python-can + pyvesc.
    Thread-safe: usa lock per accesso al bus CAN.
    """
    def __init__(self, interface: str, bitrate: int, logger):
        self.logger = logger
        self._lock = threading.Lock()
        self._bus = None
        self.connected = False

        if not CAN_AVAILABLE:
            logger.warn("pyvesc/python-can non installati. Modalità simulata.")
            return

        try:
            self._bus = can.interface.Bus(
                channel=interface,
                bustype='socketcan',
                bitrate=bitrate
            )
            self.connected = True
            logger.info(f"CAN bus connesso: {interface} @ {bitrate} bps")
        except Exception as e:
            logger.warn(f"CAN bus non disponibile ({e}). Modalità simulata.")

    def set_rpm(self, motor_id: int, rpm: int):
        """Invia comando RPM a un VESC via CAN."""
        if not self.connected:
            return
        msg_bytes = pyvesc.encode(SetRPM(rpm))
        can_msg = can.Message(
            arbitration_id=motor_id | 0x300,  # VESC CAN extended ID format
            data=msg_bytes,
            is_extended_id=True
        )
        with self._lock:
            try:
                self._bus.send(can_msg, timeout=CAN_TIMEOUT_S)
            except can.CanError as e:
                self.logger.error(f"CAN TX error motor {motor_id}: {e}")

    def set_duty(self, motor_id: int, duty: float):
        """Invia comando duty cycle [-1, +1] a un VESC via CAN."""
        if not self.connected:
            return
        duty_clamped = max(-MAX_DUTY, min(MAX_DUTY, duty))
        msg_bytes = pyvesc.encode(SetDutyCycle(duty_clamped))
        can_msg = can.Message(
            arbitration_id=motor_id | 0x100,
            data=msg_bytes,
            is_extended_id=True
        )
        with self._lock:
            try:
                self._bus.send(can_msg, timeout=CAN_TIMEOUT_S)
            except can.CanError as e:
                self.logger.error(f"CAN TX error motor {motor_id}: {e}")

    def set_brake_current(self, motor_id: int, current_a: float):
        """Invia corrente di frenata rigenerativa [A]."""
        if not self.connected:
            return
        current_clamped = max(0.0, min(MAX_BRAKE_CURRENT_A, current_a))
        msg_bytes = pyvesc.encode(SetCurrentBrake(current_clamped))
        can_msg = can.Message(
            arbitration_id=motor_id | 0x200,
            data=msg_bytes,
            is_extended_id=True
        )
        with self._lock:
            try:
                self._bus.send(can_msg, timeout=CAN_TIMEOUT_S)
            except can.CanError as e:
                self.logger.error(f"CAN TX error motor {motor_id}: {e}")

    def get_values(self, motor_id: int) -> dict | None:
        """
        Richiede telemetria a un VESC e attende risposta.
        Restituisce dict con rpm, current, duty, temp_motor, temp_esc, voltage, fault.
        """
        if not self.connected:
            return self._simulated_values(motor_id)

        request = pyvesc.encode_request(GetValues)
        can_msg = can.Message(
            arbitration_id=motor_id | 0x400,
            data=request,
            is_extended_id=True
        )
        with self._lock:
            try:
                self._bus.send(can_msg, timeout=CAN_TIMEOUT_S)
                # Attendi risposta (filtra per ID motore)
                deadline = time.monotonic() + CAN_TIMEOUT_S
                while time.monotonic() < deadline:
                    rx = self._bus.recv(timeout=CAN_TIMEOUT_S)
                    if rx and (rx.arbitration_id & 0xFF) == motor_id:
                        msg, _ = pyvesc.decode(bytes(rx.data))
                        if isinstance(msg, GetValues):
                            return {
                                "rpm":        msg.rpm,
                                "current_a":  msg.avg_motor_current,
                                "duty":       msg.duty_cycle_now,
                                "temp_motor": msg.temp_motor,
                                "temp_esc":   msg.temp_fet,
                                "voltage":    msg.input_voltage,
                                "fault":      msg.mc_fault_code,
                            }
            except (can.CanError, Exception) as e:
                self.logger.debug(f"CAN RX error motor {motor_id}: {e}")
        return None

    def _simulated_values(self, motor_id: int) -> dict:
        """Valori simulati per test senza hardware."""
        return {
            "rpm": 0, "current_a": 0.0, "duty": 0.0,
            "temp_motor": 25.0, "temp_esc": 25.0,
            "voltage": 24.0, "fault": 0,
        }

    def close(self):
        if self._bus:
            self._bus.shutdown()


class DifferentialKinematics4WD:
    """
    Cinematica differenziale per rover 4WD con sterzo skid.
    Converte Twist (v, ω) in velocità lineare per ciascuna ruota.
    """
    def __init__(self):
        self.half_track = TRACK_WIDTH_M / 2.0

    def twist_to_wheel_velocities(self, v: float, omega: float) -> dict[int, float]:
        """
        Restituisce {motor_id: velocità_lineare_ms} per i 4 motori.
        Skid steering: ruote sinistra/destra hanno velocità diverse.
        """
        v_left  = v - omega * self.half_track
        v_right = v + omega * self.half_track

        # Limita alla velocità massima
        v_max = rpm_to_ms(MAX_RPM_MOTOR)
        scale = max(abs(v_left), abs(v_right)) / v_max
        if scale > 1.0:
            v_left  /= scale
            v_right /= scale

        return {
            MOTOR_FL_ID: v_left,
            MOTOR_RL_ID: v_left,
            MOTOR_FR_ID: v_right,
            MOTOR_RR_ID: v_right,
        }

    def wheel_velocities_to_rpm(self, wheel_vels: dict[int, float]) -> dict[int, int]:
        """Converte velocità lineari [m/s] in RPM elettrici per ogni motore."""
        return {
            mid: int(ms_to_rpm(v) * MOTOR_SIGN[mid])
            for mid, v in wheel_vels.items()
        }


class RegenBrakeController:
    """
    Gestisce la frenata rigenerativa rilevando decelerazioni rapide.
    Calcola la corrente di frenata proporzionale alla decelerazione.
    """
    def __init__(self):
        self._prev_v = 0.0
        self._prev_time = time.monotonic()

    def compute_brake_current(self, v_cmd: float) -> float | None:
        """
        Restituisce la corrente di frenata [A] se necessaria, altrimenti None.
        """
        now = time.monotonic()
        dt = now - self._prev_time
        if dt < REGEN_DECEL_WINDOW_S:
            return None

        decel = (self._prev_v - v_cmd) / dt  # positivo = decelerazione
        self._prev_v = v_cmd
        self._prev_time = now

        if decel > REGEN_DECEL_THRESHOLD:
            # Corrente proporzionale alla decelerazione (max a 1 m/s²)
            brake_current = min(MAX_BRAKE_CURRENT_A, decel * MAX_BRAKE_CURRENT_A)
            return brake_current
        return None


class VescDriverNode(Node):
    def __init__(self):
        super().__init__('vesc_driver')
        self.get_logger().info('Initializing VESC Driver Node (CAN + 4WD + Regen)...')

        # Parametri ROS
        self.declare_parameter('can_interface', CAN_INTERFACE)
        self.declare_parameter('max_linear_vel', 1.2)
        self.declare_parameter('max_angular_vel', 1.5)

        can_iface = self.get_parameter('can_interface').get_parameter_value().string_value

        # QoS safety
        qos_reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            depth=10
        )

        # --- Stato ---
        self.estop_active   = False
        self.cmd_v          = 0.0
        self.cmd_omega      = 0.0
        self.battery_soc    = 0.0
        self.stability_margin = 1.0
        self.active_cmd_source = 'legacy'
        self._last_cmd_time = time.monotonic()
        self._cmd_timeout_s = 0.5   # stop se nessun cmd per 500ms
        self._telemetry: dict[int, dict] = {mid: {} for mid in MOTOR_IDS}
        self._fault_active: dict[int, bool] = {mid: False for mid in MOTOR_IDS}

        # --- Componenti ---
        self.can_iface  = VESCCANInterface(can_iface, CAN_BITRATE, self.get_logger())
        self.kinematics = DifferentialKinematics4WD()
        self.regen      = RegenBrakeController()

        # --- Subscriptions ---
        self.create_subscription(Twist, 'cmd_vel', self._cb_cmd_vel, 10)
        self.create_subscription(Twist, 'mission/cmd_vel', self._cb_mission_cmd_vel, 10)
        self.create_subscription(Bool, 'safety/estop', self._cb_estop, qos_reliable)
        self.create_subscription(Float32, 'battery/soc_estimated', self._cb_battery_soc, 10)
        if INTERFACES_AVAILABLE:
            self.create_subscription(StabilityMargin, 'safety/stability_margin', self._cb_stability_margin, 10)

        # --- Publishers ---
        if INTERFACES_AVAILABLE:
            self.telemetry_pub = self.create_publisher(MotorTelemetry, 'motor_telemetry', 10)
            self.rover_state_pub = self.create_publisher(RoverState, 'control/rover_state', 10)
        else:
            self.telemetry_pub = self.create_publisher(
                __import__('std_msgs.msg', fromlist=['Float64MultiArray']).Float64MultiArray,
                'motor_telemetry', 10
            )
            self.rover_state_pub = None
        self.slip_pub = self.create_publisher(Float32, 'control/slip_ratio', 10)

        # --- Timer ---
        self.create_timer(1.0 / CONTROL_HZ,   self._control_loop)
        self.create_timer(1.0 / TELEMETRY_HZ, self._telemetry_loop)

        self.get_logger().info(
            f"VESC Driver ready. CAN: {can_iface} | "
            f"Motors: {MOTOR_IDS} | Sim: {not self.can_iface.connected}"
        )

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _cb_cmd_vel(self, msg: Twist):
        self._apply_cmd_vel(msg, source='legacy')

    def _cb_mission_cmd_vel(self, msg: Twist):
        self._apply_cmd_vel(msg, source='mission')

    def _apply_cmd_vel(self, msg: Twist, source: str):
        if self.estop_active:
            return
        max_v = self.get_parameter('max_linear_vel').get_parameter_value().double_value
        max_w = self.get_parameter('max_angular_vel').get_parameter_value().double_value
        self.cmd_v     = max(-max_v, min(max_v, msg.linear.x))
        self.cmd_omega = max(-max_w, min(max_w, msg.angular.z))
        self.active_cmd_source = source
        self._last_cmd_time = time.monotonic()

    def _cb_estop(self, msg: Bool):
        if msg.data and not self.estop_active:
            self.estop_active = True
            self._stop_all_motors()
            self.get_logger().fatal("E-STOP ricevuto: tutti i motori fermati.")

    def _cb_battery_soc(self, msg: Float32):
        self.battery_soc = msg.data

    def _cb_stability_margin(self, msg: StabilityMargin):
        self.stability_margin = msg.margin

    # ------------------------------------------------------------------
    # Control Loop (50 Hz)
    # ------------------------------------------------------------------
    def _control_loop(self):
        # Timeout comando: se nessun cmd_vel arriva, ferma il rover
        if (time.monotonic() - self._last_cmd_time) > self._cmd_timeout_s:
            self.cmd_v = 0.0
            self.cmd_omega = 0.0

        if self.estop_active:
            self._stop_all_motors()
            return

        # Controlla fault termici prima di inviare comandi
        if self._any_critical_fault():
            self.estop_active = True
            self._stop_all_motors()
            return

        # Calcola velocità ruote
        wheel_vels = self.kinematics.twist_to_wheel_velocities(self.cmd_v, self.cmd_omega)

        # Controlla frenata rigenerativa
        brake_current = self.regen.compute_brake_current(self.cmd_v)

        for motor_id, v_wheel in wheel_vels.items():
            if brake_current is not None and abs(self.cmd_v) < 0.01:
                # Frenata rigenerativa: applica brake current
                self.can_iface.set_brake_current(motor_id, brake_current)
            else:
                # Controllo RPM normale
                rpm = int(ms_to_rpm(v_wheel) * MOTOR_SIGN[motor_id])
                rpm = max(-MAX_RPM_MOTOR, min(MAX_RPM_MOTOR, rpm))
                self.can_iface.set_rpm(motor_id, rpm)

    # ------------------------------------------------------------------
    # Telemetry Loop (20 Hz)
    # ------------------------------------------------------------------
    def _telemetry_loop(self):
        for motor_id in MOTOR_IDS:
            values = self.can_iface.get_values(motor_id)
            if values:
                self._telemetry[motor_id] = values
                self._check_motor_fault(motor_id, values)

        self._publish_telemetry()

    def _check_motor_fault(self, motor_id: int, values: dict):
        """Controlla soglie termiche e fault VESC."""
        faults = []

        if values.get("temp_motor", 0) > TEMP_MOTOR_FAULT_C:
            faults.append(f"Motor {motor_id}: OVER-TEMP motore {values['temp_motor']:.1f}°C")
        elif values.get("temp_motor", 0) > TEMP_MOTOR_WARN_C:
            self.get_logger().warn(f"Motor {motor_id}: temp motore alta {values['temp_motor']:.1f}°C")

        if values.get("temp_esc", 0) > TEMP_ESC_FAULT_C:
            faults.append(f"Motor {motor_id}: OVER-TEMP ESC {values['temp_esc']:.1f}°C")

        if values.get("voltage", 24.0) < VOLTAGE_MIN_V:
            faults.append(f"Motor {motor_id}: UNDER-VOLTAGE {values['voltage']:.1f}V")

        if values.get("fault", 0) != 0:
            faults.append(f"Motor {motor_id}: VESC FAULT CODE {values['fault']}")

        for fault_msg in faults:
            self.get_logger().error(fault_msg)
            self._fault_active[motor_id] = True

    def _any_critical_fault(self) -> bool:
        return any(self._fault_active.values())

    def _stop_all_motors(self):
        for motor_id in MOTOR_IDS:
            self.can_iface.set_duty(motor_id, 0.0)

    def _publish_telemetry(self):
        if INTERFACES_AVAILABLE:
            msg = MotorTelemetry()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.motor_ids    = MOTOR_IDS
            msg.rpm          = [float(self._telemetry[m].get("rpm", 0))        for m in MOTOR_IDS]
            msg.current_a    = [float(self._telemetry[m].get("current_a", 0))  for m in MOTOR_IDS]
            msg.duty_cycle   = [float(self._telemetry[m].get("duty", 0))       for m in MOTOR_IDS]
            msg.temp_motor_c = [float(self._telemetry[m].get("temp_motor", 0)) for m in MOTOR_IDS]
            msg.temp_esc_c   = [float(self._telemetry[m].get("temp_esc", 0))   for m in MOTOR_IDS]
            msg.voltage_input_v = [float(self._telemetry[m].get("voltage", 0)) for m in MOTOR_IDS]
            msg.fault_codes  = [float(self._telemetry[m].get("fault", 0))      for m in MOTOR_IDS]
        else:
            from std_msgs.msg import Float64MultiArray
            msg = Float64MultiArray()
            msg.data = []
            for m in MOTOR_IDS:
                t = self._telemetry[m]
                msg.data += [
                    float(t.get("rpm", 0)), float(t.get("current_a", 0)),
                    float(t.get("temp_motor", 0))
                ]
        self.telemetry_pub.publish(msg)
        self._publish_rover_state()

    def _publish_rover_state(self):
        avg_speed = 0.0
        if self._telemetry:
            avg_speed = sum(
                rpm_to_ms(float(self._telemetry[m].get("rpm", 0.0))) * MOTOR_SIGN[m]
                for m in MOTOR_IDS
            ) / len(MOTOR_IDS)
        slip_ratio = 0.0
        if abs(self.cmd_v) > 0.05:
            slip_ratio = max(-1.0, min(1.0, (self.cmd_v - avg_speed) / abs(self.cmd_v)))
        self.slip_pub.publish(Float32(data=float(slip_ratio)))
        if not INTERFACES_AVAILABLE or self.rover_state_pub is None:
            return

        state = RoverState()
        state.header.stamp = self.get_clock().now().to_msg()
        state.mode = 'mission' if self.active_cmd_source == 'mission' else 'manual'
        state.linear_velocity_ms = float(avg_speed)
        state.angular_velocity_rads = float(self.cmd_omega)
        state.average_wheel_speed_ms = float(avg_speed)
        state.slip_ratio = float(slip_ratio)
        state.pitch_rad = 0.0
        state.roll_rad = 0.0
        state.battery_soc = float(self.battery_soc)
        state.stability_margin = float(self.stability_margin)
        state.localization_ok = True
        state.drive_ready = not self._any_critical_fault()
        state.estop_active = bool(self.estop_active)
        self.rover_state_pub.publish(state)

    def destroy_node(self):
        self._stop_all_motors()
        self.can_iface.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VescDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
