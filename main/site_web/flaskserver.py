from flask import Flask, render_template, Response, request, abort
from flask_httpauth import HTTPBasicAuth
import time
from flask_httpauth import HTTPBasicAuth
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from timer import timer

class FlaskServer:
    def __init__(self, config={}, sharedVariables=None, sharedFrame=None):
        self.config = config
        self.sharedVariables = sharedVariables
        self.sharedFrame = sharedFrame

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
            "local": {"password": "1234", "ip": '127.0.0.1'},
            "user6": {"password": "181920", "ip": '192.168.121.198'},
            "user7": {"password": "151617", "ip": '192.168.224.226'},
            "user8": {"password": "1234", "ip": '192.168.224.33'},
            "user9": {"password": "1234", "ip": '192.168.224.18'}
        }
        self.logs = {}
        self.logsAuth = {}

        # authentification
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
        
        
        @self.app.route('/commandes', methods=['POST'])
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
            return render_template('camera.html', detection_contour=self.config['detection_contour'], point_simulation=self.config["point_simulation"],point_simulation_data=self.sharedVariables['point_simulation_data'])
        
        @self.app.route('/videofeed')
        @self.auth.login_required
        def videofeed():
            return Response(self.genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
        @self.app.route('/')
        @self.auth.login_required
        @self.limiter.limit(f"{self.limit_connection_amount} per day")
        def index():
            return render_template('index.html')

    def configCommandes(self, json_data):
        # check if detection_contour is in json_data
        if "detection_contour" in json_data:
            self.config['detection_contour'] = json_data["detection_contour"]
        # check if speed_variable is in json_data
        if "speed_variable" in json_data:
            self.config['speed_variable'] = json_data["speed_variable"]
        # check if serial is in json_data
        if "serial" in json_data:
            self.config['serial'] = json_data["serial"]
        # check if point_simulation is in json_data
        if "point_simulation" in json_data:
            self.config['point_simulation'] = json_data["point_simulation"]
        # check if point_simulation_data is in json_data
        if "point_simulation_data" in json_data:
            self.sharedVariables['point_simulation_data'] = json_data["point_simulation_data"]
        if "capture_color" in json_data:
            self.sharedVariables['capture_color'] = True
        # check if mode is in json_data
        if "mode" in json_data:
            self.sharedVariables['mode'] = json_data["mode"]

    def controlCommandes(self, json_data):
        self.sharedVariables['manualControlJson'] = json_data
    
    def genFrames(self):
        while True:
            frame = self.sharedFrame.getFrame()
            # print(image is not None)
            # get width and height of frame, where frame is bytes encoded image
            if frame is not None:
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                # generate empty frame
                frame = b''
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def run(self):
        print("Starting Flask Server")
        # Start image detection thread
        self.app.run(host="0.0.0.0", debug=False)
