import streamlit as st
import cv2
import numpy as np

st.set_page_config(page_title="Pengolahan Citra Digital", layout="centered")

st.title("Rancang Bangun Aplikasi Pengolahan Citra Digital")
st.markdown("**Segmentasi Simbol Sekop ♠, Hati ♥, Wajik ♦, dan Keriting ♣ pada Kartu Remi**")
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
st.subheader("📁 Upload Gambar")
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
    if st.button("✅ Setuju & Lanjut ke Langkah Berikutnya", type="primary"):
        st.session_state.step = next_step
        st.rerun()

def btn_reset():
    st.markdown("---")
    if st.button("🔄 Reset Pipeline (Ulangi dari Langkah 1, gambar tetap)", type="secondary"):
        st.session_state.step = 1
        st.session_state.img_gray_adjusted = None
        st.session_state.img_gray_geo = None
        st.session_state.img_rgb_geo  = None
        st.rerun()

# -------------------------------------------------------
# Belum ada gambar
# -------------------------------------------------------
if st.session_state.img_rgb is None:
    st.info("👈 Silakan **upload gambar** pada area di atas untuk memulai.")
    st.stop()

# -------------------------------------------------------
# STEP 0: Preview gambar, belum mulai
# -------------------------------------------------------
if st.session_state.step == 0:
    st.header("📷 Gambar Berhasil Diupload!")
    st.image(st.session_state.img_rgb, use_container_width=True)
    st.markdown(f"**Dimensi:** {st.session_state.img_rgb.shape[1]} × {st.session_state.img_rgb.shape[0]} px")
    st.markdown("---")
    if st.button("▶️ Mulai Pipeline — Jalankan Langkah 1", type="primary"):
        st.session_state.step = 1
        st.rerun()

# -------------------------------------------------------
# LANGKAH 1: Grayscale saja
# Fungsi: cv2.cvtColor + cv2.convertScaleAbs
# Output: img_gray_adjusted → diteruskan ke Langkah 2
# -------------------------------------------------------
if st.session_state.step >= 1:
    st.header("🟢 Langkah 1: Konversi Grayscale")
    st.write("Konversi gambar RGB ke Grayscale, lalu atur kecerahan dan kontras. "
             "Hasilnya akan diteruskan ke langkah berikutnya.")

    img_rgb  = st.session_state.img_rgb
    img_gray = st.session_state.img_gray

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Citra Asli (RGB)")
        st.image(img_rgb, use_container_width=True)
        st.caption(f"Dimensi: {img_rgb.shape[1]}×{img_rgb.shape[0]} px | Dtype: {img_rgb.dtype}")
    with col2:
        st.subheader("Grayscale Default")
        st.image(img_gray, use_container_width=True)
        st.caption("Formula: Y = 0.299R + 0.587G + 0.114B")

    st.markdown("#### ⚙️ Pengaturan Grayscale")
    gs1, gs2 = st.columns(2)
    with gs1:
        brightness = st.slider("Kecerahan (Brightness)", -127, 127, 0,
                                help="Positif = lebih terang | Negatif = lebih gelap")
    with gs2:
        contrast = st.slider("Kontras (Contrast)", 0.1, 3.0, 1.0, step=0.1,
                              help="> 1.0 = kontras tinggi | < 1.0 = kontras rendah")

    # Fungsi dari ipynb: cv2.convertScaleAbs
    img_gray_adjusted = cv2.convertScaleAbs(img_gray, alpha=contrast, beta=brightness)
    st.session_state.img_gray_adjusted = img_gray_adjusted

    st.image(img_gray_adjusted,
             caption=f"Grayscale Adjusted (Brightness: {brightness:+d}, Kontras: {contrast:.1f}x)",
             use_container_width=True)

    if st.session_state.step == 1:
        st.markdown("---")
        btn_lanjut(2)

# -------------------------------------------------------
# LANGKAH 2: Operasi Geometri
# Input : img_gray_adjusted (dari Langkah 1)
# Fungsi: Negasi, Rotasi, Flipping, Cropping
# Output: img_gray_geo, img_rgb_geo → diteruskan ke Langkah 3 & 4
# -------------------------------------------------------
if st.session_state.step >= 2:
    st.markdown("---")
    st.header("🟡 Langkah 2: Operasi Aritmatika & Geometri Citra")
    st.write("Input: **Grayscale Adjusted** dari Langkah 1. "
             "Output akan diteruskan ke Langkah 3 dan Langkah 4.")

    img_gray_input = st.session_state.img_gray_adjusted.copy()
    img_rgb_input  = st.session_state.img_rgb.copy()
    h, w = img_gray_input.shape[:2]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pengaturan Rotasi & Flip")
        angle     = st.slider("Sudut Rotasi", -180, 180, 0, key="angle_slider")
        flip_mode = st.radio("Arah Flip", ["Tidak Ada", "Horizontal", "Vertikal", "Keduanya"],
                             key="flip_radio")
        apply_negasi = st.checkbox("Terapkan Negasi (Invers Warna Grayscale)", key="negasi_check")
    with col2:
        st.subheader("Pengaturan Cropping")
        start_y = st.slider("Batas Atas (Y)",  0, h, 0,  key="sy")
        end_y   = st.slider("Batas Bawah (Y)", 0, h, h,  key="ey")
        start_x = st.slider("Batas Kiri (X)",  0, w, 0,  key="sx")
        end_x   = st.slider("Batas Kanan (X)", 0, w, w,  key="ex")

    # Proses Geometri (sama persis dengan ipynb)
    if start_y < end_y and start_x < end_x:
        img_gray_input = img_gray_input[start_y:end_y, start_x:end_x]
        img_rgb_input  = img_rgb_input[start_y:end_y, start_x:end_x]

    if angle != 0:
        hc, wc = img_gray_input.shape[:2]
        M = cv2.getRotationMatrix2D((wc // 2, hc // 2), angle, 1.0)
        img_gray_input = cv2.warpAffine(img_gray_input, M, (wc, hc))
        img_rgb_input  = cv2.warpAffine(img_rgb_input,  M, (wc, hc))

    if flip_mode != "Tidak Ada":
        fc = 1 if flip_mode == "Horizontal" else (0 if flip_mode == "Vertikal" else -1)
        img_gray_input = cv2.flip(img_gray_input, fc)
        img_rgb_input  = cv2.flip(img_rgb_input,  fc)

    if apply_negasi:
        img_gray_input = 255 - img_gray_input

    # Simpan output ke session_state
    st.session_state.img_gray_geo = img_gray_input
    st.session_state.img_rgb_geo  = img_rgb_input

    st.markdown("#### Output Langkah 2 (diteruskan ke Langkah 3 & 4)")
    g1, g2 = st.columns(2)
    with g1:
        st.image(img_rgb_input,  caption="RGB setelah Geometri",       use_container_width=True)
    with g2:
        st.image(img_gray_input, caption="Grayscale setelah Geometri", use_container_width=True)

    if st.session_state.step == 2:
        st.markdown("---")
        btn_lanjut(3)

# -------------------------------------------------------
# LANGKAH 3: Deteksi Tepi
# Input : img_gray_geo (dari Langkah 2)
# Fungsi: Sobel, Prewitt
# -------------------------------------------------------
if st.session_state.step >= 3:
    st.markdown("---")
    st.header("🔵 Langkah 3: Deteksi Tepi (Edge Detection)")
    st.write("Input: **Grayscale Geometri** dari Langkah 2. Atur parameter deteksi tepi di bawah ini.")

    gray_edge_input = st.session_state.img_gray_geo

    # === Pengaturan Deteksi Tepi ===
    st.markdown("#### ⚙️ Pengaturan Deteksi Tepi")
    e1, e2 = st.columns(2)
    with e1:
        ksize = st.select_slider(
            "Ukuran Kernel Sobel",
            options=[3, 5, 7],
            value=3,
            key="ksize_slider",
            help="Kernel lebih besar = mendeteksi tepi yang lebih tebal/halus"
        )
    with e2:
        edge_thresh = st.slider(
            "Threshold Tepi (filter noise)",
            min_value=0, max_value=200, value=0,
            key="edge_thresh",
            help="Piksel di bawah nilai ini akan dihilangkan (0 = tampilkan semua)"
        )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Metode Sobel")
        sobel_x = cv2.Sobel(gray_edge_input, cv2.CV_64F, 1, 0, ksize=ksize)
        sobel_y = cv2.Sobel(gray_edge_input, cv2.CV_64F, 0, 1, ksize=ksize)
        sobel_combined = np.uint8(cv2.magnitude(sobel_x, sobel_y))
        if edge_thresh > 0:
            sobel_combined = np.where(sobel_combined >= edge_thresh, sobel_combined, 0).astype(np.uint8)
        st.image(sobel_combined, caption=f"Sobel (kernel={ksize}, threshold={edge_thresh})",
                 use_container_width=True, clamp=True)
    with col2:
        st.subheader("Metode Prewitt")
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        prewitt_x = cv2.filter2D(gray_edge_input, cv2.CV_64F, kernelx)
        prewitt_y = cv2.filter2D(gray_edge_input, cv2.CV_64F, kernely)
        prewitt_combined = np.uint8(cv2.magnitude(prewitt_x, prewitt_y))
        if edge_thresh > 0:
            prewitt_combined = np.where(prewitt_combined >= edge_thresh, prewitt_combined, 0).astype(np.uint8)
        st.image(prewitt_combined, caption=f"Prewitt (threshold={edge_thresh})",
                 use_container_width=True, clamp=True)

    if st.session_state.step == 3:
        st.markdown("---")
        btn_lanjut(4)

# -------------------------------------------------------
# LANGKAH 4: Segmentasi
# Input : img_gray_geo + img_rgb_geo (dari Langkah 2)
# Fungsi: Thresholding (Manual/Otsu) + Hierarchical Contour
# -------------------------------------------------------
if st.session_state.step >= 4:
    st.markdown("---")
    st.header("🔴 Langkah 4: Segmentasi Region-Based (Ekstraksi Simbol)")
    st.write("Input: **Output Geometri** dari Langkah 2. "
             "Atur **nilai threshold** untuk mendapatkan pemisahan simbol yang paling bersih.")

    gray_seg_input = st.session_state.img_gray_geo
    rgb_seg_input  = st.session_state.img_rgb_geo

    # === Pengaturan Threshold (UTAMA) ===
    st.markdown("#### ⚙️ Pengaturan Threshold")
    t1, t2 = st.columns([1, 2])
    with t1:
        thresh_mode = st.radio(
            "Mode Thresholding",
            ["Otsu (Otomatis)", "Manual"],
            key="thresh_mode",
            help="Otsu: threshold otomatis. Manual: Anda tentukan sendiri nilainya."
        )
        thresh_inv = st.checkbox(
            "Inverse (Balik warna threshold)",
            key="thresh_inv",
            help="Centang jika background gambar terang / simbol berwarna putih"
        )
    with t2:
        manual_thresh = st.slider(
            "Nilai Threshold Manual (0–255)",
            min_value=0, max_value=255, value=127,
            key="manual_thresh",
            disabled=(thresh_mode == "Otsu (Otomatis)"),
            help="Aktif hanya saat mode Manual. Geser untuk mendapatkan segmentasi terbaik."
        )
        st.caption("💡 **Tips:** Naikkan threshold jika terlalu banyak noise putih. "
                   "Turunkan jika simbol tidak muncul.")

    # === Pengaturan Filter Kontur (Sekunder) ===
    with st.expander("🔧 Pengaturan Lanjutan: Filter Area Kontur"):
        fa1, fa2 = st.columns(2)
        with fa1:
            min_area = st.slider("Area Minimum Simbol (px²)", 10, 500, 50, key="min_area",
                                 help="Abaikan kontur terlalu kecil (noise)")
        with fa2:
            max_area = st.slider("Area Maksimum Simbol (px²)", 1000, 50000, 15000, key="max_area",
                                 help="Abaikan kontur terlalu besar (bukan simbol)")

    # 1. Thresholding
    base_flag = cv2.THRESH_BINARY_INV if thresh_inv else cv2.THRESH_BINARY
    if thresh_mode == "Otsu (Otomatis)":
        ret, thresh_img = cv2.threshold(gray_seg_input, 0, 255, base_flag + cv2.THRESH_OTSU)
    else:
        ret, thresh_img = cv2.threshold(gray_seg_input, manual_thresh, 255, base_flag)
        ret = manual_thresh

    # 2. Cari kontur dengan hirarki
    contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 3. Filter simbol (berada di dalam kartu, ukuran sesuai parameter)
    img_symbols_mask = np.zeros_like(gray_seg_input)
    symbol_count = 0
    if hierarchy is not None:
        for i, contour in enumerate(contours):
            parent_idx = hierarchy[0][i][3]
            area = cv2.contourArea(contour)
            if parent_idx >= 0 and min_area < area < max_area:
                cv2.drawContours(img_symbols_mask, [contour], -1, 255, -1)
                symbol_count += 1

    # 4. Terapkan mask ke citra RGB
    img_segmented_symbols = cv2.bitwise_and(rgb_seg_input, rgb_seg_input, mask=img_symbols_mask)

    mode_label = "Otsu (Otomatis)" if thresh_mode == "Otsu (Otomatis)" else "Manual"
    st.info(f"🔍 Mode: **{mode_label}** | Threshold: **{ret:.0f}** | Kontur simbol terdeteksi: **{symbol_count}**")

    seg1, seg2 = st.columns(2)
    with seg1:
        st.subheader("Hasil Threshold")
        st.image(thresh_img,
                 caption=f"Threshold={ret:.0f} | {'Inverse' if thresh_inv else 'Normal'}",
                 use_container_width=True)
    with seg2:
        st.subheader("Hasil Segmentasi Simbol ♠♥♦♣")
        st.image(img_segmented_symbols,
                 caption=f"Simbol Tersegmentasi ({symbol_count} kontur)",
                 use_container_width=True)

    st.success("🎉 Pipeline selesai! Semua langkah telah berhasil dijalankan.")
    btn_reset()

