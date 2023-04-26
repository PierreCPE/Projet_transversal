from flask import Flask, render_template, Response, request, abort

class FlaskServer:
    def __init__(self, config = {}, sharedVariables = None, sharedFrame = None):
        self.config = config
        self.sharedVariables = sharedVariables
        self.sharedFrame = sharedFrame
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'index', self.index)
        # add camera page
        self.app.add_url_rule('/camera.html', '', self.camera_page)
        # add video feed
        self.app.add_url_rule('/videofeed', 'videofeed', self.videofeed)
        # add commandes
        self.app.add_url_rule('/commandes', 'controlCommandes', self.controlCommandes, methods=['POST'])
        # self.sharedFrame = self.config['shared_frame']


    def controlCommandes(self):
        json_data = request.get_json()
        # print(json_data)
        max_speed = 30
        speed = 0
        if self.config['speed_variable']:
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
            if self.config['serial']:
                self.config['ser'].write(cmd.encode())
        else:
            if self.config['serial']:
                self.config['ser'].write("stop\n\r".encode())
        return 'OK'

    def genFrames(self):
        while True:
            frame = self.sharedFrame.getFrame()
            # print(image is not None)
            # get width and height of frame, where frame is bytes encoded image
            if frame is not None:
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame  + b'\r\n')
            else:
                # generate empty frame
                frame = b''
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame  + b'\r\n')

    def camera_page(self):
        print("camera_page_request")
        return render_template('camera.html') 
    
    def videofeed(self):
        return Response(self.genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def index(self):
        self.config['blabla'] = "blabla"
        return render_template('index.html')

    def run(self):
        print("Starting Flask Server")
        # Start image detection thread
        self.app.run(host="0.0.0.0", debug=False)