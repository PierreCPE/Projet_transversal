import numpy as np
import serial
import sounddevice as sd
import scipy.signal as sig
import os
import threading
from rplidar import RPLidar
from rplidar import RPLidarException
import time
import subprocess


class RobotServer:
    def __init__(self, config = {}, sharedVariables = None ,sharedFrame = None):
        self.config = config
        self.sharedVariables = sharedVariables
        self.sharedFrame = sharedFrame
        self.max_speed = 30
        self.speed = 0
        self.maxLookSpeed = 20
        self.lastSpeed = 0
        self.direction = [0, 0] # (-1 to 0)
        self.lastDirection = [0, 0] # (-1 to 0)
        self.lookSpeed = 0
        self.lastLookSpeed = 0
        self.lookDirection = [0, 0] # in degrees (-80 to 80)
        self.lastLookDirection = [0, 0] # in degrees (-80 to 80)
        self.require_update = False
        self.last_mode = self.sharedVariables['mode']
        if config['serial']:
            self.ser = serial.Serial(config['serial_port'], 
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=None)
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
        self.timer_mode3 = time.time()
        self.timer_play_sound = time.time()
        self.messages_to_serial = []
        # Init du lidar
        if config['utilisation_lidar']:
            PORT_NAME = '/dev/ttyUSB0'
            self.lidar = RPLidar(PORT_NAME)
            #Params du robot pour le lidar
        self.flag_obstacle = False #mm
        self.distance_min_obst = 300 #mm
        self.angle_seuil = 30 # 30 degres

        self.led_statut = 0
        self.last_led_statut = 0
        self.led_delay_stop = time.time()

    def stopRobot(self):
        if self.direction != [0, 0]:
            self.direction = [0, 0]
            self.sendUART("0&0&0")
    
    def check_obstacle(self):
        if not 'utilisation_lidar' in self.config or not self.config['utilisation_lidar']:
            return False
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
                
                if (tuple[1]>=(180-self.angle_seuil) and (tuple[1] <=180+self.angle_seuil)):
                    if tuple[2]<=self.distance_min_obst : 
                        print(tuple)
                        self.flag_obstacle = True
                        if tuple[1]>= 180 :
                            print("Je tourne à gauche")
                            self.direction = [-1,0]
                            self.speed = self.max_speed/2

                        else :
                            print("Je tourne à droite")
                            self.direction = [1,0]
                            self.speed = self.max_speed/2

                            

                else : 
                    self.flag_obstacle = False
                    # Config speciale en fonction du mode
                    self.direction = [0,1]
            
            
            return self.flag_obstacle
        except RPLidarException :
            self.lidar.clear_input()
    

    def updateRobot(self):
        self.messages_to_serial.clear()
        # Ajout de detection d'obstacle de check_obstacle if check_obstacle
        # Selon le mode stop le robot ou fait un son
        self.check_obstacle()
        if self.lookDirection [0] < 0:
            self.lookDirection[0] = 0
        if self.lookDirection [0] > 180:
            self.lookDirection[0] = 180
        if self.lookDirection [1] < 0:
            self.lookDirection[1] = 0
        if self.lookDirection [1] > 180:
            self.lookDirection[1] = 180
        # LED
        # if self.last_led_statut != self.led_statut:
        if self.led_statut:
            self.sendUART("3&1")
        else:
            self.sendUART("3&0")

        # Look direction
        if self.lastLookDirection != self.lookDirection:
            cmd = f"1&{int(self.lookDirection[0])}"
            self.sendUART(cmd)
            cmd = f"2&{int(self.lookDirection[1])}"
            self.sendUART(cmd)
            # print("write lookDirection")

        self.lastLookDirection = self.lookDirection.copy()

        # Direction
        if self.lastDirection != self.direction:
            if self.direction == [0, 0]:
                self.lastDirection = self.direction
                self.stopRobot()
                return
            x_left = self.direction[0]
            y_left = self.direction[1]
            rotation_coef = (x_left / 2)
            right_power = round(-self.speed*(y_left + rotation_coef),2)
            left_power = round(-self.speed*(y_left - rotation_coef),2)
            cmd = f"0&{int(right_power)}&{int(left_power)}"
            if (right_power != 0 or left_power != 0):
                self.sendUART(cmd)
            else:
                self.stopRobot()
        self.write()
        self.last_led_statut = self.led_statut
        self.lastDirection = self.direction.copy()
        
    def sendUART(self, cmd):
        self.messages_to_serial.append(cmd)

    def write(self):
        if len(self.messages_to_serial) == 0:
            return
        message = ",".join(self.messages_to_serial)
        message += "$"
        print("write:",message)
        if self.config['serial']:
            self.ser.flushInput()
            self.ser.flushOutput() #On nettoie les buffers
            self.ser.write(message.encode())
        if self.config['simulation_robot']:
            if not 'serial_output' in self.sharedVariables:
                self.sharedVariables['serial_output'] = []
                # print("create serial_output")
            # print("write in fake serial:",message)
            self.sharedVariables['serial_output'].append(message)

    def read(self):
        if self.config['serial']:
            return self.ser.readline().decode('utf-8')
        if self.config['simulation_robot']:
            return self.sharedVariables['serial_input']
        return ""
    
    def modeManualInit(self):
        print("modeManualInit")
        command = "mode_manual_activate.wav"
        self.playSound(command)
        
    def manualControl(self):
        if 'manualControlJson' in self.sharedVariables:
            json_data = self.sharedVariables['manualControlJson']
            del self.sharedVariables['manualControlJson']
            if 'A' in json_data:
                self.led_statut = True
                self.led_delay_stop = time.time()+2
            if time.time() > self.led_delay_stop:
                if not 'A' in json_data:
                    self.led_statut = False
            self.speed = 0
            self.lookSpeed = 0
            if self.config['speed_variable']:
                if 'LT' in json_data:
                    self.speed = self.max_speed*json_data['LT']
            else:
                self.speed = self.max_speed
                self.direction = [0, 0]

            if self.config['look_speed_variable']:
                if 'RT' in json_data:
                    self.lookSpeed = self.maxLookSpeed*json_data['RT']
            else:
                self.lookSpeed = self.maxLookSpeed

            # print("lookSpeed:",self.lookSpeed)
            if 'JoystickRight' in json_data:
                x_left = self.lookSpeed*json_data["JoystickRight"][0]
                y_left = self.lookSpeed*json_data["JoystickRight"][1]
                self.lookDirection[0] += x_left
                self.lookDirection[1] += y_left

            # print("lookDirection:",self.lookDirection)
            if 'JoystickLeft' in json_data:
                x_left = json_data["JoystickLeft"][0]
                y_left = json_data["JoystickLeft"][1]
                self.direction = [x_left, y_left]
            else:
                self.direction = [0, 0]
        else:
            self.speed = 0
            self.direction = [0, 0]
            self.lookSpeed = 0
                
        
    def mode1Init(self):
        command = "mode_1_activate.wav"
        self.playSound(command)

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
        command = "mode_2_activate.wav"
        self.playSound(command)
        print("mode2Init")
        self.nb_bruits_consecutifs = 0
        self.bruit_detecte = False
        self.premiere_detection = True
        self.max_spectres_moyen = []
        self.speed = 0.0  
        self.direction = [0, 0]
        print("Enregistrement du seuil ambiant en cours")
        signal = sd.rec(int(self.duree * self.Fs), samplerate=self.Fs, channels=1)
        sd.wait()

        f, t, S = sig.spectrogram(signal[:, 0], fs=self.Fs, window='hann', nperseg=self.taille_fenetre,
                                noverlap=self.taille_fenetre - self.pas, nfft=self.taille_fft, detrend=False)

        freq_bin = np.logical_and(f > self.freq_min, f <= self.freq_max)
        spectre_moyen1 = np.mean(np.abs(S[freq_bin, :]), axis=0)

        self.seuil = 20 * np.std(spectre_moyen1)
        print("La valeur seuil est :", self.seuil)
        print(" ")
        return spectre_moyen1

        
    def mode2Control(self, spectre_moyen1):
        if self.nb_bruits_consecutifs >= 2:
            return  

        print("Enregistrement en cours")
        signal = sd.rec(int(self.duree * self.Fs), samplerate=self.Fs, channels=1)
        sd.wait()

        f, t, S = sig.spectrogram(signal[:, 0], fs=self.Fs, window='hann', nperseg=self.taille_fenetre,
                                noverlap=self.taille_fenetre - self.pas, nfft=self.taille_fft, detrend=False)

        freq_bin = np.logical_and(f > self.freq_min, f <= self.freq_max)
        spectre_moyen2 = np.mean(np.abs(S[freq_bin, :]), axis=0)

        max_bruit = np.max(spectre_moyen2)

        if max_bruit > self.seuil:
            print('Bruit détecté, fuyons!')
            self.max_spectres_moyen.append(max_bruit)
            if self.premiere_detection:
                self.premiere_detection = False
            else:
                self.nb_bruits_consecutifs += 1
            print("La valeur maximale du bruit est :", max_bruit)

        else:
            print('Aucun bruit bizarre, restons bien caché!')
            if not self.premiere_detection:
                self.bruit_detecte = False

        print("Les valeurs max des bruits sont :", self.max_spectres_moyen)
        print("   ")

        if len(self.max_spectres_moyen) > 2:
            if self.max_spectres_moyen[-2] < self.max_spectres_moyen[-1]:
                print("Le bruit augmente.")
                self.speed = 10.0  
                self.direction = [1, 0]
            elif self.max_spectres_moyen[-2] > self.max_spectres_moyen[-1]:
                print("Le bruit diminue.")
                self.speed = 10.0  
                self.direction = [-1, 0] 
            else:
                print("Le bruit est constant.")
        elif len(self.max_spectres_moyen) == 1:
            print("Le bruit est constant.")
        else:
            print("Aucun bruit détecté.")

        self.seuil_precedent = self.seuil
    
        
    def mode3Init(self):
        self.timer_mode3 = time.time()
        print("mode3Init")
        duree =5    
        # command = "combat-laser.wav"
        # self.playSound(command)
        self.timer_mode3 = time.time()
        self.mode3_phase = 'record'
        self.mode3_playing = False
        self.mode3_count = 0

    def mode3Control(self):
        if self.mode3_phase == 'record':
            self.timer_mode3 = time.time()
            self.mode3record()
            self.mode3_phase = 'play'
            self.mode3_count = 0
            self.mode3_playing = True
        elif self.mode3_phase == 'play':
            self.mode3Play()
            if self.mode3_count > 3 and time.time() - self.timer_mode3 > 3*3:
                self.mode3_phase = 'record'
        else:
            self.timer_mode3 = time.time()
            self.mode3_count = 0
            self.mode3_phase = 'record'

    def mode3record(self):
        print("Début enregistrement")
        duree = 3
        if self.config['windows']:
            print("Fake record windows")
        else:
            command = f"arecord -d {duree} -D hw:2,0 -f S16_LE -r 16000 -c 1 son.wav"
            thread = threading.Thread(target=execute_command, args=(command,))
            thread.start()
              
    def mode3Play(self):
        if not self.mode3_playing:
                self.mode3_playing = True
                command = "son.wav"
                self.mode3_count += 1
                if self.mode3_count > 3:
                    return
                self.playSound(command)
                print(f"play {self.mode3_count}")
        else:
            if time.time() - self.timer_mode3 > 3*(self.mode3_count+1):
                self.mode3_phase = 'play'
                self.mode3_playing = False
    
    def playSound(self, sounds):
        if self.config['windows']:
            thread = threading.Thread(target=execute_sound_windows, args=(sounds,))
            thread.start()
            
        else:
            if  isinstance(sounds, str):
                command= f"aplay -c 1 -t wav -r 16000 -f mu_law '{sounds}'"
                thread = threading.Thread(target=execute_command, args=(command,))
            else:
                self.timer_play_sound = time.time()
                for sound in sounds:
                    command = f"aplay -c 1 -t wav -r 16000 -f mu_law '{sound}'"
                    thread = threading.Thread(target=execute_command, args=(command,))
            thread.start()

    def run(self):
        print("RobotServer running")
        while True:
            try:
                if "mode" in self.sharedVariables :
                    if self.sharedVariables['mode'] == 0:
                        if self.last_mode != 0:
                            self.modeManualInit()
                        self.manualControl()
                    elif self.sharedVariables['mode'] == 1:
                        if self.last_mode != 1:
                            self.mode1Init()
                        self.mode1Control()
                    elif self.sharedVariables['mode'] == 2:
                        if self.last_mode != 2:
                            self.mode2Init()
                        self.mode2Control()

                    elif self.sharedVariables['mode'] == 3:
                        if self.last_mode != 3:
                            self.mode3Init()
                        self.mode3Control()
                    else:
                        print("WARNING: Mode not implemented. Default manual control")
                else:
                    print("WARNING: Mode not implemented. Default manual control")
                    self.manualControl()
                self.updateRobot()
                self.last_mode = self.sharedVariables['mode']
                time.sleep(0.05)
            except Exception as e:
                print("ERROR: ", e)
                self.last_mode = self.sharedVariables['mode']
                self.stopRobot()
                command = "erreur.wav"
                self.playSound(command)
                break
            
def execute_sound_windows(sound):
    import winsound
    winsound.PlaySound(sound, winsound.SND_FILENAME)  

def execute_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if output:
        print(f" \n{output.decode()}")
    if error:
        print(f"Error \n{error.decode()}")