import math
from simulationsensor import LidarSimulationSensor
class RobotDifferential:
    def __init__(self, carte_largeur, carte_hauteur, robot_largeur, robot_hauteur, vitesse_max, vitesse_rotation_max, config, sharedVariables):
        import pygame        
        self.carte_largeur = carte_largeur
        self.carte_hauteur = carte_hauteur
        self.robot_largeur = robot_largeur
        self.robot_hauteur = robot_hauteur
        self.vitesse_max = vitesse_max
        self.vitesse_rotation_max = vitesse_rotation_max
        
        self.config = config
        self.sharedVariables = sharedVariables
        pygame.init()
        self.fenetre = pygame.display.set_mode((self.carte_largeur, self.carte_hauteur))
        pygame.display.set_caption("Contrôle du robot")

        scale = 15
        self.robot_image = pygame.image.load("robot.png")
        self.robot_image = pygame.transform.scale(self.robot_image.copy(), (self.robot_largeur * scale, self.robot_hauteur * scale))

        self.fond_image = pygame.image.load("simulation_background.png")
        self.fond_image = pygame.transform.scale(self.fond_image.copy(), (self.carte_largeur, self.carte_hauteur))


        self.robot_x = self.carte_largeur // 2 - self.robot_largeur // 2
        self.robot_y = self.carte_hauteur // 2 - self.robot_hauteur // 2
        self.robot_angle = 0
        self.lidar = LidarSimulationSensor(self)

    def serial_input(self):
        if 'serial_output' in self.sharedVariables:
            serial_output = self.sharedVariables['serial_output']
            print("serial_output:", serial_output)

    def checkCollision(self):
        # check if pixel at pos is black
        offset_x = int(self.robot_x)
        offset_y = int(self.robot_y)
        for i in range(self.robot_image.get_width()):
            for j in range(self.robot_image.get_height()):
                if self.collision(offset_x + i, offset_y + j):
                    print('collision')
                    return True
        return False

    def collision(self, x, y):
        try:
            return self.fond_image.get_at((int(x),int(y))) == (0, 0, 0, 255)
        except IndexError:
            return True

    def control(self):
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                return False

        scan = self.lidar.scan()
        vitesse_lineaire = 0
        vitesse_rotation = 0
        self.serial_input()
        touches = pygame.key.get_pressed()
        if touches[pygame.K_z]:
            vitesse_lineaire = self.vitesse_max
        elif touches[pygame.K_s]:
            vitesse_lineaire = -self.vitesse_max

        if touches[pygame.K_q]:
            vitesse_rotation = self.vitesse_rotation_max
        elif touches[pygame.K_d]:
            vitesse_rotation = -self.vitesse_rotation_max

        vitesse_gauche = (2 * vitesse_lineaire - vitesse_rotation * self.robot_largeur) / (2 * self.robot_hauteur)
        vitesse_droite = (2 * vitesse_lineaire + vitesse_rotation * self.robot_largeur) / (2 * self.robot_hauteur)

        vitesse_avance = (vitesse_gauche + vitesse_droite) / 2
        vitesse_rotation = (vitesse_droite - vitesse_gauche) * (180 / math.pi)

        self.robot_angle += math.radians(vitesse_rotation)
        self.robot_x += vitesse_avance * math.cos(self.robot_angle)
        self.robot_y -= vitesse_avance * math.sin(self.robot_angle)

        self.robot_x = max(0, min(self.carte_largeur - self.robot_largeur, self.robot_x))
        self.robot_y = max(0, min(self.carte_hauteur - self.robot_hauteur, self.robot_y))
        
        if self.checkCollision():
            self.robot_x -= vitesse_avance * math.cos(self.robot_angle)
            self.robot_y += vitesse_avance * math.sin(self.robot_angle)

        return True

    def run(self):
        en_cours = True
        horloge = pygame.time.Clock()

        while en_cours:
            en_cours = self.control()

            self.fenetre.fill((255, 255, 255))

            self.fenetre.blit(self.fond_image, (0, 0))
            self.lidar.draw()
            robot_image_rotate = pygame.transform.rotate(self.robot_image.copy(), math.degrees(self.robot_angle)+90)
            center = robot_image_rotate.get_rect().center
            self.fenetre.blit(robot_image_rotate, (self.robot_x - center[0], self.robot_y-center[1]))
            pygame.display.flip()
            horloge.tick(60)

        pygame.quit()

