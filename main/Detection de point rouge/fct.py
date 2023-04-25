# import cv2
# import numpy as np

# def fct(image):

#     # Convertir la trame vidéo en HSV
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

#     # Appliquer le masque pour détecter les pixels rouges
#     masque = cv2.inRange(hsv, rouge_clair, rouge_fonce)

#     # Trouver les contours des objets dans l'image
#     contours, hierarchie = cv2.findContours(masque, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#     # Dessiner des contours bleus autour des objets détectés
#     for contour in contours:
#         cv2.drawContours(image, [contour], 0, (0, 255, 255), 2)

#     # Dessiner la croix au centre de la vidéo
#     epaisseur_ligne = 2 # l'épaisseur des lignes de la croix
#     couleur_ligne = (255, 255, 255) # la couleur de la croix 
#     cv2.line(image, (centreX_video, centreY_video - 10), (centreX_video, centreY_video + 10), couleur_ligne, epaisseur_ligne)
#     cv2.line(image, (centreX_video - 10, centreY_video), (centreX_video + 10, centreY_video), couleur_ligne, epaisseur_ligne)

#     # Afficher la trame courante avec les contours dans une fenêtre de sortie
#     cv2.imshow("Video de la detection de la couleur precedement choisie ECHAP pour partir", image)

#     if cpt % 100 == 0: #Si cpt est un multiple de 100 alors on rentre dans la boucle. 
#         # Trouver le plus grand contour (l'objet rouge entouré de bleu)
#         surface_max=None #le contour ayant la plus grande surface dans l'image
#         val_surface_max=0 #la valeur de la surface  maximale trouvée
#         for contour in contours:
#             surface_contour = cv2.contourArea(contour) #calcule la surface du contour courant 
#             if surface_contour > val_surface_max:
#                 surface_max = contour #contiends le contour avec la plus grande surface
#                 val_surface_max = surface_contour #contiends la valeur de cette surface maximale
        
#         #Si aucun contour n'a été détecté dans l'image, surface_max restera à None.

#         # Si un objet rouge entouré de bleu a été détecté, récupérer sa position et la comparer avec le centre de l'image
#         if np.all(surface_max) != None:
#             # Récupérer les coordonnées du rectangle englobant du plus grand contour
#             x, y, l, h = cv2.boundingRect(surface_max) #x et y sont les coordonnée en haut a gauche du rectangle. l et h sont la longueur et la hauteur du rectangle

#             # Calculer la position de l'objet par rapport au centre de l'image
#             centreX_rect = x + l / 2
#             centreY_rect = y + h / 2

#             x= centreX_rect -centreX_video
#             y= centreY_rect -centreY_video  
        
#             #si x est positif, le robot doit tourner à droite. Plus x est grand, plus le centre de la video est loin de l'objet au sens de l'horizontale
#             #si y est positif, le robot doit baisser la tete. Plus y est grand, plus le centre de la video est loin de l'objet au sens de la verticale
        
#             print('')
#             print(x, y)
#             print('')

