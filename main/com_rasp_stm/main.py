#!/usr/bin/python3 #-*- coding: latin-1 -*-
import serial
import time
ser = serial.Serial(
    port='/dev/ttyUSB0',
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
#Encodage en byte + mise de la commande
input = input("Commande svp: ")
message_arret = input+"$"
message = message_arret.encode()
print("message envoyé : ")
print(message)
#this will store the line
seq = []
count = 1

while True: #on effectue une boucle infinie
    
    ser.flushInput()
    ser.flushOutput() #On nettoie les buffers
    # for character in message :

    #     print(character)
    ser.write(message)
    # serial.write(b"salut$")
    # recep = serial.read(serial.in_waiting)
    print("message bien envoyé")
    print("avant message recu : ")
    #reception = (ser.readline(ser.in_waiting)) #On lit sur le port serie et on affecte dans une variable #read().decode("utf8",errors="replace")
    for c in ser.read():
        seq.append(chr(c)) #convert from ANSII
        joined_seq = ''.join(str(v) for v in seq) #Make a string from array

        if chr(c) == '\n':
            print("Line " + str(count) + ': ' + joined_seq)
            seq = []
            count += 1
            break
    break
print("message recu : ")
print(seq) #On imprime dans la console
print ("fini")


