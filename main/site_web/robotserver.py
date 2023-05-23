import numpy as np
import serial
import sounddevice as sd
import scipy.signal as sig
import os
import threading
import subprocess
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
        
    def stopRobot(self):
        if self.direction != [0, 0]:
            self.direction = [0, 0]
            self.write("1&0&0$\n\r")

    def updateRobot(self):
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
            cmd = f"1&{int(right_power)}&{int(left_power)}$\n\r"
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
                self.direction = [-1, 0]
            elif self.max_spectres_moyen[-2] > self.max_spectres_moyen[-1]:
                print("Le bruit diminue.")
                self.speed = 10.0  
                self.direction = [1, 0] 
            else:
                print("Le bruit est constant.")
        elif len(self.max_spectres_moyen) == 1:
            print("Le bruit est constant.")
        else:
            print("Aucun bruit détecté.")

        self.seuil_precedent = self.seuil
    
    def mode3Control(self):
        print("RobotMode3 Control")
        self.mode3Init()
        self.mode3record() 
        self.mode3Play()
        
    def mode3Init(self):
        print("RobotMode3 Initializing")
        duree =5    
        commands2 = ["aplay -c 1 -t wav -r 44100 -f mu_law 'combat-laser.wav'"]
        threads2 = []
        for command in commands2:
            thread2 = threading.Thread(target=execute_command, args=(command,))
            thread2.start()
            threads2.append(thread2)

    def mode3record(self):
        print("Début enregistrement")
        duree = 5    
        commands = [f"arecord -d {duree} -D hw:2,0 -f S16_LE -r 16000 -c 1 son.wav","echo 'Enregistrement terminé'"]
        threads = []
        for command in commands:
            thread = threading.Thread(target=execute_command, args=(command,))
            thread.start()
            threads.append(thread)
            time.sleep(5)
              
    def mode3Play(self):
        commands1 = ["aplay -c 1 -t wav -r 16000 -f mu_law 'son.wav'","aplay -c 1 -t wav -r 16000 -f mu_law 'son.wav'","aplay -c 1 -t wav -r 16000 -f mu_law 'son.wav'"]
        threads1 = []     
        for command in commands1 :
            thread1 = threading.Thread(target=execute_command, args=(command,))
            thread1.start()
            threads1.append(thread1)
            time.sleep(6)
        print("Lecture terminée")
    
    def run(self):
        print("RobotServer running")
        while True:
            if "mode" in self.sharedVariables :
                if self.sharedVariables['mode'] == 0:
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
                self.last_mode = self.sharedVariables['mode']
            else:
                print("WARNING: Mode not implemented. Default manual control")
                self.manualControl()
            self.updateRobot()

def execute_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if output:
        print(f" \n{output.decode()}")
    if error:
        print(f"Error \n{error.decode()}")