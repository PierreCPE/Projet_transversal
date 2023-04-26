import numpy as np

class RobotServer:
    def __init__(self, config = {}, sharedVariables = None ,sharedFrame = None):
        self.config = config
        self.sharedVariables = sharedVariables
        self.sharedFrame = sharedFrame
        self.max_speed = 30
        self.speed = 0
        self.direction = [0, 0]
        self.require_update = False
    
    def updateRobot(self, cmd):
        x_left = self.direction
        y_left = self.direction
        rotation_coef = (x_left / 2)
        right_power = -self.speed*(y_left + rotation_coef)
        left_power = -self.speed*(y_left - rotation_coef)
        cmd = f"mogo 1:{right_power} 2:{left_power}\n\r"
        print(f"Send {cmd}")
        if self.config['serial']:
            self.config['ser'].write(cmd.encode())
        else:
            if self.config['serial']:
                self.config['ser'].write("stop\n\r".encode())

    def manualControl(self):
        if 'manualControlJson' in self.sharedVariables:
            del self.sharedVariables['manualControlJson']
            json_data = self.sharedVariables['manualControlJson']
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
                rotation_coef = (x_left / 2)
                right_power = -self.speed*(y_left + rotation_coef)
                left_power = -self.speed*(y_left - rotation_coef)
                cmd = f"mogo 1:{right_power} 2:{left_power}\n\r"
                print(f"Send {cmd}")
                if self.config['serial']:
                    self.config['ser'].write(cmd.encode())
            else:
                if self.config['serial']:
                    self.config['ser'].write("stop\n\r".encode())
        
    def mode1Control(self):
        if "detected_object_xy_norm" in self.sharedVariables:
            x = self.sharedVariables['detected_object_xy_norm'][0]
            y = self.sharedVariables['detected_object_xy_norm'][1]
            print(f"Need to go to {x},{y}")

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