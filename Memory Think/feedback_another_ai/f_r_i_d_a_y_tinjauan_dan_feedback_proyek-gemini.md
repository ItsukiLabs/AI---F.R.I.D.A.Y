# F.R.I.D.A.Y — Feedback Eksternal & Tinjauan Arsitektur

**Evaluator:** AI Assistant (Senior Technical Reviewer)
**Tanggal:** 2026-10-25
**Konteks Tinjauan:** Dokumen Tinjauan Proyek F.R.I.D.A.Y (commit `94c24b2`)

---

## 1. Penilaian Umum
Tingkat rekayasa perangkat lunak (*software engineering*) dalam proyek ini berada di level **Outstanding**. Keputusan Anda untuk tidak menggunakan abstraksi *langchain/llamaindex* yang berlebihan dan memilih implementasi transparan berbasis *jsonschema* dan iterasi *native* sangat tepat untuk proyek dengan fokus keandalan jangka panjang. 

Namun, ada tiga area pertumbuhan utama yang perlu segera Anda mitigasi sebelum melangkah lebih jauh ke perangkat keras (*hardware*): **Konsistensi Penyimpanan, Keamanan Aksi Fisik, dan Pencarian Bahasa Indonesia.**

---

## 2. Feedback Utama & Jawaban Pertanyaan Evaluasi

### A. Arsitektur Penyimpanan & Konsistensi (Menjawab Q2 & Potongan Kode 9.2)
*   **Diagnosa:** Celah S5 (sesi gagal disimpan setelah perangkat bergerak) adalah gejala dari *distributed monolith*. Menggunakan 2 file JSON dan 1 SQLite memaksa Anda membangun mekanisme *rollback* dan catatan koreksi tekstual di memori LLM, yang sangat rapuh.
*   **Analisis Kode (9.2):** Penanganan `except Exception` yang lebar dan mencoba menyimpan profil/sesi berulang kali saat terjadi kegagalan adalah *code smell* bahwa sistem penyimpanan Anda tidak memiliki sifat ACID.
*   **Langkah Selanjutnya:** Tidakkah lebih aman jika Anda memindahkan Profil dan Sesi ke dalam SQLite yang sama dengan Arsip? 
    *   Dengan menggunakan satu database SQLite, Anda bisa memanfaatkan `BEGIN TRANSACTION`. Jika aksi ke perangkat berhasil, tetapi penulisan log sesi gagal, keseluruhan transaksi *database* bisa digagalkan, memastikan konsistensi antara state memori dan log aksi. Anda tidak perlu lagi melakukan "catatan koreksi di dalam teks".

### B. Keamanan Aksi Fisik & Penjadwalan M11 (Menjawab Q1, Q6, & Potongan Kode 9.1, 9.6)
*   **Diagnosa:** Mengizinkan LLM mengeksekusi aktuator fisik (`STANDARD`) tanpa gerbang keamanan, bahkan untuk AC/lampu, adalah risiko besar (*red flag*). Keamanan (M11) tidak boleh datang setelah perangkat pintar terhubung (M5).
*   **Analisis Kode (9.1 & 9.6):** Di `_execute_tool_call`, alat langsung dieksekusi setelah validasi skema. Mengandalkan `read_only_hint` (9.6) dari penyedia *tool* untuk izin otomatis adalah celah otorisasi (CWE-862). Penyedia *tool* tidak boleh mendeklarasikan keamanannya sendiri.
*   **Langkah Selanjutnya:** Majukan M11 (versi MVP) ke Sprint 3. Bisakah Anda menambahkan mekanisme interupsi sederhana di `_execute_tool_call`?
    *   Misalnya: Jika `tool.permission_tier == STANDARD | CRITICAL`, lemparkan `ToolRequiresConfirmationError`. Interupsi iterasi LLM, kembalikan kontrol ke CLI, minta user mengetik `y/n`, lalu masukkan hasilnya sebagai *Tool Result* ke iterasi berikutnya. Ini akan melindungi Anda dari *prompt injection* yang tidak disengaja lewat Arsip (M2b).

### C. Retrival Bahasa Indonesia (Menjawab Q4 & Potongan Kode 9.5)
*   **Diagnosa:** Pencarian *keyword* (FTS5 BM25) murni akan sangat membatasi kemampuan *recall* F.R.I.D.A.Y karena morfologi bahasa Indonesia (imbuhan "me-", "di-", "-nya", "-kan") yang kaya.
*   **Analisis Kode (9.5):** Membuang diakritik (`unicode61`) tidak menyelesaikan masalah *stemming* bahasa Indonesia. 
*   **Langkah Selanjutnya:** Untuk ukuran data personal (skala MB), SQLite sudah memiliki ekstensi eksternal seperti `sqlite-vec`. Tidakkah lebih efisien menggunakan model *embedding* lokal kecil yang *multilingual* (seperti `paraphrase-multilingual-MiniLM-L12-v2` via `sentence-transformers`) daripada repot membangun *stemmer* bahasa Indonesia (seperti Sastrawi) di FTS5?
    *   Jika Anda tetap ingin menggunakan FTS5 untuk kesederhanaan, tokenizer `trigram` adalah pilihan *fallback* yang jauh lebih baik daripada BM25 mentah untuk mengakomodasi imbuhan, meski akan sedikit bising (*noisy*).

### D. Optimasi Biaya & Prompt Caching (Menjawab Q9 & Potongan Kode 9.8)
*   **Diagnosa:** ±3,4 ribu token per panggilan tanpa *caching* akan menghabiskan anggaran $5 Anda dengan cepat, terutama dengan batas 6 iterasi per turn.
*   **Analisis:** Mekanisme `find_tools` yang memuat *tool* secara dinamis di tengah *turn* justru merusak *prompt cache*. Cache pada Anthropic bekerja pada awalan (*prefix*) statis.
*   **Langkah Selanjutnya:** Bagaimana jika Anda menyusun struktur prompt menjadi: `[1. Semua Tool Registry, 2. System Prompt, 3. Profile Block, 4. History]`? 
    *   Selama *Tool Registry* statis, blok 1, 2, dan 3 dapat di-*cache* (dengan parameter `cache_control` Anthropic). Paradoksnya, memberikan 100 *tool* sekaligus dengan *caching* justru bisa jauh lebih murah (dan tidak membuang 1 iterasi *find_tools*) dibandingkan memberikan 5 *tool* yang berubah-ubah secara dinamis setiap turn.

---

## 3. Ulasan Spesifik pada Potongan Kode Lainnya

*   **Kode 9.3 (Kompaksi):** 
    *   *Bug:* Jika `response.text` kosong, Anda kehilangan konteks.
    *   *Saran:* Terapkan *Fail Loud*. Jika LLM merespons kosong atau *rate limited*, batalkan kompaksi (kembalikan `False` atau lempar `CompactionError`). Jangan menghapus `session.messages` sebelum `session.summary` divalidasi tidak kosong atau rusak.
*   **Kode 9.4 (Profil di System Prompt):**
    *   *Saran:* Profil memang berisiko membuat LLM bingung antara *fakta tetap* (Profil) dan *kejadian historis* (Arsip). Perbarui instruksinya menjadi: *"This profile represents absolute facts. Use these facts directly. Do not use tools to recall memory if the answer is already here."*
*   **Kode 9.7 (Retensi Tool):**
    *   *Saran:* Membaca riwayat mentah (Anthropic message block) sangat rentan rusak saat migrasi ke model lokal. Lebih baik jika state retensi *tool* disimpan secara terstruktur (misal: di tabel SQLite tersendiri untuk *Tool Usage History*), alih-alih diurai dari `session.messages`.
*   **Kode 9.10 (Waktu UTC):**
    *   *Saran:* Zona waktu sebaiknya diletakkan di **Fakta Profil**, bukan config statis. Mengapa? Jika Anda bepergian dan meminta F.R.I.D.A.Y menyalakan alarm atau AC, Anda ingin dia memahami zona waktu fisik Anda saat itu, yang bisa Anda perbarui lewat percakapan ("Saya sedang di Bali sekarang").

---

## 4. Proses & Evaluasi (Menjawab Q8 & Q10)
Proses kerja Anda (Riset -> Plan -> Implementasi -> Log -> Test) sangat bagus untuk mencegah *technical debt*. Namun, satu area yang bisa ditingkatkan adalah **Metrik Evaluasi Otomatis (M16)**.
Daripada menunda ke Sprint 12, buatlah 1 skrip tes sederhana (menggunakan model *haiku* yang lain sebagai *judge*) untuk menilai *tool correctness*. Berikan input palsu, dan biarkan *judge* menilai apakah F.R.I.D.A.Y memanggil *tool* M5 yang tepat dengan argumen yang tepat.

**Kesimpulan:** Anda membangun sesuatu yang solid. Rapikan arsitektur penyimpanan (menjadi satu transaksi SQLite) dan terapkan gerbang otorisasi MVP sebelum menancapkan kabel ke Home Assistant Anda!