#!/usr/bin/env python3

import rospy
import cv2
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge

# Importaciones específicas de la arquitectura Duckietown
from duckietown.dtros import DTROS, NodeType, TopicType

class QRCodeDetectorNode(DTROS):
    def __init__(self, node_name):
        # Inicializamos el nodo heredando de DTROS como un nodo de PERCEPCIÓN
        super(QRCodeDetectorNode, self).__init__(node_name=node_name, node_type=NodeType.PERCEPTION)
        
        self.detector = cv2.QRCodeDetector()
        self.bridge = CvBridge()
        
        # Suscriptor: Lee las imágenes comprimidas de la cámara del Duckiebot
        self.sub_img = rospy.Subscriber(
            "~image_in", CompressedImage, self.image_cb, queue_size=1, buff_size="10MB"
        )
        
        # Publicador: Publicará el texto del QR detectado en un nuevo tópico
        self.pub_qr = rospy.Publisher(
            "~qr_data", String, queue_size=10, dt_topic_type=TopicType.PERCEPTION
        )
        self.loginfo("Nodo Lector de QR inicializado.")

    def image_cb(self, msg):
        try:
            # 1. Convertir la imagen comprimida de ROS a una imagen de OpenCV (cv2)
            img = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")
            
            # 2. Detectar y decodificar el QR
            data, bbox, _ = self.detector.detectAndDecode(img)
            
            # 3. Si se encuentra un QR, lo publicamos para que otros nodos lo usen
            if data:
                self.loginfo(f"¡QR Detectado!: {data}")
                self.pub_qr.publish(String(data))
                
        except Exception as e:
            self.logerr(f"Error procesando la imagen de la cámara: {e}")

if __name__ == "__main__":
    # Inicializar el nodo
    node = QRCodeDetectorNode("qr_detector_node")
    # Mantener el nodo corriendo
    rospy.spin()