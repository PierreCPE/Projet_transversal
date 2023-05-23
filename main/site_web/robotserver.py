import numpy as np
import serial
import sounddevice as sd
import scipy.signal as sig
import os
from rplidar import RPLidar
from rplidar import RPLidarException
import time

class RobotServer:
    def __init__(self, config = {}, sharedVariables = None ,sharedFrame = None):
        self.config = config
        self.sharedVariables = sharedVariables
        self.sharedFrame = sharedFrame
        self.max_speed = 30
        self.speed = 0
        self.lastSpeed = 0
        self.direction = [0, 0]
        self.lastDirection = [0, 0]
        self.require_update = False
        self.last_mode = self.sharedVariables['mode']
        if config['serial']:
            self.ser = serial.Serial(config['serial_port'])
            self.ser.baudrate = config['serial_baudrate']
        # Sampling frequency
        self.freq = self.config['mode3_freq']
        # Recording duration
        self.duration = self.config['mode3_duration']
        
        # Mode 2 parameters
        self.freq_min = 500
        self.freq_max = 4000
        self.taille_fenetre = 256 
        self.pas = 128
        self.taille_fft = 512 
        self.Fs = 44100
        self.duree = 1
        self.max_spectres_moyen=[]
        self.nb_bruits_consecutifs = 0
        self.bruit_detecte = False
        self.premiere_detection = True
        self.seuil = None
        
        # Init du lidar
        PORT_NAME = 'COM7'
        self.lidar = RPLidar(PORT_NAME)
            #Params du robot pour le lidar
        self.flag_obstacle = False #mm
        self.distance_min_obst = 1000 #mm


    
    def stopRobot(self):
        if self.direction != [0, 0]:
            self.direction = [0, 0]
            self.write("stop\n\r")
    
    def check_obstacle(self):
        try :
            self.lidar_database_temp = []
            
            ####
            # si dans la direction de la cible, sur une largeur L1 (= largeur du robot+ sécurité), 
            # il n'y a aucun obstacle à une distance inférieurs à D , alors tu avances tout droit vers la destination
            # Sinon s'il y a un obstacle dans la largeur L1 à moins de D mètres sur le chemin vers la destination, 
            # alors calcul des azimuts correspondant au bord de l'obstacle. Choix le coté où 
            # l'erreur d'azimut est le plus petit, et tu vises cet azimut +- l'angle nécessaire pour passer à une distance L1 de l'obstacle
            ####

            for scan in self.lidar.iter_scans():
                self.scan = scan 
                break
            self.lidar_database_temp.append([time.time(),self.scan])

            #Traitement de lidar_database_temp
            
            for i, tuple in enumerate(self.scan): 
                
                if (tuple[1]>=330 or tuple[1] <=30):
                    if tuple[2]<=self.distance_min_obst : 
                        print(tuple)
                        self.flag_obstacle = True 
                else : 
                    self.flag_obstacle = False
            #On reçoit la generatrice du lidar et on l'append a notre list
            
            
            return self.flag_obstacle
        except RPLidarException :
            self.lidar.clear_input()

    
    def updateRobot(self):
        # Ajout de detection d'obstacle de check_obstacle if check_obstacle
        # Selon le mode stop le robot ou fait un son
        
        self.check_obstacle()
        
        # Direction
        if self.lastDirection != self.direction:
            if self.direction == [0, 0]:
                self.stopRobot()
                return
            
            x_left = self.direction[0]
            y_left = self.direction[1]
            rotation_coef = (x_left / 2)
            right_power = round(-self.speed*(y_left + rotation_coef),2)
            left_power = round(-self.speed*(y_left - rotation_coef),2)
            cmd = f"mogo 1:{right_power} 2:{left_power}\n\r"
            print(f"Send {cmd}")
            if (right_power != 0 or left_power != 0):
                self.write(cmd)
            else:
                self.stopRobot()

        self.lastDirection = self.direction

    def write(self, cmd):
        print("write:",cmd)
        if self.config['serial']:
            self.ser.write(cmd.encode())
        if self.config['simulation_robot']:
            self.sharedVariables['serial_output'] = cmd

    def read(self):
        if self.config['serial']:
            return self.ser.readline().decode('utf-8')
        if self.config['simulation_robot']:
            return self.sharedVariables['serial_input']
        return ""

    def manualControl(self):
        if 'manualControlJson' in self.sharedVariables:
            json_data = self.sharedVariables['manualControlJson']
            print("Manual control")
            del self.sharedVariables['manualControlJson']
            self.speed = 0
            if self.config['speed_variable']:
                if 'LT' in json_data:
                    self.speed = self.max_speed*json_data['LT']
                    print("Speed", self.speed)
            else:
                self.speed = self.max_speed
                self.direction = [0, 0]
            if 'JoystickLeft' in json_data:
                self.direction = json_data['JoystickLeft']
                x_left = json_data["JoystickLeft"][0]
                y_left = json_data["JoystickLeft"][1]
                self.direction = [x_left, y_left]
            else:
                self.direction = [0, 0]
        else:
            self.speed = 0
            self.direction = [0, 0]
                
        
    def mode1Init(self):
        pass

    def mode1Control(self):
        if self.sharedVariables['detected_object'] and 'detected_object_xy_norm' in self.sharedVariables:
            self.speed = 10
            x = -self.sharedVariables['detected_object_xy_norm'][0]
            y = self.sharedVariables['detected_object_xy_norm'][1]
            #print(f"Need to go to {x},{y}")
            self.direction = [x, 0.7]
        else:
            self.speed = 0
            self.direction = [0, 0]


    def mode2Init(self):
        self.nb_bruits_consecutifs = 0
        self.bruit_detecte = False
        self.premiere_detection = True
        self.seuil = None
        self.max_spectres_moyen = []
        

    def mode2Control(self):
        print("Enregistrement en cours")
        signal = sd.rec(int(self.duree * self.Fs), samplerate=self.Fs, channels=1)
        sd.wait()

        f, t, S = sig.spectrogram(signal[:, 0], fs=self.Fs, window='hann', nperseg=self.taille_fenetre,
                                noverlap=self.taille_fenetre - self.pas, nfft=self.taille_fft, detrend=False)

        freq_bin = np.logical_and(f > self.freq_min, f <= self.freq_max)
        spectre_moyen = np.mean(np.abs(S[freq_bin, :]), axis=0)

        if self.seuil is None:
            self.seuil = 20 * np.std(spectre_moyen)

        max_bruit = np.max(spectre_moyen)

        if max_bruit > self.seuil:
            print('Bruit détecté, fuyons!')
            if self.premiere_detection:
                self.premiere_detection = False
            else:
                self.nb_bruits_consecutifs += 1

            if self.nb_bruits_consecutifs == 2:
                print('Trop de bruits détectés, arrêt du programme.')
            else:
                self.max_spectres_moyen.append(max_bruit)
        else:
            print('Aucun bruit bizarre, restons bien caché!')
            if not self.premiere_detection:
                self.bruit_detecte = False

        print("La valeur seuil est :", self.seuil)
        print("La valeur maximale du bruit est :", max_bruit)
        print()

        print("Le valeur max des bruit sont :", self.max_spectres_moyen)

        if self.max_spectres_moyen[0] < self.max_spectres_moyen[1]:
            print("Le bruit augmente.")
        elif self.max_spectres_moyen[0] > self.max_spectres_moyen[1]:
            print("Le bruit diminue.")
        else:
            print("Le bruit est constant.")



    def mode3Control(self):
        # check if sharedvariable has mode3_record to true
        if 'mode3_record' in self.sharedVariables and self.sharedVariables['mode3_record']:
            self.mode3Record()
        else:
            self.mode3Play()

    def mode3Init(self):
        self.playSound("mode3_init.wav")

    def mode3Record(self):
        pass
    
    def playSound(self, path):
        print("Playing sound")
        # execute command "aplay -c 1 -t wav -r 44100 -f mu_law son.wav"
        os.system(f"aplay -c 1 -t wav -r 44100 -f mu_law {path}")

    def run(self):
        print("RobotServer running")
        while True:
            if "mode" in self.sharedVariables :
                if self.sharedVariables['mode'] == 0:
                    self.manualControl()
                elif self.sharedVariables['mode'] == 1:
                    if self.last_mode != 3:
                        self.mode1Init()
                    self.mode1Control()
                elif self.sharedVariables['mode'] == 2:
                    self.mode2Control()
                elif self.sharedVariables['mode'] == 3:
                    if self.last_mode != 3:
                        self.mode3Init()
                    self.mode3Control()
                else:
                    print("WARNING: Mode not implemented. Default manual control")
                self.last_mode = self.sharedVariables['mode']
            else:
                print("WARNING: Mode not implemented. Default manual control")
                self.manualControl()
            self.updateRobot()