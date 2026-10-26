# F.R.I.D.A.Y — Status Terkini

> Satu halaman "posisi sekarang". **Diperbarui setiap kali satu tahap selesai** (aturan proyek sejak 2026-10-25). Riwayat lengkap ada di `Memory Think/SPRINT{N}_LOG.md`; halaman ini hanya keadaan terakhir.

**Diperbarui:** 2026-10-26 — Tahap 4 selesai (mini-M11 + jurnal aksi), awal Sprint 4.

## Posisi

| | |
|---|---|
| Sprint aktif | **Sprint 4** (M11 Security mini + M16 Evaluasi mini). Sprint 3 selesai (M4 + M5 simulasi). |
| Rencana berjalan | Rencana 5 tahap pasca-feedback 4 model AI: Tahap 1 ✅, Tahap 2 ✅, Tahap 3 ✅, Tahap 4 (mini-M11 + jurnal aksi) ✅, Tahap 5 (mini-M16 + observability) ⬜ |
| Test | 402 passed, 4 skipped (Windows); 4 test khusus Linux (izin file) ikut jalan di CI |
| CI | GitHub Actions, Linux + Windows, LLM palsu — hijau pada push terakhir (`a659d50`) |
| Commit terakhir yang di-push | Tahap 4 (lihat `git log -1`) |
| Model LLM | `claude-haiku-4-5` (development) |

## Yang sudah bisa dilakukan F.R.I.D.A.Y

- Mengobrol lewat CLI (`python -m backend.cli`), dengan memori percakapan, fakta profil, dan pencarian obrolan lama.
- Mencari tool yang dibutuhkan sendiri (`find_tools`), memuat otomatis tool baca, mempertahankan tool yang baru dipakai.
- Mengontrol rumah simulasi (lampu, AC): nyala/mati, kecerahan, suhu target; membedakan suhu target vs suhu ruangan.
- Jujur saat gagal: perangkat offline, konfirmasi hilang (baca ulang), perangkat lambat ("masih diproses"), tool tidak ada.
- Bertanya balik saat perintah ambigu ("lampu yang mana?").
- Menyimpan turn yang terputus (error, Ctrl+C) dengan penanda, tanpa kehilangan catatan aksi.
- Menjawab jam dalam waktu lokal.
- **Minta izin:** hanya menjalankan tool yang terdaftar di `config/permissions.json`. Aksi penting (atau aksi biasa yang diberi `confirm`) ditanyakan y/n di terminal, langsung ke pemilik, bukan lewat AI.
- **Mencatat setiap perintah perangkat** di jurnal aksi, sebelum dan sesudah dikirim. Saat CLI dibuka, perintah yang hasilnya belum jelas dilaporkan (`/journal`, `/journal ack`), tidak diulang otomatis.
- Perintah "masih diproses" yang tidak terkonfirmasi dalam 1 menit menjadi "tidak jelas".
- Menolak dua perintah ke perangkat yang sama dalam satu langkah. Isi arsip dan hasil tool diperlakukan sebagai data, bukan perintah.

## Celah yang diketahui (belum ditutup)

| Celah | Rencana |
|---|---|
| Ketahanan terhadap perintah selundupan baru diuji 7 skenario manual (semua lolos); penjaga pintu belum otomatis minta konfirmasi setelah F.R.I.D.A.Y membaca data luar | Tahap 5: aturan "baca data luar → aksi wajib konfirmasi" + uji ulang semua skenario dari awal |
| Shadow perangkat hanya di memori (jejak perintahnya sudah ada di jurnal) | Saat adapter perangkat nyata |
| `find_tools` masih menampilkan tier versi tool (kosmetik) | Kecil, kapan saja |
| Persetujuan lewat suara/kamera + verifikasi "ini benar pemilik" | Sprint 5 / M11 lanjutan |
| Belum ada evaluasi terukur (skenario tetap, metrik) dan pencatatan biaya per turn | Tahap 5 / Sprint 4 (M16 mini) |
| Pencarian bahasa Indonesia tanpa stemming (`kucing` ≠ `kucingnya`) | Diukur dulu di Tahap 5 |
| Format pesan terikat Anthropic; penanda turn berupa teks | Sebelum Sprint 8 (satu perubahan skema) |
| Gaya bahasa campur "Anda"/"kamu", emoji | M15 (Sprint 10) |
| Perangkat nyata belum ada | Versi berikutnya (PR user: pilih gateway, inventaris perangkat) |

## Langkah berikutnya

1. **Tahap 5:** 15–20 skenario evaluasi + metrik + catatan token/biaya/latensi per turn; eksperimen `find_tools` vs semua tool, prompt caching, pencarian Indonesia.

Sebelum tiap tahap, asisten menulis daftar rencana bernomor dan menunggu persetujuan.

## Untuk pemilik (di luar repo)

- Perbarui **Node.js** ke v24.22.1 dan **PHP** ke 8.4.27 (rilis keamanan Okt 2026) — lihat `SPRINT3_LOG.md` 2026-10-25.
- Opsional: tambahkan `FRIDAY_TIMEZONE=Asia/Jakarta` ke `.env`.
