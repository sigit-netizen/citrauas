import cv2
import numpy as np

def proses_geometri(img_gray, img_rgb, angle=0, flip_mode="Tidak Ada", negasi=False, 
                    start_y=None, end_y=None, start_x=None, end_x=None):
    """
    Melakukan operasi geometri dan aritmatika (cropping, rotasi, flip, negasi).
    
    Returns:
    - (img_gray_hasil, img_rgb_hasil)
    """
    img_gray_res = img_gray.copy()
    img_rgb_res = img_rgb.copy()
    h, w = img_gray_res.shape[:2]
    
    # 1. Cropping
    sy = start_y if start_y is not None else 0
    ey = end_y if end_y is not None else h
    sx = start_x if start_x is not None else 0
    ex = end_x if end_x is not None else w
    
    if sy < ey and sx < ex:
        img_gray_res = img_gray_res[sy:ey, sx:ex]
        img_rgb_res = img_rgb_res[sy:ey, sx:ex]
        
    # 2. Rotasi
    if angle != 0:
        hc, wc = img_gray_res.shape[:2]
        M = cv2.getRotationMatrix2D((wc // 2, hc // 2), angle, 1.0)
        img_gray_res = cv2.warpAffine(img_gray_res, M, (wc, hc))
        img_rgb_res  = cv2.warpAffine(img_rgb_res,  M, (wc, hc))
        
    # 3. Flip
    if flip_mode != "Tidak Ada":
        fc = 1 if flip_mode == "Horizontal" else (0 if flip_mode == "Vertikal" else -1)
        img_gray_res = cv2.flip(img_gray_res, fc)
        img_rgb_res  = cv2.flip(img_rgb_res,  fc)
        
    # 4. Negasi
    if negasi:
        img_gray_res = 255 - img_gray_res
        
    return img_gray_res, img_rgb_res
