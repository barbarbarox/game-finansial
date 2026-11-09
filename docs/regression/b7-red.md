# Reproduksi Masalah B7: Menekan E Dekat Ibu Memicu Furnitur Dapur
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Pemain berdiri di depan Ibu di dapur (x=20, y=13) menghadap Ibu dan menekan tombol E.
- **Hasil Aktual:** Dialog interaksi yang muncul adalah `int_dapur` ("Tekan [E] Memasak Bersama Ibu") dari kompor dapur, bukan dialog NPC Ibu (`dia_ibu_home`).
- **Tangkapan Layar:** `docs/regression/b7_interaksi_ibu_dapur_red.png`
- **Akar Masalah:** `_checkInteractables()` di `World.js` memilih elemen pertama dalam radius 50px tanpa memprioritaskan NPC (+20px) dan tanpa memperhitungkan arah hadap pemain (Rule 84).
