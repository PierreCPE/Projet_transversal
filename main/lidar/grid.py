import numpy as np
import matplotlib.pyplot as plt

def generate_grid_image(points, image_size, grid_resolution):
    x_min = np.min(points[:, 0])
    x_max = np.max(points[:, 0])
    y_min = np.min(points[:, 1])
    y_max = np.max(points[:, 1])
    # image_size = (int(int(x_max-x_min)/grid_resolution[0]), int(int(y_max-y_min)/grid_resolution[0]))
    # Créer une image vide
    image = np.zeros(image_size)
    image.fill(255)
    print("Image size:",image_size)
    # Calculer la taille d'une cellule de grille
    cell_size = (grid_resolution[0], grid_resolution[1])
    print("Cell size:",cell_size)
    # Parcourir tous les points
    for point in points:
        # Obtenir les coordonnées du point
        x, y = point
        # Calculer les indices de la cellule de grille correspondante
        grid_x = int((x-x_min) // cell_size[0])
        grid_y = int((y-y_min) // cell_size[1])
        # Mettre à jour la valeur de la cellule de grille correspondante
        image[grid_x, grid_y] = 0

    # Afficher l'image générée
    return image

def image_to_points(image, grid_resolution):
    points = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i,j] == 0:
                points.append([i*grid_resolution[0], j*grid_resolution[1]])
    return np.array(points)