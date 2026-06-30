# Aturan Pengembangan Aplikasi Pengolahan Citra Digital

## 1. Prinsip Utama: Modular — Modul Python adalah Sumber Kebenaran

Seluruh logika pemrosesan citra disimpan di folder **`pengolah_citra/`** sebagai modul Python terpisah.  
`app.py` dan `praktik.ipynb` **tidak boleh** menulis ulang logika OpenCV — cukup memanggil fungsi dari modul.

> **Aturan:** Jika sebuah fungsi tidak ada di dalam modul `pengolah_citra/`, maka fungsi tersebut **tidak boleh** ditulis ulang di `app.py` maupun `praktik.ipynb`. Tambahkan ke modul yang sesuai terlebih dahulu.

### Struktur Modul

```
pengolah_citra/
├── __init__.py
├── langkah1_grayscale.py   → proses_grayscale()
├── langkah2_geometri.py    → proses_geometri()
├── langkah3_tepi.py        → deteksi_sobel(), deteksi_prewitt()
└── langkah4_segmentasi.py  → proses_segmentasi()
```

---

## 2. Alur Pipeline (Sequential)

Output dari setiap langkah **wajib diteruskan** sebagai input ke langkah berikutnya.

```
Load Gambar (cv2.imread / Upload)
     │
     ▼
Langkah 1: Grayscale
  - Input  : Gambar asli (RGB) → img_rgb, img_gray
  - Proses : proses_grayscale(img_gray, brightness, contrast)
  - Output : img_gray_adjusted
     │
     ▼
Langkah 2: Operasi Geometri (Cropping + Flip)
  - Input  : img_gray_adjusted (dari Langkah 1), img_rgb
  - Proses : proses_geometri(... flip_mode, start_y, end_y, start_x, end_x)
  - Output : img_gray_geo, img_rgb_geo
     │
     ├──────────────────────────┐
     ▼                          ▼
Langkah 3: Deteksi Tepi     Langkah 4: Segmentasi
  - Input  : img_gray_geo     - Input  : img_gray_geo + img_rgb_geo
  - Proses : deteksi_sobel()  - Proses : proses_segmentasi() → Otsu + Contour
             deteksi_prewitt()- Output : thresh_img, img_segmented_symbols
  - Output : ditampilkan saja
```

---

## 3. Aturan Per Langkah

### Langkah 1 — Grayscale SAJA
- Hanya berisi: konversi RGB → Grayscale + pengaturan **Brightness** dan **Contrast**.
- **Tidak boleh** mengandung: rotasi, flip, crop, resize, atau operasi lainnya.
- UI Streamlit: 2 kolom — kiri (citra asli RGB), kanan (slider + hasil grayscale).
- Output wajib: `img_gray_adjusted`

### Langkah 2 — Operasi Geometri
- Menggunakan `img_gray_adjusted` dari Langkah 1 dan `img_rgb` asli.
- Operasi yang tersedia: **Cropping** (Atas/Bawah/Kiri/Kanan) dan **Flip** (Tidak / Dibalik).
- Operasi yang **dihapus/tidak dipakai**: Rotasi, Negasi.
- Flip "Dibalik" = `flip_mode="Keduanya"` (horizontal + vertikal sekaligus).
- Output wajib: `img_gray_geo` dan `img_rgb_geo`

### Langkah 3 — Deteksi Tepi
- Menggunakan `img_gray_geo` dari Langkah 2.
- Menjalankan dua metode sekaligus: **Sobel** (kernel=3) dan **Prewitt**.
- Parameter dijalankan dengan nilai **default** (tanpa UI slider di app).
- Output hanya untuk ditampilkan, tidak diteruskan ke langkah berikutnya.

### Langkah 4 — Segmentasi
- Menggunakan `img_gray_geo` dan `img_rgb_geo` dari Langkah 2.
- Metode: **Otsu Thresholding** (otomatis) + **Hierarchical Contour** (Region-Based).
- Parameter dijalankan dengan nilai **default** (tanpa UI slider di app):
  - `use_otsu = True`, `use_inverse = False`
  - `min_area = 50`, `max_area = 15000`
- Output: `thresh_img` (hasil threshold) dan `img_segmented_symbols` (simbol tersegmentasi).

---

## 4. Ketentuan Reset

- Tombol Reset di akhir Langkah 4 hanya mereset **langkah pipeline** ke Langkah 1.
- Gambar yang sudah di-upload **tidak ikut direset**.
- Variabel yang direset: `img_gray_adjusted`, `img_gray_geo`, `img_rgb_geo`.

---

## 5. Sinkronisasi `app.py` ↔ `praktik.ipynb`

- Perubahan pada **modul** (`pengolah_citra/*.py`) otomatis berlaku di keduanya.
- Jika menambah parameter baru ke fungsi modul, update default-value di `app.py` **dan** di sel notebook yang memanggil fungsi tersebut.
- Setelah mengubah file modul, **Restart Kernel** di Jupyter Notebook agar perubahan terbaca.
