#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#pip install opencv-contrib-python

import serial
from flask_httpauth import HTTPBasicAuth
from flask import Flask, render_template, Response, request, abort, jsonify, session, redirect, url_for
import cv2
import numpy as np
import os
import logging
import math
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

auth = HTTPBasicAuth()
app = Flask(__name__)
limit_connection_amount = 200

app.secret_key = "my_secret_key"

users = {"user": "password"}
allowed_ips = ["127.0.0.1"]

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

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/protected')
@auth.login_required
def protected_route():
    return "Vous êtes connecté en tant que : {} et votre adresse IP est autorisée.".format(auth.current_user())


def gen_frames():
    cap = cv2.VideoCapture(0) # Replace 0 with your camera index if you have multiple cameras

    # Obtenir les propriétés de la vidéo
    largeur = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hauteur = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    centreX_video = largeur // 2
    centreY_video = hauteur // 2
    cpt = 0
    detection = config['detection_contour']
    while True:
        if detection:
            res, image = cap.read() #res est un bollean qui verifie si la video a pu etre lue et image est une "capture de video"
            if not res:
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
            cv2.line(image, (centreX_video - 10, centreY_video), (centreX_video + 10, centreY_video), couleur_l
