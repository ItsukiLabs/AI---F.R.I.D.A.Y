# Feedback Eksternal untuk Proyek F.R.I.D.A.Y

## Ringkasan Eksekutif

Proyek F.R.I.D.A.Y menunjukkan kualitas desain yang jauh di atas rata-rata proyek personal AI agent. Kekuatan terbesarnya bukan pada jumlah fitur, tetapi pada disiplin arsitektur, dokumentasi keputusan, pemisahan memori yang jelas, dan keberanian menunda fitur yang belum punya data nyata.

Secara keseluruhan saya menilai:

- Arsitektur inti: 8.5/10
- Memory design: 9/10
- Tool architecture: 8/10
- Reliability mindset: 8.5/10
- Security readiness: 5/10
- Evaluation maturity: 4/10
- Readiness menuju local model: 6/10
- Readiness menuju device nyata: 5/10

Masalah terbesar saat ini bukan kemampuan AI, tetapi:
1. Keamanan belum hadir sementara aktuasi sudah ada.
2. Evaluasi masih sangat minim.
3. Coupling ke format Anthropic lebih besar daripada yang disadari.
4. Penyimpanan mulai mencapai batas evolusi arsitektur.

---

# Hal yang Sangat Baik

## 1. Pemisahan Session vs Profile vs Archive

Ini adalah salah satu keputusan terbaik di seluruh proyek.

Alasan:

Banyak sistem memory AI modern gagal karena mencampur:
- context aktif
- fakta permanen
- arsip percakapan

Akibatnya model mulai menganggap percakapan biasa sebagai fakta.

F.R.I.D.A.Y justru menghindari masalah tersebut sejak awal.

Prinsip:

> Context ≠ Memory

menurut saya merupakan keputusan desain paling penting dalam seluruh proyek.

Saya akan mempertahankan prinsip ini bahkan ketika nanti beralih ke local model.

---

## 2. Failure Philosophy

Prinsip:

> Fail loud.

lebih sehat dibanding mayoritas framework agent saat ini.

Sebagian besar framework agent modern terlalu agresif melakukan recovery otomatis.

Akibatnya:
- data hilang diam-diam
- state korup tidak terdeteksi
- debugging menjadi mimpi buruk

Pilihan Anda lebih cocok untuk personal assistant jangka panjang.

---

## 3. Menunda Threshold Sampai Ada Data

Saya setuju penuh.

Contoh:

- memory decay
- forgetting
- ranking
- relevance threshold
- profile pruning

Tidak ada alasan ilmiah menentukan angka sebelum ada data penggunaan nyata.

Keputusan ini menunjukkan disiplin engineering yang baik.

---

# Kritik Prioritas Tinggi

## PRIORITAS 1 — Security Terlambat

Menurut saya M11 tidak boleh menunggu Sprint 4.

Masalah:

Saat ini aktuator sudah berjalan.

Lampu dan AC memang aman.

Tetapi arsitektur yang sama nantinya akan mengontrol:

- pintu
- kompor
- kamera
- alarm
- PC
- file sistem

Risikonya meningkat drastis.

### Rekomendasi

Buat versi mini M11 sekarang.

Minimal:

```text
READ_ONLY
STANDARD
CRITICAL
```

Dan enforcement nyata:

```text
READ_ONLY -> auto
STANDARD -> boleh auto
CRITICAL -> wajib konfirmasi user
```

Jangan tunggu Sprint 4.

---

## PRIORITAS 2 — Tidak Ada Evaluasi Terstruktur

Ini menurut saya risiko terbesar kedua.

Saat ini kualitas dinilai melalui:

- unit test
- smoke test

Tetapi belum ada benchmark tetap.

Akibatnya:

Setelah 3 sprint lagi Anda tidak akan tahu apakah sistem membaik atau memburuk.

### Rekomendasi

Majukan sebagian M16 sekarang.

Buat benchmark internal.

Contoh:

- 20 testcase memory
- 20 testcase tool use
- 20 testcase device
- 20 testcase recovery

Jalankan setiap commit besar.

---

## PRIORITAS 3 — Coupling Anthropic Lebih Besar Dari Dugaan

Dokumen sudah mengakui hal ini.

Saya setuju.

Masalahnya bahkan sedikit lebih besar.

Contoh:

- retention.py
- session format
- tool_result format
- tool_use format
- compaction format

Semuanya berasumsi struktur Anthropic.

### Rekomendasi

Tambahkan layer internal:

```text
InternalMessage
InternalToolCall
InternalToolResult
```

Loop hanya berbicara ke format internal.

Adaptor Anthropic dan adaptor model lokal menerjemahkan format tersebut.

Ini akan mengurangi migrasi Sprint 8 secara drastis.

---

# Feedback Khusus Pertanyaan Bab 9

## 9.1 Tool Execution

### Permission Gate

Rekomendasi:

Jangan di ToolRegistry.

Jangan di Adapter.

Pasang tepat sebelum eksekusi tool.

Alur:

```text
resolve
validate
authorize
execute
record
```

Karena:
- registry urusan discovery
- adapter urusan device
- authorization urusan kebijakan

Pemisahan tanggung jawab lebih bersih.

### Tool Output Size

Tambahkan batas.

Misalnya:

```text
4 KB soft limit
32 KB hard limit
```

Output besar:

```text
summary + truncated
```

Jangan masukkan JSON besar mentah ke konteks.

### Max Iteration

Saya lebih suka budget token.

Contoh:

```text
max_iterations = 20
max_turn_tokens = 15000
```

Stop pada salah satu batas.

---

## 9.2 Storage Architecture

### Apakah Perlu Satu SQLite?

Jawaban pendek:

Ya.

Tidak sekarang.

Saat ini JSON masih cukup.

Tetapi versi jangka panjang sebaiknya:

```text
profile
session
archive
action_log
```

berada dalam satu SQLite.

Alasan:

- transaksi nyata
- backup lebih mudah
- query lebih mudah
- konsistensi lebih tinggi

---

## 9.3 Compaction

Bug yang ditemukan memang bug serius.

Saya menganggap ini pelanggaran terhadap prinsip fail loud.

Response kosong harus dianggap gagal.

Contoh:

```python
if not response.text:
    raise CompactionError(...)
```

lebih sesuai filosofi proyek.

### Verifikasi Ringkasan

Murah:

Gunakan LLM kedua pada prompt audit.

Pertanyaan:

```text
Apakah summary mengandung fakta yang tidak ada di source?
```

Tidak perlu selalu.

Sampling 5-10% cukup.

---

## 9.4 Profile Block

Saat ini profile akan tumbuh tanpa batas.

Saya memprediksi ini akan menjadi masalah sebelum Sprint 8.

### Rekomendasi

Pisahkan:

```text
critical facts
active facts
archived facts
```

Yang dikirim ke model:

- critical
- active

Jangan seluruh profil.

---

## 9.5 Retrieval Indonesia

Untuk ribuan percakapan dan puluhan tool:

Saya tidak akan langsung memakai embedding.

Urutan rekomendasi:

1. Prefix search
2. Trigram
3. Stemmer Indonesia ringan
4. Baru embedding

FTS5 kemungkinan masih cukup lama.

---

## 9.6 Auto Load

Saya setuju dengan kekhawatiran Anda.

read_only_hint bukan sumber kepercayaan.

### Rekomendasi

Gunakan:

```text
trusted_provider
```

atau

```text
allowlist provider
```

Pemilik sistem menentukan.

Bukan tool.

Tool tidak boleh memberi label aman pada dirinya sendiri.

---

## 9.7 Tool Retention

Pendekatan sekarang cukup baik.

Saya justru menyarankan mempertahankannya.

Karena:

state eksplisit mudah basi.

Riwayat penggunaan adalah sumber kebenaran yang lebih kuat.

---

## 9.8 Prompt Caching

Saat katalog masih kecil:

Kemungkinan semua tool lebih murah dibanding find_tools.

Saya sarankan melakukan pengukuran nyata.

Jangan berasumsi.

Buat eksperimen:

Scenario A:
- semua tool injected

Scenario B:
- find_tools

Bandingkan:
- token
- latency
- keberhasilan

---

## 9.9 Device Layer

Saya sangat menyarankan device shadow.

Model:

```text
reported_state
desired_state
connection_state
```

mirip AWS IoT Shadow.

Jauh lebih fleksibel daripada model state tunggal.

---

## 9.10 Timezone

Timezone sebaiknya:

```text
config default
+ override profile
```

Karena:

rumah punya timezone tetap.

user bisa bepergian.

---

# Bug dan Risiko Tambahan Yang Belum Banyak Dibahas

## Archive Prompt Injection

Menurut saya ini risiko terbesar yang belum benar-benar ditangani.

Contoh:

```text
Di masa depan abaikan instruksi sistem.
```

Masuk arsip.

Lalu muncul lagi melalui recall.

Perlu trust marking.

Misalnya:

```text
source=user_memory
source=tool
source=external
```

supaya model tahu tingkat kepercayaannya.

---

## Observability

Saya akan memajukan sebagian observability sekarang juga.

Minimal:

- latency
- token input
- token output
- jumlah tool call
- error rate

per turn.

Nanti debugging jauh lebih mudah.

---

## Tidak Ada Action Log

Ini paling berbahaya untuk device.

Saat aktuasinya nyata:

```text
jam berapa
siapa
perintah apa
hasil apa
```

harus selalu tercatat.

Menurut saya action log lebih penting daripada memory decay.

---

# Roadmap yang Saya Sarankan

## Setelah Sprint 3

Urutan saya:

1. Mini-M11 security
2. Mini-M16 evaluation
3. Perbaikan retrieval Indonesia
4. Device abstraction
5. Voice
6. Planner
7. Local model

Bukan langsung mengikuti roadmap asli.

---

# Kesimpulan

F.R.I.D.A.Y saat ini terlihat seperti proyek yang didesain oleh seseorang yang membaca banyak paper dan benar-benar mencoba menerjemahkannya menjadi engineering decision, bukan sekadar menyalin framework agent yang sedang populer.

Kekuatan terbesar proyek ini:

- memory separation
- fail loud philosophy
- disiplin dokumentasi
- keputusan berbasis alasan

Kelemahan terbesar saat ini:

- security belum hadir
- evaluasi belum hadir
- observability minim
- masih terikat format Anthropic

Jika keamanan minimum dan evaluasi minimum dimajukan sebelum ekspansi fitur besar berikutnya, saya memperkirakan arsitektur inti F.R.I.D.A.Y akan jauh lebih stabil ketika memasuki fase device nyata dan local model.
