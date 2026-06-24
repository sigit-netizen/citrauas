import cv2
import numpy as np

def deteksi_sobel(img_gray, ksize=3, edge_thresh=0):
    """
    Melakukan deteksi tepi menggunakan operator Sobel.
    """
    sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=ksize)
    sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=ksize)
    sobel_combined = np.uint8(cv2.magnitude(sobel_x, sobel_y))
    
    if edge_thresh > 0:
        sobel_combined = np.where(sobel_combined >= edge_thresh, sobel_combined, 0).astype(np.uint8)
        
    return sobel_combined

def deteksi_prewitt(img_gray, edge_thresh=0):
    """
    Melakukan deteksi tepi menggunakan operator Prewitt.
    """
    kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
    kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
    
    prewitt_x = cv2.filter2D(img_gray, cv2.CV_64F, kernelx)
    prewitt_y = cv2.filter2D(img_gray, cv2.CV_64F, kernely)
    prewitt_combined = np.uint8(cv2.magnitude(prewitt_x, prewitt_y))
    
    if edge_thresh > 0:
        prewitt_combined = np.where(prewitt_combined >= edge_thresh, prewitt_combined, 0).astype(np.uint8)
        
    return prewitt_combined
