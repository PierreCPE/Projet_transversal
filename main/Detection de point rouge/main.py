import test
import detection_pt_rouge_video_continue_gomete
import time

test.capture_image()
time.sleep(2) # Sleep for 3 seconds
detection_pt_rouge_video_continue_gomete.detect_pt()

# erease img2
# pour laisser le choix de si on prend une nouvelle photo ou couleur de base