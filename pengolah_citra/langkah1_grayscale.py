import cv2
import numpy as np

def proses_grayscale(img_gray, brightness=0, contrast=1.0):
    """
    Mengatur kecerahan dan kontras pada citra grayscale.
    
    Parameters:
    - img_gray: Citra grayscale (numpy array)
    - brightness: Nilai kecerahan (-127 s/d 127)
    - contrast: Nilai kontras (0.1 s/d 3.0)
    
    Returns:
    - Citra grayscale yang telah diatur brightness & contrast-nya
    """
    # Gunakan convertScaleAbs untuk mengatur contrast (alpha) dan brightness (beta)
    img_gray_adjusted = cv2.convertScaleAbs(img_gray, alpha=contrast, beta=brightness)
    return img_gray_adjusted
