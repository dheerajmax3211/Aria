import threading
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from loguru import logger


class HUDServer:
    def __init__(self, port: int = 7474):
        self.port = port
        self.server = None
        self.thread = None
        self.status = "initializing"
        self.current_task = ""
        self.weather = ""
        self.time_str = ""
        self.upcoming_event = ""
        self.active = False

    def start(self):
        if self.active:
            return
        self.active = True
        hud = self

        class HUDHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/api/status":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    data = json.dumps({
                        "status": hud.status,
                        "task": hud.current_task,
                        "weather": hud.weather,
                        "time": hud.time_str,
                        "upcoming": hud.upcoming_event,
                    })
                    self.wfile.write(data.encode())
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    html = """<!DOCTYPE html>
<html>
<head>
<title>ARIA HUD</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0a0a0f; color: #00d4ff; font-family: 'Courier New', monospace; overflow: hidden; }
.hud { position: fixed; top: 0; left: 0; right: 0; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; background: rgba(0,20,40,0.85); border-bottom: 1px solid rgba(0,212,255,0.3); z-index: 9999; }
.status { font-size: 14px; text-transform: uppercase; letter-spacing: 2px; }
.status.listening { color: #00ff88; text-shadow: 0 0 10px #00ff88; }
.status.thinking { color: #ffaa00; text-shadow: 0 0 10px #ffaa00; }
.status.speaking { color: #00d4ff; text-shadow: 0 0 10px #00d4ff; }
.status.idle { color: #666; }
.clock { font-size: 18px; font-weight: bold; }
.weather { font-size: 13px; color: #88aacc; }
.task { font-size: 12px; color: #556; margin-top: 2px; }
.event { font-size: 12px; color: #ffaa00; }
.scanline { position: fixed; top: 0; left: 0; right: 0; height: 2px; background: rgba(0,212,255,0.1); animation: scan 4s linear infinite; pointer-events: none; }
@keyframes scan { 0% { top: 0; } 100% { top: 100vh; } }
</style>
</head>
<body>
<div class="hud">
<div>
<div class="status idle" id="status">INITIALIZING</div>
<div class="task" id="task"></div>
</div>
<div style="text-align:center">
<div class="clock" id="clock"></div>
<div class="event" id="event"></div>
</div>
<div style="text-align:right">
<div class="weather" id="weather"></div>
</div>
</div>
<div class="scanline"></div>
<script>
function update() {
fetch('/api/status').then(r=>r.json()).then(d=>{
document.getElementById('status').textContent = d.status;
document.getElementById('status').className = 'status ' + d.status.toLowerCase();
document.getElementById('task').textContent = d.task || '';
document.getElementById('weather').textContent = d.weather || '';
document.getElementById('clock').textContent = d.time || new Date().toLocaleTimeString();
document.getElementById('event').textContent = d.upcoming || '';
});
}
update();
setInterval(update, 2000);
</script>
</body>
</html>"""
                    self.wfile.write(html.encode())

            def log_message(self, format, *args):
                pass

        def run_server():
            self.server = HTTPServer(("127.0.0.1", self.port), HUDHandler)
            logger.info(f"HUD server started at http://127.0.0.1:{self.port}")
            self.server.serve_forever()

        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()

    def update_status(self, status: str, task: str = ""):
        self.status = status
        if task:
            self.current_task = task

    def update_weather(self, weather: str):
        self.weather = weather

    def update_time(self):
        self.time_str = datetime.now().strftime("%I:%M:%S %p").lstrip("0")

    def update_event(self, event: str):
        self.upcoming_event = event

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.active = False
            logger.info("HUD server stopped")
