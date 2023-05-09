import numpy as np
import sounddevice as sd
import scipy.signal as sig
import matplotlib.pyplot as plt
import pyaudio

p = pyaudio.PyAudio()

#PARAMETRES ANALYSE SPECTRALE

freq_min = 500
freq_max = 4000

# Taille de la fenetre d'analyse spéctrale en échantillons
taille_fenetre = 256 
#Plus elle est grande, plus la resolution fréquentielle est fine mais plus la resolution temporelle sera mauvaise.

# Pas entre chaque fenetre d'analyse
pas = 128
#Plus le pas est grand, plus l'analyse est fine mais plus elle est lente

# Taille de la FFT
taille_fft = 512 
# Elle permettra de determiner le nombre de points de la tranfomé de fourier. C'est la resolution fréquentielle. On note 
# que taille_fft >= taille_fenetre.


#PARAMETRES D'ENREGISTREMENT

# Fréquence d'échantillonnage
Fs = 44100 

# Durée de l'enregistrement en secondes
duree = 1

max_spectres_moyen=[]
nb_bruits_consecutifs = 0
bruit_detecte = False
premiere_detection = True
seuil = None

colors = ['cyan', 'magenta', 'yellow', 'orange', 'purple',  'pink', 'blue', 'green', 'red',  'gray']
fig, ax = plt.subplots()

#max_bruit = None

#ENREGISTREMENT
i=0
while nb_bruits_consecutifs < 2 and  not bruit_detecte:
    print("Enregistrement en cours")
    signal = sd.rec(int(duree * Fs), samplerate=Fs, channels=1) #Enregistre un signal audio à l'aide de la bibliothèque sounddevice pour une durée duree avec une fréquence d'échantillonnage Fs et un seul canal.
    sd.wait()
    
    f, t, S = sig.spectrogram(signal[:,0], fs=Fs, window='hann', nperseg=taille_fenetre, noverlap=taille_fenetre-pas, nfft=taille_fft, detrend=False) # Effectue une transformée de Fourier à court terme (STFT) sur le signal audio enregistré pour obtenir le spectrogramme S avec les fréquences f et les temps t.

    freq_bin = np.logical_and(f > freq_min, f <= freq_max) # Sélectionne les fréquences d'intérêt en utilisant une plage de fréquences comprises entre freq_min et freq_max.

    spectre_moyen = np.mean(np.abs(S[freq_bin, :]), axis=0) #Calcule le spectre moyen en prenant la moyenne de la valeur absolue des amplitudes des fréquences d'intérêt.
    
    ax.plot(t, spectre_moyen, color=colors[i%len(colors)], label="Spectre moyen "+str(i+1))
    
    if seuil is None: #Si la variable seuil n'a pas encore été initialisée, elle est initialisée ici.
        seuil = 20 * np.std(spectre_moyen) #Calcule le seuil en multipliant 20 par l'écart type du spectre moyen.
        ax.axhline(y=seuil, color='black', linestyle='--', label='Seuil') #Trace une ligne horizontale pour représenter la valeur seuil sur la figure.


    max_bruit= np.max(spectre_moyen) # Calcule la valeur maximale du spectre moyen.

    if max_bruit > seuil:
        
        print('Bruit détecté, fuyons!')
        if premiere_detection:  #Si c'est la première fois qu'un bruit est détecté, la variable
            premiere_detection = False
        else:
            nb_bruits_consecutifs += 1 #Sinon, on incrémente le nombre de bruits consécutifs.
        
        if nb_bruits_consecutifs == 2:  # Si deux bruits consécutifs ont été détectés, le programme s'arrête.
            print('Trop de bruits détectés, arrêt du programme.')
            break

        max_spectres_moyen.append(max_bruit)
        
        
    else:
        print('Aucun bruit bizarre, restons bien caché!')
        if not premiere_detection:
            bruit_detecte = False

    
    print("La valeur seuil est : ", seuil)
    print("La valeur maximale du bruit est : ", max_bruit)
    print("    ")

    i=i+1
    

print("Le valeur max des bruit sont : ", max_spectres_moyen)


if max_spectres_moyen[0] < max_spectres_moyen[1]:
    print("Le bruit augmente.")
elif max_spectres_moyen[0] > max_spectres_moyen[1]:
    print("Le bruit diminue.")
else:
    print("Le bruit est constant.")


ax.set_xlabel('Temps (s)')
ax.set_ylabel('Amplitude')
ax.set_title('Spectres moyens')
ax.legend()


plt.show()


#idee: detection temps reeel => affiche le son en temps reele et met des pt rouges sur les pics trop haut? 