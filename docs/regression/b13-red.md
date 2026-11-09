# Reproduksi Masalah B13: Sprite NPC Budi Bergaya Kartun
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Bandingkan berkas `assets/npcs/npc_budi.png` dengan `assets/characters/char_player_m_casual.png`.
- **Hasil Aktual:** Budi digambar dalam proporsi kepala terlalu besar (chibi/vektor kartun), hanya 1 frame statis, tanpa outline piksel retro 1px konsisten dengan pemain.
- **Tangkapan Layar:** `docs/regression/b13_sprite_budi_kartun_red.png`
- **Akar Masalah:** Prompt generasi sprite Budi di v4 menghasilkan gaya kartun anime halus alih-alih sprite piksel 32x64 3-arah (Rule 85 §4).
