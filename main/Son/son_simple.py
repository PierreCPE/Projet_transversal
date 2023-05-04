import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Paramètres d'enregistrement
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5

# Initialisation de PyAudio
p = pyaudio.PyAudio()

# Ouverture du flux audio en entrée
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Enregistrement du son
frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

# Fermeture du flux audio en entrée
stream.stop_stream()
stream.close()

# Conversion des données audio en un tableau NumPy
audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

# Calcul du spectre de Fourier
fft_data = np.fft.fft(audio_data)
freqs = np.fft.fftfreq(len(fft_data), 1.0/RATE)
magnitude = np.abs(fft_data)

# Affichage du spectre de Fourier
plt.plot(freqs[:len(freqs)//2], magnitude[:len(magnitude)//2])
plt.xlabel('Fréquence (Hz)')
plt.ylabel('Amplitude')
plt.show()

# Fermeture de PyAudio
p.terminate()
