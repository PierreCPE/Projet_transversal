#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

#pip install opencv-contrib-python

import serial
from flask_httpauth import HTTPBasicAuth
from flask import Flask, render_template, Response, request,  abort
import cv2
import numpy as np
import os
import logging
import math
import sched, time, threading


auth = HTTPBasicAuth()
app = Flask(__name__)
ip_list = set()

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

def check_ip(f):
    def wrapped(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in allowed_ips:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return wrapped


@app.route('/protected')
@auth.login_required
def protected_route():
    ip_address = request.remote_addr
    ip_list.add(ip_address)
    return "Vous êtes connecté en tant que : {} et votre adresse IP est autorisée.".format(auth.current_user())


def gen_frames():
    cap = cv2.VideoCapture(0) # Replace 0 with your camera index if you have multiple cameras

    # Obtenir les propriétés de la vidéo
    largeur = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hauteur = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    centreX_video = largeur // 2
    centreY_video = hauteur // 2
    cpt=0
    detection = config['detection_contour']
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

            if cpt % 100 == 0: #Si cpt est un multiple de 100 alors on rentre dans la boucle. 
                # Trouver le plus grand contour (l'objet rouge entouré de bleu)
                surface_max=None #le contour ayant la plus grande surface dans l'image
                val_surface_max=0 #la valeur de la surface  maximale trouvée
                for contour in contours:
                    surface_contour = cv2.contourArea(contour) #calcule la surface du contour courant 
                    if surface_contour > val_surface_max:
                        surface_max = contour #contiends le contour avec la plus grande surface
                        val_surface_max = surface_contour #contiends la valeur de cette surface maximale
            cpt = cpt + 1
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
                #x_norm = x/ largeur
                #y_norm = y / hauteur   
                #si x est positif, le robot doit tourner à droite. Plus x est grand, plus le centre de la video est loin de l'objet au sens de l'horizontale
                #si y est positif, le robot doit baisser la tete. Plus y est grand, plus le centre de la video est loin de l'objet au sens de la verticale

                print('')
                print("Coordonnée de", x, "et de " ,y,"par rapport au centre")
                print('')


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

@app.route('/')
@auth.login_required
@check_ip
def index(): 
    ip_address = request.remote_addr
    ip_list.add(ip_address)
    return render_template('index.html')

def print_ip_list():
    print("IPs ayant tenté de se connecter au site :")
    for ip in ip_list:
        print(ip)

def schedule_ip_display():
    s = sched.scheduler(time.time, time.sleep)
    while True:
        s.enter(5, 1, print_ip_list, ()) # 600 secondes = 10 minutes
        s.run()

    

@app.route('/camera.html')
@auth.login_required
def camera_page():
    ip_address = request.remote_addr
    ip_list.add(ip_address)
    return render_template('camera.html')


@app.route('/videofeed')
@auth.login_required
def videofeed():
    ip_address = request.remote_addr
    ip_list.add(ip_address)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/commandes', methods=['POST'])
@auth.login_required
def controlCommandes():
    ip_address = request.remote_addr
    ip_list.add(ip_address)
    json_data = request.get_json()
    # print(json_data)
    max_speed = 30
    speed = 0
    if config['speed_variable']:
        if 'LT' in json_data:
            speed = max_speed*json_data['LT']
            print("Speed",speed)
    else:
        speed = max_speed
    if 'JoystickLeft' in json_data:
        x_left = json_data["JoystickLeft"][0]
        y_left = json_data["JoystickLeft"][1]
        rotation_coef = (x_left / 2)
        right_power = -speed*(y_left + rotation_coef)
        left_power = -speed*(y_left - rotation_coef)
        cmd = f"mogo 1:{right_power} 2:{left_power}\n\r"
        print(f"Send {cmd}")
        if config['serial']:
            ser.write(cmd.encode())
    else:
        if config['serial']:
            ser.write("stop\n\r".encode())
    return 'OK'


if __name__=="__main__" :
    # Configuration
    ###########################################
    config = {}
    config['detection_contour'] = True
    config['serial'] = False # Activer ou non le port serial
    config['serial_port'] = 'COM8' # Port série
    # config['serial_port'] = '/dev/ttyUSB0' # Port série
    config['serial_baudrate'] = 115200 # Baudrate du port série
    config['gomete_path'] = "gomete.jpg"
    config['speed_variable'] = True # Fixe ou non la vitesse du robot (si non dépendente de la touche LT)
    config['log_all_requests'] = False
    ###########################################


    if config['serial']:
        ser = serial.Serial(config['serial_port'])
        ser.baudrate = config['serial_baudrate']

    # Chargement de l'image "gomete"
    gomete = cv2.imread(config['gomete_path'])
    
    # Extraire les valeurs minimale et maximale de rouge dans l'image "gomete"
    hsv_gomete = cv2.cvtColor(gomete, cv2.COLOR_BGR2HSV)
    min_h, max_h, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,0])
    min_s, max_s, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,1])
    min_v, max_v, _, _ = cv2.minMaxLoc(hsv_gomete[:,:,2])

    # Définir les couleurs de la plage de couleurs à détecter à partir de l'image "test"
    rouge_clair = np.array([min_h, min_s, min_v])
    rouge_fonce = np.array([max_h, max_v, max_v])
    if config['log_all_requests']:
        app.logger.disabled = True

    allowed_ips = ['134.214.51.114', '192.168.56.1', '192.168.202.1', '192.168.99.33','127.0.0.1']

    users = {
        "user1": "1234",
        "user2": "5678"
    }
    #lancement regulier de la lecture des IPs
    ip_display_thread = threading.Thread(target=schedule_ip_display)
    ip_display_thread.daemon = True
    ip_display_thread.start()

    app.run(host="0.0.0.0", debug=False)
    if config['serial']:
        ser.close()
