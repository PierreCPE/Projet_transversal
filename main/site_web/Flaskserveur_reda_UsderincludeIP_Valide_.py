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
        self.limit_connection_amount = 2000
        self.limiter = Limiter(
            get_remote_address,
            app=self.app,
            default_limits=["2000 per day", "500 per hour"]
        )

        self.users = {
        "user1": {"password": "1234", "ip": '134.214.51.114'},
        "user2": {"password": "5678", "ip": '192.168.56.1'},
        "user3": {"password": "91011", "ip": '192.168.202.1'},
        "user4": {"password": "121314", "ip": '192.168.121.33'},
        "user5": {"password": "151617", "ip": '127.0.0.1'},
        "user6": {"password": "181920", "ip": '192.168.121.198'},
        "user7": {"password": "151617", "ip": '192.168.224.226'},
        "user8": {"password": "1234", "ip": '192.168.224.33'},
        "user9": {"password": "1234", "ip": '192.168.224.18'}
        }

        @self.auth.verify_password
        def verify_password(username, password):
            client_ip = request.remote_addr
            if username in self.users and self.users[username]['password'] == password and self.users[username]['ip'] == client_ip:
                return True
            return False

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

if __name__=="__main__":
    global auth
    limit_connection_amount = 200
    auth = HTTPBasicAuth()
    flask_app = FlaskApp()
    flask_app.run()
