# M5 — Device Abstraction Layer

> Status (per 2026-10-25): **mock lengkap** — driver `MockHome` + `DeviceService` (shadow desired/reported, `operation_id`, status, baca ulang, pending) + tool yang dibuat dari kemampuan perangkat. Adapter perangkat nyata **ditunda** ke versi F.R.I.D.A.Y berikutnya (PR user di `SPRINT3_LOG.md` 2026-10-23). Bagian bertanggal di bawah mencatat tiap tahap.

## Kegunaan

Lapisan yang membuat perangkat fisik (lampu, AC, dan seterusnya) bisa dipakai agent sebagai tool biasa. Adapter per ekosistem perangkat menerjemahkan perangkat menjadi `ToolContract` lalu mendaftarkannya ke katalog M4. Agent tidak pernah tahu protokol perangkatnya.

## Pendekatan

- **Cetak biru dari SAGE** (PAPER_NOTES.md #5): exception perangkat dikembalikan ke agent sebagai observasi, dan evaluasi dilakukan **tanpa hardware** dengan pola state awal, perintah, cek state akhir.
- **Registrasi lewat M4:** adapter memanggil `catalog.sync(provider, tools)` dan `catalog.describe_domain(...)`. Perubahan daftar perangkat mengubah kontrak tool, lalu `content_hash` membuat katalog ikut berubah tanpa restart (ScaleMCP).
- **Mulai dari mock.** Sprint 3 belum menyentuh Home Assistant atau MQTT. Mock dipakai untuk menguji M4 dengan penyedia nyata dan untuk membuat pertanyaan A2 konkret.

## Ringkasan Teknis (mock, 2026-09-17)

- `backend/devices/mock_home.py`
  - `MockDevice(device_id, name, room, kind, state)` dengan jenis `lamp` atau `air_conditioner`.
  - `MockHome`: state di memori, `apply()` dan `read_state()`, `snapshot()`, `diff(expected)` sebagai cek state akhir ala SAGE, `actions` sebagai instrumen test (bukan log aksi durable A2).
  - `fail_next(device_id, mode)`: `OFFLINE` tidak menerapkan apa pun lalu raise; `LOST_ACK` **menerapkan** perubahan lalu raise, meniru perangkat yang konfirmasinya timeout.
  - `MockHomeAdapter(home).sync_into(catalog, pinned=False)`: 5 tool di domain `home`, yaitu `home_list_devices`, `home_get_state` (read-only), `home_set_power`, `lamp_set_brightness`, `ac_set_temperature` (aktuator, `STANDARD`, idempoten). `device_id` berupa enum yang dibangkitkan dari perangkat, dengan deskripsi nama dan ruangan. Setiap tool punya contoh kalimat pemicu bahasa Indonesia.
- Test: `test_mock_home.py` (19 kasus: state, injeksi kegagalan, sync idempoten, perangkat baru terdeteksi lewat hash, pencarian frasa sehari-hari, alur penuh `find_tools` lalu `home_set_power`, argumen boolean-sebagai-string ditolak sebelum menyentuh perangkat) dan `test_a2_trace.py` (9 skenario A2, lihat `M2_memory.md`).

## Alur

1. Startup: `MockHomeAdapter(home).sync_into(catalog)`.
2. Turn: user bilang "nyalakan lampu ruang tamu". Tool rumah tidak terpasang, hanya `find_tools` yang tahu domain `home`.
3. Model memanggil `find_tools("nyalakan lampu")`, tool rumah di-bind ke registry turn.
4. Model memanggil `home_set_power(device_id="lampu_ruang_tamu", on=true)`. Skema divalidasi dulu, lalu `MockHome.apply()`.
5. Sukses: state baru jadi observasi. Gagal: teks `DeviceError` jadi observasi `is_error`.

## Bahasa Awam

Belum ada lampu sungguhan yang disambungkan. Yang ada adalah **rumah boneka** di dalam program: satu lampu ruang tamu dan satu AC kamar, lengkap dengan saklarnya. F.R.I.D.A.Y bisa menyalakan, mematikan, dan mengecek rumah boneka ini persis seperti nanti ke rumah asli. Rumah boneka ini juga bisa disuruh "pura-pura rusak": diam tidak merespons, atau diam-diam menyala tapi tidak mengirim kabar. Dengan begitu kita bisa melihat apa yang terjadi saat ada masalah, tanpa takut merusak apa pun.

## Keputusan desain

- Satu domain `home` untuk seluruh adapter, bukan satu domain per perangkat. Pencarian nama ruangan tetap kena lewat ringkasan domain dan deskripsi `device_id`.
- Aktuator ditandai `STANDARD`, bukan `CRITICAL`. Lampu dan AC bisa dibalik. Kunci pintu atau kompor nanti `CRITICAL` dan menunggu M11.
- `lamp_set_brightness` dan `ac_set_temperature` sekaligus menyalakan perangkat, supaya "agak gelap" cukup satu panggilan.

## Belum digarap / TODO

- **Keputusan A2** (lima pertanyaan di `M2_memory.md`). Kalau opsi (c) dipilih, adapter membaca ulang state setelah `DeviceError` dan mengembalikannya di observasi.
- Adapter nyata (Home Assistant/MQTT, blueprint Enhancing IoT + HearthNet).
- Disambiguasi perangkat berbasis alias ("lampu dekat lemari"), gerbang Clarifying ala Sasha.
- Kompresi respons state perangkat nyata (ToolLLM) sebelum masuk konteks.
- Benchmark tugas ala SAGE dengan LLM asli, dinilai dengan 7 mode kegagalan Sasha (M16).

## [2026-10-23] Baca ulang state setelah perintah gagal (A2 keputusan 2)

Tool aktuator (`home_set_power`, `lamp_set_brightness`, `ac_set_temperature`) sekarang lewat `MockHomeAdapter._command`. Kalau device melempar `DeviceError`, adapter membaca state lagi: perubahan sudah terjadi → hasil sukses dengan `note` ("did not confirm ..., but reading the state back shows the change took effect"); belum terjadi → error berisi state aktual; baca ulang ikut gagal → error "actual state unknown". Pola ini yang harus diikuti adapter nyata: setiap device butuh operasi baca state. `MockHome.apply` sendiri tidak berubah (test `test_mock_home.py` untuk `LOST_ACK` tetap berlaku di level rumah).

## [2026-10-25] Tahap 2 — kontrak Device + lapisan generik (device shadow)

Mengikuti feedback 4 model AI (lihat `SPRINT3_LOG.md` 2026-10-25). M5 sekarang tiga lapis, sehingga adapter nyata nanti cukup menulis lapis pertama:

| Lapis | File | Isi |
|---|---|---|
| Driver (spesifik protokol) | `backend/devices/mock_home.py` (`MockHome`) | `descriptors()`, `read_state(id)`, `apply(id, **changes)`. Nanti: Home Assistant / MQTT. |
| Layanan (sama untuk semua driver) | `backend/devices/service.py` (`DeviceService`) | Validasi perubahan terhadap kemampuan perangkat **sebelum** driver disentuh; `operation_id` per perintah; status akhir `succeeded`/`failed`/`pending`/`unknown`; shadow `desired` (permintaan terakhir, tetap ada walau gagal) vs `reported` (laporan terakhir + waktunya); baca ulang setelah error (A2 keputusan 2) dengan **toleransi** nilai analog. |
| Tool (dibuat dari kemampuan) | `backend/devices/tools.py` (`build_device_tools`) | `home_list_devices`, `home_get_state`, `home_set_power`, dan `home_set_<kemampuan>` untuk setiap kemampuan yang bisa diubah. Kemampuan baru (mis. `fan_speed`) otomatis dapat tool tanpa kode baru. |

Kontrak ada di M0: `backend/schemas/device_contract.py` (`Capability`, `DeviceDescriptor`, `DeviceSnapshot`, `CommandStatus`, `DeviceCommandResult`, `DEVICE_CONTRACT_VERSION = 1.0.0`), dengan kemampuan standar `POWER` (`on`), `BRIGHTNESS`, `TARGET_TEMPERATURE` (toleransi 0,5), `CURRENT_TEMPERATURE` (hanya baca).

**Perubahan yang terlihat model:**
- `temperature` diganti `target_temperature` (yang diminta) + `current_temperature` (suhu ruangan terukur; AC simulasi 29,0 °C, tetap).
- Nama tool: `lamp_set_brightness` → `home_set_brightness`, `ac_set_temperature` → `home_set_target_temperature`. `home_get_state` dan `home_set_power` versi 2.0.0.
- Hasil aksi sekarang hasil perintah (`operation_id`, `status`, `requested`, `reported`, `message`). Status selain `succeeded` → tool error berisi status + `operation_id`, supaya model tidak bisa membacanya sebagai sukses.
- **Perubahan perilaku yang disengaja:** membaca perangkat offline bukan lagi tool error, tapi snapshot `connection: offline`, `stale: true`, `reported` = state terakhir yang diketahui + waktunya, dan `message` yang melarang menyajikannya sebagai state sekarang.
- Nilai boolean hanya cocok dengan boolean (`True == 1` di Python tidak diterima diam-diam; driver yang wajib menormalkan).

**Belum:** status `pending` belum pernah dihasilkan (mock belum punya perangkat lambat) — Tahap 3. Shadow hanya di memori (hilang saat restart); jurnal aksi yang tahan restart = Tahap 4 (M11).

## [2026-10-25] Tahap 3 — perangkat lambat (pending) dan "lampu yang mana?"

- **Pending:** driver boleh melempar `CommandAccepted` (bukan `DeviceError`) kalau perangkat menerima perintah tapi baru menjalankannya nanti. `DeviceService` lalu memberi status `pending` tanpa baca ulang (membaca sekarang cuma menunjukkan state lama), menyimpan operasi, dan saat pembacaan berikutnya menunjukkan perubahannya, operasi itu jadi `succeeded` (`get_operation(id)`). `DeviceSnapshot.pending_operations` (kontrak 1.1.0) + pesan "jangan bilang sudah selesai". Bagi model, `pending` **bukan** tool error, tapi hasilnya membawa `note` yang melarang mengaku selesai.
- **Mock:** `MockHome.make_slow(device_id, reads)` — perintah baru diterapkan setelah `reads` kali pembacaan state (meniru LoRa kelas A yang baru menerima perintah setelah uplink berikutnya); `queued()` untuk melihat antrean. CLI: `/slow <device_id> <reads>`, `/state` menampilkan antrean.
- **Disambiguasi (Sasha, gerbang Clarifying):** `two_lamp_home()` (lampu utama + lampu baca di ruang tamu; `default_home()` tidak berubah). Setiap tool aktuator membawa aturan "kalau ucapan user cocok dengan lebih dari satu perangkat dan tidak disebut yang mana, tanya dulu", ditambah satu kalimat di system prompt. CLI: `--home dua-lampu`.
- **Smoke test API asli (2026-10-25):** perangkat lambat → model bilang "sedang diproses", lalu "belum nyala, masih diproses" ✅. "nyalakan lampunya dong" di rumah 2 lampu → bertanya balik dengan dua pilihan ✅. "nyalakan lampu ruang tamu" → model memilih lampu utama tanpa bertanya (tafsiran wajar, dicatat).
- **Celah yang diketahui:** operasi pending yang tidak pernah terwujud (mis. perintah lain menimpanya) tetap `pending` selamanya — belum ada batas waktu; shadow dan operasi hanya di memori (hilang saat restart) → jurnal aksi M11 (Sprint 4).
