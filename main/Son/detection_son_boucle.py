import numpy as np
import sounddevice as sd
import scipy.signal as sig

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

#ENREGISTREMENT

for i in range(5):
    print("Enregistrement en cours")
    signal = sd.rec(int(duree * Fs), samplerate=Fs, channels=1)
    sd.wait()

    f, t, S = sig.spectrogram(signal[:,0], fs=Fs, window='hann', nperseg=taille_fenetre, noverlap=taille_fenetre-pas, nfft=taille_fft, detrend=False)

    freq_bin = np.logical_and(f > freq_min, f <= freq_max)

    spectre_moyen = np.mean(np.abs(S[freq_bin, :]), axis=0)

    seuil = 10 * np.std(spectre_moyen)
    max_bruit= np.max(spectre_moyen)
    if max_bruit > seuil:
        print('Bruit détecté, fuyons!')
    else:
        print('Aucun bruit bizarre, restons bien caché!')

    max_spectres_moyen.append(max_bruit)
    print("La valeur seuil est : ", seuil)
    print("La valeur maximale du bruit est : ", max_bruit)

print("Le valeur max des 5 bruit sont : ", max_spectres_moyen)

if max_spectres_moyen[0] >max_spectres_moyen[1] and max_bruit > seuil:
    print("Le bruit augmente")

#Je veux que mon code garde le meme seuil a chaque eregistrement et que ma boucle me permette de voir si le bruit detecte est de plus en plus fort ou pas 