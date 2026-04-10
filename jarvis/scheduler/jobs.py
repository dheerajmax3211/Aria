from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger


class SchedulerJobs:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}

    def add_job(self, name: str, func, cron_trigger: dict):
        try:
            job = self.scheduler.add_job(
                func,
                trigger="cron",
                **cron_trigger,
                id=name,
                replace_existing=True,
            )
            self.jobs[name] = job
            logger.info(f"Scheduled job '{name}': {cron_trigger}")
        except Exception as e:
            logger.error(f"Failed to schedule job '{name}': {e}")

    def add_interval_job(self, name: str, func, hours: int = 0, minutes: int = 0):
        try:
            job = self.scheduler.add_job(
                func,
                trigger="interval",
                hours=hours,
                minutes=minutes,
                id=name,
                replace_existing=True,
            )
            self.jobs[name] = job
            logger.info(f"Interval job '{name}': every {hours}h {minutes}m")
        except Exception as e:
            logger.error(f"Failed to schedule interval job '{name}': {e}")

    def remove_job(self, name: str):
        if name in self.jobs:
            self.jobs[name].remove()
            del self.jobs[name]
            logger.info(f"Removed job '{name}'")

    def start(self):
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down")

    def get_next_run(self, name: str) -> str:
        if name in self.jobs:
            next_run = self.jobs[name].next_run_time
            if next_run:
                return next_run.strftime("%I:%M %p")
        return "Unknown"

    def add_recurring_job(self, name: str, func, day_of_week: str = "mon-fri", hour: int = 9, minute: int = 0):
        try:
            job = self.scheduler.add_job(
                func,
                trigger="cron",
                day_of_week=day_of_week,
                hour=hour,
                minute=minute,
                id=f"recurring_{name}",
                replace_existing=True,
            )
            self.jobs[f"recurring_{name}"] = job
            logger.info(f"Recurring job '{name}': {day_of_week} at {hour:02d}:{minute:02d}")
        except Exception as e:
            logger.error(f"Failed to schedule recurring job '{name}': {e}")

    def list_jobs(self) -> list[dict]:
        result = []
        for name, job in self.jobs.items():
            next_run = job.next_run_time
            result.append({
                "name": name,
                "next_run": next_run.strftime("%Y-%m-%d %I:%M %p") if next_run else "Unknown",
                "trigger": str(job.trigger),
            })
        return result
