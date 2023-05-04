import numpy as np
import serial

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
        if config['serial']:
            self.ser = serial.Serial(config['serial_port'])
            self.ser.baudrate = config['serial_baudrate']
    
    def stopRobot(self):
        if self.config['serial']:
                    self.ser.write("stop\n\r".encode())

    def updateRobot(self):
        # Direction
        if self.lastDirection != self.direction and self.direction != [0, 0]:
            x_left = self.direction[0]
            y_left = self.direction[1]
            rotation_coef = (x_left / 2)
            right_power = round(-self.speed*(y_left + rotation_coef),2)
            left_power = round(-self.speed*(y_left - rotation_coef),2)
            cmd = f"mogo 1:{right_power} 2:{left_power}\n\r"
            print(f"Send {cmd}")
            if self.config['serial'] and (right_power != 0 or left_power != 0):
                self.ser.write(cmd.encode())
            else:
                self.stopRobot()
        else:
            self.stopRobot()
        self.lastDirection = self.direction

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

    def run(self):
        print("RobotServer running")
        while True:
            if "mode" in self.sharedVariables :
                if self.sharedVariables['mode'] == 0:
                    self.manualControl()
                elif self.sharedVariables['mode'] == 1:
                    self.mode1Control()
                else:
                    print("WARNING: Mode not implemented. Default manual control")
            else:
                print("WARNING: Mode not implemented. Default manual control")
                self.manualControl()
            self.updateRobot()