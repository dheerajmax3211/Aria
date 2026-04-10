# JARVIS — Personal AI Assistant

> A truly agentic, always-on, voice-first personal AI system.

## Current Status: All 11 Phases Complete ✅

**34 tools loaded.** JARVIS boots, listens for "hey jarvis", understands speech, thinks with context and memory, executes tools, and speaks back — all automatically.

## Quick Start

### Prerequisites

- Python 3.11+
- Ollama (installed and running)
- Working microphone
- Working speakers/headphones

### Setup

```bash
# 1. Enter the project
cd D:\Projects\Jarvis

# 2. Install dependencies
pip install -r jarvis\requirements.txt

# 3. Install and start Ollama
# Download from https://ollama.com
ollama pull deepseek-r1:8b
ollama serve

# 4. Copy and fill .env
copy .env.example .env
# Edit .env with your preferences

# 5. Run
python -m jarvis.main
```

### .env Configuration

Required:
```env
JARVIS_NAME=JARVIS
USER_NAME=YourName
USER_LOCATION=YourCity
OLLAMA_MODEL=deepseek-r1:8b
```

Optional (enable features):
```env
OPENWEATHER_API_KEY=your_key        # Weather briefings
ELEVENLABS_API_KEY=your_key         # Premium voice
TELEGRAM_BOT_TOKEN=your_token       # Remote control from phone
GITHUB_TOKEN=your_token             # GitHub operations
GOOGLE_CREDENTIALS_PATH=./path      # Calendar, Gmail, Drive
```

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│  PERCEPTION  │───▶│    BRAIN     │───▶│     ACTION       │
│  LAYER       │    │    LAYER     │    │     LAYER        │
│              │    │              │    │                  │
│ - Wake Word  │    │ - LLM Core   │    │ - Computer Ctrl  │
│ - STT        │    │ - Tool Reg   │    │ - Google APIs    │
│ - VAD        │    │ - Context    │    │ - Git/GitHub     │
│ - Mute Detect│    │ - Memory     │    │ - Web Browser    │
└──────────────┘    └──────┬───────┘    │ - File System    │
                           │            │ - Messaging      │
┌──────────────┐    ┌──────▼───────┐    └──────────────────┘
│   OUTPUT     │◀───│    MEMORY    │
│   LAYER      │    │    LAYER     │
│              │    │              │
│ - TTS        │    │ - Short-term │
│ - Speaker    │    │ - Long-term  │
│              │    │ - Episodic   │
└──────────────┘    └──────────────┘
```

## Project Structure

```
jarvis/
├── main.py                    # Entry point — boots everything
├── config.py                  # Pydantic-settings config
├── requirements.txt
├── .env.example
│
├── perception/
│   ├── stt.py                 # Speech-to-text (faster-whisper)
│   ├── vad.py                 # Voice activity detection
│   ├── wake_word.py           # Wake word (openWakeWord)
│   └── mute_detector.py       # Microphone level monitor
│
├── output/
│   ├── tts.py                 # Edge TTS + ElevenLabs
│   ├── speaker.py             # Audio playback
│   └── hud.py                 # [Stub — Phase 11]
│
├── brain/
│   ├── llm.py                 # Ollama wrapper
│   ├── context_builder.py     # Builds system prompt with context
│   ├── tool_registry.py       # All registered tools
│   ├── router.py              # [Stub — Phase 3]
│   └── planner.py             # [Stub — Phase 10]
│
├── memory/
│   ├── short_term.py          # In-RAM conversation buffer
│   ├── long_term.py           # ChromaDB vector memory
│   ├── episodic.py            # SQLite: tasks, jobs, learning
│   └── user_profile.py        # JSON: preferences, facts, projects
│
├── agents/
│   ├── computer_control.py    # OS-level control (pyautogui)
│   ├── file_agent.py          # File system operations
│   ├── weather_agent.py       # Weather fetch + briefing
│   ├── google_agent.py        # Drive, Calendar, Gmail
│   ├── messaging_agent.py     # Telegram, WhatsApp
│   ├── dev_agent.py           # Project scaffolding, tests
│   ├── git_agent.py           # Git operations
│   ├── web_agent.py           # Search, scrape, research
│   ├── job_agent.py           # Job search, cover letters
│   └── learning_agent.py      # Language + skill tutoring
│
├── integrations/
│   ├── google/
│   │   ├── auth.py            # OAuth2 flow
│   │   ├── calendar.py
│   │   ├── drive.py
│   │   └── gmail.py
│   ├── github.py              # GitHub REST API
│   ├── telegram_bot.py        # Remote interface
│   ├── whatsapp.py            # WhatsApp Web automation
│   └── openweather.py         # Weather API
│
├── scheduler/
│   ├── jobs.py                # APScheduler management
│   └── briefing.py            # Morning/evening briefings
│
├── templates/prompts/
│   └── system_prompt.txt      # Voice-optimized prompt
│
├── data/                      # Persistent storage
└── logs/                      # Loguru output
```

## Complete Tool List (34 tools)

### Computer Control (6)
`open_app`, `close_app`, `run_command`, `take_screenshot`, `list_processes`, `kill_process`

### File Management (6)
`list_dir`, `create_dir`, `create_file`, `read_file`, `delete_file`, `search_files`

### Communication (7)
`get_weather`, `get_calendar`, `get_emails`, `send_email`, `search_emails`, `list_drive`, `send_whatsapp`

### Developer (8)
`create_project`, `write_tests`, `git_init`, `git_add`, `git_commit`, `git_push`, `git_status`, `git_branch`

### Web & Research (2)
`web_search`, `scrape_page`

### Jobs (2)
`search_jobs`, `cover_letter`

### Learning (3)
`start_learning`, `learning_progress`, `quiz`

## Roadmap

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation | ✅ Complete |
| 2 | Wake Word + Daemon | ✅ Complete |
| 3 | Memory + Context | ✅ Complete |
| 4 | Weather + Scheduler | ✅ Complete |
| 5 | Computer Control | ✅ Complete |
| 6 | Google Integrations | ✅ Complete |
| 7 | Messaging | ✅ Complete |
| 8 | Developer Tools + Git | ✅ Complete |
| 9 | Web Agent + Job Finder | ✅ Complete |
| 10 | Learning Companion | ✅ Complete |
| 11 | HUD + Polish | ✅ Complete |

## Auto-Start (Windows)

Run PowerShell as Administrator:
```powershell
.\setup_windows_autostart.ps1
```

## License

Private project. Not for distribution.
