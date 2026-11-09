# Reproduksi Masalah B8: Rak Buku Kelas Tidak di Sudut Kiri Ruangan
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Periksa posisi `slot_sch_rak_buku_kelas` di `school.layout.json`.
- **Hasil Aktual:** Rak buku berada di koordinat x=2, y=4 (di tengah dinding samping kiri), bukan di pojok kiri belakang menempel dinding atas.
- **Tangkapan Layar:** `docs/regression/b8_rak_buku_kelas_red.png`
- **Akar Masalah:** Tata letak kelas menaruh rak buku di lorong samping meja siswa alih-alih di sudut kiri atas ruangan.
