#!/usr/bin/env python3
"""
Winch Manager Node - Axiom Rover "Mulo"
Implementa:
  - PID sulla tensione del cavo con anti-windup
  - Controllo modale (passive / assisted / anchor)
  - ZMP (Zero-Moment Point) anti-ribaltamento in tempo reale
  - Modello dinamico cavo linearizzato (Eulero-Lagrange: molla-smorzatore)
  - Emergency stop hardware-aware (pubblica su /safety/estop)
"""
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String, Float32, Bool
from geometry_msgs.msg import Vector3
import math

from rover_interfaces.msg import StabilityMargin, WinchCommand, WinchState

# ---------------------------------------------------------------------------
# Costanti fisiche rover (da winch_dynamics.md e mulo_specs.md)
# ---------------------------------------------------------------------------
ROVER_MASS_KG       = 80.0      # kg (rover vuoto)
GRAVITY             = 9.81      # m/s²
WHEELBASE           = 0.8       # m (interasse)
TRACK_WIDTH         = 0.6       # m (carreggiata, da URDF box width)
COG_HEIGHT          = 0.2       # m (altezza baricentro)
WINCH_HEIGHT        = 0.35      # m (altezza punto di tiro rispetto suolo)
WINCH_HEIGHT_REL    = WINCH_HEIGHT - COG_HEIGHT  # braccio rispetto CoG

# Modello cavo (Eulero-Lagrange linearizzato: cavo = molla + smorzatore)
CABLE_STIFFNESS_K   = 8000.0    # N/m  (rigidezza cavo)
CABLE_DAMPING_C     = 120.0     # N·s/m (smorzamento cavo)
CABLE_MASS          = 0.5       # kg   (massa cavo distribuita, approssimata)

# Limiti operativi
MAX_TENSION_N       = 500.0     # N  (carico di rottura limite)
WARN_TENSION_N      = 380.0     # N  (soglia warning pre-emergenza)
MAX_PITCH_RAD       = 0.45      # rad (~26°)
MAX_ROLL_RAD        = 0.35      # rad (~20°)
SAFETY_FACTOR_ZMP   = 1.3       # margine ZMP

# PID gains (tensione)
KP_TENSION          = 0.012
KI_TENSION          = 0.003
KD_TENSION          = 0.006
ANTI_WINDUP_LIMIT   = 50.0      # limite integrale anti-windup

# Setpoint tensione per modalità
TENSION_PASSIVE_N   = 30.0      # N  (tensione minima per non impigliarsi)
TENSION_ASSISTED_N  = 200.0     # N  (tiro assistito standard)
TENSION_ANCHOR_N    = 420.0     # N  (ancoraggio massimo)

CONTROL_DT          = 0.1       # s  (periodo loop controllo 10 Hz)


class CableDynamicsModel:
    """
    Modello dinamico linearizzato del cavo basato su Eulero-Lagrange.
    Stato: [elongazione x, velocità elongazione x_dot]
    Equazione: m_eff * x_ddot + c * x_dot + k * x = F_ext
    """
    def __init__(self):
        self.x     = 0.0   # elongazione [m]
        self.x_dot = 0.0   # velocità elongazione [m/s]
        self.m_eff = CABLE_MASS / 3.0  # massa efficace (distribuzione lineare)

    def step(self, f_ext: float, dt: float) -> float:
        """
        Integra il modello con Eulero esplicito.
        Restituisce la tensione stimata [N].
        """
        x_ddot = (f_ext - CABLE_DAMPING_C * self.x_dot - CABLE_STIFFNESS_K * self.x) / self.m_eff
        self.x_dot += x_ddot * dt
        self.x     += self.x_dot * dt
        tension_estimated = CABLE_STIFFNESS_K * self.x + CABLE_DAMPING_C * self.x_dot
        return max(0.0, tension_estimated)

    def reset(self):
        self.x = 0.0
        self.x_dot = 0.0


class TensionPID:
    """PID con anti-windup e derivative filtering."""
    def __init__(self, kp, ki, kd, dt, windup_limit):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.windup_limit = windup_limit
        self._integral  = 0.0
        self._prev_error = 0.0
        self._alpha = 0.1  # filtro derivata (EMA)
        self._d_filtered = 0.0

    def compute(self, setpoint: float, measured: float) -> float:
        error = setpoint - measured
        self._integral = max(-self.windup_limit,
                             min(self.windup_limit,
                                 self._integral + error * self.dt))
        derivative_raw = (error - self._prev_error) / self.dt
        self._d_filtered = self._alpha * derivative_raw + (1.0 - self._alpha) * self._d_filtered
        output = self.kp * error + self.ki * self._integral + self.kd * self._d_filtered
        self._prev_error = error
        return output

    def reset(self):
        self._integral   = 0.0
        self._prev_error = 0.0
        self._d_filtered = 0.0


class ZMPStabilityMonitor:
    """
    Calcola il Zero-Moment Point proiettato sul piano del suolo.
    Supporto: rettangolo definito da wheelbase x track_width.
    Considera: peso rover, forza verricello, angoli IMU.
    """
    def __init__(self):
        self.half_wb = WHEELBASE / 2.0
        self.half_tw = TRACK_WIDTH / 2.0

    def compute_zmp(self, pitch_rad: float, roll_rad: float,
                    tension_n: float) -> tuple[float, float]:
        """
        Restituisce (zmp_x, zmp_y) nel frame rover [m].
        zmp_x positivo = verso anteriore.
        """
        weight = ROVER_MASS_KG * GRAVITY
        # Componente peso proiettata
        fx_gravity = weight * math.sin(pitch_rad)
        fz_gravity = weight * math.cos(pitch_rad) * math.cos(roll_rad)
        # Momento ribaltante del verricello (tiro orizzontale approssimato)
        # Il cavo tira in avanti/alto: momento = tensione * braccio verticale
        moment_winch_pitch = tension_n * WINCH_HEIGHT_REL
        moment_gravity_pitch = fz_gravity * 0.0  # CoG centrato per definizione

        # ZMP longitudinale (pitch)
        zmp_x = (moment_winch_pitch - fx_gravity * COG_HEIGHT) / fz_gravity if fz_gravity > 1.0 else 0.0

        # ZMP laterale (roll) — forza laterale da pendenza laterale
        fy_gravity = weight * math.sin(roll_rad)
        zmp_y = (-fy_gravity * COG_HEIGHT) / fz_gravity if fz_gravity > 1.0 else 0.0

        return zmp_x, zmp_y

    def is_stable(self, pitch_rad: float, roll_rad: float,
                  tension_n: float) -> tuple[bool, float]:
        """
        Restituisce (stabile, margine_normalizzato).
        margine = 1.0 → ZMP al centro; 0.0 → ZMP al bordo; <0 → ribaltamento.
        """
        zmp_x, zmp_y = self.compute_zmp(pitch_rad, roll_rad, tension_n)
        # Margine normalizzato rispetto al poligono di supporto
        margin_x = 1.0 - abs(zmp_x) / (self.half_wb / SAFETY_FACTOR_ZMP)
        margin_y = 1.0 - abs(zmp_y) / (self.half_tw / SAFETY_FACTOR_ZMP)
        margin = min(margin_x, margin_y)
        return margin > 0.0, margin


class WinchManagerNode(Node):
    def __init__(self):
        super().__init__('winch_manager')
        self.get_logger().info('Initializing Winch Manager Node (PID + ZMP + Euler-Lagrange)...')

        # --- Stato ---
        self.current_mode    = "passive"
        self.current_tension = 0.0
        self.current_pitch   = 0.0
        self.current_roll    = 0.0
        self.cable_length    = 0.0   # m (da encoder)
        self.cable_velocity  = 0.0   # m/s (derivata encoder)
        self._prev_cable_len = 0.0
        self.estop_active    = False
        self.external_stability_margin = 1.0
        self.external_safe_tension_n = MAX_TENSION_N
        self.current_setpoint_n = TENSION_PASSIVE_N

        # --- Componenti ---
        self.cable_model = CableDynamicsModel()
        self.pid = TensionPID(KP_TENSION, KI_TENSION, KD_TENSION,
                              CONTROL_DT, ANTI_WINDUP_LIMIT)
        self.zmp_monitor = ZMPStabilityMonitor()

        # --- Subscriptions ---
        self.create_subscription(Float32, 'winch/load_cell_tension',
                                 self._cb_tension, 10)
        self.create_subscription(Float32, 'sensors/pitch',
                                 self._cb_pitch, 10)
        self.create_subscription(Float32, 'sensors/roll',
                                 self._cb_roll, 10)
        self.create_subscription(Float32, 'winch/cable_length_m',
                                 self._cb_cable_length, 10)
        self.create_subscription(String, 'winch/set_mode',
                                 self._cb_set_mode, 10)
        self.create_subscription(WinchCommand, 'mission/winch_command',
                                 self._cb_winch_command, 10)
        self.create_subscription(Bool, 'safety/estop',
                                 self._cb_estop, 10)
        self.create_subscription(StabilityMargin, 'safety/stability_margin',
                                 self._cb_stability_margin, 10)

        # --- Publishers ---
        self.status_pub       = self.create_publisher(String,  'winch/status', 10)
        self.motor_cmd_pub    = self.create_publisher(Float32, 'winch/motor_duty', 10)
        self.estop_pub        = self.create_publisher(Bool,    'safety/estop', 10)
        self.zmp_pub          = self.create_publisher(Vector3, 'winch/zmp_debug', 10)
        self.tension_est_pub  = self.create_publisher(Float32, 'winch/tension_estimated', 10)
        self.winch_state_pub  = self.create_publisher(WinchState, 'winch/state', 10)

        self.create_timer(CONTROL_DT, self._control_loop)
        self.get_logger().info('Winch Manager ready.')

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _cb_tension(self, msg: Float32):
        self.current_tension = msg.data
        if self.current_tension > MAX_TENSION_N:
            self._trigger_estop(f"Tensione critica: {self.current_tension:.1f} N > {MAX_TENSION_N} N")
        elif self.current_tension > WARN_TENSION_N:
            self.get_logger().warn(f"Tensione alta: {self.current_tension:.1f} N")

    def _cb_pitch(self, msg: Float32):
        self.current_pitch = msg.data
        if abs(self.current_pitch) > MAX_PITCH_RAD:
            self._trigger_estop(f"Pitch critico: {math.degrees(self.current_pitch):.1f}°")

    def _cb_roll(self, msg: Float32):
        self.current_roll = msg.data
        if abs(self.current_roll) > MAX_ROLL_RAD:
            self._trigger_estop(f"Roll critico: {math.degrees(self.current_roll):.1f}°")

    def _cb_cable_length(self, msg: Float32):
        self.cable_velocity  = (msg.data - self._prev_cable_len) / CONTROL_DT
        self._prev_cable_len = self.cable_length
        self.cable_length    = msg.data

    def _cb_set_mode(self, msg: String):
        new_mode = msg.data.lower()
        if new_mode not in ("passive", "assisted", "anchor"):
            self.get_logger().warn(f"Modalità sconosciuta: {new_mode}")
            return
        if self.estop_active:
            self.get_logger().error("E-Stop attivo: impossibile cambiare modalità.")
            return
        self.current_mode = new_mode
        self.current_setpoint_n = {
            "passive": TENSION_PASSIVE_N,
            "assisted": TENSION_ASSISTED_N,
            "anchor": TENSION_ANCHOR_N,
        }.get(new_mode, TENSION_PASSIVE_N)
        self.pid.reset()
        self.cable_model.reset()
        self.get_logger().info(f"Modalità verricello: {new_mode}")

    def _cb_estop(self, msg: Bool):
        if msg.data and not self.estop_active:
            self._trigger_estop("E-Stop ricevuto da topic esterno")

    def _cb_stability_margin(self, msg: StabilityMargin):
        self.external_stability_margin = msg.margin
        self.external_safe_tension_n = max(20.0, msg.safe_winch_tension_n)

    def _cb_winch_command(self, msg: WinchCommand):
        if msg.inhibit_motion:
            self._publish_motor_cmd(0.0)
            return
        requested_mode = msg.mode.lower().strip()
        if requested_mode:
            self._cb_set_mode(String(data=requested_mode))
        if msg.tension_setpoint_n > 0.0:
            self.current_setpoint_n = min(msg.tension_setpoint_n, self.external_safe_tension_n)

    # ------------------------------------------------------------------
    # Control Loop (10 Hz)
    # ------------------------------------------------------------------
    def _control_loop(self):
        if self.estop_active:
            self._publish_motor_cmd(0.0)
            return

        # 1. Aggiorna modello dinamico cavo
        # La forza esterna è la forza applicata dal motore (stimata dal duty precedente)
        # Qui usiamo la tensione misurata come feedback diretto al modello
        tension_model = self.cable_model.step(self.current_tension, CONTROL_DT)
        self.tension_est_pub.publish(Float32(data=float(tension_model)))

        # 2. Verifica ZMP
        stable, zmp_margin = self.zmp_monitor.is_stable(
            self.current_pitch, self.current_roll, self.current_tension)

        zmp_x, zmp_y = self.zmp_monitor.compute_zmp(
            self.current_pitch, self.current_roll, self.current_tension)
        self.zmp_pub.publish(Vector3(x=zmp_x, y=zmp_y, z=float(zmp_margin)))

        effective_margin = min(zmp_margin, self.external_stability_margin)

        if not stable or effective_margin <= 0.0:
            self._trigger_estop(f"ZMP fuori poligono di supporto (margine={zmp_margin:.3f})")
            return

        # 3. Seleziona setpoint tensione in base alla modalità
        setpoint = min(self._get_tension_setpoint(effective_margin), self.external_safe_tension_n)
        self.current_setpoint_n = setpoint

        # 4. PID → duty cycle motore verricello [-1.0, +1.0]
        duty = self.pid.compute(setpoint, self.current_tension)
        duty = max(-1.0, min(1.0, duty))

        # 5. Riduzione preventiva se ZMP si avvicina al limite (margine < 0.3)
        if effective_margin < 0.3:
            scale = max(0.1, effective_margin / 0.3)
            duty *= scale
            self.get_logger().warn(f"Stability margin basso ({effective_margin:.2f}): duty scalato a {duty:.3f}")

        self._publish_motor_cmd(duty)
        self._publish_status(setpoint, duty, effective_margin)
        self._publish_winch_state(setpoint, duty, tension_model, effective_margin)

    def _get_tension_setpoint(self, zmp_margin: float) -> float:
        base = self.current_setpoint_n

        # Riduzione proporzionale se ZMP si avvicina al limite
        if zmp_margin < 0.5:
            reduction = 1.0 - (0.5 - zmp_margin)  # lineare da 1.0 a 0.5
            base *= max(0.3, reduction)
        return base

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _publish_motor_cmd(self, duty: float):
        self.motor_cmd_pub.publish(Float32(data=float(duty)))

    def _publish_status(self, setpoint: float, duty: float, zmp_margin: float):
        status = (f"mode={self.current_mode} | "
                  f"tension={self.current_tension:.1f}N (sp={setpoint:.1f}N) | "
                  f"duty={duty:.3f} | "
                  f"pitch={math.degrees(self.current_pitch):.1f}° | "
                  f"zmp_margin={zmp_margin:.3f}")
        self.status_pub.publish(String(data=status))

    def _publish_winch_state(self, setpoint: float, duty: float, tension_model: float, stability_margin: float):
        msg = WinchState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.mode = self.current_mode
        msg.tension_measured_n = float(self.current_tension)
        msg.tension_estimated_n = float(tension_model)
        msg.tension_setpoint_n = float(setpoint)
        msg.cable_length_m = float(self.cable_length)
        msg.cable_velocity_ms = float(self.cable_velocity)
        msg.motor_duty = float(duty)
        msg.stability_margin = float(stability_margin)
        msg.stability_limited = stability_margin < 0.5
        msg.estop_active = bool(self.estop_active)
        self.winch_state_pub.publish(msg)

    def _trigger_estop(self, reason: str):
        if self.estop_active:
            return
        self.estop_active = True
        self.current_mode = "passive"
        self.pid.reset()
        self.cable_model.reset()
        self._publish_motor_cmd(0.0)
        self.estop_pub.publish(Bool(data=True))
        self.get_logger().error(f"EMERGENCY STOP: {reason}")


def main(args=None):
    rclpy.init(args=args)
    node = WinchManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
