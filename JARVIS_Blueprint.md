# PROJECT JARVIS — Architect's Blueprint
### A Truly Agentic, Always-On, Voice-First Personal AI System
*Designed for Dheeraj | Version 1.0*

---

## VISION

You don't want a chatbot. You want an operating system layer that lives between you and the digital world — one that talks, listens, thinks, acts, and remembers. This document is the complete architectural blueprint for that system. It covers every module, every integration, every design decision, and a phased roadmap to build it from scratch.

When your computer boots, JARVIS boots. It greets you. It tells you the weather. It waits. And the moment you speak, it acts.

This is not a wrapper around ChatGPT. This is infrastructure.

---

## PHILOSOPHY & DESIGN PRINCIPLES

1. **Voice-first, not voice-only** — JARVIS is primarily spoken. Text is a fallback, not the main channel.
2. **Agentic, not reactive** — JARVIS doesn't just answer. It plans, executes multi-step tasks, and reports back.
3. **Context-aware always** — JARVIS knows what you did yesterday, what project you're working on, and what you have on your calendar today.
4. **Local-first, cloud-smart** — Core processing runs locally. Heavy lifting or internet-dependent tasks use APIs.
5. **No hand-holding** — JARVIS doesn't ask "Are you sure?" for every action unless it's destructive. It acts.
6. **Failure is recoverable** — Every agent task has rollback or fallback behavior.
7. **Extensible by design** — Every module is a plugin. Adding a new capability should never require touching core code.

---

## SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        JARVIS SYSTEM                            │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  PERCEPTION  │───▶│    BRAIN     │───▶│     ACTION       │  │
│  │  LAYER       │    │    LAYER     │    │     LAYER        │  │
│  │              │    │              │    │                  │  │
│  │ - Wake Word  │    │ - LLM Core   │    │ - Computer Ctrl  │  │
│  │ - STT        │    │ - Router     │    │ - Google APIs    │  │
│  │ - Mute Detect│    │ - Planner    │    │ - Git/GitHub     │  │
│  │ - VAD        │    │ - Agent Orch │    │ - Web Browser    │  │
│  └──────────────┘    └──────┬───────┘    │ - File System    │  │
│                             │            │ - Messaging      │  │
│  ┌──────────────┐    ┌──────▼───────┐    └──────────────────┘  │
│  │   OUTPUT     │◀───│    MEMORY    │                          │
│  │   LAYER      │    │    LAYER     │                          │
│  │              │    │              │                          │
│  │ - TTS        │    │ - Short-term │                          │
│  │ - HUD/UI     │    │ - Long-term  │                          │
│  │ - Notifs     │    │ - Episodic   │                          │
│  └──────────────┘    └──────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

Every layer is a separate Python module. The Brain is the only thing that talks to all other layers. Nothing else is coupled.

---

## TECH STACK DECISIONS

These are not suggestions. These are the picks based on capability, cost, and community support.

| Component | Technology | Why |
|---|---|---|
| Language | Python 3.11+ | Ecosystem, AI libraries, speed of development |
| Wake Word | `openWakeWord` or `pvporcupine` | Lightweight, offline, accurate |
| Speech-to-Text | `faster-whisper` (local) | Free, fast, runs on CPU, Whisper quality |
| Text-to-Speech | ElevenLabs API (primary) / `Coqui TTS` (offline fallback) | ElevenLabs is best-in-class; Coqui works without internet |
| LLM - Local | Ollama + `Llama 3.1 8B` or `Qwen2.5 7B` | Fast inference, runs on 8GB VRAM or CPU |
| LLM - Cloud | Claude API (complex tasks) | Best reasoning, tool use |
| Agent Framework | LangGraph | Stateful agents, conditional logic, loops |
| Vector Memory | ChromaDB | Local, no cost, persistent |
| Computer Control | `pyautogui`, `pygetwindow`, `subprocess` | Cross-platform GUI control |
| Web Automation | Playwright | Better than Selenium, async support |
| Google APIs | `google-api-python-client` | Official SDK |
| Telegram | `python-telegram-bot` | Well-maintained, async |
| WhatsApp | WhatsApp Web via Playwright | No official API for personal use |
| Git | `gitpython` + GitHub REST API | Full git operations |
| Job Search | LinkedIn scraper / Adzuna API | Job finding agent |
| Scheduler | `APScheduler` | Cron-like jobs inside Python |
| Config | `.env` + `pydantic-settings` | Type-safe config management |
| Daemon | `systemd` (Linux) / Task Scheduler (Windows) / `launchd` (Mac) | OS-level boot |
| Internal Comms | FastAPI (local HTTP) | Modules talk via local REST |
| Logging | `loguru` | Better than stdlib logging |

---

## FULL FEATURE LIST

### 🎙️ VOICE & PERCEPTION
- **Wake word detection** — "Hey JARVIS" triggers listening. Customizable.
- **Always-listening mode** — Low CPU loop waiting for wake word. Sub-100ms detection.
- **Voice Activity Detection (VAD)** — Stops recording when you stop talking. No manual press.
- **Mute detection** — Monitors microphone input level. If you're on a call or muted, JARVIS stays silent unless spoken to via text.
- **Multi-language STT** — Whisper supports Hindi, English, and more. JARVIS can understand Hinglish.
- **Noise suppression** — Pre-process audio through `noisereduce` before transcription.

### 🗣️ VOICE OUTPUT
- **Custom JARVIS voice** — ElevenLabs voice cloning or a pre-built deep, calm, authoritative voice. Not robotic.
- **Emotional tone control** — Different tones for alerts, learning mode, casual chat, task completion.
- **Streaming TTS** — Starts speaking while still generating. No full-response wait.
- **Interrupt handling** — If you speak while JARVIS is talking, it stops and listens.
- **Offline fallback** — Coqui TTS kicks in if no internet. Slightly lower quality but functional.

### 🧠 BRAIN & REASONING
- **Router LLM** — Small, fast model that reads your command and routes it to the right agent/tool. Happens in under 1 second.
- **Planner** — For complex multi-step tasks, LangGraph planner breaks it into steps, executes sequentially, handles failures.
- **Tool calling** — LLM can invoke any registered tool. Tools are Python functions with type hints and docstrings.
- **Context injection** — Every LLM call includes: current time, today's weather, active project context, recent conversation, upcoming calendar events.
- **Dual LLM strategy** — Simple queries (weather, calculations, quick answers) → local Ollama. Complex tasks (vibe coding, research, writing) → Claude API. Cost-optimized.
- **Fallback chain** — If Claude API is down or rate-limited, falls back to local model automatically.

### 🧩 MEMORY SYSTEM
- **Conversation memory** — Last N turns kept in RAM for context. Configurable window.
- **Long-term vector memory** — ChromaDB stores embedded summaries of past conversations. JARVIS can recall things you told it months ago.
- **Episodic memory** — Structured log of completed tasks: "Pushed `feature-auth` branch to GitHub on March 15", "Created project `trading-bot` in `/projects/trading`."
- **User profile** — Stored preferences: your name, your projects, your voice preferences, your working hours, mute schedules.
- **Project context** — When you say "continue working on the trading bot," JARVIS loads all stored context for that project: tech stack, last state, open TODOs.
- **Learning progress** — For language or skill learning sessions, JARVIS tracks what was covered, quiz scores, next lesson state.

### 💻 COMPUTER CONTROL
- **Open/close applications** — "JARVIS, open VS Code" → `subprocess.Popen` or OS-specific launcher.
- **Window management** — Bring apps to foreground, resize, minimize.
- **File system operations** — Create folders, move files, delete, rename, search by name or content.
- **Screenshot + Vision** — Takes screenshot, sends to vision LLM, gets description. "JARVIS, what's on my screen?" works.
- **Keyboard/mouse automation** — Types text into apps, clicks buttons, fills forms. Full GUI automation.
- **System commands** — Shutdown, restart, sleep, volume control, brightness (platform-specific).
- **Run terminal commands** — You say it, JARVIS runs it in a subprocess and reads back the output.
- **Process management** — Kill a process by name, check CPU/memory usage.

### 📁 FILE & PROJECT MANAGEMENT
- **Create project scaffolding** — "Create a Flask REST API project in `/projects/myapi`" → JARVIS creates the full folder structure, `requirements.txt`, `README.md`, boilerplate `app.py`, `.gitignore`, `.env.example`.
- **Specify any folder** — You tell it where. It goes there.
- **Template library** — Pre-built templates for: Python CLI tool, FastAPI backend, React frontend, Spring Boot microservice, n8n workflow, data science notebook.
- **File search** — "Find all Python files modified this week in my projects folder."
- **Bulk operations** — Rename 100 files by pattern, organize photos by date, sort downloads folder.

### 🔧 DEVELOPER TOOLS (VIBE CODING MODE)
- **Pair programmer** — You describe what you want to build. JARVIS writes the code, explains every decision, and places files in the right locations.
- **Code review** — "Review this file" → reads it, spots issues, suggests improvements, explains.
- **Debug assistant** — Paste an error. JARVIS traces it, identifies root cause, suggests fix, writes the fix.
- **Refactor** — "Refactor this function to be async" → reads, rewrites, explains changes.
- **Documentation generator** — Writes docstrings, README, API docs from your code.
- **Test writer** — Generates unit tests for any function or module.
- **Git operations:**
  - `git init`, `git add`, `git commit -m "..."` — all via voice
  - Push to remote: "Push current branch to GitHub"
  - Create new branch: "Create branch `feature-auth`"
  - PR creation via GitHub REST API
  - Read diff: "What changed since last commit?"
- **GitHub operations:**
  - Create new repo (public/private) via API
  - Create issues
  - Read open issues and PRs
  - Star, fork, clone repos

### 🌦️ WEATHER & BRIEFINGS
- **Proactive morning briefing** — Every morning at your configured time, JARVIS speaks unprompted:
  - "Good morning Dheeraj. It's 8 AM. Today in Mysore it's 26°C, partly cloudy. You have two meetings — a standup at 10 and a 1:1 at 3. Three emails need your attention. Your top task today based on yesterday is finishing the auth module."
- **On-demand weather** — "JARVIS, weather in Bangalore this weekend?" → fetched and spoken.
- **Rain/storm alerts** — Proactively warns you if bad weather is forecasted.
- **API:** OpenWeatherMap (free tier works for personal use).

### 📅 GOOGLE CALENDAR
- **Read events** — "What do I have tomorrow?"
- **Create events** — "Book a meeting with Rahul on Friday at 3 PM for 1 hour, title: API discussion."
- **Update/cancel events** — "Move my 3 PM to 4 PM."
- **Smart scheduling** — "Find a free 2-hour slot this week and block it for deep work."
- **Reminders** — JARVIS speaks a reminder 15 minutes before any event.

### 📧 GMAIL
- **Read emails** — "Any important emails today?" → JARVIS summarizes unread emails, highlights urgent ones.
- **Compose and send** — "Email Priya that I'll be 10 minutes late, keep it short."
- **Reply** — "Reply to Rahul's last email, tell him the PR is ready for review."
- **Search** — "Find the email about the AWS invoice from last month."
- **Draft mode** — JARVIS drafts, reads it back, asks for confirmation before sending.

### 📂 GOOGLE DRIVE
- **Upload files/folders** — "Upload the photos in `/photos/goa-trip` to Drive in a folder called Goa 2025."
- **Download** — "Download the Q3 report from Drive to my Downloads folder."
- **Search** — "Find the spreadsheet I shared with the team last week."
- **Organize** — "Move all PDFs in my Drive root to a folder called Documents."
- **Share** — "Share the project folder with rahul@example.com with editor access."

### 💬 MESSAGING
- **Telegram:**
  - Send messages to any contact or group
  - Read latest messages from a person
  - Send files, photos, links
  - Set up a Telegram bot as JARVIS's remote interface — message JARVIS from your phone when away from PC
- **WhatsApp:**
  - Via WhatsApp Web automation (Playwright)
  - Send messages to contacts
  - Send media
  - Note: WhatsApp Web must be logged in once. Sessions persist.
- **Upcoming:** Matrix/Signal support can be added as plugins.

### 🔍 WEB & RESEARCH AGENT
- **Web search** — "Search for the latest LangGraph tutorials" → searches, reads top results, summarizes.
- **Deep research** — "Research the best vector databases in 2025" → visits multiple pages, synthesizes, gives structured report.
- **Fact-checking** — "Is this true: X?" → searches, validates, responds with sources.
- **Content summarization** — "Summarize this article: [URL]" → fetches, strips, summarizes.
- **Competitor research, market research, technical research** — all via Playwright + LLM.

### 💼 JOB FINDER AGENT
- **Search jobs** — "Find Senior Java Engineer roles in Bangalore above 30 LPA."
- **Sources** — LinkedIn (scraping), Naukri API, Adzuna API, Indeed scraping.
- **Filter** — By location, salary, company size, remote/hybrid.
- **Save to file** — Outputs a structured list to a CSV or JSON in your specified folder.
- **Track applications** — Maintains a SQLite DB of jobs you've applied to, status, follow-up dates.
- **Resume tailor** — Given a job description, rewrites your resume bullet points to match. Outputs a `.docx`.
- **Cover letter** — Generates a custom cover letter for any JD.

### 🎓 LEARNING COMPANION
- **Language learning** — "I want to learn Japanese. Start from basics."
  - JARVIS structures a full curriculum
  - Teaches one concept per session via conversation
  - Asks questions, waits for your response, corrects pronunciation via STT
  - Tracks progress: vocabulary learned, grammar covered, next lesson
  - Uses spaced repetition logic for vocab review
- **Programming tutoring** — "Teach me LangGraph from scratch."
  - Explains concepts, gives code examples, runs them, shows output
  - Interactive exercises: "Now you write a function that does X"
  - Reviews your attempt, gives feedback
- **Session state persisted** — You can resume any learning session days later. JARVIS knows exactly where you left off.
- **Quiz mode** — "Quiz me on what I've learned in Japanese so far."

### ⏰ PROACTIVE & SCHEDULED TASKS
- **Morning briefing** — Configurable time. Weather + Calendar + Email summary + Top task.
- **Evening summary** — What was completed today. What's pending. Calendar for tomorrow.
- **Custom reminders** — "Remind me every day at 7 PM to track my workout."
- **Recurring tasks** — "Every Monday morning, fetch the top 5 AI news stories and brief me."
- **Idle check-ins** — If you've been inactive for X hours during working hours, JARVIS asks if you need help getting started.
- **Bill reminders, subscription tracking** — Add manually or parse from Gmail.

### 🖥️ OPTIONAL HUD (Heads-Up Display)
- A lightweight always-on-top transparent overlay on your screen.
- Shows: current JARVIS status (listening / thinking / speaking), today's weather, time, active task, upcoming calendar event.
- Built with `tkinter` or `PyQt6` or a local web UI served on `localhost:7474` that auto-opens on boot.
- Iron Man-inspired: dark, minimal, glowing accents. Feels like a real HUD.

---

## PROJECT FOLDER STRUCTURE

```
jarvis/
│
├── main.py                    # Entry point. Boots everything.
├── config.py                  # Loads .env, pydantic-settings model
├── .env                       # All secrets (never commit this)
├── requirements.txt
├── README.md
│
├── perception/
│   ├── wake_word.py           # Wake word detection loop
│   ├── stt.py                 # Speech-to-text (faster-whisper)
│   ├── vad.py                 # Voice activity detection
│   └── mute_detector.py       # Microphone level monitor
│
├── output/
│   ├── tts.py                 # ElevenLabs + Coqui fallback
│   ├── speaker.py             # Audio playback, interrupt handling
│   └── hud.py                 # Optional overlay UI
│
├── brain/
│   ├── router.py              # Routes intent to correct agent
│   ├── planner.py             # Multi-step task planner (LangGraph)
│   ├── llm.py                 # LLM abstraction (Ollama / Claude)
│   ├── context_builder.py     # Builds system prompt with context
│   └── tool_registry.py       # All registered tools in one place
│
├── memory/
│   ├── short_term.py          # In-RAM conversation buffer
│   ├── long_term.py           # ChromaDB vector memory
│   ├── episodic.py            # SQLite log of completed tasks
│   └── user_profile.py        # Preferences, projects, settings
│
├── agents/
│   ├── computer_control.py    # OS-level control agent
│   ├── file_agent.py          # File system operations
│   ├── dev_agent.py           # Vibe coding, project scaffolding
│   ├── git_agent.py           # Git + GitHub operations
│   ├── google_agent.py        # Drive, Calendar, Gmail
│   ├── messaging_agent.py     # Telegram, WhatsApp
│   ├── web_agent.py           # Search, browse, research
│   ├── weather_agent.py       # Weather fetch + briefing
│   ├── job_agent.py           # Job search + tracking
│   └── learning_agent.py      # Language + skill tutoring
│
├── integrations/
│   ├── google/
│   │   ├── auth.py            # OAuth2 flow
│   │   ├── drive.py
│   │   ├── calendar.py
│   │   └── gmail.py
│   ├── github.py              # GitHub REST API wrapper
│   ├── telegram_bot.py        # Remote interface from phone
│   ├── whatsapp.py            # WhatsApp Web automation
│   └── openweather.py
│
├── scheduler/
│   ├── jobs.py                # All scheduled jobs (APScheduler)
│   └── briefing.py            # Morning/evening briefing logic
│
├── templates/
│   ├── projects/
│   │   ├── fastapi/           # FastAPI boilerplate
│   │   ├── flask/
│   │   ├── react/
│   │   ├── springboot/
│   │   └── cli_tool/
│   └── prompts/               # System prompt templates
│
├── data/
│   ├── chroma_db/             # Vector memory store
│   ├── jarvis.db              # SQLite: episodic memory, jobs, learning
│   └── user_profile.json
│
└── logs/
    └── jarvis.log             # Loguru output
```

---

## DATA FLOW — HOW A REQUEST IS PROCESSED

This is what happens from the moment you say "Hey JARVIS, create a Python project called ImageSorter in /projects and push it to a new GitHub repo."

```
1. wake_word.py detects "Hey JARVIS"
         │
         ▼
2. vad.py starts recording until silence
         │
         ▼
3. stt.py (faster-whisper) transcribes audio → text
         │
         ▼
4. context_builder.py adds: time, weather, calendar, recent memory
         │
         ▼
5. router.py sends to LLM → identifies intent: "create_project + git_push"
         │
         ▼
6. planner.py (LangGraph) breaks it into steps:
   Step 1: Create /projects/ImageSorter with Python template
   Step 2: Initialize git repo
   Step 3: Create GitHub repo via API
   Step 4: Add remote, commit, push
         │
         ▼
7. Each step runs via the relevant agent:
   → file_agent.py: creates folder + files
   → git_agent.py: git init, add, commit
   → github.py: creates repo "ImageSorter"
   → git_agent.py: adds remote, pushes
         │
         ▼
8. episodic.py logs: "Created ImageSorter project + pushed to GitHub at 3:14 PM"
         │
         ▼
9. tts.py speaks: "Done. ImageSorter is live on GitHub. The repo is at
   github.com/dheeraj/ImageSorter. I've pushed an initial commit with
   the Python CLI template."
```

Total time: 15-30 seconds for a task this complex. Most simple commands: under 5 seconds.

---

## BOOT SEQUENCE

When your PC starts, this is what happens:

1. OS runs the JARVIS startup service (systemd / Task Scheduler).
2. `main.py` initializes all modules, checks API keys, loads user profile, loads memory.
3. The HUD (if enabled) appears on screen — minimal, dark, glowing.
4. JARVIS speaks the boot greeting (ElevenLabs voice, custom audio):

> *"JARVIS online. All systems nominal. Good morning, Dheeraj. It's Monday, 8:15 AM. 24 degrees in Mysore today, clear skies. You have a standup at 10 AM. Two unread emails flagged for attention. Ready."*

5. Wake word listener goes active. JARVIS is now waiting.

---

## STARTUP SETUP (OS-LEVEL DAEMON)

**Linux (systemd):**
```ini
# /etc/systemd/system/jarvis.service
[Unit]
Description=JARVIS AI Assistant
After=network.target sound.target

[Service]
Type=simple
User=dheeraj
WorkingDirectory=/home/dheeraj/jarvis
ExecStart=/home/dheeraj/jarvis/venv/bin/python main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Run: `sudo systemctl enable jarvis && sudo systemctl start jarvis`

**Windows:**
Task Scheduler → New Task → Trigger: "At log on" → Action: Run `pythonw.exe main.py` in jarvis directory.

**Mac:**
`launchd` plist file in `~/Library/LaunchAgents/`. Auto-starts on login.

---

## CONFIGURATION (.env)

```env
# Identity
JARVIS_NAME=JARVIS
USER_NAME=Dheeraj
USER_LOCATION=Mysore, India
WORKING_HOURS_START=9
WORKING_HOURS_END=21

# Voice
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=your_voice_id
WAKE_WORD=hey jarvis
STT_MODEL=base.en              # faster-whisper model size

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
CLAUDE_API_KEY=your_key
LLM_MODE=hybrid                # local / cloud / hybrid

# Integrations
OPENWEATHER_API_KEY=your_key
GITHUB_TOKEN=your_token
GITHUB_USERNAME=dheeraj
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Google (path to OAuth credentials)
GOOGLE_CREDENTIALS_PATH=./integrations/google/credentials.json

# Paths
PROJECTS_ROOT=/home/dheeraj/projects
DOWNLOADS_FOLDER=/home/dheeraj/Downloads

# Scheduling
MORNING_BRIEFING_TIME=08:00
EVENING_SUMMARY_TIME=21:00
```

---

## AGENT DESIGN PATTERN

Every agent follows the same interface. This is what makes JARVIS extensible — adding a new agent never touches existing code.

```python
# agents/base_agent.py
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    name: str
    description: str  # Used by router to understand when to call this agent
    
    @abstractmethod
    async def execute(self, task: str, context: dict) -> AgentResult:
        """
        task: natural language description of what to do
        context: current system context (time, memory, user prefs)
        returns: AgentResult with success, message, data
        """
        pass
    
    async def rollback(self, task_id: str):
        """Optional: undo last action if failed"""
        pass
```

Every agent: `DevAgent`, `GitAgent`, `GoogleAgent`, `WebAgent`, etc. — implements this interface. The planner calls them without knowing how they work internally.

---

## TELEGRAM AS MOBILE REMOTE

This is crucial — when you're away from your PC, you still have JARVIS.

Set up a Telegram bot (`@YourJarvisBot`). JARVIS runs a Telegram listener in the background. When you message your bot:

- "JARVIS, what's on my calendar tomorrow?" → responds in Telegram
- "JARVIS, push the current branch" → executes on your PC, responds in Telegram
- "JARVIS, send an email to Priya..." → done remotely
- "JARVIS, what files are in my Downloads?" → responds with list

Your PC becomes a server that JARVIS controls via Telegram. Full remote capability.

---

## WHATSAPP INTEGRATION (IMPORTANT NOTE)

WhatsApp has no official API for personal accounts. The approach:
- Use **Playwright** to automate WhatsApp Web (`web.whatsapp.com`)
- Log in once via QR code. Session cookie persists.
- JARVIS opens a headless browser, navigates to the contact, sends the message.
- Limitation: WhatsApp can ban accounts for automation abuse. Use responsibly — low frequency.
- Alternative: Use **WhatsApp Business API** if you have a business account (free tier available).

---

## VIBE CODING MODE — DEEP DIVE

When you say "Let's build X" or "I want to code Y with you":

1. JARVIS enters `dev_agent` mode — dedicated context window for this session.
2. It asks clarifying questions upfront: "What's the tech stack? What should it do? Any constraints?"
3. It proposes the file structure. You confirm or adjust.
4. It writes files one by one, explains each, and places them in the target folder.
5. It can run the code (`subprocess`) and read the output back to you.
6. If there's an error, it reads the traceback, identifies the fix, applies it.
7. It tracks a TODO list of what's been done and what's next in the session.
8. At any point: "JARVIS, commit what we have so far" → git commit with auto-generated commit message.
9. At end: "JARVIS, we're done" → writes a session summary to episodic memory. Pushes to GitHub if asked.

---

## LEARNING COMPANION MODE — DEEP DIVE

Say: "JARVIS, I want to learn Japanese. Let's start."

JARVIS:
1. Checks episodic memory — have you started Japanese before? Loads progress.
2. If fresh: builds a structured curriculum (Hiragana → Katakana → Basic grammar → N5 vocabulary → etc.)
3. Begins the session: explains the first concept verbally and displays it in the HUD.
4. Asks you to repeat or answer.
5. Listens to your response via STT, evaluates correctness.
6. Provides correction and encouragement.
7. Tracks: vocabulary learned, grammar rules covered, accuracy scores.
8. At end of session: "We covered 12 new Hiragana characters today. Your accuracy was 83%. Next session starts with the remaining 6."
9. Proactively schedules the next session: "I've blocked 30 minutes tomorrow at 8 PM for Japanese. Want me to send a Telegram reminder?"

Same pattern for: programming languages, DSA, system design, any topic.

---

## PHASES — BUILD ROADMAP

### PHASE 1: FOUNDATION (Week 1–2)
**Goal:** JARVIS boots, listens, responds via voice. Basic Q&A works.

- Set up Python environment, Ollama, `faster-whisper`, ElevenLabs.
- Build `perception/stt.py` and `output/tts.py`.
- Build `brain/llm.py` — wraps Ollama. Simple call-response.
- Build `main.py` — basic loop: record → transcribe → LLM → speak.
- Test end-to-end: ask a question by voice, get spoken response.

**Milestone:** You say "What's 2+2?" JARVIS speaks back "Four."

---

### PHASE 2: WAKE WORD + DAEMON (Week 3)
**Goal:** JARVIS is always-on. You don't press anything.

- Integrate `openWakeWord` for "hey jarvis" detection.
- Add VAD to detect silence and stop recording.
- Set up OS daemon (systemd / Task Scheduler).
- Add mute detection (monitor mic input level).
- Boot greeting with ElevenLabs voice.

**Milestone:** PC boots. JARVIS speaks. You say "Hey JARVIS, good morning." It responds.

---

### PHASE 3: MEMORY + CONTEXT (Week 4)
**Goal:** JARVIS remembers what you said 5 minutes ago and 5 days ago.

- Build `memory/short_term.py` — conversation buffer.
- Build `memory/long_term.py` — ChromaDB integration.
- Build `memory/user_profile.py` — load/save preferences.
- Inject context into every LLM call.
- Test: tell JARVIS your name and favorite project. Close and reopen. Ask "What's my name?" — it should remember.

**Milestone:** Context-aware, persistent memory works.

---

### PHASE 4: WEATHER + SCHEDULER (Week 5)
**Goal:** Proactive briefings. JARVIS speaks unprompted.

- Build `agents/weather_agent.py` — OpenWeatherMap integration.
- Build `scheduler/briefing.py` — morning + evening briefings.
- Set up `APScheduler` in `main.py`.
- Add on-demand weather: "Hey JARVIS, weather tomorrow?"

**Milestone:** 8 AM — JARVIS speaks your morning briefing without being asked.

---

### PHASE 5: COMPUTER CONTROL (Week 6–7)
**Goal:** JARVIS controls your PC.

- Build `agents/computer_control.py` — open apps, manage windows.
- Build `agents/file_agent.py` — create, move, rename, search files.
- Integrate `pyautogui` for keyboard/mouse.
- Add screenshot + vision: send screenshot to Claude vision API.
- Test: "Open VS Code", "Create folder /projects/test", "What's on my screen?"

**Milestone:** JARVIS opens VS Code, creates a folder, reads your screen.

---

### PHASE 6: GOOGLE INTEGRATIONS (Week 8)
**Goal:** Drive, Calendar, Gmail — fully working.

- Complete OAuth2 flow in `integrations/google/auth.py`.
- Build `calendar.py`, `drive.py`, `gmail.py`.
- Build `agents/google_agent.py` — routes calendar/drive/gmail tasks.
- Test all operations: create event, upload file, send email.

**Milestone:** "Book a meeting Friday 3 PM with Rahul" works end-to-end.

---

### PHASE 7: MESSAGING (Week 9)
**Goal:** Telegram fully working. WhatsApp basic working.

- Set up Telegram bot + listener in `integrations/telegram_bot.py`.
- Build `agents/messaging_agent.py`.
- Implement WhatsApp Web automation via Playwright.
- Test: "Message Rahul on Telegram that I'll be late."

**Milestone:** JARVIS sends a Telegram message. Remote control from your phone works.

---

### PHASE 8: DEVELOPER TOOLS + GIT (Week 10–11)
**Goal:** Full vibe coding and Git workflow via voice.

- Build `agents/dev_agent.py` — project scaffolding, code writing, code review.
- Build `agents/git_agent.py` — full git operations via GitPython.
- Build GitHub REST integration for repo creation, PRs.
- Add project templates to `templates/projects/`.
- Test full flow: "Create a FastAPI project in /projects/api and push to GitHub."

**Milestone:** Complete project created and pushed to GitHub via voice.

---

### PHASE 9: WEB AGENT + JOB FINDER (Week 12)
**Goal:** JARVIS browses the web, finds jobs, does research.

- Build `agents/web_agent.py` — Playwright-based browser + search.
- Build `agents/job_agent.py` — job search, SQLite tracking, resume tailoring.
- Test: "Find Java engineer roles above 30 LPA in Bangalore" → structured output.

**Milestone:** Job list saved to CSV. Resume tailored for a specific JD.

---

### PHASE 10: LEARNING COMPANION + LangGraph PLANNER (Week 13–14)
**Goal:** Full multi-step planning. Learning sessions work.

- Build `agents/learning_agent.py` with curriculum + progress tracking.
- Build `brain/planner.py` — LangGraph stateful agent with conditional routing.
- Upgrade `brain/router.py` to use planner for complex multi-step commands.
- Test: "JARVIS, teach me Python decorators" → full interactive session.

**Milestone:** Multi-step tasks execute correctly. Learning sessions are persistent.

---

### PHASE 11: HUD + POLISH (Week 15–16)
**Goal:** It feels like Iron Man's JARVIS.

- Build HUD overlay (PyQt6 or local web UI).
- Add Iron Man boot sound + animation on startup.
- Add interrupt handling in TTS (stop speaking when you start talking).
- Add JARVIS personality to all system prompts — calm, confident, precise.
- Add graceful degradation for all failures.
- Logging, error reporting, restart-on-crash.

**Milestone:** JARVIS feels production-grade. Shows off to anyone who sees your screen.

---

## TOTAL ESTIMATED TIMELINE
**16 weeks of focused weekend + evening work.** Each phase has a clear, testable milestone. You never have a half-built system — every phase adds something real that works.

---

## WHAT MAKES THIS YOUR OWN

This isn't a product. It's your infrastructure. It knows your name, your projects, your calendar, your learning goals, your GitHub username, your Telegram. It grows with you. Every new integration is one file. Every new command is one tool registered in `tool_registry.py`.

You'll never go back to Googling things manually. You'll never manually push to GitHub again. You'll never miss a meeting again. You'll never not know the weather. You'll have a coding partner available 24/7 who never gets tired and never judges.

And when someone asks "How'd you build that?" — you say: "My AI did most of it."

That's the goal. Go build it.

---

*Blueprint authored by Claude | April 2026*
*For questions on any module — ask. I'll architect every single piece.*
