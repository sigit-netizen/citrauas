import streamlit as st
import cv2
import numpy as np
import sys
import os

# Menambahkan parent directory ke sys.path agar folder pengolah_citra terbaca
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import modul pengolah citra
from pengolah_citra.langkah1_grayscale import proses_grayscale
from pengolah_citra.langkah2_geometri import proses_geometri
from pengolah_citra.langkah3_tepi import deteksi_sobel, deteksi_prewitt
from pengolah_citra.langkah4_segmentasi import proses_segmentasi

st.set_page_config(page_title="Pengolahan Citra Digital", layout="centered")

st.title("Implementasi Pengolahan Citra Digital untuk Segmentasi Remi dan Deteksi Tepi Menggunakan Metode Sobel dan Prewitt")
st.markdown("**Segmentasi Simbol Sekop, Hati, Wajik, dan Keriting pada Kartu Remi**")
st.markdown("---")

# -------------------------------------------------------
# Inisialisasi Session State
# -------------------------------------------------------
defaults = {
    "step": 0,
    "img_rgb": None,
    "img_gray": None,
    "img_gray_adjusted": None,   # Output Langkah 1
    "img_gray_geo": None,        # Output Langkah 2
    "img_rgb_geo": None,         # Output Langkah 2
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------------
# Utama: Upload Gambar
# -------------------------------------------------------
st.subheader("Upload Gambar")
uploaded_file = st.file_uploader("Pilih gambar kartu remi", type=["jpg", "jpeg", "png", "bmp"])

if uploaded_file is not None:
    image_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_bgr = cv2.imdecode(image_bytes, 1)
    st.session_state.img_rgb  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    st.session_state.img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

# -------------------------------------------------------
# Helper: Tombol Navigasi
# -------------------------------------------------------
def btn_lanjut(next_step):
    if st.button("Setuju & Lanjut ke Langkah Berikutnya", type="primary"):
        st.session_state.step = next_step
        st.rerun()

def btn_reset():
    st.markdown("---")
    if st.button("Reset Pipeline (Ulangi dari Langkah 1, gambar tetap)", type="secondary"):
        st.session_state.step = 1
        st.session_state.img_gray_adjusted = None
        st.session_state.img_gray_geo = None
        st.session_state.img_rgb_geo  = None
        st.rerun()

# -------------------------------------------------------
# Belum ada gambar
# -------------------------------------------------------
if st.session_state.img_rgb is None:
    st.info("Silakan **upload gambar** pada area di atas untuk memulai.")
    st.stop()

# -------------------------------------------------------
# STEP 0: Preview gambar, belum mulai
# -------------------------------------------------------
if st.session_state.step == 0:
    st.markdown("<h3 style='text-align: center;'>Gambar Berhasil Diupload!</h3>", unsafe_allow_html=True)
    
    # Gunakan kolom agar gambar berada di tengah dan lebih kecil (minimalis)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(st.session_state.img_rgb, use_container_width=True)
        st.markdown(f"<p style='text-align: center;'><b>Dimensi:</b> {st.session_state.img_rgb.shape[1]} × {st.session_state.img_rgb.shape[0]} px</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Mulai Pipeline — Jalankan Langkah 1", type="primary", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

# -------------------------------------------------------
# LANGKAH 1: Grayscale saja
# -------------------------------------------------------
if st.session_state.step >= 1:
    st.header("Langkah 1: Konversi Grayscale")
    st.write("Konversi gambar RGB ke Grayscale, lalu atur kecerahan dan kontras. Hasilnya akan diteruskan ke langkah berikutnya.")

    img_rgb  = st.session_state.img_rgb
    img_gray = st.session_state.img_gray

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Citra Asli (RGB)")
        st.image(img_rgb, use_container_width=True)
        st.caption(f"Dimensi: {img_rgb.shape[1]}×{img_rgb.shape[0]} px | Dtype: {img_rgb.dtype}")
        
    with col2:
        st.subheader("Hasil Grayscale & Pengaturan")
        brightness = st.slider("Kecerahan (Brightness)", -127, 127, 0)
        contrast = st.slider("Kontras (Contrast)", 0.1, 3.0, 1.0, step=0.1)

        # === PAKAI MODUL ===
        img_gray_adjusted = proses_grayscale(img_gray, brightness=brightness, contrast=contrast)
        st.session_state.img_gray_adjusted = img_gray_adjusted

        st.image(img_gray_adjusted,
                 caption=f"Grayscale Adjusted (B: {brightness:+d}, C: {contrast:.1f}x)",
                 use_container_width=True)

    if st.session_state.step == 1:
        st.markdown("---")
        btn_lanjut(2)

# -------------------------------------------------------
# LANGKAH 2: Operasi Geometri
# -------------------------------------------------------
if st.session_state.step >= 2:
    st.markdown("---")
    st.header("Langkah 2: Operasi Aritmatika & Geometri Citra")
    st.write("Input: **Grayscale Adjusted** dari Langkah 1. Output akan diteruskan ke Langkah 3 dan Langkah 4.")

    img_gray_input = st.session_state.img_gray_adjusted
    img_rgb_input  = st.session_state.img_rgb
    h, w = img_gray_input.shape[:2]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Flip Citra")
        flip_pilihan = st.radio("Arah Flip", ["Tidak", "Dibalik"], key="flip_radio")
        # Map pilihan ke parameter yang dikenali modul
        flip_mode = "Keduanya" if flip_pilihan == "Dibalik" else "Tidak Ada"
        
    with col2:
        st.subheader("Pengaturan Cropping")
        c1, c2 = st.columns(2)
        with c1:
            start_y = st.slider("Batas Atas (Y)",  0, h, 0,  key="sy")
            end_y   = st.slider("Batas Bawah (Y)", 0, h, h,  key="ey")
        with c2:
            start_x = st.slider("Batas Kiri (X)",  0, w, 0,  key="sx")
            end_x   = st.slider("Batas Kanan (X)", 0, w, w,  key="ex")

    # === PAKAI MODUL ===
    img_gray_res, img_rgb_res = proses_geometri(
        img_gray_input, img_rgb_input, 
        angle=0, flip_mode=flip_mode, negasi=False,
        start_y=start_y, end_y=end_y, start_x=start_x, end_x=end_x
    )

    # Simpan output ke session_state
    st.session_state.img_gray_geo = img_gray_res
    st.session_state.img_rgb_geo  = img_rgb_res

    st.markdown("#### Output Langkah 2 (diteruskan ke Langkah 3 & 4)")
    g1, g2 = st.columns(2)
    with g1:
        st.image(img_rgb_res,  caption="RGB setelah Geometri",       use_container_width=True)
    with g2:
        st.image(img_gray_res, caption="Grayscale setelah Geometri", use_container_width=True)

    if st.session_state.step == 2:
        st.markdown("---")
        btn_lanjut(3)

# -------------------------------------------------------
# LANGKAH 3: Deteksi Tepi
# -------------------------------------------------------
if st.session_state.step >= 3:
    st.markdown("---")
    st.header("Langkah 3: Deteksi Tepi (Edge Detection)")
    st.write("Input: **Grayscale Geometri** dari Langkah 2.")

    gray_edge_input = st.session_state.img_gray_geo

    # Parameter default
    ksize = 3
    edge_thresh = 0

    # === PAKAI MODUL ===
    sobel_combined = deteksi_sobel(gray_edge_input, ksize=ksize, edge_thresh=edge_thresh)
    prewitt_combined = deteksi_prewitt(gray_edge_input, edge_thresh=edge_thresh)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Metode Sobel")
        st.image(sobel_combined, caption=f"Sobel (kernel={ksize}, threshold={edge_thresh})", use_container_width=True, clamp=True)
    with col2:
        st.subheader("Metode Prewitt")
        st.image(prewitt_combined, caption=f"Prewitt (threshold={edge_thresh})", use_container_width=True, clamp=True)

    if st.session_state.step == 3:
        st.markdown("---")
        btn_lanjut(4)

# -------------------------------------------------------
# LANGKAH 4: Segmentasi
# -------------------------------------------------------
if st.session_state.step >= 4:
    st.markdown("---")
    st.header("Langkah 4: Segmentasi Region-Based (Ekstraksi Simbol)")
    st.write("Input: **Output Geometri** dari Langkah 2. Hasil pemisahan simbol dilakukan secara otomatis menggunakan Otsu Thresholding.")

    gray_seg_input = st.session_state.img_gray_geo
    rgb_seg_input  = st.session_state.img_rgb_geo

    # === Pengaturan Default (Tanpa UI) ===
    use_otsu = True
    manual_thresh = 127
    thresh_inv = False
    min_area = 50
    max_area = 15000

    # === PAKAI MODUL ===
    ret_val, thresh_img, symbol_count, img_segmented_symbols = proses_segmentasi(
        gray_seg_input, rgb_seg_input,
        use_otsu=use_otsu, manual_thresh=manual_thresh, use_inverse=thresh_inv,
        min_area=min_area, max_area=max_area
    )

    mode_label = "Otsu (Otomatis)" if use_otsu else "Manual"
    st.info(f"Mode: **{mode_label}** | Threshold: **{ret_val:.0f}** | Kontur simbol terdeteksi: **{symbol_count}**")

    seg1, seg2 = st.columns(2)
    with seg1:
        st.subheader("Hasil Threshold")
        st.image(thresh_img, caption=f"Threshold={ret_val:.0f} | {'Inverse' if thresh_inv else 'Normal'}", use_container_width=True)
    with seg2:
        st.subheader("Hasil Segmentasi Simbol")
        st.image(img_segmented_symbols, caption=f"Simbol Tersegmentasi ({symbol_count} kontur)", use_container_width=True)

    st.success("Pipeline selesai! Semua langkah telah berhasil dijalankan.")
    btn_reset()
