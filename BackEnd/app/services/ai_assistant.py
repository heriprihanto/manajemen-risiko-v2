"""AI Assistant service — abstraksi multi-provider LLM.

Provider yang didukung: OpenAI, Gemini (Google AI), dan Anthropic.
Konfigurasi (provider, API key, model) disimpan di tabel tr_pengaturan dan
dikelola melalui halaman Pengaturan Aplikasi oleh Admin.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
from typing import Any, AsyncIterator

import httpx

logger = logging.getLogger(__name__)

# ─── Prompt Templates ───────────────────────────────────────────────

SYSTEM_PROMPT = """Kamu adalah asisten AI ahli Manajemen Risiko untuk instansi pemerintah daerah di Indonesia, berdasarkan Peraturan Walikota (Perwal) Nomor 1 Tahun 2026 tentang Manajemen Risiko.

Tugasmu:
1. Membantu merumuskan pernyataan risiko yang baik (format: Kejadian + Penyebab + Dampak)
2. Menyarankan Rencana Tindak Pengendalian (RTP) yang terukur dan aplikatif
3. Mengidentifikasi celah pengendalian dan merekomendasikan perbaikan
4. Membantu menentukan media informasi & komunikasi pengendalian (Form 8)
5. Membantu menentukan metode pemantauan pengendalian intern / PI (Form 9)
6. Menjawab pertanyaan seputar regulasi manajemen risiko pemerintah daerah

Aturan:
- Jawab dalam Bahasa Indonesia yang formal namun mudah dipahami ASN
- Berikan jawaban yang spesifik dan kontekstual, hindari template generik
- Jika diminta merekomendasikan, berikan 2-3 alternatif pilihan
- Sertakan alasan singkat di setiap rekomendasi
- Jangan mengada-ada aturan hukum; jika tidak yakin, sampaikan dengan jujur
- Gunakan terminologi Perwal No. 1/2026 (Risiko Strategis Pemda, Strategis OPD, Operasional OPD)
"""

RISK_GENERATOR_PROMPT = """Berdasarkan sasaran/kegiatan berikut, bantu rumuskan risiko-risiko yang mungkin terjadi.

Sasaran / Kegiatan: {sasaran}
{context_info}
Instruksi:
- Rumuskan 3 risiko potensial dengan format:
  • Uraian Risiko: pernyataan risiko (Apa kejadiannya?)
  • Penyebab: akar penyebab utama
  • Dampak: konsekuensi jika risiko terjadi
  • Kategori: (Operasional / Keuangan / Kebijakan / Kepatuhan / Reputasi / Fraud / Lingkungan)
- Setiap risiko harus spesifik, terukur, dan relevan dengan konteks OPD pemerintah daerah.

Jawab dalam format JSON array:
[
  {{
    "uraian_risiko": "...",
    "penyebab": "...",
    "dampak": "...",
    "kategori": "..."
  }}
]
"""

RTP_SUGGESTION_PROMPT = """Bantu rekomendasikan Rencana Tindak Pengendalian (RTP) berdasarkan informasi berikut:

Risiko: {uraian_risiko}
Kode Risiko: {kode_risiko}
Level Risiko: {level_risiko}
Pemilik Risiko: {pemilik_risiko}
Celah Pengendalian: {celah}
Pengendalian yang Sudah Ada: {pengendalian_ada}
{context_info}
Instruksi:
- Berikan 2-3 alternatif Rencana Tindak Pengendalian yang konkret, terukur, dan dapat dilaksanakan OPD.
- Untuk setiap RTP, sertakan:
  • Respon Risiko: (kurangi_kemungkinan / kurangi_dampak / bagi / hindari / terima)
  • Rencana Tindak: langkah spesifik yang harus dilakukan
  • Media Komunikasi (Form 8): sarana untuk mengkomunikasikan pengendalian ini
  • Penyedia Informasi: siapa yang menyediakan informasi
  • Penerima Informasi: siapa yang menerima informasi
  • Metode Pemantauan (Form 9): cara memantau efektivitas pengendalian
  • Penanggung Jawab Pemantauan: siapa yang bertanggung jawab memantau

Jawab dalam format JSON array:
[
  {{
    "respon_risiko": "...",
    "rencana_tindak": "...",
    "media_komunikasi": "...",
    "penyedia_informasi": "...",
    "penerima_informasi": "...",
    "metode_pemantauan": "...",
    "penanggung_jawab_pemantauan": "..."
  }}
]
"""

TREATED_RISK_SUGGESTION_PROMPT = """Bantu analisis dan rekomendasikan Level Treated Risk (Tingkat Risiko Setelah Adanya RTP):

Uraian Risiko: {uraian_risiko}
Level Inheren: {level_inheren} (Kemungkinan: {kemungkinan_inheren}, Dampak: {dampak_inheren})
Pengendalian Terpasang: {pengendalian_ada}
Karakteristik Respon Risiko: {respon_risiko}
Rencana Tindak Pengendalian (RTP): {rencana_tindak}
{context_info}

Petunjuk Khusus Sesuai Regulasi Perwal 1/2026:
1. Sesuaikan penilaian dengan karakteristik Rencana Tindak Pengendalian (RTP):
   - Jika RTP berkarakteristik 'kurangi_kemungkinan', tingkat kemungkinan yang harus berkurang/turun.
   - Jika RTP berkarakteristik 'kurangi_dampak', tingkat dampak yang harus berkurang/turun.
   - Jika keduanya, baik kemungkinan maupun dampak dapat berkurang secara proporsional.
2. Nilai kemungkinan treated (1..5) dan dampak treated (1..5) bersifat realistis dan tidak boleh melampaui nilai inheren awal.
3. Berikan justifikasi teknis mengapa tindakan pengendalian tersebut efektif mengoreksi risiko.

Jawab HANYA dalam format JSON object:
{{
  "kemungkinan_treated": 2,
  "dampak_treated": 3,
  "justifikasi": "Uraian justifikasi mengapa kemungkinan atau dampak terkoreksi setelah implementasi RTP..."
}}
"""

CHAT_SYSTEM_PROMPT = SYSTEM_PROMPT + """

Kamu juga bisa membaca konteks data risiko OPD yang diberikan untuk memberikan jawaban yang lebih relevan.
Selalu jawab secara ringkas, jelas, dan actionable.
"""


# ─── Provider Adapters ───────────────────────────────────────────────

async def _call_openai(
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Call OpenAI Chat Completions API."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model or "o4-mini",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            try:
                err_json = resp.json()
                msg = err_json.get("error", {}).get("message") or resp.text
            except Exception:
                msg = resp.text
            raise RuntimeError(f"OpenAI error ({resp.status_code}): {msg}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_gemini(
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Call Google Gemini (Generative Language) API."""
    model_name = model or "gemini-3.8-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    # Convert chat messages to Gemini format
    system_text = ""
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        elif msg["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

    payload: dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if system_text:
        payload["systemInstruction"] = {"parts": [{"text": system_text}]}

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload)
        if resp.status_code != 200:
            try:
                err_json = resp.json()
                msg = err_json.get("error", {}).get("message") or resp.text
            except Exception:
                msg = resp.text
            raise RuntimeError(f"Gemini error ({resp.status_code}): {msg}")
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates or not candidates[0].get("content", {}).get("parts"):
            raise RuntimeError(f"Gemini tidak mengembalikan teks jawaban: {data}")
        return candidates[0]["content"]["parts"][0]["text"]


async def _call_anthropic(
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Call Anthropic Messages API."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    system_text = ""
    api_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

    payload: dict[str, Any] = {
        "model": model or "claude-sonnet-5-5",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": api_messages,
    }
    if system_text:
        payload["system"] = system_text

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            try:
                err_json = resp.json()
                msg = err_json.get("error", {}).get("message") or resp.text
            except Exception:
                msg = resp.text
            raise RuntimeError(f"Anthropic error ({resp.status_code}): {msg}")
        data = resp.json()
        return data["content"][0]["text"]


async def _call_hermes(
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Call local Hermes Agent CLI in one-shot mode (-z)."""
    hermes_bin = shutil.which("hermes") or os.path.expanduser("~/.local/bin/hermes")
    if not os.path.exists(hermes_bin):
        raise RuntimeError(f"Binary hermes tidak ditemukan di '{hermes_bin}'. Pastikan Hermes Agent terpasang di komputer.")

    # Flatten system and conversation messages into a clean prompt
    system_text = ""
    turns = []
    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "")
        if role == "system":
            system_text = content
        elif role == "user":
            turns.append(f"User: {content}")
        elif role == "assistant":
            turns.append(f"Assistant: {content}")

    prompt_parts = []
    if system_text:
        prompt_parts.append(f"[Instruksi Sistem]\n{system_text.strip()}\n")
    if turns:
        prompt_parts.append("\n".join(turns))
    full_prompt = "\n".join(prompt_parts)

    cmd = [hermes_bin, "-z", full_prompt]
    if model and model.strip() and model.strip() != "gpt-6-astra":
        cmd.extend(["-m", model.strip()])

    logger.info("Memanggil Hermes Agent lokal via CLI")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=90.0)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        raise RuntimeError("Hermes Agent timeout (tidak merespons dalam 90 detik)")

    if proc.returncode != 0:
        err_msg = stderr.decode().strip() or stdout.decode().strip() or f"Kode keluar {proc.returncode}"
        raise RuntimeError(f"Hermes Agent error: {err_msg}")

    result = stdout.decode().strip()
    if not result:
        raise RuntimeError("Hermes Agent mengembalikan respon kosong.")
    return result


PROVIDERS = {
    "openai": _call_openai,
    "gemini": _call_gemini,
    "anthropic": _call_anthropic,
    "hermes": _call_hermes,
}


# ─── Public Interface ────────────────────────────────────────────────

async def call_llm(
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Panggil LLM provider yang dikonfigurasi. Raise ValueError jika provider tidak dikenal."""
    fn = PROVIDERS.get(provider)
    if fn is None:
        raise ValueError(f"Provider AI tidak dikenal: {provider}")
    return await fn(api_key, model, messages, temperature, max_tokens)


def build_risk_prompt(sasaran: str, context: dict | None = None) -> list[dict]:
    """Bangun messages untuk generate risiko dari sasaran/kegiatan."""
    context_info = ""
    if context:
        parts = []
        if context.get("opd"):
            parts.append(f"OPD: {context['opd']}")
        if context.get("jenis_risiko"):
            parts.append(f"Jenis Risiko: {context['jenis_risiko']}")
        if context.get("tahun"):
            parts.append(f"Tahun: {context['tahun']}")
        if parts:
            context_info = "Konteks:\n" + "\n".join(f"- {p}" for p in parts)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": RISK_GENERATOR_PROMPT.format(
            sasaran=sasaran, context_info=context_info
        )},
    ]


def build_rtp_prompt(risk_data: dict, context: dict | None = None) -> list[dict]:
    """Bangun messages untuk saran RTP dari data risiko."""
    context_info = ""
    if context:
        parts = []
        if context.get("opd"):
            parts.append(f"OPD: {context['opd']}")
        if context.get("tahun"):
            parts.append(f"Tahun: {context['tahun']}")
        if parts:
            context_info = "Konteks:\n" + "\n".join(f"- {p}" for p in parts)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": RTP_SUGGESTION_PROMPT.format(
            uraian_risiko=risk_data.get("uraian_risiko", ""),
            kode_risiko=risk_data.get("kode_risiko", ""),
            level_risiko=risk_data.get("level_risiko", "Belum dianalisis"),
            pemilik_risiko=risk_data.get("pemilik_risiko", "Belum ditetapkan"),
            celah=risk_data.get("celah_pengendalian", "Belum diidentifikasi"),
            pengendalian_ada=risk_data.get("pengendalian_ada", "Belum ada"),
            context_info=context_info,
        )},
    ]


def build_treated_prompt(risk_data: dict, context: dict | None = None) -> list[dict]:
    """Bangun messages untuk saran Treated Risk berdasarkan karakteristik RTP."""
    context_info = ""
    if context:
        parts = []
        if context.get("opd"):
            parts.append(f"OPD: {context['opd']}")
        if context.get("tahun"):
            parts.append(f"Tahun: {context['tahun']}")
        if parts:
            context_info = "Konteks:\n" + "\n".join(f"- {p}" for p in parts)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TREATED_RISK_SUGGESTION_PROMPT.format(
            uraian_risiko=risk_data.get("uraian_risiko", ""),
            level_inheren=risk_data.get("level_inheren", "Sedang"),
            kemungkinan_inheren=risk_data.get("kemungkinan_inheren", 3),
            dampak_inheren=risk_data.get("dampak_inheren", 3),
            pengendalian_ada=risk_data.get("pengendalian_ada", "Belum ada"),
            respon_risiko=risk_data.get("respon_risiko", "kurangi_kemungkinan"),
            rencana_tindak=risk_data.get("rencana_tindak", ""),
            context_info=context_info,
        )},
    ]


def build_chat_messages(
    user_message: str,
    history: list[dict] | None = None,
    context: dict | None = None,
) -> list[dict]:
    """Bangun messages untuk chat copilot."""
    system = CHAT_SYSTEM_PROMPT
    if context:
        ctx_parts = []
        if context.get("opd"):
            ctx_parts.append(f"OPD aktif: {context['opd']}")
        if context.get("tahun"):
            ctx_parts.append(f"Tahun: {context['tahun']}")
        if context.get("jumlah_risiko"):
            ctx_parts.append(f"Jumlah risiko teridentifikasi: {context['jumlah_risiko']}")
        if context.get("jumlah_prioritas"):
            ctx_parts.append(f"Jumlah risiko prioritas: {context['jumlah_prioritas']}")
        if ctx_parts:
            system += "\n\nKonteks data OPD saat ini:\n" + "\n".join(f"- {p}" for p in ctx_parts)

    messages: list[dict] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history[-10:])  # Max 10 pesan terakhir
    messages.append({"role": "user", "content": user_message})
    return messages


def parse_json_from_llm(text: str) -> list[dict] | None:
    """Ekstrak JSON array dari respons LLM (toleran terhadap markdown code blocks)."""
    cleaned = text.strip()
    # Hapus markdown code block
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return [result]
    except json.JSONDecodeError:
        # Coba cari JSON array di dalam teks
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                pass
    return None
