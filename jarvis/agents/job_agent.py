import os
import csv
import json
from loguru import logger


class JobAgent:
    name = "job_agent"
    description = "Job search, filtering, application tracking, resume tailoring, and cover letter generation"

    def __init__(self, db_path: str = "data/jarvis.db"):
        self.db_path = db_path

    def search_jobs(self, query: str, location: str = "", salary_min: str = "", remote: str = "", company_size: str = "") -> str:
        try:
            import requests
            url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": "demo",
                "app_key": "demo",
                "results_per_page": 20,
                "what": query,
            }
            if location:
                params["where"] = location

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if not results:
                    return f"No jobs found for '{query}' in {location}"

                filtered = results
                if remote.lower() in ("yes", "true", "remote"):
                    filtered = [j for j in filtered if "remote" in j.get("title", "").lower() or "remote" in json.dumps(j.get("description", "")).lower() or j.get("contract_type", "").lower() == "remote"]
                if salary_min:
                    try:
                        min_val = int(salary_min)
                        filtered = [j for j in filtered if j.get("salary_min", 0) >= min_val or j.get("salary_max", 0) >= min_val]
                    except ValueError:
                        pass

                if not filtered:
                    return f"Jobs found but none matched your filters (remote={remote}, salary>={salary_min})"

                parts = []
                for job in filtered[:10]:
                    salary = ""
                    if job.get("salary_min") and job.get("salary_max"):
                        salary = f" | Salary: {job['salary_min']:,.0f}-{job['salary_max']:,.0f}"
                    contract = f" | {job.get('contract_type', 'Full-time')}" if job.get('contract_type') else ""
                    parts.append(f"{job.get('title', 'N/A')} at {job.get('company', {}).get('display_name', 'N/A')} - {job.get('location', {}).get('display_name', 'N/A')}{salary}{contract}")
                return f"Jobs found ({len(filtered)} total, showing {len(parts)}):\n" + "\n".join(parts)
            return f"Job search failed: {response.text}"
        except Exception as e:
            return f"Job search failed: {e}. Add Adzuna API credentials for full access."

    def save_jobs_to_file(self, jobs: list, filepath: str, format: str = "json") -> str:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            if format == "csv":
                with open(filepath, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["title", "company", "location", "salary_min", "salary_max", "url"])
                    writer.writeheader()
                    for job in jobs:
                        writer.writerow({
                            "title": job.get("title", ""),
                            "company": job.get("company", {}).get("display_name", ""),
                            "location": job.get("location", {}).get("display_name", ""),
                            "salary_min": job.get("salary_min", ""),
                            "salary_max": job.get("salary_max", ""),
                            "url": job.get("redirect_url", ""),
                        })
            else:
                with open(filepath, "w") as f:
                    json.dump(jobs, f, indent=2)
            return f"Saved {len(jobs)} jobs to {filepath} ({format})"
        except Exception as e:
            return f"Failed to save jobs: {e}"

    def generate_cover_letter(self, job_title: str, company: str, skills: str = "") -> str:
        letter = (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my interest in the {job_title} position at {company}. "
            f"With my background and skills"
            f"{' in ' + skills if skills else ''}"
            f", I believe I would be a valuable addition to your team.\n\n"
            f"I am particularly drawn to this opportunity because of {company}'s reputation "
            f"for innovation and excellence.\n\n"
            f"Thank you for considering my application. I look forward to discussing how my "
            f"experience aligns with your needs.\n\n"
            f"Sincerely,\n[Your Name]"
        )
        return letter

    def tailor_resume(self, job_description: str, current_resume: str = "") -> str:
        if not current_resume:
            return "Please provide your current resume content so I can tailor it to this job description."

        keywords = []
        important_terms = ["python", "java", "javascript", "react", "aws", "docker", "kubernetes", "sql", "nosql", "rest", "graphql", "ci/cd", "agile", "scrum", "leadership", "communication", "team", "design", "architecture", "testing", "debugging"]
        jd_lower = job_description.lower()
        for term in important_terms:
            if term in jd_lower:
                keywords.append(term)

        suggestions = []
        suggestions.append(f"Key skills to emphasize based on this job description: {', '.join(keywords[:10])}")
        suggestions.append(f"\nRecommendations:")
        suggestions.append(f"1. Move these keywords to the top of your skills section: {', '.join(keywords[:5])}")
        suggestions.append(f"2. Quantify your achievements with metrics (e.g., 'Improved performance by 30%')")
        suggestions.append(f"3. Use action verbs: Led, Designed, Implemented, Optimized, Deployed")
        suggestions.append(f"4. Mirror the job description's language in your experience bullets")
        suggestions.append(f"5. Highlight any projects or experience directly relevant to {job_description.split()[0] if job_description else 'this role'}")

        tailored = f"Resume Tailoring Report\n{'='*40}\n" + "\n".join(suggestions)
        logger.info(f"Resume tailored for job description ({len(keywords)} keywords identified)")
        return tailored

    def export_resume(self, tailored_content: str, filepath: str = "data/tailored_resume.txt") -> str:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(tailored_content)
            return f"Tailored resume saved to {filepath}"
        except Exception as e:
            return f"Failed to export resume: {e}"

    def get_job_applications(self) -> str:
        import sqlite3
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM job_applications ORDER BY timestamp DESC LIMIT 20")
                apps = [dict(row) for row in cursor.fetchall()]
            if not apps:
                return "No job applications tracked yet."
            parts = ["Job applications tracked:"]
            for app in apps:
                parts.append(f"- {app.get('role', 'N/A')} at {app.get('company', 'N/A')} ({app.get('status', 'applied')}) - {app.get('timestamp', '')[:10]}")
            return "\n".join(parts)
        except Exception as e:
            return f"Failed to get job applications: {e}"

    def track_application(self, company: str, role: str, source: str = "", status: str = "applied", notes: str = "") -> str:
        import sqlite3
        from datetime import datetime
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO job_applications (timestamp, company, role, source, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (datetime.now().isoformat(), company, role, source, status, notes),
                )
            logger.info(f"Job application tracked: {role} at {company}")
            return f"Tracked application: {role} at {company} ({status})"
        except Exception as e:
            return f"Failed to track application: {e}"
