# Catatan Keamanan Aplikasi (SECURITY-NOTES.md)

Penerapan prinsip keamanan OWASP Top 10 (2021) pada Life Journey:

## 1. Pemetaan Risiko & Mitigasi

| OWASP Risk | Ancaman | Mitigasi yang Diterapkan | Lokasi / Kode |
|---|---|---|---|
| A03: Injection | XSS via nama pemain / input teks / save data | Dilarang keras menggunakan `innerHTML`, `outerHTML`, atau `eval`. Semua injeksi teks dinamis menggunakan `textContent` dan sanitasi regex ketat. | `src/ui/*`, `src/domain/evaluation.js`, `src/state/persistence.js` |
| A04: Insecure Design | Manipulasi saldo / transaksi tidak wajar | Integritas keuangan dijamin di domain via append-only ledger dengan validasi invarian ketat (saldo tidak bisa negatif, nominal integer rupiah). UI tidak menghitung uang. | `src/domain/ledger.js` |
| A05: Security Misconfiguration | Skrip eksternal / penyusupan CDN | CSP ketat di `<meta http-equiv="Content-Security-Policy">`. Hook debug `window.__LJ__` hanya aktif bila `debugEnabled: true` dan ada param `?debug=1`. | `index.html`, `src/game/scenes/World.js` |
| A06: Vulnerable & Outdated Components | Dependensi rentan pihak ketiga | Semua vendor dipin dan diunduh lokal ke `vendor/`. Phaser 3.80.1 SHA-256 diverifikasi. | `vendor/phaser.min.js` |
| A08: Software & Data Integrity Failures | Kerusakan data / prototype pollution di LocalStorage | Sanitasi skema ketat saat memuat save: whitelist key, cek prototype injection (`__proto__`, `constructor`, `prototype`), validasi tipe & rentang data. | `src/state/schema.js`, `src/state/persistence.js` |

## 2. Checksum Vendor
- `vendor/phaser.min.js` (Phaser v3.80.1): `62081f6a1b51d040473f919ffedef9009953c20833518e146da5a8d1c9405ea8`
