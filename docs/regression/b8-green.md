# Laporan Pengujian Hijau: B8 (Penataan Rak Buku Kelas)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/school.layout.json`, `tools/test_j1_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b8_rak_buku_kelas_red.png`
  - SESUDAH (GREEN): `docs/regression/b8_rak_buku_kelas_green.png`
- **Akar Masalah:**
  Slot rak buku kelas `slot_sch_rak_buku_kelas` sebelumnya diletakkan pada koordinat $(x=2, y=4)$ yang menempel pada dinding samping bukan sudut kiri atas dinding belakang.
- **Perbaikan yang Diterapkan:**
  Memindahkan slot rak buku ke sudut kiri atas dinding belakang kelas pada koordinat $(x=2, y=2)$.
- **Hasil Verifikasi:**
  Pengujian UI nyata memeriksa slot rak buku berada tepat di $(x=2, y=2, w=2, h=3)$ menempel dinding belakang sudut kiri.
