import numpy as np
import serial
import sounddevice as sd
import time
class SimulationServer:
    def __init__(self, config = {}, sharedVariables = None ,sharedFrame = None):
        self.config = config
        self.mogo = [0, 0]
        self.running = False
        self.isStop = False
        

    def stopRobot(self):
        pass

    def draw(self):
        # Draw a representation of robot in flat map with pygame
        pass

    def update(self):
        # print("update")
        pass

    def write(self, cmd):
        if self.config['serial']:
            self.ser.write(cmd.encode())
        if self.config['simulation_robot']:
            self.sharedVariables['serial_input'] = cmd

    def read(self):
        if self.config['serial']:
            return self.ser.readline().decode('utf-8')
        if self.config['simulation_robot']:
            return self.sharedVariables['serial_output']
        return ""

    def run(self):
        print("SimulationServer running")
        self.maxFPS = 60
        self.maxTickRate = 60
        self.tickRate = 0
        self.fps = 0
        self.lastTime = time.time()
        self.running = True
        while self.running:
            if time.time() - self.lastTime >= 1:
                print("FPS:", self.fps)
                print("TickRate:", self.tickRate)
                self.fps = 0
                self.tickRate = 0
                self.lastTime = time.time()

            if self.tickRate < self.maxTickRate:
                self.tickRate += 1
                self.update()

            if self.fps < self.maxFPS:
                self.fps += 1
                self.draw()
                
            
        while True:
            print("Simulation")
            #Boucle principale, limite les fps et tickrate
            
            
            