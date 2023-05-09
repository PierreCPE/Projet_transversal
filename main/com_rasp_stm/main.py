#!/usr/bin/python3 #-*- coding: latin-1 -*-
import serial
import time
ser = serial.Serial(
    port='/dev/ttyUSB1',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=None
)
#ser=serial.Serial('/dev/ttyUSB0',115200) #On defini un objet serial avec l'adresse du port et la vitesse
if not ser.isOpen(): #Est ce que le port est open si non alors on l'ouvre.
    ser.open()
print('com is open', ser.isOpen())
ser.flushInput()
ser.flushOutput() #On nettoie les buffers
message = b"0&14&15,1$"
#Encodage en byte.
print("message envoyé : ")
print(message)

while True: #on effectue une boucle infinie



    # for character in message :

    #     print(character)
    ser.write(message)
    # serial.write(b"salut$")
    # recep = serial.read(serial.in_waiting)
    print("message bien envoyé")
    print("avant message recu : ")
    reception = (ser.read()) #On lit sur le port serie et on affecte dans une variable #read().decode("utf8",errors="replace")
    time.sleep(1) 
    break
print("message recu : ")
print(reception) #On imprime dans la console
print ("fini")


