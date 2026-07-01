#!/usr/bin/env python3
"""
Laser Target Detector Node - Axiom Rover "Mulo"
Rileva un punto laser al suolo (es. verde a 532 nm), calcola la sua posizione 3D 
rispetto al rover e pubblica il vettore per l'inseguimento autonomo.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import Vector3Stamped, PoseStamped
from std_msgs.msg import Header
import numpy as np
import math

try:
    import cv2
    from cv_bridge import CvBridge
    CV_BRIDGE_AVAILABLE = True
except ImportError:
    CV_BRIDGE_AVAILABLE = False

class LaserTargetDetectorNode(Node):
    def __init__(self):
        super().__init__('laser_target_detector')
        self.get_logger().info('Avvio del nodo Laser Target Detector...')

        # ---------------------------------------------------------------------------
        # Parametri ROS 2
        # ---------------------------------------------------------------------------
        # Default: Laser verde (range HSV tipico: H=35-85, S=100-255, V=150-255)
        self.declare_parameter('hsv_h_min', 35)
        self.declare_parameter('hsv_h_max', 85)
        self.declare_parameter('hsv_s_min', 100)
        self.declare_parameter('hsv_s_max', 255)
        self.declare_parameter('hsv_v_min', 150)
        self.declare_parameter('hsv_v_max', 255)
        
        self.declare_parameter('min_target_area', 4.0)       # Pixel
        self.declare_parameter('max_target_area', 500.0)     # Pixel
        self.declare_parameter('depth_neighborhood', 3)      # Finestra NxN per la profondità
        self.declare_parameter('publish_debug_img', True)    # Pubblicazione immagine di debug

        # Parametri geometrici di calibrazione camera (fallback se non c'è CameraInfo)
        # Basati su RealSense D435i inclinata a 15 gradi (0.26 rad) a 32 cm di altezza e 42 cm di sbalzo
        self.declare_parameter('camera_pitch_rad', 0.26)
        self.declare_parameter('camera_x_m', 0.42)
        self.declare_parameter('camera_y_m', 0.0)
        self.declare_parameter('camera_z_m', 0.32)

        # ---------------------------------------------------------------------------
        # Stato Interno
        # ---------------------------------------------------------------------------
        self.latest_depth_msg = None
        self.camera_info_received = False
        
        # Parametri intrinseci di default (RealSense 640x480 con FOV ~1.5 rad)
        self.fx = 336.8
        self.fy = 336.8
        self.cx = 320.0
        self.cy = 240.0

        if not CV_BRIDGE_AVAILABLE:
            self.get_logger().error("Errore: OpenCV o cv_bridge non sono installati! Rilevamento disattivato.")
            return
            
        self.bridge = CvBridge()

        # ---------------------------------------------------------------------------
        # Subscriptions
        # ---------------------------------------------------------------------------
        self.create_subscription(Image, 'camera/rgb/image_raw', self._cb_rgb, 10)
        self.create_subscription(Image, 'camera/depth/image_raw', self._cb_depth, 10)
        self.create_subscription(CameraInfo, 'camera/rgb/camera_info', self._cb_camera_info, 10)

        # ---------------------------------------------------------------------------
        # Publishers
        # ---------------------------------------------------------------------------
        # Vettore per l'inseguimento compatibile con shared_autonomy
        self.leader_vector_pub = self.create_publisher(Vector3Stamped, 'mission/leader_vector', 10)
        
        # Pose target nel frame locale odom/base_link per visualizzazione RViz
        self.target_pose_pub = self.create_publisher(PoseStamped, 'navigation/target_pose', 10)
        
        # Immagine binaria di debug per la taratura HSV
        self.debug_img_pub = self.create_publisher(Image, 'camera/rgb/laser_mask', 10)

        self.get_logger().info('Laser Target Detector inizializzato con successo.')

    def _cb_camera_info(self, msg: CameraInfo):
        """Riceve le informazioni intrinseche della camera."""
        if not self.camera_info_received:
            # Matrice K = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
            if len(msg.k) >= 9:
                self.fx = msg.k[0]
                self.cx = msg.k[2]
                self.fy = msg.k[4]
                self.cy = msg.k[5]
                self.camera_info_received = True
                self.get_logger().info(f"Parametri intrinseci camera caricati da CameraInfo: fx={self.fx:.2f}, fy={self.fy:.2f}, cx={self.cx:.2f}, cy={self.cy:.2f}")

    def _cb_depth(self, msg: Image):
        """Memorizza l'ultimo frame di profondità."""
        self.latest_depth_msg = msg

    def _cb_rgb(self, msg: Image):
        """Callback immagine RGB: esegue la detection e la proiezione 3D."""
        if self.latest_depth_msg is None:
            # Nessuna profondità ancora disponibile
            return

        try:
            # Conversione in OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            cv_depth = self.bridge.imgmsg_to_cv2(self.latest_depth_msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().error(f"Errore nella conversione dell'immagine: {e}")
            return

        # Rilevamento del punto laser
        laser_pixel = self._detect_laser_spot(cv_image)

        if laser_pixel is not None:
            u, v = laser_pixel
            
            # Lettura della profondità
            depth_m = self._get_depth_at_pixel(cv_depth, u, v, self.latest_depth_msg.encoding)
            
            if depth_m is not None and depth_m > 0.1:
                # De-proiezione 2D -> 3D nel frame ottico della camera (camera_optical_frame)
                # Z: avanti, X: destra, Y: basso
                z_opt = depth_m
                x_opt = (u - self.cx) * z_opt / self.fx
                y_opt = (v - self.cy) * z_opt / self.fy
                
                # Conversione in camera_link (X: avanti, Y: sinistra, Z: alto)
                # Dalle specifiche URDF: camera_optical_frame ha rotazione rpy="-1.5708 0 -1.5708"
                x_cam = z_opt
                y_cam = -x_opt
                z_cam = -y_opt
                
                # Conversione da camera_link a base_link (inclinazione pitch + pos)
                x_base, y_base, z_base = self._transform_to_base_link(x_cam, y_cam, z_cam)
                
                # Calcolo di range e bearing rispetto al centro del rover (base_link)
                range_m = math.sqrt(x_base**2 + y_base**2)
                bearing_rad = math.atan2(y_base, x_base)
                
                # Pubblicazione dei risultati
                self._publish_target(range_m, bearing_rad, x_base, y_base, z_base, msg.header)
            else:
                # Trovato nell'immagine ma senza profondità valida
                self._publish_empty_target(msg.header)
        else:
            # Nessun laser rilevato
            self._publish_empty_target(msg.header)

    def _detect_laser_spot(self, cv_img):
        """Filtra l'immagine per trovare il baricentro del punto laser verde/rosso."""
        # Recupero dei parametri HSV
        h_min = self.get_parameter('hsv_h_min').value
        h_max = self.get_parameter('hsv_h_max').value
        s_min = self.get_parameter('hsv_s_min').value
        s_max = self.get_parameter('hsv_s_max').value
        v_min = self.get_parameter('hsv_v_min').value
        v_max = self.get_parameter('hsv_v_max').value
        
        min_area = self.get_parameter('min_target_area').value
        max_area = self.get_parameter('max_target_area').value

        # Conversione in HSV
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        
        # Thresholding
        mask = cv2.inRange(hsv, np.array([h_min, s_min, v_min]), np.array([h_max, s_max, v_max]))
        
        # Pulizia morfologica per eliminare rumore singolo e compattare il punto
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Pubblicazione immagine di debug (opzionale)
        if self.get_parameter('publish_debug_img').value:
            try:
                debug_msg = self.bridge.cv2_to_imgmsg(mask, encoding='mono8')
                debug_msg.header.stamp = self.get_clock().now().to_msg()
                debug_msg.header.frame_id = "camera_optical_frame"
                self.debug_img_pub.publish(debug_msg)
            except Exception as e:
                self.get_logger().error(f"Impossibile pubblicare immagine di debug: {e}")

        # Ricerca contorni
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_u, best_v = None, None
        max_contour_area = 0.0

        for c in contours:
            area = cv2.contourArea(c)
            if min_area <= area <= max_area:
                # Seleziona il contorno con l'area maggiore (il punto più netto)
                if area > max_contour_area:
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        best_u = int(M["m10"] / M["m00"])
                        best_v = int(M["m01"] / M["m00"])
                        max_contour_area = area

        if best_u is not None:
            return (best_u, best_v)
        return None

    def _get_depth_at_pixel(self, cv_depth, u, v, encoding):
        """Ottiene la profondità in metri mediando su una piccola ROI per superare NaN/zero."""
        window_size = self.get_parameter('depth_neighborhood').value
        half = window_size // 2
        height, width = cv_depth.shape[:2]

        u_min = max(0, u - half)
        u_max = min(width - 1, u + half)
        v_min = max(0, v - half)
        v_max = min(height - 1, v + half)

        roi = cv_depth[v_min:v_max+1, u_min:u_max+1]
        
        # Pulisce da NaN, Inf e z<=0
        valid_mask = np.logical_and(np.isnan(roi) == False, np.isinf(roi) == False)
        valid_mask = np.logical_and(valid_mask, roi > 0)
        valid_depths = roi[valid_mask]

        if len(valid_depths) == 0:
            return None

        median_depth = np.median(valid_depths)

        # Conversione in metri a seconda del formato immagine (16U = mm, 32F = m)
        if "16U" in encoding:
            return float(median_depth) / 1000.0
        else:
            return float(median_depth)

    def _transform_to_base_link(self, x_cam, y_cam, z_cam):
        """Trasforma le coordinate da camera_link a base_link tramite geometria analitica."""
        pitch = self.get_parameter('camera_pitch_rad').value
        tx = self.get_parameter('camera_x_m').value
        ty = self.get_parameter('camera_y_m').value
        tz = self.get_parameter('camera_z_m').value

        # Rotazione attorno all'asse Y (Pitch di camera_link)
        # x_base = x_cam * cos(pitch) + z_cam * sin(pitch) + tx
        # y_base = y_cam + ty
        # z_base = -x_cam * sin(pitch) + z_cam * cos(pitch) + tz
        cos_p = math.cos(pitch)
        sin_p = math.sin(pitch)

        x_base = x_cam * cos_p + z_cam * sin_p + tx
        y_base = y_cam + ty
        z_base = -x_cam * sin_p + z_cam * cos_p + tz

        return x_base, y_base, z_base

    def _publish_target(self, range_m, bearing_rad, x_base, y_base, z_base, header):
        """Pubblica il target per shared_autonomy e visualizzazione."""
        stamp = self.get_clock().now().to_msg()
        
        # 1. leader_vector (x: range, y: bearing, z: confidence = 1.0)
        vec_msg = Vector3Stamped()
        vec_msg.header.stamp = stamp
        vec_msg.header.frame_id = "base_link"
        vec_msg.vector.x = float(range_m)
        vec_msg.vector.y = float(bearing_rad)
        vec_msg.vector.z = 1.0  # Rilevato con successo
        self.leader_vector_pub.publish(vec_msg)

        # 2. target_pose (per RViz/debug)
        pose_msg = PoseStamped()
        pose_msg.header.stamp = stamp
        pose_msg.header.frame_id = "base_link"
        pose_msg.pose.position.x = float(x_base)
        pose_msg.pose.position.y = float(y_base)
        pose_msg.pose.position.z = float(z_base)
        # Orientamento nullo
        pose_msg.pose.orientation.w = 1.0
        self.target_pose_pub.publish(pose_msg)

        self.get_logger().debug(f"Target rilevato: range={range_m:.2f}m, bearing={math.degrees(bearing_rad):.1f}°")

    def _publish_empty_target(self, header):
        """Pubblica un target vuoto (confidence = 0.0) per arrestare il rover se il laser scompare."""
        vec_msg = Vector3Stamped()
        vec_msg.header.stamp = self.get_clock().now().to_msg()
        vec_msg.header.frame_id = "base_link"
        vec_msg.vector.x = 0.0
        vec_msg.vector.y = 0.0
        vec_msg.vector.z = 0.0  # Perso / Non visibile
        self.leader_vector_pub.publish(vec_msg)


def main(args=None):
    rclpy.init(args=args)
    node = LaserTargetDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
