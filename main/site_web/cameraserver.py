import cv2
import numpy as np
import time

class CameraServer:
    def __init__(self, config = {}, sharedVariables = None ,sharedFrame = None):
        self.config = config
        self.sharedVariables = sharedVariables
        self.sharedFrame = sharedFrame
        # self.sharedFrame = self.config['shared_frame']
        self.initRedPointDetection()

    def initRedPointDetection(self):
        # Chargement de l'image "gomete"
        gomete = cv2.imread(self.config['gomete_path'])
        
        # Extraire les valeurs minimale et maximale de rouge dans l'image "gomete"
        self.hsv_gomete = cv2.cvtColor(gomete, cv2.COLOR_BGR2HSV)
        min_h, max_h, _, _ = cv2.minMaxLoc(self.hsv_gomete[:,:,0])
        min_s, max_s, _, _ = cv2.minMaxLoc(self.hsv_gomete[:,:,1])
        min_v, max_v, _, _ = cv2.minMaxLoc(self.hsv_gomete[:,:,2])

        # Définir les couleurs de la plage de couleurs à détecter à partir de l'image "test"
        self.rouge_clair = np.array([min_h, min_s, min_v])
        self.rouge_fonce = np.array([max_h, max_v, max_v])

    def applyRedPointDetection(self, image):
        # Obtenir les dimensions de la vidéo
        hauteur, largeur, _ = image.shape
        centreX_video = largeur // 2
        centreY_video = hauteur // 2
        # Convertir la trame vidéo en HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Appliquer le masque pour détecter les pixels rouges
        masque = cv2.inRange(hsv, self.rouge_clair, self.rouge_fonce)
        # Trouver les contours des objets dans l'image
        contours, hierarchie = cv2.findContours(masque, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Dessiner des contours bleus autour des objets détectés
        for contour in contours:
            cv2.drawContours(image, [contour], 0, (255, 255, 0), 2)
        # Dessiner la croix au centre de la vidéo
        epaisseur_ligne = 2 # l'épaisseur des lignes de la croix
        couleur_ligne = (255, 255, 255) # la couleur de la croix 
        cv2.line(image, (centreX_video, centreY_video - 10), (centreX_video, centreY_video + 10), couleur_ligne, epaisseur_ligne)
        cv2.line(image, (centreX_video - 10, centreY_video), (centreX_video + 10, centreY_video), couleur_ligne, epaisseur_ligne)
        # Trouver le plus grand contour (l'objet rouge entouré de bleu)
        surface_max=None #le contour ayant la plus grande surface dans l'image
        val_surface_max=0 #la valeur de la surface  maximale trouvée
        for contour in contours:
            surface_contour = cv2.contourArea(contour) #calcule la surface du contour courant 
            if surface_contour > val_surface_max:
                surface_max = contour #contiends le contour avec la plus grande surface
                val_surface_max = surface_contour #contiends la valeur de cette surface maximale
        #Si aucun contour n'a été détecté dans l'image, surface_max restera à None.
        # Si un objet rouge entouré de bleu a été détecté, récupérer sa position et la comparer avec le centre de l'image
        if np.all(surface_max) != None:
            
            # Récupérer les coordonnées du rectangle englobant du plus grand contour
            x, y, l, h = cv2.boundingRect(surface_max) #x et y sont les coordonnée en haut a gauche du rectangle. l et h sont la longueur et la hauteur du rectangle
            # Calculer la position de l'objet par rapport au centre de l'image
            centreX_rect = x + l / 2
            centreY_rect = y + h / 2

            x= centreX_rect -centreX_video
            y= centreY_rect -centreY_video

            x_norm = 2*x / largeur
            y_norm = 2*y / hauteur
            #arrondir les valeurs de x_norm et y_norm à 2 chiffres après la virgule
            x_norm = round(x_norm,2)
            y_norm = round(y_norm,2)

            # draw a green point of 12px at x_norm, y_norm
            cv2.circle(image, (int(centreX_rect), int(centreY_rect)), 12, (0, 255, 0), -1)
            # écrit x_norm et y_norm sur l'image en bas à gauche en vert de taille 20 et en gras
            cv2.putText(image, "x: " + str(x_norm) + " y: " + str(y_norm), (10, hauteur - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)


            #si x est positif, le robot doit tourner à droite. Plus x est grand, plus le centre de la video est loin de l'objet au sens de l'horizontale
            #si y est positif, le robot doit baisser la tete. Plus y est grand, plus le centre de la video est loin de l'objet au sens de la verticale
            self.sharedVariables['detected_object'] = True
            self.sharedVariables['detected_object_xy_norm'] = [x_norm,y_norm]
        return image, surface_max, centreX_video, centreY_video


    def run(self):
        print("Starting camera server")
        # Capture de la video
        cap = cv2.VideoCapture(0) # Replace 0 with your camera index if you have multiple cameras
        cpt=0
        
        while True:
            detection = self.config['detection_contour']
            res, image = cap.read() #res est un bollean qui verifie si la video a pu etre lu est image est une "capture de video"
            image = cv2.flip(image, 1) #mirroir de l'image
            if res == False:
                break
            if detection:
                image, surface_max, centreX_video, centreY_video = self.applyRedPointDetection(image)
                # Définir la qualité maximale pour la compression JPEG
                quality = self.config['video_quality']
                # Définir les paramètres pour l'encodage JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                ret,buffer = cv2.imencode('.jpg', image, encode_param)
                frame = buffer.tobytes()
                # Afficher la trame courante avec les contours dans une fenêtre de sortie
                self.sharedFrame.setFrame(frame)
            else:
                # encode image with a fixed buffer length
                # Définir la qualité maximale pour la compression JPEG
                quality = self.config['video_quality']
                # Définir les paramètres pour l'encodage JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                ret,buffer = cv2.imencode('.jpg', image,encode_param)
                frame = buffer.tobytes()
                self.sharedFrame.setFrame(frame)
            time.sleep(0.05)
        cap.release()