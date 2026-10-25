# Feedback Eksternal untuk F.R.I.D.A.Y

> Ditulis: 2026-10-25. Berdasarkan dokumen `FRIDAY_PROJECT_REVIEW.md` (commit `94c24b2`).
> Fokus: kritik konkret, skenario gagal, alternatif. Bukan pujian umum.
>
> Dokumen ini adalah jawaban lengkap atas `FRIDAY_PROJECT_REVIEW.md`: penilaian umum, kekuatan yang harus dipertahankan, masalah kritis dengan severity, jawaban untuk §10 (prioritas), masukan per kode §9.1–§9.10, saran proses, prioritas tindakan, dan catatan tambahan.

---

## Daftar Isi

1. [Penilaian Umum](#1-penilaian-umum)
2. [Kekuatan yang Harus Dipertahankan](#2-kekuatan-yang-harus-dipertahankan)
3. [Masalah Kritis (dengan Severity)](#3-masalah-kritis-dengan-severity)
4. [Jawaban untuk §10 (Prioritas)](#4-jawaban-untuk-10-prioritas)
5. [Masukan per Kode (§9.1–§9.10)](#5-masukan-per-kode-91910)
6. [Saran Proses](#6-saran-proses)
7. [Prioritas Tindakan (Urutan yang Disarankan)](#7-prioritas-tindakan-urutan-yang-disarankan)
8. [Catatan Tambahan](#8-catatan-tambahan)
9. [Penutup](#9-penutup)

---

## 1. Penilaian Umum

Proyek ini **jauh di atas rata-rata** untuk solo developer. Yang paling menonjol:

- **Dokumentasi keputusan** (bukan cuma kode) sangat rapi. Log append-only + catatan per-modul = fondasi yang kuat untuk kesinambungan.
- **Prinsip desain dipegang konsisten dan diuji** — contoh: smoke test "nasi goreng" membuktikan prompt kompaksi benar-benar mencegah promosi fakta. Ini jarang ada.
- **Test coverage 280 test** dengan LLM palsu + smoke test manual = kombinasi tepat untuk tahap ini.
- **Self-assessment jujur** — daftar kekurangan di §5–§7 menunjukkan kedewasaan yang jarang.

Tapi ada **risiko struktural** yang kalau tidak ditangani sekarang akan makin mahal nanti. Dokumen ini fokus ke sana.

---

## 2. Kekuatan yang Harus Dipertahankan

1. **Prinsip "context ≠ memory"** dan implementasinya (profil hanya lewat tool eksplisit, arsip verbatim). Ini keputusan produk yang benar dan konsisten.
2. **Pemisahan M2a/M2b/M2c** dengan alasan yang jelas per lapisan.
3. **Atomic write + schema validation + domain exception** di store. Robustness M2a bagus.
4. **Karakterisasi test A2** (`test_a2_trace.py`) — keputusan proses yang matang: perilaku yang tidak diinginkan dikunci sebagai test supaya tidak bisa hilang/basi.
5. **Append-only log** — koreksi sebagai entry baru, bukan edit. Ini menjaga integritas riwayat.
6. **Smoke test dengan model asli** — mengungkap hal yang tidak bisa ditangkap `FakeLLMClient` (UTC, profil vs arsip, janji proaktif).

---

## 3. Masalah Kritis (dengan Severity)

### 3.1 [KRITIS] Bug kompaksi — silent data loss (§9.3)

```python
session.summary = response.text or session.summary
session.archived_turns.extend(to_summarize)
session.messages = remaining
```

Kalau `response.text` kosong:
- `session.summary` **tetap** (ringkasan lama)
- `to_summarize` **tetap dipindah** keluar dari `messages`

**Akibat:** pesan lama hilang dari konteks aktif tanpa peringatan. Masih ada di arsip, tapi hanya terjangkau lewat `recall_memory`. Ini **melanggar prinsip #3 "fail loud"** yang dipegang proyek.

**Perbaikan:** perlakukan empty response sebagai kegagalan:

```python
if not response.text:
    logger.warning("compaction returned empty summary; aborting")
    return False  # atau raise CompactionError
session.summary = response.text
session.archived_turns.extend(to_summarize)
session.messages = remaining
```

**Test:** tambahkan kasus `FakeLLMClient` yang mengembalikan `text=None`/`""` → assert `session.messages` tidak berubah dan `summary` tidak berubah.

### 3.2 [TINGGI] Provider lock-in lebih parah dari yang diklaim (§5.4 no. 1)

Format Anthropic (`tool_use`/`tool_result`) merembes ke:
- `loop.py` — `_assistant_message()`, `_execute_tool_call()`
- `session.py` — `to_llm_messages()`
- `compaction.py` — `_find_safe_cut_index()`
- `retention.py` — `recently_used_tool_names()`

Klaim "provider-agnostic" sudah tepat disebut belum terbukti. Untuk Sprint 8 (local model), ini akan menyentuh **4 modul**, bukan cuma `llm_client.py`.

**Saran:** definisikan format `Message` netral **sekarang** (atau setidaknya dokumentasikan setiap titik yang menyentuh format Anthropic), dan buat adapter yang mengkonversi. Meskipun hanya Anthropic yang diimplementasi, abstraksinya memaksa disiplin.

**Realistis untuk model lokal:** model open-weight (Llama/Qwen/Mistral) bisa tool calling dengan prompting yang baik, tapi `find_tools` + dynamic loading lebih sulit untuk model <30B. Siapkan **fallback "inject semua tool"** kalau model lokal gagal dengan discovery — ini menukar context size dengan reliability.

### 3.3 [TINGGI] Urutan roadmap — keamanan dan evaluasi terlambat

Device control sudah ada di Sprint 3 (aktuator `STANDARD` langsung dijalankan), M11 baru Sprint 4. Untuk lampu/AC risikonya kecil, tapi pola ini akan terbawa ke kunci pintu/kompor.

**Minimal sekarang (sebelum M5 adapter nyata):**
1. **Konfirmasi untuk `CRITICAL`** — meskipun cuma prompt "yakin? (y/n)" di CLI, ini membangun kebiasaan.
2. **Allowlist per provider** untuk `AutoLoadPolicy` — jangan percaya `read_only_hint` yang dideklarasikan adapter sendiri (§9.6). Adapter yang salah/berbahaya bisa menandai aktuator sebagai read-only.
3. **Time-bound permission** ala HearthNet — permission expires after N seconds.

### 3.4 [TINGGI] Evaluasi di Sprint 12 terlalu lambat

Tanpa metrik, setiap keputusan "sudah cukup baik" tidak terukur. Smoke test sekali dengan 1 model dan 8 skenario tidak cukup.

**Minimal harness sekarang:**
- 10–20 skenario scripted: `(initial_state, command, expected_final_state)` ala SAGE.
- Metrik **terpisah**: `task_completion` vs `tool_correctness` (temuan ScaleMCP: task completion tinggi bisa menutupi tool correctness rendah).
- Catat: steps, latency, cost per scenario.
- Jalankan dengan `FakeLLMClient` (deterministik) + smoke test manual berkala.

### 3.5 [SEDANG] Overhead dokumentasi mulai tidak seimbang

145 KB log + 190 KB paper notes untuk 3 sprint. Membantu kesinambungan, tapi satu sesi kerja (2026-09-11) **hilang** karena tidak sempat ditulis — artinya proses ini belum menjamin konsistensi.

**Saran:**
- Pindah tracking ke GitHub Issues/Projects (lebih terlihat, bisa di-filter, tidak hilang di file besar).
- Atau pisahkan "decision log" (ringkas, per keputusan) dari "chronological log" (detail, opsional).
- Template dengan field wajib (Apa/Alasan/TODO) tapi narasi opsional.

### 3.6 [SEDANG] Prompt caching belum dipakai (§9.8)

Smoke test: 3.4 rb token input per panggilan, 18 panggilan untuk 12 baris input. Definisi tool + system prompt + riwayat mendominasi.

**Struktur yang disarankan:**

```
[tools stabil]  ← cache_control breakpoint 1
[system prompt stabil]  ← cache_control breakpoint 2
[profile block semi-stabil]  ← cache_control breakpoint 3 (opsional)
[riwayat dinamis]
```

**Catatan:** `find_tools` yang mengubah daftar tool di tengah turn memecah prefix cache. Untuk katalog kecil (<20 tool), pertimbangkan **inject semua tool sekaligus** — lebih mahal per panggilan tapi cache-friendly dan menghilangkan 1 iterasi `find_tools`. Ukur kedua pendekatan.

### 3.7 [SEDANG] `max_iterations = 6` terlalu kecil

`find_tools` memakan 1 iterasi; tugas device multi-langkah bisa mentok. Naikkan ke 10, atau **ganti ke budget token/biaya** (lebih masuk akal untuk agen — Anda sudah punya `usage.input_tokens`).

### 3.8 [SEDANG] Tiga store terpisah tanpa transaksi bersama

S5 gap masih terbuka: sesi gagal disimpan setelah lampu menyala = jejak hilang. Saran jangka menengah: **satu SQLite dengan transaksi per turn** — menyelesaikan S5, urutan tulis, dan jadi fondasi concurrent access saat suara + CLI + proaktif berjalan bersamaan nanti.

**Migrasi bertahap:** wrapper yang membungkus ketiga store dalam satu transaksi dulu (sesi + profil + arsip + log aksi), tanpa mengubah skema file JSON.

---

## 4. Jawaban untuk §10 (Prioritas)

Tabel ringkas:

| # | Pertanyaan | Rekomendasi |
|---|---|---|
| 1 | M11 & M16 dimajukan? | **Ya.** Minimal M11: konfirmasi `CRITICAL` + allowlist provider. Minimal M16: 10–20 skenario SAGE-style + metrik terpisah. |
| 2 | Tiga store vs satu SQLite? | **Satu SQLite** dengan transaksi per turn. Migrasi bertahap: wrapper yang membungkus ketiga store dalam satu transaksi dulu. |
| 3 | Portabilitas model lokal | **Definisikan format `Message` netral sekarang**, adapter ke Anthropic. Realistis: model open-weight bisa tool calling, tapi `find_tools` + dynamic loading lebih sulit untuk model kecil — siapkan fallback "inject semua tool". |
| 4 | Retrieval bahasa Indonesia | **FTS5 + prefix `*`** dulu (murah). Ukur. Kalau kurang, stemmer Sastrawi sederhana. Embedding lokal kecil opsi terakhir. |
| 5 | Memori vs Mem0/Zep/MemGPT | Pemisahan sudah tepat. Yang kurang: temporal validity, forgetting/decay, konsolidasi background — **sengaja ditunda, dan itu keputusan yang benar** untuk sekarang. |
| 6 | Keamanan aksi fisik | **Lease model HearthNet** + konfirmasi `CRITICAL` + allowlist per provider + time-bound permission. Prompt injection: trust marker di hasil `recall_memory`. |
| 7 | Antarmuka device generik | `list_devices()`, `read_state(id)`, `apply(id, changes)` dengan **desired vs reported** split. Tool per aksi + generic `apply` sebagai fallback. State `pending` untuk device lambat. |
| 8 | Evaluasi tanpa hardware | **SAGE-style**: initial state + command + check final state. Sasha 7 failure modes. Metrik: task completion, **tool correctness (terpisah!)**, steps, latency, cost. |
| 9 | Biaya | **Prompt caching** (tools + system stable prefix). Haiku untuk dev, Sonnet untuk task kompleks. Batasi profile block, kompres tool result. |
| 10 | Proses | Riset dulu + plan mode + log append-only **bagus**. Tapi: pindah tracking ke issue tracker, atau ringkas log. Tambah **replay system** untuk regression. |
| 11 | Bug/celah | Lihat §3 dan §5 — paling kritis: bug kompaksi, `except Exception` terlalu lebar di `_persist`, deteksi "turn interrupted" fragile, mock home reset tiap CLI run, profile tidak dibatasi ukurannya. |

### Q1 — Urutan roadmap

**Ya, majukan M11 dan M16.**

- **M11 minimal sekarang:** konfirmasi `CRITICAL` + allowlist provider untuk `AutoLoadPolicy`. Tidak perlu full M11.
- **M16 minimal sekarang:** 10–20 skenario SAGE-style + metrik terpisah (task completion vs tool correctness). Ini akan menangkap regresi saat refactor antarmuka device nanti.
- **M16 penuh** tetap bisa di Sprint 12.

### Q2 — Arsitektur penyimpanan

**Satu SQLite dengan transaksi per turn.** Ini menyelesaikan:
- S5 gap (jejak aksi hilang)
- Urutan tulis profil → sesi → arsip
- Concurrent access saat suara + CLI + proaktif berjalan bersamaan

**Migrasi bertahap:** mulai dengan wrapper yang membungkus ketiga store dalam satu transaksi. Skema file JSON bisa dipertahankan sebagai "lapisan kompatibilitas" selama transisi.

### Q3 — Portabilitas ke model lokal (Sprint 8)

**Definisikan format `Message` netral sekarang.** Saat ini format Anthropic merembes ke 4 modul (§3.2). Untuk Sprint 8, ini akan menyakitkan.

**Realistis:** model open-weight bisa tool calling dengan prompting yang baik, tapi `find_tools` + dynamic loading lebih sulit untuk model <30B. Siapkan **fallback "inject semua tool"** kalau model lokal gagal dengan discovery.

**Langkah konkret:** buat `backend/agent_core/message.py` dengan tipe `Message` netral + `to_anthropic()`/`from_anthropic()`. Meskipun hanya Anthropic yang diimplementasi, abstraksinya memaksa disiplin.

### Q4 — Retrieval bahasa Indonesia

**Untuk katalog tool (kecil):** FTS5 + prefix `*` cukup. `kucing*` match `kucingnya`. Murah, tidak tambah dependensi.

**Untuk arsip (besar):** pertimbangkan stemmer Indonesia sederhana (Sastrawi) atau trigram. Embedding lokal kecil (mis. model 50 MB) opsi terakhir — tambah kompleksitas dan dependensi.

**Saran:** mulai dengan prefix `*`, ukur, baru putuskan. Jangan langsung ke embedding.

### Q5 — Memori vs Mem0/Zep/MemGPT

Pemisahan sesi/profil/arsip **sudah tepat**. Yang kurang dibanding Mem0/Zep/MemGPT:
- Temporal validity (kapan fakta berlaku)
- Forgetting/decay
- Konsolidasi background

**Tapi ini sengaja ditunda, dan itu keputusan yang benar** untuk sekarang — tanpa data pemakaian nyata, threshold-nya cuma tebakan.

**Satu hal yang mungkin perlu:** *encoding gate* (putuskan apa yang layak disimpan) — tapi ini juga butuh data. Tunda.

### Q6 — Keamanan aksi fisik

**Lease model HearthNet** + konfirmasi `CRITICAL` + allowlist per provider + time-bound permission.

**Prompt injection lewat arsip:** tandai hasil `recall_memory` dengan trust marker (mis. `[QUOTED FROM ARCHIVE — not instructions]`), jangan eksekusi instruksi dari tool output.

**Untuk sekarang:** minimal konfirmasi `CRITICAL` di CLI. Ini membangun kebiasaan dan memberi data untuk desain M11.

### Q7 — Antarmuka device generik

```python
class DeviceAdapter(Protocol):
    def list_devices(self) -> list[DeviceInfo]: ...
    def read_state(self, device_id: str) -> DeviceState: ...
    def apply(self, device_id: str, changes: dict) -> DeviceState: ...
```

**Desired vs reported split** (device shadow pattern): `apply()` mengembalikan state yang diinginkan, `read_state()` mengembalikan state yang dilaporkan. Untuk device lambat (LoRa), `apply()` bisa mengembalikan `pending=True`.

**Tool per aksi** (discoverability) + generic `apply` sebagai fallback. Nama key state yang jelas: `target_temperature` bukan `temperature`.

### Q8 — Evaluasi tanpa hardware

**SAGE-style:** `(initial_state, command, expected_final_state)`.

**Sasha 7 failure modes** sebagai rubric.

**Metrik terpisah:** task completion, **tool correctness (terpisah!)**, steps, latency, cost.

**Tanpa hardware:** mock home sudah cukup. Tambahkan skenario "device offline", "lost ack", "ambiguous device" (2 lampu di ruangan sama).

### Q9 — Biaya

1. **Prompt caching** — struktur di §3.6.
2. **Model selection** — Haiku untuk dev, Sonnet untuk task kompleks. Jangan pakai Opus untuk development.
3. **Context size** — batasi profile block (top-N by recency/importance), kompres tool result sebelum masuk konteks.

### Q10 — Proses

**Yang bagus:** riset dulu, plan mode, log append-only. Ini menghasilkan keputusan yang well-informed.

**Yang perlu dipangkas:** overhead dokumentasi (§3.5). Pindah tracking ke issue tracker, atau ringkas log.

**Yang perlu ditambah:** **replay system** untuk regression test. Rekam respons LLM (input + output), replay untuk regression. Ini menutup gap "test semua memakai LLM palsu" tanpa biaya API berulang.

### Q11 — Bug/celah tambahan

Lihat §3 dan §5. Yang paling kritis:
- Bug kompaksi (§3.1)
- `except Exception` terlalu lebar di `_persist` — `KeyboardInterrupt` (Ctrl+C) tidak menyimpan turn parsial
- Deteksi "turn interrupted" bergantung invarian pesan (fragile — mutation test membuktikan)
- Mock home reset tiap CLI run (membingungkan — meskipun disengaja)
- Profile tidak dibatasi ukurannya (biaya + lost-in-the-middle naik seiring fakta)
- Text correction notes fragile — pertimbangkan `Session.metadata: dict` terstruktur

---

## 5. Masukan per Kode (§9.1–§9.10)

### §9.1 — Loop agent dan eksekusi tool

**Masalah:**
- Tidak ada titik untuk izin (M11) di antara validasi dan eksekusi.
- Hasil tool di-`json.dumps` utuh tanpa batas ukuran.
- Pesan exception tool dikirim verbatim ke LLM (bisa bocorkan detail internal).
- Beberapa `tool_use` dalam satu respons dijalankan berurutan tanpa memperhatikan ketergantungan.

**Saran:**
- **Gerbang izin** di `_execute_tool_call` sebelum `registered.fn(**call.arguments)`:

  ```python
  if registered.contract.permission_tier == PermissionTier.CRITICAL:
      if not permission_gate.request(call.name, call.arguments):
          return "Action denied by user.", True
  ```

- **Batas ukuran hasil tool** — potong di N KB, tambahkan `... (truncated)`.
- **Sanitasi exception** — jangan kirim `str(exc)` mentah; kirim tipe + pesan yang sudah di-filter.
- **`max_iterations` berbasis budget** — ganti ke `max_tokens_budget` atau `max_cost_budget`.

### §9.2 — Orchestrator dan urutan tulis

**Masalah:**
- Tiga store terpisah tanpa transaksi bersama.
- Deteksi "turn terputus" bergantung invarian pesan.
- Penanda/koreksi ditempel sebagai teks ke pesan assistant — model membacanya sebagai ucapannya sendiri.
- `except Exception` lebar; `KeyboardInterrupt` tidak menyimpan turn parsial.

**Saran:**
- **Satu SQLite dengan transaksi per turn** (§3.8).
- **Structured metadata** di `SessionRecord`:

  ```python
  class SessionRecord(BaseModel):
      ...
      events: list[SessionEvent] = []  # interrupted, profile_save_failed, archive_failed
  ```

  Ini lebih baik daripada text notes yang bisa disalahartikan model.

- **Tangkap `KeyboardInterrupt`** secara eksplisit dan simpan turn parsial sebelum re-raise.

### §9.3 — Kompaksi

Lihat §3.1. **Bug kritis.**

**Keraguan lain:**
- Ringkasan dibuat oleh model yang sama (Haiku) tanpa verifikasi. **Saran murah:** cek apakah ringkasan mengandung named entity yang tidak ada di `to_summarize` (false positive check). Tidak sempurna, tapi menangkap halusinasi kasar.
- `_find_safe_cut_index` hanya memotong di pesan user berupa teks — satu rantai tool yang panjang tidak pernah bisa dikompaksi. **Saran:** izinkan potong di `tool_result` terakhir dari satu rantai, asalkan tidak memutus pasangan `tool_use`/`tool_result`.

### §9.4 — Blok profil di system prompt

**Masalah:**
- Tidak ada batas jumlah fakta.
- Tidak ada urutan prioritas.
- Instruksi tidak menjelaskan bahwa profil adalah sumber utama (temuan smoke test: model malah `recall_memory`).
- System prompt berubah setiap fakta berubah (mengganggu prompt caching).

**Saran:**
- **Batasi top-N** (mis. 50 fakta terbaru/terpenting). Selebihnya via retrieval.
- **Instruksi eksplisit:**

  ```
  The block above is the PRIMARY source of facts about the user.
  Use recall_memory ONLY for old conversations not covered by this block.
  ```

- **Pisahkan cache:** taruh blok profil **setelah** system prompt stabil, sebagai `cache_control` breakpoint terpisah.

### §9.5 — Tokenizer pencarian

**Untuk katalog tool (kecil):** prefix `*` cukup.

**Untuk arsip (besar):** stemmer Sastrawi atau trigram. Ukur dulu.

**Catatan:** `unicode61` tidak menangani imbuhan Indonesia. `kucing` ≠ `kucingnya`. Prefix `*` adalah perbaikan termurah.

### §9.6 — Auto-load tool katalog

**Masalah:** keputusan keamanan bergantung pada `read_only_hint` yang dideklarasikan penyedia tool sendiri.

**Saran:**
- **Allowlist per provider** — tentukan di config provider mana yang boleh auto-load.
- **Jangan percaya `read_only_hint`** untuk aktuator. Kalau `permission_tier != READ_ONLY`, jangan auto-load meskipun `read_only_hint=True`.
- **Gerbang `find_tools`** memberi nilai nyata (model melihat deskripsi + tier), tapi bukan pengganti izin. Izin tetap di M11.

### §9.7 — Retensi tool lintas turn

**Masalah:** logika bergantung pada bentuk pesan Anthropic; hanya membaca `session.messages`, jadi turn yang sudah dikompaksi tidak dihitung; tool yang gagal karena offline tidak dipertahankan.

**Saran:**
- **State eksplisit** di sesi: `session.active_tools: list[str]`. Lebih tahan terhadap kompaksi dan perubahan format pesan.
- **Pertahankan tool yang gagal karena offline** — model perlu tahu tool itu ada saat device kembali online.

### §9.8 — Prompt caching

Lihat §3.6.

**Struktur yang disarankan:**

```
[tools stabil]           ← cache_control
[system prompt stabil]   ← cache_control
[profile block]          ← cache_control (opsional)
[riwayat dinamis]
```

**Catatan:** `find_tools` memecah prefix cache. Untuk katalog kecil, inject semua tool lebih cache-friendly.

### §9.9 — Adapter device dan read-back

**Masalah:**
- Read-back langsung setelah error tidak cocok untuk device lambat (LoRa kelas A).
- Perbandingan `==` tidak cocok untuk nilai analog.
- Key `temperature` ambigu.
- Pola ini ada di mock, belum di antarmuka generik.

**Saran:**
- **Desired vs reported split** (device shadow pattern).
- **State `pending`** untuk device lambat — perintah tertunda bukan gagal.
- **Toleransi perbandingan** untuk nilai analog (mis. `abs(a - b) < 0.5`).
- **Nama key yang jelas:** `target_temperature`, `current_temperature`, `brightness_pct`.
- **Antarmuka generik** (§Q7) yang wajib diikuti adapter nyata.

### §9.10 — Waktu

**Saran:** timezone di **config** (`.env`, mis. `TIMEZONE=Asia/Jakarta`), bukan profil. Profil untuk fakta tentang user; timezone adalah setting.

`get_current_time()` mengembalikan waktu lokal + offset + nama zona.

---

## 6. Saran Proses

### 6.1 Yang harus dipertahankan
- Riset paper dulu sebelum desain.
- Plan mode sebelum implementasi.
- Log append-only.
- Test dengan `FakeLLMClient` + smoke test manual.
- Karakterisasi test untuk perilaku yang tidak diinginkan.

### 6.2 Yang perlu dipangkas
- **Overhead dokumentasi** (§3.5). Pindah tracking ke issue tracker, atau ringkas log.
- **Paper notes** — 190 KB untuk 130 paper. Pertimbangkan ringkasan 1 paragraf per paper + link, bukan catatan detail.

### 6.3 Yang perlu ditambah
- **Replay system** untuk regression test — rekam respons LLM, replay untuk regression. Menutup gap "test semua memakai LLM palsu" tanpa biaya API berulang.
- **Observability** — log terstruktur (JSON) dengan cost/latency per turn. Murah, akan sangat membantu debugging.
- **CI** — GitHub Actions untuk menjalankan test otomatis di setiap push. Ini akan menangkap regresi lebih awal.

### 6.4 Timeboxing
Sprint 3 punya jeda 5 minggu. **Timebox per sprint** (mis. 2 minggu) dengan "definition of done" yang jelas akan membantu momentum.

---

## 7. Prioritas Tindakan (Urutan yang Disarankan)

### Segera (sebelum M5 adapter nyata)
1. **Fix bug kompaksi** (§3.1) — kritis, melanggar prinsip "fail loud".
2. **Konfirmasi `CRITICAL`** di CLI — minimal prompt "yakin? (y/n)".
3. **Allowlist per provider** untuk `AutoLoadPolicy`.
4. **Naikkan `max_iterations`** ke 10 atau ganti ke budget token.
5. **Timezone lokal** di `get_current_time`.

### Jangka pendek (1–2 sprint)
6. **Minimal evaluation harness** — 10–20 skenario SAGE-style + metrik terpisah.
7. **Prompt caching** — struktur stable prefix.
8. **Antarmuka device generik** + kontrak Device + nama key yang jelas.
9. **Instruksi profil** — "fakta profil = sumber utama; recall untuk percakapan lama".

### Jangka menengah (2–4 sprint)
10. **Definisikan format `Message` netral** — adapter ke Anthropic.
11. **Satu SQLite dengan transaksi per turn** — S5, urutan tulis, concurrent access.
12. **State `pending`** di mock + disambiguasi/bertanya balik.
13. **Observability** — log terstruktur + CI.
14. **Replay system** untuk regression test.

### Jangka panjang (Sprint 8+)
15. **Fallback "inject semua tool"** untuk model lokal yang gagal dengan discovery.
16. **Pindah ke satu SQLite** penuh.
17. **Evaluasi penuh** (M16) dengan benchmark yang lebih luas.

---

## 8. Catatan Tambahan

Beberapa hal yang tidak masuk ke bagian utama tapi relevan:

1. **Soal "A3"** — di log Sprint 2, user menyebut "A1, A2 dan A3" tapi opsi yang ditawarkan asisten cuma A1/A2/Sprint 3. Mungkin maksudnya "A1, A2, dan B/C" atau "A1, A2, dan Sprint 3". Tidak kritis, tapi bisa diklarifikasi di log berikutnya.

2. **Soal sesi 2026-09-11 yang hilang** — ini contoh nyata kenapa proses dokumentasi perlu diperkuat. Replay system atau issue tracker akan membantu mencegah ini.

3. **Soal mock home reset tiap CLI run** — ini disengaja sebagai uji "jangan percaya riwayat", tapi untuk pengguna baru (atau Anda sendiri setelah lama tidak pakai) ini membingungkan. Pertimbangkan flag `--persist-home` untuk menyimpan state mock ke file, atau tampilkan pesan jelas saat startup: "Rumah simulasi dimulai dari keadaan mati."

4. **Soal "provider-agnostic"** — saya sarankan untuk **tidak** mengklaim provider-agnostic sampai abstraksi `Message` netral benar-benar ada. Klaim yang jujur: "Anthropic-first, dengan rencana abstraksi di Sprint 8."

---

## 9. Penutup

Proyek ini punya fondasi yang kuat: prinsip yang jelas, test yang disiplin, dan dokumentasi keputusan yang rapi. Risiko terbesarnya bukan teknis — tapi **kombinasi provider lock-in + urutan roadmap + overhead dokumentasi** yang kalau tidak ditangani sekarang akan makin mahal nanti.

Tiga hal yang paling mendesak:
1. **Fix bug kompaksi** — melanggar prinsip yang Anda pegang sendiri.
2. **Konfirmasi `CRITICAL` + allowlist provider** — sebelum device nyata.
3. **Minimal evaluation harness** — sebelum refactor besar.

Sisanya bisa bertahap. Anda sudah punya disiplin dan dokumentasi yang cukup untuk mengeksekusi perbaikan ini dengan baik.

---

*Feedback ini fokus ke kritik konkret. Kalau ada keputusan yang saya salah pahami atau konteks yang terlewat, silakan dibantah — itu justru membantu.*