#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

#pip install opencv-contrib-python

import serial
from flask import Flask, render_template, Response, request
import cv2
import numpy as np


def gen_frames():
    cap = cv2.VideoCapture(0) # Replace 0 with your camera index if you have multiple cameras

    # Obtenir les propriétés de la vidéo
    largeur = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hauteur = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    centreX_video = largeur // 2
    centreY_video = hauteur // 2

    detection = True
    while True:
        if detection:
            res, image = cap.read() #res est un bollean qui verifie si la video a pu etre lu est image est une "capture de video"
            if res == False:  
                break

            # Convertir la trame vidéo en HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Appliquer le masque pour détecter les pixels rouges
            masque = cv2.inRange(hsv, rouge_clair, rouge_fonce)

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
            ret,buffer = cv2.imencode('.jpg', image)

            frame = buffer.tobytes()
            # Afficher la trame courante avec les contours dans une fenêtre de sortie
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame  + b'\r\n')
        else:
            ret, frame = cap.read()
            if not ret:
                break
            ret,buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    #cap.release()


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera.html')
def camera_page():
    return render_template('camera.html')

@app.route('/videofeed')
def videofeed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/commandes', methods=['POST'])
def controlCommandes():
    json_data = request.get_json()
    # print(json_data)
    if 'JoystickLeft' in json_data:
        x_left = json_data["JoystickLeft"][0]
        y_left = json_data["JoystickLeft"][1]
        speed = 30
        cmd = f'mogo 1:{-speed*y_left} 2:{-speed*y_left}\n\r'
        print(f"Send {cmd}")
        ser.write(cmd.encode())
        # print("Move")
    else:
        ser.write("stop\n\r".encode())
    return 'OK'

if __name__=="__main__" :
    ser = serial.Serial("COM8")
    ser.baudrate = 115200
    # Chargement de l'image "gomete"
    gomete = cv2.imread('gomete.jpg')
    
    # Extraire les valeurs minimale et maximale de rouge dans l'image "gomete"
    hsv_gomete = cv2.cvtColor(gomete, cv2.COLOR_BGR2HSV)
    min_h, max_h, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,0])
    min_s, max_s, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,1])
    min_v, max_v, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,2])

    # Définir les couleurs de la plage de couleurs à détecter à partir de l'image "test"
    rouge_clair = np.array([min_h, min_s, min_v])
    rouge_fonce = np.array([max_h, max_v, max_v])
    app.run(debug=False)
    ser.close()
