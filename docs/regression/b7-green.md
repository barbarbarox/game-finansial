# Laporan Pengujian Hijau: B7 (Konflik Interaksi Dapur Ibu)

- **Status:** PASS (HIJAU)
- **Komponen:** `src/game/interactionTarget.js`, `src/game/scenes/World.js`, `data/maps/home.layout.json`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b7_interaksi_ibu_dapur_red.png`
  - SESUDAH (GREEN): `docs/regression/b7_interaksi_dapur_ibu_green.png`
- **Akar Masalah:**
  Area interactable kompor (`int_dapur`, `masak_ibu`) memiliki bounding box $(x=18.5..21.5, y=12..13)$ yang tumpang-tindih dengan posisi Ibu $(x=20, y=13.5)$. Pemilihan interaksi lama hanya mengambil elemen pertama dalam radius tanpa bobot prioritas NPC.
- **Perbaikan yang Diterapkan:**
  1. Menghapus interactable aktivitas `int_dapur` yang bertumpuk.
  2. Mengimplementasikan `findBestInteractionTarget()` di `src/game/interactionTarget.js` dengan bobot prioritas NPC (+20px bonus) dan penalti arah hadap sudut (Rule 84).
  3. Memperbarui `_checkInteractables()` di `World.js` untuk memicu dialog NPC (`startDialogue`) saat target terbaik adalah NPC.
- **Hasil Verifikasi:**
  Pemain mendekati Ibu di dapur dan menekan `E` langsung membuka dialog resmi Ibu (`dia_ibu_home`, speaker `Ibu`) tanpa konflik kompor.
