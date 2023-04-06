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
duree = 3


#ENREGISTREMENT
spectres_moyen = []
for i in range(5):
    print("Enregistrement en cours")
    signal = sd.rec(int(duree * Fs), samplerate=Fs, channels=1)
    sd.wait()
    print("Enregistrement terminé")


    f, t, S = sig.spectrogram(signal[:,0], fs=Fs, window='hann', nperseg=taille_fenetre, noverlap=taille_fenetre-pas, nfft=taille_fft, detrend=False)


    freq_bin = np.logical_and(f > freq_min, f <= freq_max)



    spectre_moyen = np.mean(np.abs(S[freq_bin, :]), axis=0)
    spectres_moyen.append(spectre_moyen)

    seuil = 10 * np.std(spectre_moyen)
    if np.max(spectre_moyen) > seuil:
        print('Bruit détecté, fuyons!')

        if i>0:

            seuil = 10 * np.std(spectre_moyen)
            if np.max(spectre_moyen) > seuil:
                print('Bruit de plus en plus fort!')
                
        else:
            print('Le bruit se calme!')
    
    else:
        print('Aucun bruit bizarre, restons bien caché!')