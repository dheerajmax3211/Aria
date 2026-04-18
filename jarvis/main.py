import signal
import sys
from datetime import datetime
from loguru import logger

from jarvis.config import settings
from jarvis.perception.vad import VoiceActivityDetector
from jarvis.perception.stt import SpeechToText
from jarvis.perception.wake_word import WakeWordDetector
from jarvis.perception.mute_detector import MuteDetector
from jarvis.output.tts import TextToSpeech
from jarvis.output.hud import HUDServer
from jarvis.brain.llm import LLMCore
from jarvis.brain.context_builder import ContextBuilder
from jarvis.brain.tool_registry import ToolRegistry
from jarvis.brain.router import IntentRouter
from jarvis.brain.planner import TaskPlanner
from jarvis.brain.architect import ArchitectAgent
from jarvis.brain.emotional_intelligence import EmotionalIntelligence
from jarvis.memory.journal import Journal
from jarvis.memory.short_term import ShortTermMemory
from jarvis.memory.graph_memory import GraphMemoryAgent
from jarvis.memory.user_profile import UserProfile
from jarvis.agents.weather_agent import WeatherAgent
from jarvis.agents.computer_control import ComputerControlAgent
from jarvis.agents.file_agent import FileAgent
from jarvis.agents.google_agent import GoogleAgent
from jarvis.agents.messaging_agent import MessagingAgent
from jarvis.agents.dev_agent import DevAgent
from jarvis.agents.git_agent import GitAgent
from jarvis.agents.web_agent import WebAgent
from jarvis.agents.job_agent import JobAgent
from jarvis.agents.learning_agent import LearningAgent
from jarvis.integrations.github import GitHubIntegration
from jarvis.scheduler.jobs import SchedulerJobs
from jarvis.scheduler.briefing import BriefingGenerator


def setup_logging() -> None:
    """Configures the loguru logger with console and file handlers."""
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | <level>{message}</level>")
    logger.add("logs/jarvis.log", rotation="10 MB", level="DEBUG", encoding="utf-8")


def get_time_greeting() -> str:
    """Returns an appropriate time-based greeting (morning, afternoon, or evening)."""
    hour = datetime.now().hour
    if hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    else:
        return "evening"


def main() -> None:
    setup_logging()
    logger.info(f"Starting {settings.jarvis_name}...")
    logger.info(f"User: {settings.user_name} | Location: {settings.user_location}")

    logger.info("Initializing modules...")
    vad = VoiceActivityDetector()
    stt = SpeechToText()
    tts = TextToSpeech()
    llm = LLMCore()
    wake_word = WakeWordDetector()
    mute_detector = MuteDetector()

    short_term = ShortTermMemory(max_turns=20)
    graph_memory = GraphMemoryAgent()
    user_profile = UserProfile()
    journal = Journal()
    emotional = EmotionalIntelligence(journal=journal)

    weather_agent = WeatherAgent()
    computer_control = ComputerControlAgent()
    file_agent = FileAgent()
    google_agent = GoogleAgent()

    context_builder = ContextBuilder(user_profile, short_term, graph_memory, journal, emotional, weather_agent, google_agent)
    messaging_agent = MessagingAgent(llm=llm)
    dev_agent = DevAgent()
    git_agent = GitAgent()
    web_agent = WebAgent()
    job_agent = JobAgent()
    learning_agent = LearningAgent(user_profile)

    architect = ArchitectAgent(user_name=settings.user_name)

    github = None
    if settings.github_token and settings.github_username:
        github = GitHubIntegration(settings.github_token, settings.github_username)
        logger.info("GitHub integration initialized")
    else:
        logger.warning("GitHub token not set, GitHub integration disabled")

    tool_registry = ToolRegistry()
    tool_registry.register_tool("open_app", computer_control.open_application, "Open an application by name or path", ["app_name"])
    tool_registry.register_tool("close_app", computer_control.close_application, "Close an application by process name", ["app_name"])
    tool_registry.register_tool("run_command", computer_control.run_command, "Run a terminal command and return output", ["command"])
    tool_registry.register_tool("take_screenshot", computer_control.take_screenshot, "Take a screenshot and save to file", ["filepath"])
    tool_registry.register_tool("analyze_screen", computer_control.analyze_screenshot, "Take a screenshot and describe what is on screen", ["filepath"])
    tool_registry.register_tool("type_text", computer_control.type_text, "Type text into the active window", ["text"])
    tool_registry.register_tool("click_at", computer_control.click_at, "Click at screen coordinates", ["x", "y"])
    tool_registry.register_tool("press_key", computer_control.press_key, "Press a keyboard key", ["key"])
    tool_registry.register_tool("hotkey", computer_control.hotkey, "Press a keyboard shortcut", ["keys"])
    tool_registry.register_tool("scroll", computer_control.scroll, "Scroll up or down", ["clicks"])
    tool_registry.register_tool("list_processes", computer_control.list_processes, "List running processes", [])
    tool_registry.register_tool("kill_process", computer_control.kill_process, "Kill a process by name", ["process_name"])
    tool_registry.register_tool("get_system_info", computer_control.get_system_info, "Get CPU and memory usage", [])
    tool_registry.register_tool("bring_window", computer_control.bring_to_foreground, "Bring a window to foreground", ["window_title"])
    tool_registry.register_tool("minimize_window", computer_control.minimize_window, "Minimize a window", ["window_title"])
    tool_registry.register_tool("maximize_window", computer_control.maximize_window, "Maximize a window", ["window_title"])
    tool_registry.register_tool("list_dir", file_agent.list_directory, "List files and folders in a directory", ["path"])
    tool_registry.register_tool("create_dir", file_agent.create_directory, "Create a new directory", ["path"])
    tool_registry.register_tool("create_file", file_agent.create_file, "Create a file with content", ["path", "content"])
    tool_registry.register_tool("read_file", file_agent.read_file, "Read file contents", ["path"])
    tool_registry.register_tool("delete_file", file_agent.delete_file, "Delete a file or directory", ["path"])
    tool_registry.register_tool("move_file", file_agent.move_file, "Move a file or directory", ["source", "destination"])
    tool_registry.register_tool("rename_file", file_agent.rename_file, "Rename a file", ["old_path", "new_name"])
    tool_registry.register_tool("search_files", file_agent.search_files, "Search for files by glob pattern", ["pattern", "path"])
    tool_registry.register_tool("get_file_info", file_agent.get_file_info, "Get file size, modification date, type", ["path"])
    tool_registry.register_tool("get_weather", weather_agent.get_current, "Get current weather for user location", [])
    tool_registry.register_tool("get_weather_forecast", weather_agent.get_forecast, "Get weather forecast for upcoming days", ["days"])
    tool_registry.register_tool("get_calendar", google_agent.get_calendar_events, "Get upcoming calendar events", [])
    tool_registry.register_tool("get_emails", google_agent.get_unread_emails, "Get unread email summary", [])
    tool_registry.register_tool("send_email", google_agent.send_email, "Send an email", ["to", "subject", "body"])
    tool_registry.register_tool("search_emails", google_agent.search_emails, "Search emails by query", ["query"])
    tool_registry.register_tool("list_drive", google_agent.list_drive_files, "List recent Google Drive files", [])
    tool_registry.register_tool("create_drive_folder", google_agent.create_folder, "Create a folder in Google Drive", ["folder_name"])
    tool_registry.register_tool("share_drive_file", google_agent.share_file, "Share a Drive file with someone", ["file_id", "email", "role"])
    tool_registry.register_tool("reply_to_email", google_agent.reply_to_email, "Reply to an email", ["message_id", "reply_body"])
    tool_registry.register_tool("create_email_draft", google_agent.create_draft, "Create an email draft for review", ["to", "subject", "body"])
    tool_registry.register_tool("find_free_calendar_slot", google_agent.find_free_slot, "Find a free time slot in calendar", ["duration_minutes"])
    tool_registry.register_tool("cancel_calendar_event", google_agent.cancel_event, "Cancel a calendar event", ["event_id"])
    tool_registry.register_tool("send_whatsapp", messaging_agent.send_whatsapp, "Send WhatsApp message to contact", ["contact_name", "message"])
    tool_registry.register_tool("create_project", dev_agent.create_project_scaffold, "Create a project scaffold (python, fastapi, react, cli_tool)", ["path", "project_type"])
    tool_registry.register_tool("review_code", dev_agent.review_code, "Review code for issues and improvements", ["file_path"])
    tool_registry.register_tool("debug_code", dev_agent.debug_code, "Analyze code for bugs and errors", ["file_path", "error_message"])
    tool_registry.register_tool("refactor_code", dev_agent.refactor_code, "Get refactoring suggestions for code", ["file_path", "instruction"])
    tool_registry.register_tool("generate_docs", dev_agent.generate_docs, "Find documentation gaps in code", ["file_path"])
    tool_registry.register_tool("write_tests", dev_agent.write_tests, "Generate test stubs for a source file", ["file_path"])
    tool_registry.register_tool("git_init", git_agent.init_repo, "Initialize a git repository", ["path"])
    tool_registry.register_tool("git_add", git_agent.add_files, "Stage files for commit", ["path", "files"])
    tool_registry.register_tool("git_commit", git_agent.commit, "Commit staged changes with message", ["path", "message"])
    tool_registry.register_tool("git_push", git_agent.push, "Push to remote repository", ["path", "remote", "branch"])
    tool_registry.register_tool("git_status", git_agent.status, "Show git repository status", ["path"])
    tool_registry.register_tool("git_branch", git_agent.create_branch, "Create and switch to a new branch", ["path", "branch_name"])
    tool_registry.register_tool("git_diff", git_agent.diff, "Show changes since last commit", ["path"])
    tool_registry.register_tool("web_search", web_agent.search, "Search the web and return results", ["query"])
    tool_registry.register_tool("scrape_page", web_agent.scrape_page, "Scrape text content from a URL", ["url"])
    tool_registry.register_tool("summarize_url", web_agent.summarize_url, "Fetch and summarize content from a URL", ["url"])
    tool_registry.register_tool("search_jobs", job_agent.search_jobs, "Search for jobs by query and location", ["query", "location"])
    tool_registry.register_tool("cover_letter", job_agent.generate_cover_letter, "Generate a cover letter for a job", ["job_title", "company", "skills"])
    tool_registry.register_tool("start_learning", learning_agent.start_session, "Start or resume a learning session", ["subject"])
    tool_registry.register_tool("get_curriculum", learning_agent.get_curriculum, "Show the full curriculum for a subject", ["subject"])
    tool_registry.register_tool("learning_progress", learning_agent.get_progress, "Check learning progress for a subject", ["subject"])
    tool_registry.register_tool("next_lesson", learning_agent.next_lesson, "Get the next lesson for a subject", ["subject"])
    tool_registry.register_tool("quiz", learning_agent.quiz, "Start a quiz for a subject", ["subject", "num_questions"])
    tool_registry.register_tool("spaced_repetition", learning_agent.spaced_repetition_review, "Review items due for spaced repetition", ["subject"])
    tool_registry.register_tool("deep_research", web_agent.deep_research, "Research a topic across multiple pages and synthesize a report", ["query", "num_pages"])
    tool_registry.register_tool("fact_check", web_agent.fact_check, "Fact-check a claim by searching for sources", ["claim"])
    tool_registry.register_tool("competitor_research", web_agent.competitor_research, "Research competitors of a company", ["company", "industry"])
    tool_registry.register_tool("market_research", web_agent.market_research, "Research market size and trends for a topic", ["topic"])
    tool_registry.register_tool("tailor_resume", job_agent.tailor_resume, "Tailor resume to match a job description", ["job_description", "current_resume"])
    tool_registry.register_tool("export_resume", job_agent.export_resume, "Export tailored resume to file", ["tailored_content", "filepath"])
    tool_registry.register_tool("bulk_rename", file_agent.bulk_rename, "Rename multiple files by replacing a pattern", ["path", "pattern", "replacement"])
    tool_registry.register_tool("organize_files", file_agent.organize_by_extension, "Organize files into folders by extension", ["path"])
    tool_registry.register_tool("sort_downloads", file_agent.sort_downloads, "Sort downloads folder into categorized subfolders", ["downloads_path"])
    tool_registry.register_tool("star_repo", github.star_repo if github else lambda r: "GitHub not configured", "Star a GitHub repository", ["repo"])
    tool_registry.register_tool("fork_repo", github.fork_repo if github else lambda o, r: "GitHub not configured", "Fork a GitHub repository", ["owner", "repo"])
    tool_registry.register_tool("clone_repo", github.clone_repo if github else lambda u, p: "GitHub not configured", "Clone a GitHub repository", ["repo_url", "local_path"])
    tool_registry.register_tool("set_brightness", computer_control.set_brightness, "Set screen brightness level", ["level"])
    tool_registry.register_tool("sleep_system", computer_control.sleep_system, "Put the system to sleep", [])
    tool_registry.register_tool("restart_system", computer_control.restart_system, "Restart the system", [])
    tool_registry.register_tool("cancel_restart", computer_control.cancel_restart, "Cancel a pending restart", [])

    tool_registry.register_tool("add_todo", journal.add_todo, "Add a todo for today", ["task", "priority"])
    tool_registry.register_tool("complete_todo", journal.complete_todo, "Mark a todo as completed", ["task_id"])
    tool_registry.register_tool("get_todos", lambda: str(journal.get_todos()), "Get today's todos", [])
    tool_registry.register_tool("get_pending_todos", lambda: str(journal.get_pending_todos()), "Get all pending todos", [])
    tool_registry.register_tool("get_journal_day", journal.get_day_summary, "Get journal entry for a specific date", ["date_str"])
    tool_registry.register_tool("search_journal", journal.search_days, "Search journal entries from the past N days", ["keyword", "days_back"])
    tool_registry.register_tool("set_mood", journal.set_mood, "Log current mood", ["mood", "notes"])
    tool_registry.register_tool("get_mood_trend", emotional.get_mood_summary, "Get mood trend summary", [])
    tool_registry.register_tool("add_journal_note", journal.add_note, "Add a note to today's journal", ["note"])
    tool_registry.register_tool("remember_fact", graph_memory.store_background, "Explicitly save an important fact, note, or preference to long-term memory for later recall.", ["text"])
    tool_registry.register_tool("search_memory", graph_memory.recall_timeline, "Search long-term memory for previously stored facts or temporal details.", ["query"])

    router = IntentRouter(llm)
    planner = TaskPlanner(llm, tool_registry)

    hud = HUDServer()
    hud.start()

    try:
        import webbrowser
        webbrowser.open("http://127.0.0.1:7474")
        logger.info("HUD browser window opened")
    except Exception as e:
        logger.warning(f"Could not auto-open HUD: {e}")

    scheduler = SchedulerJobs()
    briefing = BriefingGenerator(weather_agent, graph_memory, user_profile)

    tool_registry.register_tool("send_whatsapp_media", messaging_agent.send_whatsapp_media, "Send media (photo/video/document) via WhatsApp", ["contact_name", "file_path", "caption"])
    tool_registry.register_tool("send_telegram_media", messaging_agent.send_telegram_media, "Send media via Telegram", ["chat_id", "file_path", "caption", "media_type"])
    tool_registry.register_tool("add_reminder", briefing.add_reminder, "Add a custom reminder", ["message", "time_str", "recurring"])
    tool_registry.register_tool("add_subscription", briefing.add_subscription, "Track a subscription or bill", ["name", "amount", "billing_cycle", "next_due"])
    tool_registry.register_tool("get_job_applications", job_agent.get_job_applications, "View tracked job applications", [])
    tool_registry.register_tool("track_application", job_agent.track_application, "Track a new job application", ["company", "role", "source", "status", "notes"])
    tool_registry.register_tool("save_jobs_csv", lambda q, loc, fp: job_agent.save_jobs_to_file([], fp, "csv") or "Use search_jobs first, then save_jobs_csv", "Save job search results to CSV", ["query", "location", "filepath"])
    tool_registry.register_tool("architect_build", architect.start_task, "Delegate a complex build/debug/refactor task to the Architect (Qwen)", ["task", "context", "project_path"])
    tool_registry.register_tool("architect_status", architect.get_progress, "Check the Architect's current progress", [])

    def morning_briefing():
        logger.info("Running morning briefing")
        text = briefing.generate_morning_briefing()
        if text:
            tts.speak(text, tone="calm")
            graph_memory.store_background("Delivered morning briefing.")

    def evening_summary():
        logger.info("Running evening summary")
        text = briefing.generate_evening_summary()
        if text:
            tts.speak(text, tone="calm")
            graph_memory.store_background("Delivered evening summary.")

    morning_hour, morning_minute = map(int, settings.morning_briefing_time.split(":"))
    evening_hour, evening_minute = map(int, settings.evening_summary_time.split(":"))

    scheduler.add_job("morning_briefing", morning_briefing, {
        "hour": morning_hour,
        "minute": morning_minute,
    })
    scheduler.add_job("evening_summary", evening_summary, {
        "hour": evening_hour,
        "minute": evening_minute,
    })
    scheduler.start()

    tools_description = tool_registry.get_tool_descriptions()
    tool_instruction = (
        f"\n\nYou have access to these tools:\n{tools_description}\n\n"
        "To use a tool, include THIS format in your response with valid JSON arguments inside the parentheses: [TOOL:tool_name({\"key\": \"value\"})]\n"
        "Examples:\n"
        "- [TOOL:open_app({\"app_name\": \"notepad\"})]\n"
        "- [TOOL:run_command({\"command\": \"dir\"})]\n"
        "- [TOOL:get_weather()]\n"
        "You can use multiple tools. After using tools, provide a natural spoken response."
    )

    logger.info(f"All modules ready ({len(tool_registry.tools)} tools, router, planner, HUD)")

    def shutdown(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully")
        tts.stop()
        scheduler.shutdown()
        hud.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    now = datetime.now()
    day = now.strftime("%A")
    time_str = now.strftime("%I:%M %p").lstrip("0")

    greeting_parts = [f"{settings.jarvis_name} online. All systems nominal. Good {get_time_greeting()}, {settings.user_name}. It's {day}, {time_str}."]

    if weather_agent:
        weather_brief = weather_agent.get_briefing()
        if weather_brief:
            greeting_parts.append(weather_brief)
        else:
            greeting_parts.append(f"Temperature in {settings.user_location}.")

    if google_agent:
        cal = google_agent.get_calendar_events()
        if cal and "not configured" not in cal.lower():
            greeting_parts.append(cal)
        emails = google_agent.get_unread_emails()
        if emails and "not configured" not in emails.lower():
            greeting_parts.append(emails)

    pending = journal.get_pending_todos()
    if pending:
        greeting_parts.append(f"You have {len(pending)} pending todos.")

    greeting_parts.append(f"{len(tool_registry.tools)} tools loaded. HUD at http://127.0.0.1:7474. Ready.")

    greeting = " ".join(greeting_parts)
    logger.info(greeting)
    tts.speak(greeting, tone="calm")
    hud.update_status("idle")
    hud.update_time()

    if weather_agent:
        try:
            w = weather_agent.get_current()
            if w:
                hud.update_weather(w[:100])
        except Exception:
            pass

    mute_detector.check_mute()

    last_interaction = datetime.now()
    idle_check_interval = 3600
    idle_check_threshold = 7200

    logger.info(f"Wake word listener active. Say '{settings.wake_word}' to begin.")

    while True:
        try:
            hud.update_status("listening")
            hud.update_time()

            now = datetime.now()
            if (now - last_interaction).total_seconds() > idle_check_interval:
                hour = now.hour
                if settings.working_hours_start <= hour <= settings.working_hours_end:
                    if (now - last_interaction).total_seconds() > idle_check_threshold:
                        idle_msg = f"Hey {settings.user_name}, you've been away for a while. Need help getting started?"
                        logger.info(f"Idle check-in: {idle_msg}")
                        tts.speak(idle_msg, tone="calm")
                        last_interaction = now

            wake_word.listen()

            audio = vad.record_until_silence()

            if len(audio) == 0:
                logger.info("No audio captured after wake word, returning to listen mode")
                hud.update_status("idle")
                continue

            text = stt.transcribe(audio)

            if not text:
                logger.info("No speech detected, returning to listen mode")
                hud.update_status("idle")
                continue

            logger.info(f"User said: '{text}'")
            last_interaction = datetime.now()

            if not mute_detector.should_respond():
                logger.info("Microphone muted, ignoring input")
                hud.update_status("idle")
                continue

            hud.update_status("thinking", text)

            mood = emotional.detect_mood(text)
            logger.info(f"Detected mood: {mood}")

            short_term.add("user", text)

            route = router.route(text, [{"name": name, "description": val["description"], "parameters": val["parameters"]} for name, val in tool_registry.tools.items()], conversation_history=short_term.get_history()[:-1])
            intent = route.get("tool", "chat")
            args = route.get("args", {})

            if intent == "plan":
                logger.info("Planner activated for multi-step task")
                hud.update_status("planning", args.get("task", text))
                result = planner.execute(args.get("task", text))
                hud.update_status("speaking")
                response = llm.chat(
                    f"The following steps were executed:\n{result}\n\nProvide a natural spoken summary.",
                    system_prompt=llm.system_prompt,
                )
            elif intent == "chat":
                use_cloud = llm.is_complex_task(text)
                base_prompt = llm.system_prompt + tool_instruction
                context_prompt = context_builder.build_system_prompt(base_prompt, text)
                conversation_history = short_term.get_history()[:-1]
                response = llm.chat(text, system_prompt=context_prompt, conversation_history=conversation_history, use_cloud=use_cloud)
                hud.update_status("speaking")
            else:
                result = tool_registry.execute_tool(intent, **args)
                hud.update_status("speaking")
                conversation_history = short_term.get_history()[:-1]
                response = llm.chat(
                    f"Tool '{intent}' returned: {result}\n\nProvide a natural spoken response.",
                    system_prompt=llm.system_prompt,
                    conversation_history=conversation_history
                )

            tool_calls = tool_registry.parse_tool_calls(response)
            if tool_calls:
                logger.info(f"Detected {len(tool_calls)} additional tool call(s)")
                tool_results = []
                for call in tool_calls:
                    result = tool_registry.execute_tool(call["tool"], **call["args"])
                    tool_results.append(f"{call['tool']}: {result}")
                    graph_memory.store_background(f"Executed tool: {call['tool']} with result: {str(result)[:200]}")

                if tool_results:
                    tool_context = "\n".join(tool_results)
                    response = llm.chat(
                        f"Based on these tool results, provide a natural spoken response:\n{tool_context}",
                        system_prompt=llm.system_prompt,
                    )

            logger.info(f"{settings.jarvis_name}: '{response}'")

            clean_response = tool_registry.clean_response(response)
            short_term.add("assistant", clean_response)

            tone = "neutral"
            if any(w in clean_response.lower() for w in ["alert", "warning", "urgent", "important"]):
                tone = "urgent"
            elif any(w in clean_response.lower() for w in ["good news", "great", "wonderful", "excellent"]):
                tone = "happy"
            elif any(w in clean_response.lower() for w in ["done", "complete", "finished", "ready"]):
                tone = "calm"

            tts.speak(clean_response, tone=tone)

            if len(text) > 20:
                graph_memory.store_background(f"User: {text} | ARIA: {clean_response}")
                journal.log_conversation(text, clean_response)

            hud.update_status("idle")

            architect_result = architect.get_result()
            if architect_result:
                logger.info(f"Architect task completed: {architect_result[:100]}...")
                completion_msg = (
                    f"Hey {settings.user_name}, the task you asked me to build is complete. "
                    f"Here's what the Architect delivered:\n\n{architect_result[:500]}..."
                )
                tts.speak(completion_msg, tone="happy")
                graph_memory.store_background(f"Architect task completed: {architect_result[:500]}")

        except KeyboardInterrupt:
            shutdown(None, None)
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            tts.speak("Something went wrong. Please try again.")
            hud.update_status("idle")


if __name__ == "__main__":
    main()
