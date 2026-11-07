# UI Design Rules — Life Journey
> Versi 1.0 · 2026-11-08  
> Dokumen ini adalah sumber kebenaran tunggal untuk semua desain antarmuka (HUD, panel, tombol, dialog).  
> **Setiap perubahan UI wajib mengacu file ini.**

---

## 1. Prinsip Utama

| # | Prinsip | Alasan |
|---|---------|--------|
| U1 | **Konsistensi Token** | Semua warna, spasi, radius harus dari `tokens.css`. Tidak ada nilai "magic number" di file JS/CSS lain. |
| U2 | **Hierarki Visual Jelas** | HUD (z-index 50) → Panel Modal (z-index 200) → Dialog NPC (z-index 300) → Alert darurat (z-index 400). |
| U3 | **Pixel-art Friendly** | Semua ukuran adalah kelipatan 4px. Tidak ada shadow blur > 8px pada elemen game utama. Border 2px solid, bukan shadow tipis. |
| U4 | **Keterbacaan** | Teks ≥ 12px. Kontras warna minimal WCAG AA (4.5:1). Teks currency selalu `tabular-nums`. |
| U5 | **Anti-XSS** | Tidak ada `innerHTML`/`outerHTML`/`eval` untuk data dinamis. Semua data = `textContent`. |
| U6 | **Offline First** | Tidak ada CDN font. Font stack: `'Nunito', system-ui, sans-serif`. |

---

## 2. Palet Warna UI (dari `tokens.css`)

### 2.1 Warna Semantik
| Token | Hex | Digunakan untuk |
|-------|-----|-----------------|
| `--color-bg-primary` | `#121A2E` | Background body / game canvas |
| `--color-bg-panel` | `#1F2A44` | Background semua panel / modal |
| `--color-bg-card` | `#34456B` | Card item, row tabel, badge |
| `--color-text-primary` | `#FBF6EA` | Teks utama (label, judul) |
| `--color-text-secondary` | `#F7EEDA` | Teks sekunder |
| `--color-text-muted` | `#B8A88A` | Label kecil, header tabel |
| `--color-accent` | `#D9A441` | Tombol primary, judul panel, ikon aktif, nilai currency |
| `--color-accent-hover` | `#C4832E` | Hover tombol primary |
| `--color-danger` | `#C0654A` | Tombol danger, angka negatif, peringatan |
| `--color-success` | `#6F9262` | Transaksi positif, misi selesai |
| `--color-border` | `#34456B` | Semua border panel, divider |

### 2.2 Warna Status Bar
| Status | Token | Kondisi |
|--------|-------|---------|
| Bensin penuh | `--color-success` | ≥ 60% |
| Bensin sedang | `--color-warning` = `--color-gold` | 30%–59% |
| Bensin kritis | `--color-danger` | < 30% |

---

## 3. Tipografi

| Kategori | Font | Size | Weight | Token warna |
|----------|------|------|--------|-------------|
| Label HUD | Nunito | 11px | 600 | `--color-text-muted` |
| Nilai HUD | Nunito | 13px | 700 | `--color-text-primary` atau `--color-accent` |
| Judul Panel | Nunito | 15px | 700 | `--color-accent` |
| Body Panel | Nunito | 13px | 400 | `--color-text-primary` |
| Item nama | Nunito | 13px | 600 | `--color-text-primary` |
| Item harga | Nunito | 12px | 700 | `--color-accent` |
| Tabel header | Nunito | 11px | 400 uppercase | `--color-text-muted` |
| Currency | Nunito | — | 700 | `--color-accent` (positif) / `--color-danger` (negatif) |
| Prompt interaksi | Nunito | 12px | 700 | `--color-accent` |

---

## 4. Layout HUD (`lj-hud`)

```
┌────────────────────────────────────────────────────────────────┐
│ [💰 Kas: Rp15.000] [🏦 Tabungan: Rp5.000] [⛽ Bensin ████░░ 70%] │  ← KIRI (hud-stats)
│                  [📅 Bulan 1·Hari 3]  [🎯 Misi: ...]            │  ← TENGAH (hud-center)
│                                     [📒 Buku Kas] [📊 Anggaran] │  ← KANAN (hud-nav)
└────────────────────────────────────────────────────────────────┘
```

### 4.1 Spesifikasi HUD
- **Tinggi:** 48px fixed
- **Background:** `rgba(18, 26, 46, 0.92)` (semi-transparan)
- **Border-bottom:** `2px solid var(--color-border)`
- **Padding horizontal:** `var(--space-md)` (16px)
- **Layout:** CSS Flexbox, `justify-content: space-between`, `align-items: center`
- **z-index:** 50

### 4.2 HUD Badge (tiap status indicator)
- **Padding:** `4px 10px`
- **Background:** `var(--color-bg-card)`
- **Border:** `1px solid var(--color-border)`
- **Border-radius:** `var(--radius-sm)` (4px)
- **Gap antar badge:** `var(--space-sm)` (8px)
- **Icon:** karakter emoji/unicode sebelum label (tidak perlu gambar)

### 4.3 Bensin Bar
- Bar visual lebar 64px, tinggi 8px
- Border-radius: 4px
- Warna fill: lihat §2.2

---

## 5. Tombol (`lj-btn`)

### 5.1 Jenis Tombol
| Kelas | Background | Border | Teks | Digunakan untuk |
|-------|------------|--------|------|-----------------|
| `.lj-btn.primary` | `--color-accent` | — | `--color-bg-primary` | Aksi utama (Beli, Nabung, Konfirmasi) |
| `.lj-btn.secondary` | `--color-bg-card` | `--color-accent` | `--color-text-primary` | Aksi sekunder (Buku Kas, Anggaran) |
| `.lj-btn.danger` | `--color-bg-card` | `--color-danger` | `--color-danger` | Reset, Keluar |
| `.lj-btn.ghost` | `transparent` | `--color-border` | `--color-text-muted` | Tutup, Batal |

### 5.2 Ukuran Tombol
| Ukuran | Padding | Font Size | Min Width |
|--------|---------|-----------|-----------|
| Normal | `8px 16px` | 13px | 80px |
| Kecil (HUD) | `4px 10px` | 11px | 60px |
| Besar (Modal CTA) | `10px 24px` | 14px | 120px |

### 5.3 State Tombol
- **:hover** — brightness +10%, transition 120ms
- **:active** — scale(0.97), transition 60ms
- **:focus-visible** — outline: `2px solid var(--color-accent)`, offset 2px
- **:disabled** — opacity 0.4, cursor not-allowed

---

## 6. Panel Modal (`lj-panel`)

### 6.1 Struktur Wajib
```
.lj-modal-backdrop          ← full-screen overlay, rgba(0,0,0,0.65)
  └── .lj-panel              ← panel utama
        ├── .panel-header    ← flex row: judul kiri + tombol ✕ kanan
        │     ├── h2.panel-title
        │     └── button.lj-btn.ghost.btn-close (teks: "✕")
        └── .panel-body      ← konten scrollable jika perlu
```

### 6.2 Spesifikasi Panel
- **Max-width:** 480px (panel toko), 640px (buku kas), 560px (anggaran)
- **Max-height:** 80vh, `overflow-y: auto`
- **Background:** `var(--color-bg-panel)`
- **Border:** `2px solid var(--color-border)`
- **Border-radius:** `var(--radius-lg)` (16px)
- **Padding:** `var(--space-md)` (16px)
- **Box-shadow:** `0 8px 32px rgba(0,0,0,0.6)`
- **z-index:** 200
- **Posisi:** `position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%)`

### 6.3 Panel Header
- **Height:** 48px
- **Display:** flex, justify-content: space-between, align-items: center
- **Border-bottom:** `1px solid var(--color-border)`
- **Margin-bottom:** `var(--space-md)`
- Judul: `font-size: 15px; font-weight: 700; color: var(--color-accent)`
- Tombol ✕: `.lj-btn.ghost`, ukuran 28×28px, posisi absolute top-right ATAU di flex-end

---

## 7. Item Toko (`shop-item-card`)

```
┌──────────────────────────────────────────────┐
│  🍔 Nasi Goreng Kantin          Rp 8.000 [Beli] │
└──────────────────────────────────────────────┘
```

- **Layout:** flex row, `justify-content: space-between`, `align-items: center`
- **Background:** `var(--color-bg-card)`
- **Border:** `1px solid var(--color-border)`
- **Border-radius:** `var(--radius-md)` (8px)
- **Padding:** `10px 14px`
- **Gap antar card:** `var(--space-sm)` (8px)
- **Hover:** border-color `var(--color-accent)`, transition 120ms

---

## 8. Dialog Interaksi NPC (`lj-npc-dialog`)

Dialog muncul ketika player mendekati NPC dalam radius 56px.

### 8.1 Struktur
```
.lj-npc-dialog                ← popup di atas NPC, Phaser atau DOM
  ├── .npc-portrait           ← 32×32 avatar placeholder (warna + initial)
  ├── .npc-bubble             ← speech bubble
  │     ├── .npc-name         ← nama NPC
  │     └── .npc-text         ← dialog text
  └── .npc-choices            ← daftar pilihan (jika ada)
        ├── button.lj-btn.secondary  ← pilihan 1
        └── button.lj-btn.secondary  ← pilihan 2
```

### 8.2 Spesifikasi Dialog
- **Trigger:** proximity ≤ 56px (Euclidean) + tombol [E] atau [Space] untuk buka, [Esc] atau klik luar untuk tutup
- **Posisi:** DOM overlay, centered di bawah HUD, atau di atas NPC jika ruang cukup
- **Max-width:** 360px
- **Background:** `var(--color-bg-panel)`
- **Border:** `2px solid var(--color-accent)` (berbeda dari panel biasa agar terasa "dialog")
- **Border-radius:** `12px`
- **z-index:** 300
- **Portrait:** bulatan 40px, background `var(--color-bg-card)`, teks inisial NPC `font-size: 18px; color: var(--color-accent)`
- **Nama NPC:** `font-size: 12px; font-weight: 700; color: var(--color-accent); text-transform: uppercase`
- **Teks dialog:** `font-size: 13px; line-height: 1.5; color: var(--color-text-primary)`
- **Tombol pilihan:** `.lj-btn.secondary`, lebar penuh (`width: 100%`)
- **Proximity indicator:** ring berkedip warna `--color-accent` di atas NPC saat dalam jangkauan

### 8.3 Perilaku
1. NPC `inRange` → tampilkan badge "Tekan [E]" di atas kepala NPC (Phaser text, bukan DOM)
2. Tombol [E] ditekan → tutup badge, buka `.lj-npc-dialog` DOM
3. Jika NPC punya `choices` → tampilkan tombol pilihan; tiap pilihan memicu `CustomEvent('lj:npcChoice', {npcId, choiceId})`
4. Jika tidak ada `choices` → tampilkan satu tombol "Tutup"
5. [Esc] → tutup dialog
6. Dialog hanya satu yang aktif sekaligus (`singleton`)

---

## 9. Ikon (`icon_sheet_ui`)

- Sheet: `assets/icons/icon_sheet_ui.png`, 128×128px, 16 ikon @32×32
- Render pada HTML: `<canvas>` 20×20px atau `background-image` sprite-offset
- **Fallback wajib:** jika ikon gagal load → tampilkan emoji unicode
- Ikon yang digunakan di HUD:
  | Slot | Ikon | Emoji fallback |
  |------|------|----------------|
  | 0 | Kas | 💰 |
  | 1 | Tabungan | 🏦 |
  | 2 | Bensin | ⛽ |
  | 3 | Misi | 🎯 |
  | 4 | Kalender | 📅 |
  | 5 | Buku Kas | 📒 |
  | 6 | Anggaran | 📊 |
  | 7 | Pengaturan | ⚙️ |

---

## 10. Animasi & Transisi

| Elemen | Properti | Durasi | Easing |
|--------|----------|--------|--------|
| Tombol hover | background, color | 120ms | ease |
| Tombol active | transform: scale | 60ms | ease |
| Panel muncul | opacity 0→1, translateY 8px→0 | 200ms | ease-out |
| Panel tutup | opacity 1→0, translateY 0→8px | 150ms | ease-in |
| Bar bensin fill | width | 300ms | ease |
| NPC proximity ring | opacity pulse | 800ms | ease-in-out infinite |
| HUD nilai berubah | flash kuning 1 frame | 200ms | — |

---

## 11. Layout Responsif

Game berjalan di resolusi tetap **960×540px** (16:9). UI DOM di-overlay di atasnya.

- Jangan gunakan satuan `vw`/`vh` di dalam panel; gunakan `px` atau `%` relatif terhadap panel.
- HUD selalu 100% lebar canvas (960px).
- Panel modal: posisi fixed center (`top: 50%; left: 50%; transform: translate(-50%,-50%)`).
- Pada layar lebih kecil dari 960px: `transform: scale()` pada `#game-container` di `index.html`.

---

## 12. Checklist Validasi UI (sebelum commit)

- [ ] Semua nilai warna menggunakan token `var(--color-*)` 
- [ ] Semua teks dinamis menggunakan `.textContent` (bukan `.innerHTML`)
- [ ] Semua tombol punya `type="button"` eksplisit
- [ ] Semua elemen interaktif punya `:focus-visible` outline
- [ ] Semua modal punya `role="dialog"` dan `aria-modal="true"`
- [ ] HUD tetap terbaca di atas latar pixel-art (ada backdrop semi-transparan)
- [ ] Tidak ada font dari CDN eksternal
- [ ] Semua icon ada fallback emoji
- [ ] Dialog NPC bisa ditutup dengan [Esc]
- [ ] z-index sesuai hierarki (§2 Prinsip U2)

