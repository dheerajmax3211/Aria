# PHASE 1: FOUNDATION — Implementation Plan

## Goal
JARVIS boots, listens, responds via voice. Basic Q&A works.
**Milestone:** You say "What's 2+2?" → JARVIS speaks back "Four."

---

## What This Phase Delivers
- Complete project folder structure (all 11 phases' directories, with Phase 1 modules implemented)
- Config system ready for all future phases
- Speech-to-Text pipeline (faster-whisper)
- Text-to-Speech pipeline (ElevenLabs + Coqui offline fallback)
- LLM core (Ollama wrapper, dual-model ready for Phase 2+)
- Main loop: record → transcribe → LLM → speak
- Logging system
- .env template with all future-phase keys pre-defined

---

## Folder Structure to Create

```
jarvis/
│
├── main.py                    # Entry point. Boots everything. Phase 1: basic loop
├── config.py                  # Loads .env, pydantic-settings model
├── .env.example               # Template (never commit real .env)
├── requirements.txt
├── README.md
│
├── perception/
│   ├── __init__.py
│   ├── stt.py                 # Speech-to-text (faster-whisper) — PHASE 1
│   ├── vad.py                 # Voice activity detection — PHASE 1 (basic)
│   ├── wake_word.py           # Wake word detection — STUB (Phase 2)
│   └── mute_detector.py       # Microphone level monitor — STUB (Phase 2)
│
├── output/
│   ├── __init__.py
│   ├── tts.py                 # ElevenLabs + Coqui fallback — PHASE 1
│   ├── speaker.py             # Audio playback, interrupt — PHASE 1 (basic)
│   └── hud.py                 # Optional overlay UI — STUB (Phase 11)
│
├── brain/
│   ├── __init__.py
│   ├── llm.py                 # LLM abstraction (Ollama) — PHASE 1
│   ├── router.py              # Routes intent to correct agent — STUB (Phase 3)
│   ├── planner.py             # Multi-step task planner — STUB (Phase 10)
│   ├── context_builder.py     # Builds system prompt with context — STUB (Phase 3)
│   └── tool_registry.py       # All registered tools — STUB (Phase 5)
│
├── memory/
│   ├── __init__.py
│   ├── short_term.py          # In-RAM conversation buffer — STUB (Phase 3)
│   ├── long_term.py           # ChromaDB vector memory — STUB (Phase 3)
│   ├── episodic.py            # SQLite log of completed tasks — STUB (Phase 3)
│   └── user_profile.py        # Preferences, projects, settings — STUB (Phase 3)
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract base class — PHASE 1 (interface definition)
│   ├── computer_control.py    # OS-level control agent — STUB (Phase 5)
│   ├── file_agent.py          # File system operations — STUB (Phase 5)
│   ├── dev_agent.py           # Vibe coding, project scaffolding — STUB (Phase 8)
│   ├── git_agent.py           # Git + GitHub operations — STUB (Phase 8)
│   ├── google_agent.py        # Drive, Calendar, Gmail — STUB (Phase 6)
│   ├── messaging_agent.py     # Telegram, WhatsApp — STUB (Phase 7)
│   ├── web_agent.py           # Search, browse, research — STUB (Phase 9)
│   ├── weather_agent.py       # Weather fetch + briefing — STUB (Phase 4)
│   ├── job_agent.py           # Job search + tracking — STUB (Phase 9)
│   └── learning_agent.py      # Language + skill tutoring — STUB (Phase 10)
│
├── integrations/
│   ├── __init__.py
│   ├── google/
│   │   ├── __init__.py
│   │   ├── auth.py            # OAuth2 flow — STUB (Phase 6)
│   │   ├── drive.py           — STUB (Phase 6)
│   │   ├── calendar.py        — STUB (Phase 6)
│   │   └── gmail.py           — STUB (Phase 6)
│   ├── github.py              # GitHub REST API wrapper — STUB (Phase 8)
│   ├── telegram_bot.py        # Remote interface from phone — STUB (Phase 7)
│   ├── whatsapp.py            # WhatsApp Web automation — STUB (Phase 7)
│   └── openweather.py         # Weather API — STUB (Phase 4)
│
├── scheduler/
│   ├── __init__.py
│   ├── jobs.py                # All scheduled jobs (APScheduler) — STUB (Phase 4)
│   └── briefing.py            # Morning/evening briefing logic — STUB (Phase 4)
│
├── templates/
│   ├── __init__.py
│   ├── projects/              # Project boilerplates — STUB (Phase 8)
│   └── prompts/               # System prompt templates — PHASE 1 (base system prompt)
│
├── data/                      # Persistent storage — PHASE 1 (directory created)
│
└── logs/                      # Loguru output — PHASE 1
```

---

## Files to Implement (Phase 1 Actual Code)

### 1. `requirements.txt`
All dependencies for Phase 1, plus future-phase deps commented out:
- `faster-whisper` — STT
- `elevenlabs` — TTS (primary)
- `coqui-tts` or `TTS` — TTS (offline fallback)
- `ollama` or `requests` — LLM via Ollama API
- `pydantic` + `pydantic-settings` — Config
- `python-dotenv` — .env loading
- `loguru` — Logging
- `sounddevice` + `numpy` + `scipy` — Audio recording/playback
- `noisereduce` — Audio noise suppression
- `requests` — HTTP calls

### 2. `.env.example`
Complete template with ALL keys for all 11 phases:
```env
# Identity
JARVIS_NAME=JARVIS
USER_NAME=YourName
USER_LOCATION=YourCity, YourCountry
WORKING_HOURS_START=9
WORKING_HOURS_END=21

# Voice
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
WAKE_WORD=hey jarvis
STT_MODEL=base.en

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
CLAUDE_API_KEY=
LLM_MODE=local

# Integrations (future phases)
OPENWEATHER_API_KEY=
GITHUB_TOKEN=
GITHUB_USERNAME=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
GOOGLE_CREDENTIALS_PATH=./integrations/google/credentials.json

# Paths
PROJECTS_ROOT=
DOWNLOADS_FOLDER=

# Scheduling
MORNING_BRIEFING_TIME=08:00
EVENING_SUMMARY_TIME=21:00
```

### 3. `config.py`
Pydantic-settings model that:
- Loads all .env variables with type safety
- Validates required keys at startup
- Provides sensible defaults for non-critical settings
- Exposes a single `settings` object imported everywhere
- Includes Phase 2+ fields so no config changes needed later

### 4. `main.py`
Entry point that:
- Initializes logging (loguru)
- Loads config, validates API keys
- Initializes STT, TTS, LLM modules
- Runs the main interaction loop:
  1. Record audio from microphone (sounddevice)
  2. Transcribe via STT
  3. Send to LLM (Ollama)
  4. Speak response via TTS
- Handles graceful shutdown (Ctrl+C)
- Prints startup status

### 5. `perception/stt.py`
Speech-to-Text module:
- Loads `faster-whisper` model (configurable size via .env)
- `transcribe(audio_bytes)` → returns text string
- Pre-processes audio through `noisereduce`
- Handles model loading errors gracefully
- Supports multi-language (Hinglish ready)

### 6. `perception/vad.py`
Voice Activity Detection (basic for Phase 1):
- Detects when user stops speaking (silence threshold)
- Used by main loop to know when recording is "done"
- Configurable silence duration threshold
- Phase 2 will enhance with more sophisticated VAD

### 7. `output/tts.py`
Text-to-Speech module:
- Primary: ElevenLabs API (streaming if available)
- Fallback: Coqui TTS (offline, lower quality)
- `speak(text)` → plays audio through speakers
- Handles API errors, network failures
- Loads voice ID from config

### 8. `output/speaker.py`
Audio playback wrapper:
- Plays audio bytes through system speakers
- Uses `sounddevice` for playback
- Basic interrupt support (stop current speech)
- Volume control hook (for Phase 11)

### 9. `brain/llm.py`
LLM abstraction layer:
- Wraps Ollama API (local model)
- `chat(prompt, system_prompt)` → returns response string
- Configurable model via .env
- Handles connection errors, model not found
- Designed for Phase 2+ dual-LLM strategy (local + Claude)

### 10. `agents/base_agent.py`
Abstract base class for all agents:
- Defines `name`, `description` properties
- Abstract `execute(task, context)` method
- Optional `rollback(task_id)` method
- This interface is used by router/planner in later phases

### 11. `templates/prompts/system_prompt.txt`
Base system prompt for JARVIS:
- Identity: "You are JARVIS, a voice-first AI assistant..."
- Tone: calm, confident, precise, concise
- Response format: short answers (voice-optimized)
- No markdown in responses (TTS can't render it)

### 12. `__init__.py` files
All directories get proper `__init__.py` for clean imports.

### 13. `data/` and `logs/` directories
Created at startup if they don't exist.

---

## What Phase 2 Will Need From Phase 1

Phase 2 (Wake Word + Daemon) builds directly on Phase 1:

1. **`config.py`** — Already has all Phase 2 fields (`WAKE_WORD`, `WORKING_HOURS_START/END`)
2. **`perception/stt.py`** — Already implemented, Phase 2 just wraps it with wake word trigger
3. **`perception/vad.py`** — Already implemented, Phase 2 enhances it
4. **`output/tts.py`** — Already implemented, Phase 2 adds boot greeting
5. **`output/speaker.py`** — Already implemented, Phase 2 uses it for greeting
6. **`brain/llm.py`** — Already implemented, Phase 2 uses it for responses
7. **`main.py`** — Phase 2 modifies the loop: instead of always recording, it waits for wake word first
8. **`requirements.txt`** — Phase 2 adds `openWakeWord` or `pvporcupine`
9. **`config.py`** — Already has all fields, no changes needed
10. **Folder structure** — All Phase 2 stub files (`wake_word.py`, `mute_detector.py`) already exist as empty modules

**Phase 2 additions will be:**
- Implement `perception/wake_word.py` (openWakeWord integration)
- Implement `perception/mute_detector.py`
- Enhance `perception/vad.py` with better silence detection
- Modify `main.py` loop to be wake-word-triggered instead of always-recording
- Add boot greeting in `main.py`
- Set up OS daemon (systemd / Task Scheduler / launchd)

---

## Build Order (Within Phase 1)

1. Create folder structure + all `__init__.py` files
2. Write `requirements.txt` + `.env.example`
3. Write `config.py` (pydantic-settings model)
4. Write `templates/prompts/system_prompt.txt`
5. Write `agents/base_agent.py` (interface)
6. Write `perception/vad.py` (silence detection)
7. Write `perception/stt.py` (faster-whisper)
8. Write `output/speaker.py` (audio playback)
9. Write `output/tts.py` (ElevenLabs + Coqui)
10. Write `brain/llm.py` (Ollama wrapper)
11. Write `main.py` (ties everything together)
12. Create stub files for all future phases (empty modules with docstrings)
13. Write `README.md` with setup instructions

---

## Testing Criteria for Phase 1

Phase 1 is complete when:
- [ ] `python main.py` starts without errors
- [ ] All config validation passes (with valid .env)
- [ ] Microphone records audio successfully
- [ ] STT transcribes spoken words to text accurately
- [ ] LLM (Ollama) receives text and returns a response
- [ ] TTS speaks the LLM response through speakers
- [ ] Full loop works: speak → transcribe → LLM → speak back
- [ ] Graceful shutdown on Ctrl+C
- [ ] Logs are written to `logs/jarvis.log`
- [ ] ElevenLabs failure falls back to Coqui TTS
- [ ] Ollama connection failure is handled gracefully

---

## External Dependencies (User Must Set Up)

Before Phase 1 can run, the user needs:
1. **Python 3.11+** installed
2. **Ollama** installed and running (`ollama serve`)
3. **Ollama model pulled** (`ollama pull llama3.1:8b` or configured model)
4. **ElevenLabs API key** (optional — Coqui fallback works without it)
5. **Microphone** connected and working
6. **Speakers/headphones** connected and working

These are documented in the README with setup commands.
