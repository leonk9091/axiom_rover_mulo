#!/usr/bin/env python3
"""
Person Following Node - Axiom Rover "Mulo"
Implementa:
  - YOLOv11 per detection persona (gambe/torso)
  - LiDAR-Inertial Odometry (LIO-SAM) per localizzazione robusta
  - Terrain Classifier CNN per adattamento parametri trazione
  - Unscented Kalman Filter (UKF) per fusione IMU + odometria + visione
  - PID adattivo per inseguimento a distanza target
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped, PoseWithCovarianceStamped
from sensor_msgs.msg import Image, PointCloud2, Imu
from std_msgs.msg import Float32, String
from nav_msgs.msg import Odometry
import numpy as np
import math
from filterpy.kalman import UnscentedKalmanFilter as UKF
from filterpy.kalman import MerweScaledSigmaPoints

# Placeholder imports (da installare: pip install ultralytics opencv-python torch torchvision)
# import cv2
# from cv_bridge import CvBridge
# from ultralytics import YOLO
# import torch
# import torch.nn as nn

# ---------------------------------------------------------------------------
# Parametri inseguimento
# ---------------------------------------------------------------------------
TARGET_DISTANCE_M   = 1.5       # m  (distanza target dalla persona)
TARGET_TOLERANCE_M  = 0.2       # m  (banda morta)
MAX_LINEAR_VEL      = 1.0       # m/s
MAX_ANGULAR_VEL     = 0.8       # rad/s

# PID inseguimento
KP_LINEAR           = 0.5
KI_LINEAR           = 0.02
KD_LINEAR           = 0.1
KP_ANGULAR          = 1.2
KI_ANGULAR          = 0.01
KD_ANGULAR          = 0.05

# UKF parametri
UKF_DT              = 0.05      # s  (20 Hz)
UKF_ALPHA           = 0.001
UKF_BETA            = 2.0
UKF_KAPPA           = 0.0

# Terrain classifier
TERRAIN_CLASSES = ["asphalt", "gravel", "grass", "sand", "mud", "rock"]
TERRAIN_TRACTION_FACTORS = {
    "asphalt": 1.0,
    "gravel":  0.85,
    "grass":   0.75,
    "sand":    0.60,
    "mud":     0.50,
    "rock":    0.70,
}


class TerrainClassifierCNN:
    """
    Classificatore CNN per tipo di terreno.
    Architettura: MobileNetV3-Small pre-trained + fine-tuning su RUGD dataset.
    Input: RGB image 224x224
    Output: classe terreno + confidence
    """
    def __init__(self):
        # Placeholder: carica modello PyTorch
        # self.model = torch.load('terrain_classifier_mobilenetv3.pth')
        # self.model.eval()
        # self.transform = torchvision.transforms.Compose([...])
        self.current_terrain = "asphalt"
        self.confidence = 1.0

    def classify(self, rgb_image_np: np.ndarray) -> tuple[str, float]:
        """
        Classifica il terreno dall'immagine RGB.
        Restituisce (classe, confidence).
        """
        # Preprocessing + inference
        # img_tensor = self.transform(rgb_image_np).unsqueeze(0)
        # with torch.no_grad():
        #     logits = self.model(img_tensor)
        #     probs = torch.softmax(logits, dim=1)
        #     class_idx = torch.argmax(probs).item()
        #     confidence = probs[0, class_idx].item()
        # return TERRAIN_CLASSES[class_idx], confidence

        # Placeholder
        return self.current_terrain, self.confidence

    def get_traction_factor(self) -> float:
        return TERRAIN_TRACTION_FACTORS.get(self.current_terrain, 0.8)


class PersonFollowingUKF:
    """
    Unscented Kalman Filter per fusione sensoriale.

    Stato x = [x, y, theta, v, omega]
      - (x, y): posizione nel frame odom [m]
      - theta: orientamento [rad]
      - v: velocità lineare [m/s]
      - omega: velocità angolare [rad/s]

    Misure:
      - z_odom: [x, y, theta] da LIO-SAM odometry
      - z_vision: [range, bearing] da YOLO detection + depth
      - z_imu: [omega] da IMU
    """
    def __init__(self):
        points = MerweScaledSigmaPoints(n=5, alpha=UKF_ALPHA, beta=UKF_BETA, kappa=UKF_KAPPA)
        self.ukf = UKF(dim_x=5, dim_z=3, dt=UKF_DT, fx=self._fx, hx=self._hx, points=points)

        # Stato iniziale
        self.ukf.x = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        # Covarianza iniziale
        self.ukf.P = np.diag([0.1, 0.1, 0.05, 0.1, 0.05])
        # Rumore processo
        self.ukf.Q = np.diag([0.01, 0.01, 0.005, 0.02, 0.01])
        # Rumore misura (adattato dinamicamente)
        self.ukf.R = np.diag([0.05, 0.05, 0.02])

    def _fx(self, x, dt):
        """Modello di transizione: cinematica differenziale."""
        x_pos, y_pos, theta, v, omega = x
        x_new = x_pos + v * math.cos(theta) * dt
        y_new = y_pos + v * math.sin(theta) * dt
        theta_new = theta + omega * dt
        theta_new = math.atan2(math.sin(theta_new), math.cos(theta_new))  # wrap
        return np.array([x_new, y_new, theta_new, v, omega])

    def _hx(self, x):
        """Modello di misura: [x, y, theta] da odometria."""
        return x[:3]

    def predict(self):
        self.ukf.predict()

    def update_odom(self, x_odom, y_odom, theta_odom):
        z = np.array([x_odom, y_odom, theta_odom])
        self.ukf.update(z)

    def update_vision(self, range_m, bearing_rad):
        """Aggiorna con misura visione (range, bearing) convertita in (x, y)."""
        x_rel = range_m * math.cos(bearing_rad)
        y_rel = range_m * math.sin(bearing_rad)
        # Trasforma in frame odom
        theta = self.ukf.x[2]
        x_abs = self.ukf.x[0] + x_rel * math.cos(theta) - y_rel * math.sin(theta)
        y_abs = self.ukf.x[1] + x_rel * math.sin(theta) + y_rel * math.cos(theta)
        # Misura: [x_target, y_target, theta_unchanged]
        z = np.array([x_abs, y_abs, theta])
        # Aumenta rumore misura per visione (meno precisa di LIO)
        R_vision = np.diag([0.3, 0.3, 0.1])
        self.ukf.R = R_vision
        self.ukf.update(z)
        self.ukf.R = np.diag([0.05, 0.05, 0.02])  # ripristina

    def update_imu(self, omega_imu):
        """Aggiorna con velocità angolare IMU."""
        # Misura: [x_unchanged, y_unchanged, omega]
        z = np.array([self.ukf.x[0], self.ukf.x[1], omega_imu])
        R_imu = np.diag([1e6, 1e6, 0.01])  # solo omega è informativo
        self.ukf.R = R_imu
        self.ukf.update(z)
        self.ukf.R = np.diag([0.05, 0.05, 0.02])

    @property
    def state(self) -> dict:
        return {
            "x": self.ukf.x[0],
            "y": self.ukf.x[1],
            "theta": self.ukf.x[2],
            "v": self.ukf.x[3],
            "omega": self.ukf.x[4],
        }


class PIDController:
    def __init__(self, kp, ki, kd, dt, limit):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.limit = limit
        self._integral = 0.0
        self._prev_error = 0.0

    def compute(self, error: float) -> float:
        self._integral += error * self.dt
        self._integral = max(-self.limit, min(self.limit, self._integral))
        derivative = (error - self._prev_error) / self.dt
        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        self._prev_error = error
        return output

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0


class PersonFollowingNode(Node):
    def __init__(self):
        super().__init__('person_following')
        self.get_logger().info('Initializing Person Following Node (YOLOv11 + LIO-SAM + UKF)...')

        # --- Stato ---
        self.person_detected = False
        self.person_range_m  = 0.0
        self.person_bearing_rad = 0.0
        self.lio_odom_x      = 0.0
        self.lio_odom_y      = 0.0
        self.lio_odom_theta  = 0.0
        self.imu_omega       = 0.0
        self.terrain_type    = "asphalt"
        self.traction_factor = 1.0

        # --- Componenti ---
        self.ukf = PersonFollowingUKF()
        self.pid_linear  = PIDController(KP_LINEAR, KI_LINEAR, KD_LINEAR, UKF_DT, 10.0)
        self.pid_angular = PIDController(KP_ANGULAR, KI_ANGULAR, KD_ANGULAR, UKF_DT, 5.0)
        self.terrain_classifier = TerrainClassifierCNN()

        # YOLO model (placeholder)
        # self.yolo = YOLO('yolov11n.pt')
        # self.bridge = CvBridge()

        # --- Subscriptions ---
        self.create_subscription(Image, 'camera/rgb/image_raw',
                                 self._cb_rgb, 10)
        self.create_subscription(PointCloud2, 'camera/depth/points',
                                 self._cb_depth, 10)
        # LIO-SAM odometry (topic standard)
        self.create_subscription(Odometry, 'lio_sam/mapping/odometry',
                                 self._cb_lio_odom, 10)
        self.create_subscription(Imu, 'imu/data',
                                 self._cb_imu, 10)

        # --- Publishers ---
        self.cmd_vel_pub    = self.create_publisher(Twist, 'cmd_vel', 10)
        self.terrain_pub    = self.create_publisher(String, 'navigation/terrain_type', 10)
        self.traction_pub   = self.create_publisher(Float32, 'navigation/traction_factor', 10)
        self.target_pose_pub = self.create_publisher(PoseStamped, 'navigation/target_pose', 10)

        # --- Timer ---
        self.create_timer(UKF_DT, self._control_loop)

        self.get_logger().info('Person Following ready. Target distance: 1.5m')

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _cb_rgb(self, msg: Image):
        """YOLO detection + terrain classification."""
        # rgb_np = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

        # 1. YOLO detection persona
        # results = self.yolo(rgb_np, classes=[0])  # class 0 = person
        # if len(results[0].boxes) > 0:
        #     box = results[0].boxes[0]  # prendi la detection più vicina
        #     cx, cy = box.xywh[0][:2].cpu().numpy()
        #     self.person_detected = True
        #     # Calcola bearing (angolo rispetto al centro immagine)
        #     img_width = rgb_np.shape[1]
        #     bearing_px = cx - img_width / 2.0
        #     self.person_bearing_rad = bearing_px / img_width * 1.0  # FOV ~60° → 1 rad
        # else:
        #     self.person_detected = False

        # 2. Terrain classification (su ROI inferiore dell'immagine)
        # roi = rgb_np[int(rgb_np.shape[0]*0.6):, :]
        # terrain, conf = self.terrain_classifier.classify(roi)
        # if conf > 0.7:
        #     self.terrain_type = terrain
        #     self.traction_factor = self.terrain_classifier.get_traction_factor()
        #     self.terrain_pub.publish(String(data=terrain))
        #     self.traction_pub.publish(Float32(data=self.traction_factor))

        pass  # placeholder

    def _cb_depth(self, msg: PointCloud2):
        """Estrae range dalla depth cloud (punto centrale della detection YOLO)."""
        # Placeholder: estrai distanza dal punto (cx, cy) della detection
        # self.person_range_m = extracted_depth
        pass

    def _cb_lio_odom(self, msg: Odometry):
        """Odometria da LIO-SAM."""
        self.lio_odom_x = msg.pose.pose.position.x
        self.lio_odom_y = msg.pose.pose.position.y
        # Estrai yaw da quaternione
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.lio_odom_theta = math.atan2(siny_cosp, cosy_cosp)

    def _cb_imu(self, msg: Imu):
        """Velocità angolare da IMU."""
        self.imu_omega = msg.angular_velocity.z

    # ------------------------------------------------------------------
    # Control Loop (20 Hz)
    # ------------------------------------------------------------------
    def _control_loop(self):
        # 1. UKF predict
        self.ukf.predict()

        # 2. UKF update con odometria LIO-SAM
        self.ukf.update_odom(self.lio_odom_x, self.lio_odom_y, self.lio_odom_theta)

        # 3. UKF update con visione (se persona rilevata)
        if self.person_detected:
            self.ukf.update_vision(self.person_range_m, self.person_bearing_rad)

        # 4. UKF update con IMU
        self.ukf.update_imu(self.imu_omega)

        state = self.ukf.state

        # 5. Calcola errore distanza e bearing
        if not self.person_detected:
            # Nessuna persona: stop
            self._publish_cmd_vel(0.0, 0.0)
            return

        distance_error = self.person_range_m - TARGET_DISTANCE_M
        bearing_error  = self.person_bearing_rad

        # Banda morta
        if abs(distance_error) < TARGET_TOLERANCE_M:
            distance_error = 0.0

        # 6. PID → velocità lineare e angolare
        v_cmd = self.pid_linear.compute(distance_error)
        w_cmd = self.pid_angular.compute(bearing_error)

        # 7. Adattamento per terreno (riduce velocità su terreni scivolosi)
        v_cmd *= self.traction_factor
        w_cmd *= self.traction_factor

        # 8. Limiti
        v_cmd = max(-MAX_LINEAR_VEL, min(MAX_LINEAR_VEL, v_cmd))
        w_cmd = max(-MAX_ANGULAR_VEL, min(MAX_ANGULAR_VEL, w_cmd))

        self._publish_cmd_vel(v_cmd, w_cmd)

        # 9. Pubblica target pose per debug
        target_pose = PoseStamped()
        target_pose.header.stamp = self.get_clock().now().to_msg()
        target_pose.header.frame_id = "odom"
        target_pose.pose.position.x = state["x"] + self.person_range_m * math.cos(state["theta"] + self.person_bearing_rad)
        target_pose.pose.position.y = state["y"] + self.person_range_m * math.sin(state["theta"] + self.person_bearing_rad)
        self.target_pose_pub.publish(target_pose)

        self.get_logger().debug(
            f"UKF state: x={state['x']:.2f} y={state['y']:.2f} θ={math.degrees(state['theta']):.1f}° | "
            f"Person: range={self.person_range_m:.2f}m bearing={math.degrees(self.person_bearing_rad):.1f}° | "
            f"Cmd: v={v_cmd:.2f} ω={w_cmd:.2f} | Terrain: {self.terrain_type} (μ={self.traction_factor:.2f})"
        )

    def _publish_cmd_vel(self, v: float, w: float):
        twist = Twist()
        twist.linear.x = v
        twist.angular.z = w
        self.cmd_vel_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = PersonFollowingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
