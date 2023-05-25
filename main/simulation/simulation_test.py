import pygame
import math

# Dimensions de la carte et du robot
CARTE_LARGEUR = 800
CARTE_HAUTEUR = 600
ROBOT_LARGEUR = 278
ROBOT_HAUTEUR = 278
ROBOT_IMG_LARGEUR = 64
ROBOT_IMG_HAUTEUR = 64

# Couleurs
COULEUR_FOND = (255, 255, 255)  # Blanc

# Chargement de l'image du robot
robot_image = pygame.image.load("robot.png")

# Position et orientation initiales du robot
robot_x = CARTE_LARGEUR // 2 - ROBOT_LARGEUR // 2
robot_y = CARTE_HAUTEUR // 2 - ROBOT_HAUTEUR // 2
robot_angle = 0

# Constantes de contrôle
VITESSE_MAX = 1000
VITESSE_ROTATION_MAX = math.pi/100

# Initialisation de Pygame
pygame.init()
fenetre = pygame.display.set_mode((CARTE_LARGEUR, CARTE_HAUTEUR))
pygame.display.set_caption("Contrôle du robot")

# Boucle principale
en_cours = True
horloge = pygame.time.Clock()
while en_cours:
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False

    # Contrôle du robot
    vitesse_lineaire = 0
    vitesse_rotation = 0

    touches = pygame.key.get_pressed()
    if touches[pygame.K_z]:
        vitesse_lineaire = VITESSE_MAX
    elif touches[pygame.K_s]:
        vitesse_lineaire = -VITESSE_MAX

    if touches[pygame.K_q]:
        vitesse_rotation = VITESSE_ROTATION_MAX
    elif touches[pygame.K_d]:
        vitesse_rotation = -VITESSE_ROTATION_MAX

    # Mise à jour de la position et de l'orientation du robot
    vitesse_gauche = (2 * vitesse_lineaire - vitesse_rotation * ROBOT_LARGEUR) / (2 * ROBOT_HAUTEUR)
    vitesse_droite = (2 * vitesse_lineaire + vitesse_rotation * ROBOT_LARGEUR) / (2 * ROBOT_HAUTEUR)

    vitesse_avance = (vitesse_gauche + vitesse_droite) / 2
    vitesse_rotation = (vitesse_droite - vitesse_gauche) * (180 / math.pi)  # Conversion en degrés

    robot_angle += math.radians(vitesse_rotation)
    robot_x += vitesse_avance * math.cos(robot_angle)
    robot_y -= vitesse_avance * math.sin(robot_angle)

    # Limitation des coordonnées du robot à l'intérieur de la carte
    robot_x = max(0, min(CARTE_LARGEUR - ROBOT_LARGEUR, robot_x))
    robot_y = max(0, min(CARTE_HAUTEUR - ROBOT_HAUTEUR, robot_y))

    # Effacement de l'écran
    fenetre.fill(COULEUR_FOND)

    # Affichage de l'image du robot
    robot_image_rotate = pygame.transform.rotate(robot_image, math.degrees(robot_angle)+90)
    fenetre.blit(robot_image_rotate, (robot_x, robot_y))

    # Rafraîchissement de l'écran
    pygame.display.flip()
    horloge.tick(60)

# Fermeture de la fenêtre Pygame
pygame.quit()
