#!/usr/bin/python3 #-*- coding: latin-1 -*-
import serial
import time

serial=serial.Serial('COM6',115200) #On defini un objet serial avec l'adresse du port et la vitesse
if not serial.isOpen(): #Est ce que le port est open si non alors on l'ouvre.
    serial.open()
print('com is open', serial.isOpen())

while True: #on effectue une boucle infinie
    serial.flushInput();serial.flushOutput() #On nettoie les buffers
    message = "salut$"
    b = message.encode('utf-8') #Encodage en byte.
    print("message envoyé : ")
    print(b)
    serial.write(b)
    number = (serial.readline().decode("utf8",errors="replace")) #On lit sur le port serie et on affecte dans une variable
    print("message recu : ")
    print(number) #On imprime dans la console
    

