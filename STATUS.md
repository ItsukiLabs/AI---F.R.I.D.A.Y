# F.R.I.D.A.Y — Status Terkini

> Satu halaman "posisi sekarang". **Diperbarui setiap kali satu tahap selesai** (aturan proyek sejak 2026-10-25). Riwayat lengkap ada di `Memory Think/SPRINT{N}_LOG.md`; halaman ini hanya keadaan terakhir.

**Diperbarui:** 2026-10-25 — Sprint 3 ditutup (Tahap 3 selesai).

## Posisi

| | |
|---|---|
| Sprint aktif | **Sprint 3 selesai** (M4 Tool Registry + M5 Device Layer, versi simulasi). Berikutnya **Sprint 4**. |
| Rencana berjalan | Rencana 5 tahap pasca-feedback 4 model AI: Tahap 1 ✅, Tahap 2 ✅, Tahap 3 ✅, Tahap 4 (mini-M11 + jurnal aksi) ⬜, Tahap 5 (mini-M16 + observability) ⬜ |
| Test | 351 passed, 3 skipped (Windows); 3 test khusus Linux ikut jalan di CI |
| CI | GitHub Actions, Linux + Windows, LLM palsu — hijau pada push terakhir |
| Commit terakhir yang di-push | lihat `git log -1` (status ini ditulis sebelum commit penutup Sprint 3) |
| Model LLM | `claude-haiku-4-5` (development) |

## Yang sudah bisa dilakukan F.R.I.D.A.Y

- Mengobrol lewat CLI (`python -m backend.cli`), dengan memori percakapan, fakta profil, dan pencarian obrolan lama.
- Mencari tool yang dibutuhkan sendiri (`find_tools`), memuat otomatis tool baca, mempertahankan tool yang baru dipakai.
- Mengontrol rumah simulasi (lampu, AC): nyala/mati, kecerahan, suhu target; membedakan suhu target vs suhu ruangan.
- Jujur saat gagal: perangkat offline, konfirmasi hilang (baca ulang), perangkat lambat ("masih diproses"), tool tidak ada.
- Bertanya balik saat perintah ambigu ("lampu yang mana?").
- Menyimpan turn yang terputus (error, Ctrl+C) dengan penanda, tanpa kehilangan catatan aksi.
- Menjawab jam dalam waktu lokal.

## Celah yang diketahui (belum ditutup)

| Celah | Rencana |
|---|---|
| **Belum ada gerbang izin**: aksi perangkat langsung dijalankan; `read_only_hint` dari tool ikut menentukan auto-load | Tahap 4 / Sprint 4 (M11 mini) |
| **S5**: kalau simpan sesi gagal setelah perangkat bergerak, jejak aksi hilang | Tahap 4 (jurnal aksi) |
| Shadow perangkat + operasi pending hanya di memori (hilang saat restart); pending tanpa batas waktu | Tahap 4 (jurnal aksi) |
| Hasil arsip/tool belum diberi label "data, bukan perintah" (prompt injection) | Tahap 4 |
| Belum ada evaluasi terukur (skenario tetap, metrik) dan pencatatan biaya per turn | Tahap 5 / Sprint 4 (M16 mini) |
| Pencarian bahasa Indonesia tanpa stemming (`kucing` ≠ `kucingnya`) | Diukur dulu di Tahap 5 |
| Format pesan terikat Anthropic; penanda turn berupa teks | Sebelum Sprint 8 (satu perubahan skema) |
| Gaya bahasa campur "Anda"/"kamu", emoji | M15 (Sprint 10) |
| Perangkat nyata belum ada | Versi berikutnya (PR user: pilih gateway, inventaris perangkat) |

## Langkah berikutnya

1. **Tahap 4 (awal Sprint 4):** gerbang izin di titik eksekusi tool (klasifikasi dari pengaturan pemilik, CRITICAL wajib konfirmasi, aksi belum terklasifikasi ditolak), jurnal aksi SQLite (`operation_id`, PREPARED → SUCCEEDED/FAILED/UNKNOWN), label "data, bukan perintah".
2. **Tahap 5:** 15–20 skenario evaluasi + metrik + catatan token/biaya/latensi per turn; eksperimen `find_tools` vs semua tool, prompt caching, pencarian Indonesia.

Sebelum tiap tahap, asisten menulis daftar rencana bernomor dan menunggu persetujuan.

## Untuk pemilik (di luar repo)

- Perbarui **Node.js** ke v24.22.1 dan **PHP** ke 8.4.27 (rilis keamanan Okt 2026) — lihat `SPRINT3_LOG.md` 2026-10-25.
- Opsional: tambahkan `FRIDAY_TIMEZONE=Asia/Jakarta` ke `.env`.
