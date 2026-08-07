# M1 — Agent Core

> Status: **Belum digarap** (rencana setelah M0 selesai). Sprint 1, Kategori riset #1 (Agentic AI / Tool Use & Function Calling).
> Paper rujukan: ReAct, Toolformer, Reflexion, LLM Agent Survey. Detail lengkap di `Memory Think/PAPER_NOTES.md`.

---

## Kegunaan

M1 adalah **"otak" pengambil keputusan** F.R.I.D.A.Y — bagian yang bikin F.R.I.D.A.Y jadi *agent* beneran, bukan sekadar chatbot yang jawab teks. Ini loop inti yang:

1. Mikir soal apa yang harus dilakukan (reasoning)
2. Mutusin apakah butuh manggil tool (dari daftar tool yang sudah punya `ToolContract` dari M0) atau langsung jawab
3. Kalau manggil tool, lihat hasilnya (observation)
4. Mikir lagi berdasarkan hasil itu — ulang sampai task selesai atau menyerah

M1 bergantung langsung ke M0: setiap tool yang bisa dipanggil loop ini **harus** sudah punya `ToolContract` yang valid, karena manifest itulah yang di-"tunjukkan" ke LLM supaya dia tahu tool apa saja yang tersedia dan kapan boleh dipakai.

## Pendekatan

Tiga paper jadi kerangka utama:

1. **ReAct** — pola loop `Thought → Action → Observation → Thought → ...`. "Thought" adalah reasoning verbal (bantu agent lacak progres & sesuaikan rencana), "Action" adalah pemanggilan tool nyata (ambil info dari luar, kurangi halusinasi dibanding cuma mikir tanpa cek fakta). Ini kerangka loop utama M1.
2. **Toolformer** — prinsip *kapan* tool sebaiknya dipanggil: tool dipanggil hanya kalau benar-benar mengurangi ketidakpastian/berguna, bukan asal panggil semua tool yang ada. Penting buat efisiensi biaya & latensi kalau F.R.I.D.A.Y punya banyak tool IoT/OS sekaligus.
3. **Reflexion** — mekanisme "belajar dari gagal" tanpa training ulang model: kalau satu percobaan gagal, agent bikin refleksi verbal (bahasa biasa, bukan update bobot) dan simpan sebagai konteks tambahan buat percobaan berikutnya. Ini yang bikin loop ReAct tidak cuma "coba-gagal-coba lagi tanpa belajar", tapi makin pintar tiap percobaan dalam sesi yang sama.

Risiko yang harus diantisipasi (dicatat di paper notes): loop ReAct bisa terjebak berulang tanpa progres — perlu guard/timeout/batas iterasi, bukan dibiarkan jalan tanpa henti.

## Ringkasan Teknis (rencana — belum ada kode)

Belum ada implementasi. Rencana kasar berdasarkan riset yang sudah dikumpulkan:

- Loop utama akan hidup di `backend/agent_core/` (folder sudah ada, masih kosong).
- Tool yang tersedia untuk loop ini diambil dari daftar `ToolContract` (M0) — dipakai sebagai bagian dari prompt/system context supaya LLM tahu tool apa saja yang ada beserta skema input/outputnya.
- Perlu komponen: (a) pemanggil LLM (thought generation), (b) parser keputusan (apakah LLM mau Action atau langsung jawab final), (c) eksekutor tool sungguhan (validasi input terhadap `input_schema` sebelum dieksekusi), (d) penyisipan observation balik ke konteks percakapan, (e) guard iterasi maksimum supaya tidak infinite loop.
- Mekanisme refleksi (Reflexion) kemungkinan besar akan menyentuh M2 (Memory) juga — refleksi kegagalan perlu disimpan somewhere, jadi ada overlap desain dengan Sprint 2.

## Bahasa Awam

Kalau M0 itu "formulir pendaftaran alat", M1 itu **orangnya yang mikir dan pakai alat itu**.

Bayangkan kamu minta tolong F.R.I.D.A.Y: *"nyalain lampu kamar terus kasih tau suhu di luar."* M1 ini yang:

1. **Mikir dulu**: "oke, ada dua hal yang harus gua lakuin — nyalain lampu, sama cek cuaca."
2. **Bertindak**: manggil alat `nyalain_lampu` (yang sudah terdaftar di M0), lihat hasilnya — berhasil apa nggak.
3. **Mikir lagi**: "oke lampu udah nyala, sekarang gua panggil alat `cek_cuaca`."
4. **Bertindak lagi**: manggil `cek_cuaca`, dapat hasilnya.
5. **Selesai**: gabungin semua hasil jadi jawaban ke kamu: "Lampu kamar udah nyala. Suhu di luar 28°C."

Kalau di tengah jalan ada yang gagal (misal alat `nyalain_lampu` error), F.R.I.D.A.Y nggak langsung nyerah atau ngulang percis sama caranya — dia "mencatat" apa yang salah (refleksi), terus coba pendekatan lain berdasarkan catatan itu. Ini bedanya F.R.I.D.A.Y sama chatbot biasa yang cuma jawab teks: F.R.I.D.A.Y benar-benar **melakukan** sesuatu, mikir sebelum dan sesudah tiap aksi, dan bisa memperbaiki diri di tengah proses.
