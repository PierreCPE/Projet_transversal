from flask import Flask, render_template, Response, request, abort
from flask_httpauth import HTTPBasicAuth
import time

class FlaskServer:
    def __init__(self, config={}, sharedVariables=None, sharedFrame=None):
        self.config = config
        self.sharedVariables = sharedVariables
        self.sharedFrame = sharedFrame
        self.app = Flask(__name__)
        self.auth = HTTPBasicAuth()
        # add index page
        self.app.add_url_rule('/', 'index', self.index)
        # add decoration to check auth
        self.auth.verify_password(self.verify_password)
        # add decoration to check ip address with allowed_ips
        self.app.before_request(self.check_ip)

        # add camera page
        self.app.add_url_rule('/camera.html', '', self.camera_page)
        # add video feed
        self.app.add_url_rule('/videofeed', 'videofeed',
                              self.auth.login_required(self.videofeed))
        # add commandes
        self.app.add_url_rule('/commandes', 'commandes',
                              self.auth.login_required(self.commandes), methods=['POST'])
        # self.sharedFrame = self.config['shared_frame']
        self.allowed_ips = ['134.214.51.114', '192.168.56.1',
                            '192.168.202.1', '192.168.99.33', '127.0.0.1','192.168.99.192']
        self.users = {
            "user1": "1234",
            "user2": "5678"
        }
        self.logs = {}
        self.logsAuth = {}

    # authentification
    def verify_password(self, username, password):
        # print(request.remote_addr,username, password)
        preverify = True
        if request.remote_addr not in self.logsAuth:
            self.logsAuth[request.remote_addr] = []
        else:
            # if remote_addr contains in logsAuth with 5 failed authentification => block ip
            if len(self.logsAuth[request.remote_addr]) > 0 and len([x for x in self.logsAuth[request.remote_addr] if x[1] == False]) >= self.config['auth_failed_limit']:
                preverify = False
                self.allowed_ips.remove(request.remote_addr)
                print("//TODO To many try from", request.remote_addr, "=> block ip")
                abort(401)  # Forbidden

            # if remote_addr contains in logsAuth and the last authentification is less than 5 seconds
            if len(self.logsAuth[request.remote_addr]) > 0 and time.time() - self.logsAuth[request.remote_addr][-1][0] < self.config['auth_try_time']:
                preverify = False
                abort(401)  # Forbidden
            
        verify = preverify and username in self.users and self.users[username] == password
        self.logsAuth[request.remote_addr].append([time.time(), verify])
        if verify:
            return username

    # check if ip is in allowed_ips
    def check_ip(self):
        if request.remote_addr not in self.logs:
            self.logs[request.remote_addr] = []
        self.logs[request.remote_addr].append([time.time(), request.path])
        # print(self.logs[request.remote_addr])
        if request.remote_addr not in self.allowed_ips:
            abort(403)  # Forbidden

    def commandes(self):
        json_data = request.get_json()
        print(json_data)
        if "control" in json_data:
            self.controlCommandes(json_data["control"])
        if "config" in json_data:
            self.configCommandes(json_data["config"])
        return 'OK'

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

    def camera_page(self):
        return render_template('camera.html', detection_contour=self.config['detection_contour'], point_simulation=self.config["point_simulation"],point_simulation_data=self.sharedVariables['point_simulation_data'])

    def videofeed(self):
        return Response(self.genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def index(self):
        self.config['blabla'] = "blabla"
        return render_template('index.html')

    def run(self):
        print("Starting Flask Server")
        # Start image detection thread
        self.app.run(host="0.0.0.0", debug=False)
