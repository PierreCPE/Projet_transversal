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
nb_bruits_consecutifs = 0
bruit_detecte = False
premiere_detection = True
seuil = None
# max_bruit = None
#ENREGISTREMENT

while nb_bruits_consecutifs < 2 and  not bruit_detecte:
    print("Enregistrement en cours")
    signal = sd.rec(int(duree * Fs), samplerate=Fs, channels=1)
    sd.wait()

    f, t, S = sig.spectrogram(signal[:,0], fs=Fs, window='hann', nperseg=taille_fenetre, noverlap=taille_fenetre-pas, nfft=taille_fft, detrend=False)

    freq_bin = np.logical_and(f > freq_min, f <= freq_max)

    spectre_moyen = np.mean(np.abs(S[freq_bin, :]), axis=0)

    if seuil is None:
        seuil = 10 * np.std(spectre_moyen)

    max_bruit= np.max(spectre_moyen)

    if max_bruit > seuil:
        
        print('Bruit détecté, fuyons!')
        if premiere_detection:
            premiere_detection = False
        else:
            nb_bruits_consecutifs += 1
        if nb_bruits_consecutifs == 2:
            print('Trop de bruits détectés, arrêt du programme.')

        max_spectres_moyen.append(max_bruit)
       
    else:
        print('Aucun bruit bizarre, restons bien caché!')
        if not premiere_detection:
            bruit_detecte = True


    print("La valeur seuil est : ", seuil)
    print("La valeur maximale du bruit est : ", max_bruit)
    print("    ")

print("Le valeur max des 5 bruit sont : ", max_spectres_moyen)

if max_spectres_moyen[0] < max_spectres_moyen[1]:
    print("Le bruit augmente.")
elif max_spectres_moyen[0] > max_spectres_moyen[1]:
    print("Le bruit diminue.")
else:
    print("Le bruit est constant.")