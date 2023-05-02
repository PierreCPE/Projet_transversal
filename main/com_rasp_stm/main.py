#!/usr/bin/python3 #-*- coding: latin-1 -*-
import serial
import time

serial=serial.Serial('/dev/ttyUSB0',115200) #On defini un objet serial avec l'adresse du port et la vitesse

while True: #on effectue une boucle infinie
    serial.flushInput();serial.flushOutput() #On nettoie les buffers
    number==(serial.readLine().decode("utf8",errors="replace")) #On lit sur le port serie et on affecte dans une variable
    print(number) #On imprime dans la console