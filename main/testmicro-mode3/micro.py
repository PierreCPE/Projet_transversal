#pip3 install sounddevice
#pip3 install wavio

# import required libraries
import sounddevice as sd
# from scipy.io.wavfile import write
#import wavio as wv

p = input("y pour lancer l'enregistrement")

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
    print(recording)
    # This will convert the NumPy array to an audio
    # file with the given sampling frequency
    # write("son.wav", freq, recording)

    print("Enregistrement terminé")

    import winsound

    for i in range(3):
        print("Lecture en cours :", i+1)
        winsound.PlaySound('son.wav',winsound.SND_FILENAME)
        print("Fin de lecture :", i+1)
        i=i+1 
    print("Fin Mode 3")
