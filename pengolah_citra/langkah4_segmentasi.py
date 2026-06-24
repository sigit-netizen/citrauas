import cv2
import numpy as np

def proses_segmentasi(img_gray, img_rgb, use_otsu=True, manual_thresh=127, 
                      use_inverse=False, min_area=50, max_area=15000):
    """
    Melakukan segmentasi citra menggunakan thresholding dan pencarian kontur hirarkis.
    """
    # 1. Thresholding
    base_flag = cv2.THRESH_BINARY_INV if use_inverse else cv2.THRESH_BINARY
    
    if use_otsu:
        ret, thresh_img = cv2.threshold(img_gray, 0, 255, base_flag + cv2.THRESH_OTSU)
    else:
        ret, thresh_img = cv2.threshold(img_gray, manual_thresh, 255, base_flag)
        ret = manual_thresh
        
    # 2. Cari kontur dengan hirarki
    contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # 3. Filter simbol
    img_symbols_mask = np.zeros_like(img_gray)
    symbol_count = 0
    if hierarchy is not None:
        for i, contour in enumerate(contours):
            parent_idx = hierarchy[0][i][3]
            area = cv2.contourArea(contour)
            if parent_idx >= 0 and min_area < area < max_area:
                cv2.drawContours(img_symbols_mask, [contour], -1, 255, -1)
                symbol_count += 1
                
    # 4. Terapkan mask ke citra RGB
    img_segmented_symbols = cv2.bitwise_and(img_rgb, img_rgb, mask=img_symbols_mask)
    
    return ret, thresh_img, symbol_count, img_segmented_symbols
