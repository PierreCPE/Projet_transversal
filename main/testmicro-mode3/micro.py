#pip3 install sounddevice
#pip3 install wavio
#pip3 install scipy
#pip3 install playsound
#pip3 install soundfile

# import required libraries
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write

from playsound import playsound

p = input("y pour lancer l'enregistrement")
print(sd.default.samplerate)
while p != "y":
    print("Mauvais caractère")
    p = input("y pour lancer l'enregistrement")

if p =="y":
    # Sampling frequency
    freq = 44100
  
    # Recording duration
    duration = 3
  
    # Start recorder with the given values 
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=1)

    print("Enregistrement en cours")
  
    # Record audio for the given number of seconds
    sd.wait()

    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    write("son.wav", freq, recording)

    print("Enregistrement terminé")

    k = 3

    for i in range(k):
        print("Lecture en cours :", i+1)
        playsound('son.wav')
        print("Fin de lecture :", i+1)
        i=i+1 
    print("Fin Mode", k)