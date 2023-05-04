# import cv2
# import numpy as np

# lo=np.array([95, 100, 50])
# hi=np.array([105, 255, 255])
# cap=cv2.VideoCapture(0)

# while True:
#     ret, frame=cap.read()
#     image=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     mask=cv2.inRange(image, lo, hi)
#     image2=cv2.bitwise_and(frame, frame, mask=mask)

#     # Détection des cercles
#     gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
#     circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
#     if circles is not None:
#         circles = np.round(circles[0, :]).astype("int")
#         for (x, y, r) in circles:
#             cv2.circle(image2, (x, y), r, (0, 255, 0), 2)
    

#     cv2.imshow('Camera', frame)
#     cv2.imshow('image2', image2)
#     cv2.imshow('Mask', mask)
#     if cv2.waitKey(1)==ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()





# # # import cv2
# # # import numpy as np

# # # lo = np.array([95, 100, 50])
# # # hi = np.array([105, 255, 255])
# # # cap = cv2.VideoCapture(0)

# # # while True:
# # #     ret, frame = cap.read()
# # #     image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
# # #     mask = cv2.inRange(image, lo, hi)
# # #     image2 = cv2.bitwise_and(frame, frame, mask=mask)
    
# # #     # Détection des cercles
# # #     gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
# # #     circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
# # #     if circles is not None:
# # #         circles = np.round(circles[0, :]).astype("int")
# # #         for (x, y, r) in circles:
# # #             cv2.circle(image2, (x, y), r, (0, 255, 0), 2)
    
# # #     # Affichage des images
# # #     combined = cv2.hconcat([frame, image2])
# # #     cv2.imshow('Combined', combined)
# # #     cv2.imshow('Mask', mask)
    
# # #     if cv2.waitKey(1) == ord('q'):
# # #         break

# # # cap.release()
# # # cv2.destroyAllWindows()





import cv2
import numpy as np

# gomete = cv2.imread('Detection de point rouge\gomete.jpg')

# # Extraire les valeurs minimale et maximale de rouge dans l'image "gomete"
# hsv_gomete = cv2.cvtColor(gomete, cv2.COLOR_BGR2HSV)
# min_h, max_h, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,0])
# min_s, max_s, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,1])
# min_v, max_v, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,2])

# # Définir les couleurs de la plage de couleurs à détecter à partir de l'image "test"
# lo = np.array([min_h, min_s, min_v])
# hi = np.array([max_h, max_v, max_v])

lo = np.array([95, 100, 50])
hi = np.array([105, 255, 255])
cap=cv2.VideoCapture(0)

while True:
    ret, frame=cap.read()
    image=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(image, lo, hi)
    image2=cv2.bitwise_and(frame, frame, mask=mask)
    
    # Trouver les cercles dans l'image2
    gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=20, param2=10, minRadius=5, maxRadius=10)
    
    # Dessiner les cercles trouvés sur une image noire
    circle_img = np.zeros_like(gray)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            cv2.circle(circle_img,(i[0],i[1]),i[2],(255,255,255),-1)
    
    # Appliquer le masque pour garder seulement les cercles de l'image2
    image_cercle = cv2.bitwise_and(image2, image2, mask=circle_img)

    cv2.imshow('Camera', frame)
    cv2.imshow('image2', image2)
    cv2.imshow('Mask', mask)
    cv2.imshow('image_cercle', image_cercle)
    
    if cv2.waitKey(1)==ord('q'):
        break
        
cap.release()
cv2.destroyAllWindows()

















# import cv2
# import numpy as np

# # Paramètres de détection de cercles
# dp = 1
# minDist = 500
# param1 = 50
# param2 = 30
# minRadius = 0
# maxRadius = 0

# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
#     # Appliquer un filtre de flou pour réduire le bruit
#     gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
#     # Détecter les cercles dans l'image
#     circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    
#     if circles is not None:
#         # Convertir les coordonnées des cercles en entiers
#         circles = np.round(circles[0, :]).astype("int")
        
#         # Créer un masque des cercles détectés
#         mask = np.zeros(gray.shape, dtype=np.uint8)
#         for (x, y, r) in circles:
#             cv2.circle(mask, (x, y), r, 255, -1)
        
#         # Appliquer une opération de fermeture pour améliorer la forme des cercles détectés
#         kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
#         mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
#         # Appliquer le masque pour ne garder que les cercles détectés
#         image_cercle = cv2.bitwise_and(frame, frame, mask=mask)
        
#         cv2.imshow('Camera', frame)
#         cv2.imshow('Mask', mask)
#         cv2.imshow('Circles', image_cercle)
    
#     if cv2.waitKey(1) == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
