# Sprint 2 — Log Pengerjaan (M2 Memory System)

> Datasheet pengerjaan Sprint 2. Setiap kali ada update fitur/logika (kode, schema, struktur), tambahkan entry baru di bawah — jangan edit entry lama, supaya riwayat tetap utuh dan tidak ambigu soal apa yang sudah dikerjakan.
>
> Selain kode, **diskusi/pembahasan penting** (pertanyaan konsep, keputusan arsitektur yang muncul dari obrolan, penjelasan yang mengubah pemahaman) juga dicatat di sini sebagai entry tersendiri — supaya ada jejak "kenapa" di balik keputusan, bukan cuma "apa" yang berubah di kode.

## Format Entry

```
## [YYYY-MM-DD] Judul singkat

- **Apa yang dikerjakan:** ...
- **File yang dibuat/diubah:** ...
- **Alasan/keputusan:** ... (kalau ada keputusan desain yang perlu diingat)
- **Belum dikerjakan / TODO lanjutan:** ...
```

---

## [2026-08-13] Setup log Sprint 2

- **Apa yang dikerjakan:** Sprint 1 (M0 Contract Layer + M1 Agent Core) selesai dan sudah di-push (commit `0c05301`, `552496e`, `f12d10a` — detail lengkap di `SPRINT1_LOG.md`). User konfirmasi lanjut ke Sprint 2 (M2 Memory System), diminta bikin file log terpisah mengikuti format `SPRINT1_LOG.md` — sesuai konvensi standing proyek ini bahwa tiap sprint punya file log sendiri di `Memory Think/`.
- **File yang dibuat/diubah:**
  - `Memory Think/SPRINT2_LOG.md` — baru (file ini).
- **Alasan/keputusan:**
  - Format & aturan sama persis dengan `SPRINT1_LOG.md` (append-only, catat diskusi bukan cuma kode) — supaya konsisten dan gampang dibandingkan lintas sprint.
  - M2 dipecah 3 sub-modul per `sprint-paper-mapping.md`: **M2a** (short-term/konteks aktif), **M2b** (long-term/retrieval-embedding), **M2c** (profile/hierarki memori & paging). 4 paper dasar sudah diriset dari sesi-sesi sebelumnya (lihat `PAPER_NOTES.md` kategori #2): **MemGPT** (⭐ Wajib — cetak biru hierarki memori ala virtual memory OS), **Generative Agents/Smallville** (memory stream + reflection berkala), **Lost in the Middle** (peringatan penempatan hasil retrieval dalam prompt), **RAG Survey 2023** (peta pola retrieval Naive→Advanced→Modular).
  - Ada overlap kecil dengan TODO tersisa M1: Reflexion di M1 saat ini cuma hidup satu sesi run — begitu M2 ada infrastruktur memori, refleksi kegagalan tool-call bisa dipersistenkan lintas sesi.
- **Belum dikerjakan / TODO lanjutan:**
  - Desain/implementasi M2 itu sendiri belum mulai — baru tahap setup log, belum ada plan mode atau kode.
  - `Memory Think/M2_memory.md` (catatan per-modul, ikut konvensi `M0_contract_layer.md`/`M1_agent_core.md`) belum dibuat — akan dibuat begitu diskusi/implementasi M2 mulai.

## [2026-08-13] Penegasan aturan: log setiap instruksi, bukan cuma kode

- **Apa yang dikerjakan:** User minta aturan standing yang sama seperti di Sprint 1 (lihat `SPRINT1_LOG.md`, entry "[2026-08-07] Penegasan aturan...") ditulis eksplisit juga di file log Sprint 2 ini — **setiap kali user menyuruh sesuatu**, entry baru ditambahkan ke `SPRINT2_LOG.md`, bukan cuma saat kode berubah, tapi juga diskusi/pertanyaan/keputusan konsep. Ini bukan aturan baru, cuma ditegaskan ulang supaya berlaku jelas per-file, tidak diasumsikan otomatis "nempel" dari Sprint 1.
- **File yang dibuat/diubah:**
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:** Sama seperti alasan aslinya di Sprint 1 — jadi rujukan/"training" biar asisten nggak salah asumsi soal apa yang sudah dibahas, dan pengingat buat user sendiri biar nggak lupa progres/keputusan yang sudah diambil. Konvensi ini sudah tercatat juga di memori eksternal (`friday_progress_tracking.md`), tapi user tetap minta ditulis eksplisit di file log tiap sprint supaya jelas dari sisi dokumen proyek sendiri, tidak bergantung ke memori asisten di luar repo.
- **Belum dikerjakan / TODO lanjutan:** Tidak ada perubahan teknis — murni penegasan konvensi kerja, sama seperti TODO entry sebelumnya (desain/implementasi M2 belum mulai).

## [2026-08-14] Audit kecukupan paper M2 + verifikasi & perbaikan 10 file baru

- **Apa yang dikerjakan:**
  1. User tanya apakah paper M2 yang ada (4 paper: MemGPT, Generative Agents, Lost in the Middle, RAG Survey) sudah cukup untuk mulai desain M2. Dianalisis per sub-modul: M2c (hirarki) & M2a (konteks aktif) & M2b (retrieval) sudah tercover, tapi ada **gap nyata**: tidak ada paper soal mekanisme *forgetting/consolidation* untuk memori jangka panjang — penting karena F.R.I.D.A.Y jalan terus-menerus lintas sesi (beda dari Smallville yang cuma simulasi terbatas), tanpa strategi forgetting storage akan tumbuh tanpa batas.
  2. User diminta cek ulang isi folder `M2/` secara langsung (bukan cuma percaya catatan lama) — ternyata folder sudah berisi **15 file**, bukan 5 seperti di `PAPER_NOTES.md` (10 file baru sudah ditambahkan user tapi belum diverifikasi/dicatat), termasuk beberapa yang persis menjawab gap forgetting yang baru disebut (MemoryBank, FSFM, Survey on Memory Mechanism of LLM Agents, dkk).
  3. Verifikasi isi vs judul via `pdftotext` untuk semua 15 file (termasuk 5 lama, dicek ulang) — pola yang sama dipakai sejak Sprint 1 untuk kasus M7/M14/M15/M17. Hasil: **13 cocok**, **2 masalah**:
     - Duplikat 100% (md5 identik): `Generative Agents...(2023).pdf` (lama, tracked git) vs `Generative Agents...— Park et al. (2023), UIST.pdf` (baru, untracked)
     - Mismatch: `The Memory Function of Sleep — Diekelmann & Born (2010), Nature Reviews Neuroscience.pdf` isinya bukan paper itu — isi asli "About Sleep's Role in Memory" oleh Rasch & Born (2013), *Physiological Reviews*
     - Bonus: 1 salah atribusi nama file (bukan mismatch konten) — "Recursively Summarizing...— Qian et al." seharusnya "— Wang et al." (penulis asli tidak ada nama Qian)
  4. Eksekusi perbaikan: hapus file duplikat yang untracked (bukan yang tracked, biar tidak ada churn git tidak perlu), rename file sleep menyesuaikan isi asli (bukan cari paper pengganti, karena isinya tetap relevan buat topik consolidation), rename file Recursively Summarizing dengan atribusi benar. Hasil akhir folder `M2/`: **14 file**, semua cocok isi vs judul, 0 duplikat, 0 mismatch.
  5. Tulis 9 entry baru lengkap di `PAPER_NOTES.md` kategori #2 (ringkasan ide inti dari abstract masing-masing via `pdftotext`, relevansi ke sub-modul M2a/b/c, catatan koreksi nama file), update ringkasan total paper (108→117) dan tambah update log ke-4. Update `sprint-paper-mapping.md`: tabel Kategori #2 diperluas dari 3 jadi 14 baris paper, jumlah di tabel induk diupdate.
- **File yang dibuat/diubah:**
  - `Paper & Journal/F.R.I.D.A.Y/M2/` — 1 file duplikat dihapus, 2 file di-rename (sleep paper, Recursively Summarizing).
  - `Memory Think/PAPER_NOTES.md` — 9 entry baru di kategori #2, update ringkasan total & update log.
  - `Memory Think/sprint-paper-mapping.md` — tabel kategori #2 diperluas 3→14 paper, tabel induk diupdate.
  - `Memory Think/SPRINT2_LOG.md` — entry ini.
- **Alasan/keputusan:**
  - Standar verifikasi "cek isi PDF asli, jangan percaya nama file" tetap dipertahankan sebagai kebiasaan proyek — kembali terbukti berguna, menemukan 1 mismatch nyata dan 1 duplikat yang kalau tidak dicek akan tercatat sebagai "sudah lengkap" padahal salah.
  - File sleep yang mismatch **tidak** diganti dengan mencari paper "The Memory Function of Sleep" yang benar — cukup rename menyesuaikan isi asli, karena paper yang ada (Rasch & Born 2013) topiknya tetap relevan langsung untuk consolidation, jadi tidak ada alasan kuat membuang isi yang sudah bagus hanya karena nama filenya salah (sama prinsipnya dengan kasus "Form Follows Function" di Sprint 1).
  - Duplikat dihapus dari sisi yang untracked di git supaya tidak ada delete+re-add churn yang tidak perlu di riwayat commit.
- **Belum dikerjakan / TODO lanjutan:**
  - Perubahan sesi ini (file paper + 2 markdown notes) **belum di-commit/push** — menunggu instruksi user, sama seperti 2 perubahan `SPRINT1_LOG.md`/`SPRINT2_LOG.md` sebelumnya yang juga masih pending commit.
  - Riset paper M2 sekarang dianggap cukup kuat untuk mulai desain — termasuk sub-topik forgetting/consolidation M2c yang sebelumnya jadi gap. Next step: mulai plan mode untuk arsitektur M2 (M2a/M2b/M2c), belum ada kode maupun `M2_memory.md` sama sekali.
