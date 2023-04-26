
import cv2
import numpy as np
import multiprocessing
from threadutils import ThreadSafeFrame, ThreadSafeDict
from flaskserver import FlaskServer
from cameraserver import CameraServer

class App:
    def __init__(self, config = None):
        # Generate default config if none is provided
        if not config:
            self.config = self.generateDefaultConfig()
        else:
            self.config = config

        # Create shared variables dictionary
        self.sharedVariables = ThreadSafeDict()

        cap = cv2.VideoCapture(0) # Replace 0 with your camera index if you have multiple cameras
        # Définir la qualité maximale pour la compression JPEG
        quality = self.config['video_quality']
        res, image = cap.read()
        cap.release()
        # Définir les paramètres pour l'encodage JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        ret,buffer = cv2.imencode('.jpg', image, encode_param)
        # On définie un objet multiprocess safe pour stocker l'image
        self.sharedFrame = ThreadSafeFrame(len(buffer.tobytes())*4)

    # Generate default config
    def generateDefaultConfig(self):
        print("Generating default config")
        # default config
        ###########################################
        config = ThreadSafeDict()
        config['detection_contour'] = True
        config['serial'] = False # Activer ou non le port serial
        # config['serial_port'] = 'COM8' # Port série
        config['serial_port'] = '/dev/ttyUSB0' # Port série
        config['serial_baudrate'] = 115200 # Baudrate du port série
        config['gomete_path'] = "img2.jpg"
        config['speed_variable'] = True # Fixe ou non la vitesse du robot (si non dépendente de la touche LT)
        config['log_all_requests'] = False
        config['video_quality'] = 50
        ###########################################
        return config

    def run(self):
        print("Starting threads")
        self.cameraProcess = multiprocessing.Process(target=runCameraServer, args=(self.config, self.sharedVariables, self.sharedFrame))
        self.cameraProcess.start()
        self.flaskProcess = multiprocessing.Process(target=runFlaskServer, args=(self.config, self.sharedVariables, self.sharedFrame))
        self.flaskProcess.start()
        input("Press enter to stop\n")
        self.cameraProcess.terminate()
        self.flaskProcess.terminate()
        print("Threads stopped")

    
def runFlaskServer(config, sharedVariables, sharedFrame):
    flaskServer = FlaskServer(config, sharedVariables, sharedFrame)
    flaskServer.run()
    
def runCameraServer(config, sharedVariables, sharedFrame):
    cameraServer = CameraServer(config, sharedVariables, sharedFrame)
    cameraServer.run()

if __name__ == '__main__':
    global config
    global sharedFrame
    app = App()
    app.run()
