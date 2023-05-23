
import cv2
import numpy as np
import multiprocessing
from threadutils import ThreadSafeFrame, ThreadSafeDict
from flaskserver import FlaskServer
from cameraserver import CameraServer
from robotserver import RobotServer
from simulationserver import SimulationServer

class App:
    def __init__(self, config = None):
        # Generate default config if none is provided
        if not config:
            self.config = self.generateDefaultConfig()
        else:
            self.config = config

        # Create shared variables dictionary
        self.sharedVariables = ThreadSafeDict()
        self.sharedVariables['point_simulation_data'] = [0,0,12] # [x,y,rayon]
        self.sharedVariables['mode'] = 0 # 0: manuel, 1: mode 1, 2: mode 2, 3: mode 3

        self.sharedVariables['detected_object'] = False
        self.sharedVariables['detected_object_xy_norm'] = [0,0]
        
        cap = cv2.VideoCapture(0) # Replace 0 with your camera index if you have multiple cameras
        # Définir la qualité maximale pour la compression JPEG
        quality = self.config['video_quality']
        res, image = cap.read()
        cap.release()
        # Définir les paramètres pour l'encodage JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        ret,buffer = cv2.imencode('.jpg', image, encode_param)
        # On définie un objet multiprocess safe pour stocker l'image
        self.sharedFrame = ThreadSafeFrame(len(buffer.tobytes())*5)
        # self.sharedFrame = ThreadSafeFrame(2000)

    # Generate default config
    def generateDefaultConfig(self):
        print("Generating default config")
        # default config
        ###########################################
        config = ThreadSafeDict()
        config['detection_contour'] = True
        config['serial'] = True # Activer ou non le port serial
        # config['serial_port'] = 'COM8' # Port série
        config['serial_port'] = '/dev/ttyUSB0' # Port série
        config['serial_baudrate'] = 19200 # Baudrate du port série
        config['gomete_path'] = "gomete.jpg"
        config['speed_variable'] = True # Fixe ou non la vitesse du robot (si non dépendente de la touche LT)
        config['log_all_requests'] = False
        config['video_quality'] = 10 # Qualité de la vidéo (0-100)
        config['point_simulation'] = False # Simule un point rouge à la place de la détection. Les coordonnées sont définies dans sharedVariables à la clé 'point_simulation_data' ([x,y,rayon])
        # Sampling frequency
        config['mode3_freq'] = 44100 # Fréquence d'échantillonnage
        # Recording duration
        config['mode3_duration'] = 3 # Durée d'enregistrement
        config['auth_failed_limit'] = 7 # Nombre de tentatives de connexion avant de bloquer l'adresse IP
        config['auth_try_time'] = 5 # Temps en secondes avant de pouvoir réessayer de se connecter
        config['simulation_robot'] = False # Activer ou non le robot de simulation
        ###########################################
        return config

    def run(self):
        print("Starting threads")
        self.cameraProcess = multiprocessing.Process(target=runCameraServer, args=(self.config, self.sharedVariables, self.sharedFrame))
        self.cameraProcess.start()
        self.flaskProcess = multiprocessing.Process(target=runFlaskServer, args=(self.config, self.sharedVariables, self.sharedFrame))
        self.flaskProcess.start()
        self.robotProcess = multiprocessing.Process(target=runRobotServer, args=(self.config, self.sharedVariables, self.sharedFrame))
        self.robotProcess.start()
        if self.config['simulation_robot']:
            self.simulationProcess = multiprocessing.Process(target=runSimulationServer, args=(self.config, self.sharedVariables))
            self.simulationProcess.start()
        input("Press enter to stop\n")
        #self.cameraProcess.terminate()
        self.flaskProcess.terminate()
        self.robotProcess.terminate()
        if self.config['simulation_robot']:
            self.simulationProcess.terminate()
        print("Threads stopped")

    
def runFlaskServer(config, sharedVariables, sharedFrame):
    flaskServer = FlaskServer(config, sharedVariables, sharedFrame)
    flaskServer.run()
    
def runCameraServer(config, sharedVariables, sharedFrame):
    cameraServer = CameraServer(config, sharedVariables, sharedFrame)
    cameraServer.run()

def runRobotServer(config, sharedVariables, sharedFrame):
    robotServer = RobotServer(config, sharedVariables, sharedFrame)
    robotServer.run()

def runSimulationServer(config, sharedVariables):
    simulationServer = SimulationServer(config, sharedVariables)
    simulationServer.run()

if __name__ == '__main__':
    app = App()
    app.run()
