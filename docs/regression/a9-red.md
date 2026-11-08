# Reproduksi Masalah A9: Bar Bensin Tidak Berubah Setelah Isi Bensin di SPBU
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI:** Bensin diset 40%. Pemain berinteraksi dengan Mas Doni di SPBU dan mengklik opsi "Isi Bensin Pertalite 2 Liter (Rp20.000)".
- **Hasil Aktual:** Nilai bensin di HUD tetap 40%, lebar bar bensin tetap 40%, dan `state.gasoline` tetap bernilai 40. Uang berkurang Rp20.000 di buku kas.
- **Tangkapan Layar:** `docs/regression/a9_gas_bar_red.png`
- **Akar Masalah:** Pilihan dialog hanya memanggil `ledger_expense` dan `start_activity: "isi_bensin_motor"` tanpa fungsi refuel domain, dan `hud.js` tidak berlangganan event domain `fuelChanged`.

