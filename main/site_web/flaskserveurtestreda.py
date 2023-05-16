#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

#pip install opencv-contrib-python

import serial
from flask_httpauth import HTTPBasicAuth
from flask import Flask, render_template, Response, request,  abort, jsonify
import cv2
import numpy as np
import os
import logging
import math
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

class FlaskApp:
    def __init__(self):
        self.auth = HTTPBasicAuth()
        self.app = Flask(__name__)
        self.limit_connection_amount = 200
        self.limiter = Limiter(
            get_remote_address,
            app=self.app,
            default_limits=["200 per day", "50 per hour"]
        )
        self.users = {
            "user1": "1234",
            "user2": "5678",
        }
        self.allowed_ips = ['134.214.51.114', '192.168.56.1',
                            '192.168.202.1', '192.168.121.33', '127.0.0.1','192.168.121.198']
        
        @self.auth.verify_password
        def verify_password(username, password):
            if username in self.users and self.users[username] == password:
                return username

        @self.app.route('/protected')
        @self.auth.login_required
        def protected_route():
            return "Vous êtes connecté en tant que : {} et votre adresse IP est autorisée.".format(self.auth.current_user())

        @self.app.route('/')
        @self.auth.login_required
        @self.limiter.limit(f"{self.limit_connection_amount} per day")
        def index():
            return render_template('index.html')

        @self.app.route('/camera.html')
        @self.auth.login_required
        def camera_page():
            return render_template('camera.html')

    def run(self):
        self.app.run(host="0.0.0.0", debug=False)
        if self.config['serial']:
            self.ser.close()


if __name__=="__main__" :
    global auth
    limit_connection_amount = 200
    auth = HTTPBasicAuth()
    flask_app = FlaskApp()
    flask_app.run()
