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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ARIA Core</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }
        body {
            background-color: #050505;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(0, 163, 255, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 85% 30%, rgba(255, 0, 128, 0.06) 0%, transparent 50%);
            color: #ffffff;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            position: relative;
        }
        
        .hud-container {
            width: 90%;
            max-width: 1200px;
            background: rgba(20, 20, 25, 0.65);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 30px;
            padding: 50px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
            position: relative;
            z-index: 10;
            display: flex;
            flex-direction: column;
            gap: 40px;
        }

        .header-grid {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
        }

        .sys-info {
            font-size: 1.1rem;
            color: #8b8b99;
            font-weight: 300;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .time-display {
            text-align: center;
        }
        .time-display h1 {
            font-size: 4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #888888);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -2px;
        }
        .time-display p {
            color: #ffb800;
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: 1px;
            margin-top: 5px;
            text-transform: uppercase;
        }

        .weather-info {
            text-align: right;
            font-size: 1.1rem;
            color: #8b8b99;
            font-weight: 400;
        }

        .ai-core {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 0;
            gap: 30px;
        }

        .orb {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #4a5568, #1a202c);
            box-shadow: 0 0 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(255,255,255,0.1);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }

        /* Ambient glowing states */
        body.state-listening .orb {
            background: radial-gradient(circle at 30% 30%, #4ae3b5, #008f5d);
            box-shadow: 0 0 60px rgba(0, 255, 136, 0.4), inset 0 0 20px rgba(255,255,255,0.4);
            animation: pulse-listen 1.5s ease-in-out infinite alternate;
        }
        body.state-thinking .orb {
            background: radial-gradient(circle at 30% 30%, #ffd000, #ff7b00);
            box-shadow: 0 0 60px rgba(255, 170, 0, 0.4), inset 0 0 20px rgba(255,255,255,0.4);
            animation: pulse-think 1s ease-in-out infinite alternate;
        }
        body.state-speaking .orb {
            background: radial-gradient(circle at 30% 30%, #00d4ff, #0051ff);
            box-shadow: 0 0 60px rgba(0, 212, 255, 0.5), inset 0 0 20px rgba(255,255,255,0.4);
            animation: pulse-speak 0.4s ease-in-out infinite alternate;
        }

        @keyframes pulse-listen { 0% { transform: scale(1); } 100% { transform: scale(1.15); box-shadow: 0 0 80px rgba(0,255,136,0.6); } }
        @keyframes pulse-think { 0% { transform: scale(1) rotate(-5deg); opacity: 0.8; } 100% { transform: scale(1.05) rotate(5deg); opacity: 1; } }
        @keyframes pulse-speak { 0% { transform: scale(1); } 100% { transform: scale(1.2); box-shadow: 0 0 90px rgba(0,212,255,0.8); } }

        .status-text {
            font-size: 2.2rem;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        
        .task-view {
            text-align: center;
            font-size: 1.3rem;
            color: #a0aec0;
            min-height: 40px;
            font-weight: 300;
            letter-spacing: 1px;
            opacity: 0.9;
        }

        .ambient-noise {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('data:image/svg+xml,%3Csvg viewBox=\"0 0 200 200\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cfilter id=\"noiseFilter\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.65\" numOctaves=\"3\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"100%25\" height=\"100%25\" filter=\"url(%23noiseFilter)\"/%3E%3C/svg%3E');
            opacity: 0.03;
            pointer-events: none;
            z-index: 1;
        }
    </style>
</head>
<body class="state-idle" id="app-body">
    <div class="ambient-noise"></div>
    <div class="hud-container">
        <div class="header-grid">
            <div class="sys-info">
                <span>ARIA CORE V2</span>
                <span style="color: #4ae3b5; font-size: 0.95rem; font-weight: 500; margin-top:4px;">SYSTEMS NOMINAL</span>
            </div>
            <div class="time-display">
                <h1 id="clock">--:--</h1>
                <p id="event"></p>
            </div>
            <div class="weather-info">
                <span id="weather">Awaiting Sensor Data...</span>
            </div>
        </div>
        
        <div class="ai-core">
            <div class="orb"></div>
            <div class="status-text" id="status">INITIALIZING</div>
        </div>

        <div class="task-view" id="task">
            Establishing connection protocols...
        </div>
    </div>

    <script>
        function update() {
            fetch('/api/status').then(r => r.json()).then(d => {
                document.getElementById('app-body').className = 'state-' + d.status.toLowerCase();
                document.getElementById('status').textContent = d.status;
                document.getElementById('task').textContent = d.task || '';
                document.getElementById('weather').textContent = d.weather || '';
                document.getElementById('clock').textContent = d.time || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                document.getElementById('event').textContent = d.upcoming || '';
            }).catch(e => console.error(e));
        }
        update();
        setInterval(update, 1000);
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
