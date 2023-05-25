
import numpy as np
import math
import pygame

class LidarSimulationSensor:
    def __init__(self, robotDiff):
        self.robotDiff = robotDiff
        self.scan_angle = []
        self.lidar_range = 300
        self.lidar_step = 0.5
        self.lidar_x = 0
        self.lidar_y = 0
    
    def getDistance(self, angle):
        return self.raycast(angle)
    
    def raycast(self, angle):
        # Return the distance of the first object in front of the lidar
        distance = -1
        while distance < self.lidar_range:
            distance += self.lidar_step
            x = self.lidar_x + distance * math.cos(math.radians(angle))
            y = self.lidar_y + distance * math.sin(math.radians(angle))
            if self.robotDiff.collision(x, y):
                break
        return distance

    def scan(self):
        # Return an array of distance
        lines_number = 50
        self.scan_angle = []
        self.lidar_x = (self.robotDiff.robot_x + self.robotDiff.robot_image.get_width()//2) + (math.cos(self.robotDiff.robot_angle)*self.robotDiff.robot_image.get_height())
        self.lidar_y = (self.robotDiff.robot_y + self.robotDiff.robot_image.get_height())+(-math.sin(self.robotDiff.robot_angle)*self.robotDiff.robot_image.get_height())
        
        for angle in np.linspace(0, 360, lines_number):
            distance = self.getDistance(angle)
            self.scan_angle.append([angle, distance])
        return self.scan_angle

    def draw(self):
        # Draw lines of lidar on screen
        for angle, distance in self.scan_angle:
            x = self.lidar_x + distance * math.cos(math.radians(angle))
            y = self.lidar_y + distance * math.sin(math.radians(angle))
            pygame.draw.line(self.robotDiff.fenetre, (255, 0, 0), (self.lidar_x, self.lidar_y), (x, y))
        pygame.draw.circle(self.robotDiff.fenetre, (0, 255, 0), (int(self.lidar_x), int(self.lidar_y)), 5)
        
