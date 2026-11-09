---
trigger: model_decision
description: "Terapkan saat mengubah cara memilih target interaksi (tombol E / klik): penentuan NPC vs objek terdekat, prioritas, petunjuk tombol di atas target, bentrok jarak NPC dengan furnitur (mis. Ibu di dapur), atau penempatan NPC terhadap interactable."
---

# 84 · Penargetan Interaksi

## 1. Masalah
Di dapur, menekan E dekat Ibu malah memicu furnitur lain, karena furnitur terlalu dekat dengan Ibu dan pemilihan target hanya berdasarkan jarak terdekat.

## 2. Algoritma pemilihan (deterministik, `src/game/interactionTarget.js`)
- Kandidat: NPC dan interactable dalam `interactRange` (default 44 px dari titik interaksi di depan pemain) dan berada di setengah bidang arah hadap.
- Skor (kecil = menang): `jarak − bobot`, bobot: **NPC 20 px**, **target objektif tutorial 40 px** (rule 82), objek biasa 0; penalti sudut menjauhi arah hadap (≤ 12 px). Seri → urutan id.
- Hanya **satu** target terpilih; **petunjuk tombol** (ikon E/Klik + kata kerja, mis. "E · Bicara dengan Ibu") dan kontur sorotan tampil di atasnya. **Tab** (atau Q) berpindah antar-kandidat bila lebih dari satu.
- Klik langsung pada NPC/objek (rule 81) menetapkan target secara eksplisit dan mengabaikan skor.

## 3. Aturan tata letak
- Tidak boleh ada interactable lain dalam radius **1,5 tile** dari titik berdiri NPC; objek dekoratif di dekat NPC tidak diberi interaksi. Contoh dapur: counter kompor **bukan** interactable; Ibu berdiri di area bebas dekat meja makan/ujung deretan counter, dengan zona pendekatan ≥ 2×1 tile (rule 73 §8).
- **Validator `interactionOverlapCheck`:** untuk tiap NPC, ambil sampel titik berdiri yang sah dalam jangkauan; NPC harus menjadi target terpilih pada **≥ 90%** sampel; selain itu gagal dan layout diperbaiki (pindah NPC atau hilangkan/geser interaktif). Hasil ke `docs/layouts/VALIDATION-<mapId>.md`.

## 4. Uji wajib (tombol E nyata)
Dari 3 titik berdiri berbeda di dekat Ibu (kiri, depan, kanan): tekan E → dialog Ibu terbuka (bukan interaksi furnitur); dekat meja makan tanpa Ibu → "Makan"; Tab berpindah target; objektif tutorial memenangkan seri; `interactionOverlapCheck` hijau untuk semua NPC di 7 peta; tangkapan layar petunjuk tombol di atas target.
