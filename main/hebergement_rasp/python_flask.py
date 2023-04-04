import os
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response
import datetime

GPIO.setmode(GPIO.BCM)
dataPin=[i for i in range(2,28)]
for dp in dataPin: GPIO.setup(dp,GPIO.IN)#,pull_up_down=GPIO.PUD_UP)

data=[]
now=datetime.datetime.now()
timeString=now.strftime("%Y-%m-%d %H:%M")
templateData={
    'title':'Raspberry Pi 3B+ Web Controller',
    'time':timeString,
    'data':data,
}

def getData():
    data=[]
    for i,dp in enumerate(dataPin): data.append(GPIO.input(dataPin[i]))
    
    return data

app=Flask(__name__)
    
@app.route('/')
def index():
    #return 'hello world!'
    now=datetime.datetime.now()
    timeString=now.strftime("%Y-%m-%d %H:%M")
    data=getData()
    templateData={
        'title':'Raspberry Pi 3B+ Web Controller',
        'time':timeString,
        'data':data,
    }
    #return render_template('rpi_index.html',**templateData)
    return render_template('html_test_raspberry_web.html',**templateData)           

@app.route('/<actionid>') 
def handleRequest(actionid):
    print("Button pressed : {}".format(actionid))
    return "OK 200"   
                              
if __name__=='__main__':
    os.system("sudo rm -r  ~/.cache/chromium/Default/Cache/*")
    app.run(debug=True, port=5000, host='172.20.10.2',threaded=True)
    #local web server http://192.168.1.200:5000/
    #after Port forwarding Manipulation http://xx.xx.xx.xx:5000/