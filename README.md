# F.R.I.D.A.Y

Asisten AI personal — agentic AI assistant dengan kemampuan tool-use, kontrol IoT/OS, memori jangka panjang, dan voice interaction, terinspirasi oleh F.R.I.D.A.Y dari fiksi.

Target proyek ini realistis: mencapai kira-kira 80–85% dari fungsionalitas yang *terlihat* (tool-use, kontrol perangkat, memori, percakapan suara), bukan mereplikasi reasoning superhuman. Dibangun bertahap mengikuti roadmap 12 sprint.

## Struktur Folder (`backend/`)

- `schemas/` — kontrak data (JSON schema) untuk tool, task, event, memory, device.
- `agent_core/` — loop inti agent (reasoning, decision-making, orchestration keputusan).
- `agent_core/tools/` — implementasi tool individual yang bisa dipanggil agent.
- `memory/` — penyimpanan dan pengambilan memori jangka panjang.
- `registry/` — pendaftaran dan penemuan tool/device yang tersedia untuk agent.
- `dal/` — data access layer, abstraksi ke database/storage.
- `security/` — autentikasi, otorisasi, dan kontrol akses.
- `orchestrator/` — koordinasi antar komponen (agent, tool, memory, device).
- `persona/` — definisi kepribadian, gaya bicara, dan perilaku asisten.
