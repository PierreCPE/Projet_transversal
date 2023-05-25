import serial
from flask_httpauth import HTTPBasicAuth
from flask import Flask, render_template, Response, request, abort, jsonify, flash, redirect, url_for
import cv2
import numpy as np
import os
import logging
import math
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import login_required, current_user

class FlaskApp:
    def __init__(self):
        self.auth = HTTPBasicAuth()
        self.app = Flask(__name__)
        self.app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
        self.limit_connection_amount = 2000
        self.limiter = Limiter(
            get_remote_address,
            app=self.app,
            default_limits=["200000 per day", "20000 per hour"]
        )

        self.users = {
            "user1": {"password": "1234", "ip": '134.214.51.114'},
            "user2": {"password": "5678", "ip": '192.168.56.1'},
            "user3": {"password": "91011", "ip": '192.168.202.1'},
            "user4": {"password": "121314", "ip": '192.168.47.33'},
            "local": {"password": "1234", "ip": '127.0.0.1'},
            "user6": {"password": "181920", "ip": '192.168.121.198'},
            "user7": {"password": "151617", "ip": '192.168.47.226'},
            "hugues": {"password": "1234", "ip": '192.168.47.33'},
            "user9": {"password": "1234", "ip": '192.168.47.18'}
        }
        self.logs = {}
        self.logsAuth = {}

        @self.auth.verify_password
        def verify_password(username, password):
                client_ip = request.remote_addr
                if not client_ip in self.tentatives:
                    self.tentatives[client_ip] = 4
                if self.tentatives[client_ip] > 0 :
                    print(self.tentatives)
                    print(self.tentatives[client_ip])
                    
                    if username in self.users and self.users[username]['password'] == password and self.users[username]['ip'] == client_ip:
                        return True
                    self.tentatives[client_ip] = self.tentatives[client_ip] - 1
                    return False
                    

                else :
                    flash("ADDRESSE IP BLOQUEE. Trop de tentatives réalisées.")
                    return False  
                
    
             
            

                

        @self.app.route('/verified')
        @self.auth.login_required
        def protected_route():
            return "Vous êtes connecté en tant que : {} et votre adresse IP est autorisée.".format(self.auth.current_user())

        @self.app.route('/', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                if verify_password(username, password):
                    return render_template('index.html')
                else:
                    flash('Erreur Username ou Mot de Passe. Veuillez réessayer.')
            return render_template('login.html')

        @self.auth.login_required
        def commandes():
            # print("commandes")
            print(request)
            json_data = request.get_json()
            print(json_data)
            if "control" in json_data:
                self.controlCommandes(json_data["control"])
            if "config" in json_data:
                self.configCommandes(json_data["config"])
            return 'OK'

        @self.app.route('/camera.html')
        @self.auth.login_required
        def camera_page():
            return render_template('camera.html')

        @self.app.route('/register', methods=['GET', 'POST'])
        @self.auth.login_required
        def register():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                ip = request.form.get('ip')
                if username not in self.users:
                    self.users[username] = {"password": password, "ip": ip}
                    return jsonify({"message": "User registered successfully"}), 201
                else:
                    return jsonify({"message": "User already exists"}), 400
            else:
                return render_template('Register.html')
            
        

    def run(self):
        self.app.run(host="0.0.0.0", debug=False)

if __name__=="__main__":
    global auth
    #global tentative
    limit_connection_amount = 200
    auth = HTTPBasicAuth()
    flask_app = FlaskApp()
    flask_app.run()
