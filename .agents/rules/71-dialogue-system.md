---
trigger: model_decision
description: "Terapkan saat membuat atau mengubah dialog NPC, tampilan potret karakter kiri-kanan, menu pilihan interaksi, efek ajakan ke aktivitas/peta, data dialog, atau aset potret."
---

# 71 · Sistem Dialog dengan Potret

## 1. Tata letak (DOM overlay di atas canvas)
- Latar dunia diredupkan (overlay `--navy-950`, opasitas ±0.5). **Potret pemain di kiri, potret NPC di kanan**, berdiri di atas kotak dialog; NPC dicerminkan agar saling berhadapan.
- Kotak dialog di bawah, selebar layar dikurangi margin: plakat nama pembicara (di sisi pembicara), teks dengan efek ketik (cepat; E/Spasi menyelesaikan baris, lalu lanjut).
- **Menu pilihan** (2–4 opsi) tampil di atas kotak dialog sebagai daftar vertikal; navigasi panah/W-S, Enter/E memilih, tombol 1–4 pintasan; mouse/sentuh didukung. Opsi tidak tersedia (mis. uang kurang, tutup) tampil nonaktif dengan alasan singkat.

## 2. Sorotan pembicara
- Pembicara: kecerahan penuh, naik 6 px. Bukan pembicara: kecerahan ±55%, saturasi ±70%, turun ke posisi dasar. Transisi 150 ms; `prefers-reduced-motion` → tanpa animasi.
- Saat pilihan ditampilkan, potret **pemain** aktif. Jika dialog melibatkan narator (tanpa pembicara), kedua potret diredupkan.
- Skala potret hanya bilangan bulat (1×/2×/3×) sesuai tinggi viewport; `image-rendering: pixelated`; potret tidak boleh menutupi kotak dialog.

## 3. Data dialog
`data/dialogues/<npcId>.json`: simpul `{id, speaker (player|npcId), text, expression?, choices[{text, next, requires?, effects[]}], next?}`. Teks Indonesia, ≤ 140 karakter per simpul. Nama pemain/orang tua/teman disisipkan lewat token (`{player}`, `{ibu}`) dan dirender dengan `textContent`.
**Efek yang diizinkan (whitelist):** transaksi ledger via domain; `startActivity(id)` (lihat 72); `transition(mapId, spawnId)`; `setFlag`; `grantAllowance`; `openPlanner`. Efek dijalankan lewat domain/MapManager biasa (validasi tetap berlaku).
**Contoh alur wajib:** teman mengajak → pilihan [Ikut ke game center / Usul nongkrong gratis / Tolak] → efek aktivitas + perpindahan peta + biaya + waktu, dengan umpan balik edukatif singkat setelahnya. Ibu pada hari 1 → uang saku → arahan anggaran. Kejadian ekonomi (`events.phase1.json`) memakai UI yang sama.

## 4. Aset potret
- Potret pemain (L dan P, kasual), ibu, ayah, teman L, teman P, penjual kantin, kasir minimarket, penjaga kosmetik, petugas SPBU, penjaga game center. Final **192×256 px**, setengah badan, tampak 3/4 **menghadap kanan** (NPC dicerminkan saat runtime), ekspresi netral ramah (variasi ekspresi opsional, belum wajib).
- Kanon pakaian/warna harus sama dengan sprite (STYLE-BIBLE). Generate dengan sprite sheet sebagai referensi; QA identitas sama seperti karakter.
- Fallback bila potret belum ada: siluet placeholder berlabel nama NPC (mode debug), dialog tetap berfungsi.

## 5. Aksesibilitas dan keamanan
Fokus terkunci di dialog; Esc tidak melewati pilihan wajib; teks terbaca (kontras ≥ 4.5:1); semua teks dinamis lewat `textContent`; data dialog divalidasi skema saat dimuat (tolak efek di luar whitelist).

## 6. Pengujian
Hook `window.__LJ__`: `startDialogue(id)`, `choose(i)`, `getDialogueState()` (speaker aktif, pilihan tersedia). Uji: sorotan berpindah saat giliran berganti, pilihan nonaktif tidak dapat dipilih, efek ledger/waktu/peta tereksekusi, tangkapan layar tiap tipe dialog pada desktop dan tablet.
