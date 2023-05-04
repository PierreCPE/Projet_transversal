#!/usr/bin/python3 #-*- coding: latin-1 -*-
import serial
import time

serial=serial.Serial('/dev/ttyUSB0',115200) #On defini un objet serial avec l'adresse du port et la vitesse
if not serial.isOpen(): #Est ce que le port est open si non alors on l'ouvre.
    serial.open()
print('com is open', serial.isOpen())

while True: #on effectue une boucle infinie
    serial.flushInput();serial.flushOutput() #On nettoie les buffers
    message = "ceci est un test$"
    print(message)
      #Encodage en byte.
    print("message envoyé : ")
    message = bytes(message,'utf8')
    print(message)
    for character in message :

        print(character)
        serial.write(character)
    # serial.write(b"salut$")
    # recep = serial.read(serial.in_waiting)
    # print(recep)
    print("avant message recu : ")
    reception = (serial.readline()) #On lit sur le port serie et on affecte dans une variable #read().decode("utf8",errors="replace")
    print(reception) #On imprime dans la console
    

