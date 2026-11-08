---
trigger: model_decision
description: "Terapkan saat menulis atau mengubah JavaScript, HTML, CSS, scene Phaser, store, ledger, mesin kejadian, penyimpanan LocalStorage, atau struktur folder src/."
---

# 30 · Arsitektur & Kode

## 1. Struktur
`index.html` · `src/domain/` (ledger, accounts, budget, clock, eventEngine, missions, evaluation) · `src/state/` (store pub-sub, persistence, schema, migrate) · `src/game/` (scenes: Boot, Preload, MainMenu, World; player, npc, interactables, assetLoader) · `src/ui/` (tokens.css, hud, cashbook, shopPanel, budgetPanel, decisionDialog, characterCreate, settings, credits) · `data/` (config & konten JSON) · `vendor/` · `assets/` · `tests/` · `docs/`.

## 2. Aturan kode
- ES Modules; tanpa variabel global; fungsi kecil; JSDoc untuk API publik domain; komentar hanya untuk logika non-trivial.
- Domain = fungsi murni + state eksplisit; tidak mengimpor Phaser/DOM. Seed RNG tersimpan di save agar perilaku dapat direproduksi.
- UI tidak menghitung uang; UI memanggil fungsi domain lalu merender hasil store.
- Phaser ↔ DOM hanya lewat store/event bus. Menutup panel melanjutkan jam permainan.

## 3. Ledger (double-entry di balik layar, tampilan sederhana di Fase 1)
- Entri: `id`, `day`, `month`, `categoryId`, `kind`, `description` (dari data, bukan input bebas), `lines[]` (akun, sisi D/K, jumlah integer). Domain menolak entri tidak seimbang atau yang membuat Kas negatif.
- Akun pribadi: Kas Pribadi, Tabungan (aset); Kekayaan Bersih (ekuitas); Uang Saku, Bonus (pendapatan); Beban Jajan, Beban Transportasi, Beban Sekolah, Beban Perawatan Diri, Beban Hiburan, Beban Komunikasi, Beban Lain-lain (beban).
- Menabung = pindah Kas → Tabungan (bukan beban). Tarik tabungan = sebaliknya.
- Fase 1 menampilkan **buku kas** (pemasukan/pengeluaran/saldo), bukan istilah debit-kredit. Struktur double-entry disiapkan agar Fase 2 dapat membuka jurnal tanpa migrasi besar.
- Kategori kebutuhan vs keinginan ditentukan di `phase1.config.json`, bukan di akun.

## 4. Invarian (tests/self-test.html, jalan di browser)
1. Σ debit = Σ kredit (tiap entri dan total buku).
2. Kas HUD = saldo akun Kas dari ledger.
3. Total pemasukan − total pengeluaran − setoran tabungan neto = perubahan Kas.
4. Tidak ada Kas/Tabungan negatif; pembelian melebihi saldo ditolak domain.
5. Muat-ulang dari LocalStorage menghasilkan state identik (round-trip).
6. Skenario acak ±30 transaksi lalu seluruh invarian dicek.

## 5. Jam permainan (DIGANTI oleh `72-time-system.md`; paragraf di bawah hanya ringkasan lama) (DIGANTI oleh ; paragraf di bawah hanya ringkasan lama)
Jam berjalan hanya saat bermain bebas; berhenti pada panel/dialog/menu. Parameter (`dayDurationSeconds`, `monthDays`, `months`) dari config. Pergantian hari: otomatis pukul 22:00, atau pemain tidur di rumah. Uang saku masuk otomatis pada hari ke-1 tiap bulan dan muncul di riwayat.

## 6. Mesin kejadian
Data-driven (`data/events.phase1.json`): `id`, jendela pemicu, syarat, bobot, teks, 2–3 pilihan, efek, `learningTag`, `feedback`. Efek hanya boleh berupa transaksi ledger dan perubahan flag/metrik yang di-whitelist. Pemilihan memakai RNG ber-seed; kejadian non-repeatable tidak muncul dua kali. Setiap pilihan menghasilkan umpan balik langsung + (bila relevan) dampak jangka panjang.

## 7. Penyimpanan
Key `lj_save_v2` (satu objek; migrasi dari `lj_save_v1` wajib, lihat 70 dan 72). Autosave setelah transaksi, pergantian hari, dan keputusan. Satu slot untuk prototype. Tombol Continue aktif hanya bila save valid. Reset dengan konfirmasi.

## 8. Hook uji untuk otomasi (hanya mode debug)
- Aktif hanya bila URL memuat `?debug=1` **dan** `debugEnabled: true` di config (default `false` untuk rilis). Mengekspos objek `window.__LJ__` dengan: `getState()`, `getLedger()`, `runInvariants()`, `teleportTo(locationId)`, `interact(id)`, `advanceDays(n)`, `triggerEvent(id)`, `choose(optionIndex)`, `buy(itemId)`, `setSeed(n)`, `toggleCollisionOverlay()`.
- Hook TIDAK boleh melewati validasi domain (tetap memanggil fungsi domain biasa), dan tidak boleh ada kode hook yang tersisa aktif saat `debugEnabled: false`.
- Tujuan: agen dan browser subagent dapat menguji skenario secara deterministik tanpa mengandalkan gerakan keyboard yang presisi.

## 9. Tools dan repo
- Skrip pipeline aset di `tools/` (lihat `60-asset-generation-qa.md`). Server statis untuk uji: perintah sederhana tanpa dependensi berat.
- Commit git di tiap gerbang; `.gitignore` memuat `assets/_raw/` bila besar.

## 10. Save v3 dan hook uji (v4)
Save v3 menambah: `energy`, `inventory[{itemId,count}]`, `vehicle{mounted,parked{map,x,y}}`, `missionsCompleted[]`, `terrain.mode`; migrasi dari v2 (energi 100, tas kosong, motor turun). Hook debug tambahan (aturan keamanan sama, hanya `?debug=1` + `debugEnabled:true`): `collisionProbe(mapId)`, `listNPCs(mapId)`, `completeMission(id)`, `useItem(slot)`, `giveItem(id,n)`, `setEnergy(n)`, `toggleVehicle()`, `measureSpeed()`, `setFuel(n)`, `advanceRealSeconds(n)` (jam palsu untuk uji bensin).


## 11. Event domain dan hook inspeksi (v5)
Perubahan state melalui satu pintu domain yang memancarkan event bertipe (`cashChanged`, `fuelChanged`, `energyChanged`, `inventoryChanged`, `backpackChanged`, `mapChanged`, dst.); UI berlangganan. Hook debug tambahan hanya untuk inspeksi/persiapan: `getInventory()`, `getFuel()`, `getPath()`, `getApproachReport(mapId)`; tidak boleh dipakai untuk menjalankan aksi yang diuji (rule 78).
