#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

#pip install opencv-contrib-python


from flask import Flask, render_template, Response
import cv2



def gen_frames():
    cap = cv2.VideoCapture(0) # Replace 0 with your camera index if you have multiple cameras
    nom="fenêtre caméra"
    #largeur=int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    #hauteur=int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #cv2.namedWindow(nom, cv2.WND_PROP_FULLSCREEN)
    detection = False
    while True:
        if detection:
            pass
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

if __name__=="__main__" :
    app.run(debug=True)