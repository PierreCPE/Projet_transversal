import cv2

def capture_image():
    # Ouvre la caméra
    cap = cv2.VideoCapture(0)

    # Boucle infinie pour l'affichage en temps réel
    while True:
        # Capture une image
        ret, frame = cap.read()

        # Affiche l'image dans la fenêtre
        cv2.imshow("Appuyer sur o lorsque la couluer que vous voulez detectée est au centre de la camera", frame)

        # Attend la touche "o" pour prendre une photo
        if cv2.waitKey(1) == ord('o'):
            # Recadre l'image
            # crop_img = frame[0:100, 0:100]

            h, l = frame.shape[:2]
            taille = 100
            x = (l - taille) // 2
            y = (h - taille) // 2
            crop_img = frame[y:y+taille, x:x+taille]

            # Enregistre l'image
            cv2.imwrite("img2.jpg", crop_img)
            break
    
    # Libère la caméra
    cap.release()

    # Ferme la fenêtre d'affichage
    cv2.destroyAllWindows()

