# Aturan Pengembangan Aplikasi Pengolahan Citra Digital

## 1. Prinsip Utama: Notebook adalah Sumber Kebenaran

`praktik.ipynb` adalah **sumber kode utama (source of truth)**.  
`app.py` hanya mengambil dan menampilkan fungsi yang **sudah ada** di `praktik.ipynb`.

> **Aturan:** Jika sebuah fitur/fungsi tidak ada di `praktik.ipynb`, maka fitur tersebut **tidak boleh** ada di `app.py`.

---

## 2. Alur Pipeline (Sequential)

Output dari setiap langkah **wajib diteruskan** sebagai input ke langkah berikutnya.

```
Upload Gambar
     │
     ▼
Langkah 1: Grayscale
  - Input  : Gambar asli (RGB)
  - Proses : Konversi ke Grayscale + Pengaturan Brightness & Contrast
  - Output : img_gray_adjusted  ──────────────────────────────────┐
                                                                   │
     ▼                                                             │
Langkah 2: Operasi Geometri                                        │
  - Input  : img_gray_adjusted (dari Langkah 1) ◄──────────────────┘
  - Proses : Negasi, Rotasi, Flipping, Cropping
  - Output : img_gray_geo, img_rgb_geo ────────────────────────────┐
                                                                    │
     ▼                                                              │
Langkah 3: Deteksi Tepi                                             │
  - Input  : img_gray_geo (dari Langkah 2) ◄────────────────────────┤
  - Proses : Sobel, Prewitt                                         │
  - Output : Citra tepi (ditampilkan, tidak diteruskan)             │
                                                                    │
     ▼                                                              │
Langkah 4: Segmentasi                                               │
  - Input  : img_gray_geo + img_rgb_geo (dari Langkah 2) ◄──────────┘
  - Proses : Otsu Thresholding + Hierarchical Contour Filtering
  - Output : Simbol kartu tersegmentasi
```

---

## 3. Aturan Per Langkah

### Langkah 1 — Grayscale SAJA
- Hanya berisi: konversi RGB → Grayscale dan pengaturan brightness/contrast.
- **Tidak boleh** mengandung: kuantisasi, sampling, resize, atau operasi lainnya.
- Output wajib: `img_gray_adjusted`

### Langkah 2 — Operasi Geometri
- Menggunakan `img_gray_adjusted` dari Langkah 1 sebagai input grayscale.
- Menggunakan `img_rgb` (gambar asli) sebagai input warna.
- Output wajib: `img_gray_geo` dan `img_rgb_geo`

### Langkah 3 — Deteksi Tepi
- Menggunakan `img_gray_geo` dari Langkah 2.
- Metode yang wajib ada: **Sobel** dan **Prewitt**.
- Output hanya untuk ditampilkan.

### Langkah 4 — Segmentasi
- Menggunakan `img_gray_geo` dan `img_rgb_geo` dari Langkah 2.
- Metode: Otsu Thresholding + Hierarchical Contour (Region-Based).

---

## 4. Ketentuan Reset
- Tombol Reset di akhir Langkah 4 hanya mereset **langkah pipeline** ke Langkah 1.
- Gambar yang sudah di-upload **tidak ikut direset**.
