#!/usr/bin/python3 #-*- coding: latin-1 -*-
import serial
import time
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=None
)
#ser=serial.Serial('/dev/ttyUSB0',115200) #On defini un objet serial avec l'adresse du port et la vitesse
if not ser.isOpen(): #Est ce que le port est open si non alors on l'ouvre.
    ser.open()
print('com is open', ser.isOpen())

while True: #on effectue une boucle infinie
    ser.flushInput()
    ser.flushOutput() #On nettoie les buffers
    message = "1234567$"
    print(message)
      #Encodage en byte.
    print("message envoyé : ")
    message = message.encode()
    print(message)
    # for character in message :

    #     print(character)
    ser.write(message)
    # serial.write(b"salut$")
    # recep = serial.read(serial.in_waiting)
    # print(recep)
    print("avant message recu : ")
    reception = (ser.read()) #On lit sur le port serie et on affecte dans une variable #read().decode("utf8",errors="replace")
    print("message recu : ")
    print(reception) #On imprime dans la console
    print ("fini")
    

