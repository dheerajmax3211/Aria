import os
import subprocess
import base64
import pyautogui
import pygetwindow as gw
from loguru import logger


class ComputerControlAgent:
    name = "computer_control"
    description = "Controls the computer: open apps, manage windows, run commands, take screenshots, manage processes, keyboard/mouse automation, system commands"

    def open_application(self, app_name: str) -> str:
        try:
            if os.name == "nt":
                os.startfile(app_name)
            else:
                subprocess.Popen(["open", app_name])
            logger.info(f"Opened application: {app_name}")
            return f"Opened {app_name}"
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return f"Could not open {app_name}: {e}"

    def close_application(self, app_name: str) -> str:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/IM", app_name], capture_output=True, text=True)
            else:
                subprocess.run(["pkill", "-f", app_name], capture_output=True, text=True)
            logger.info(f"Closed application: {app_name}")
            return f"Closed {app_name}"
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {e}")
            return f"Could not close {app_name}: {e}"

    def bring_to_foreground(self, window_title: str) -> str:
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                windows[0].activate()
                logger.info(f"Brought window to foreground: {window_title}")
                return f"Brought {window_title} to foreground"
            return f"No window found matching '{window_title}'"
        except Exception as e:
            logger.error(f"Failed to bring window forward: {e}")
            return f"Could not focus window: {e}"

    def minimize_window(self, window_title: str) -> str:
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                windows[0].minimize()
                return f"Minimized {window_title}"
            return f"No window found matching '{window_title}'"
        except Exception as e:
            return f"Failed to minimize: {e}"

    def maximize_window(self, window_title: str) -> str:
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                windows[0].maximize()
                return f"Maximized {window_title}"
            return f"No window found matching '{window_title}'"
        except Exception as e:
            return f"Failed to maximize: {e}"

    def resize_window(self, window_title: str, width: int, height: int) -> str:
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                windows[0].resizeTo(width, height)
                return f"Resized {window_title} to {width}x{height}"
            return f"No window found matching '{window_title}'"
        except Exception as e:
            return f"Failed to resize: {e}"

    def take_screenshot(self, filepath: str = "data/screenshot.png") -> str:
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            pyautogui.screenshot(filepath)
            logger.info(f"Screenshot saved to {filepath}")
            return f"Screenshot saved to {filepath}"
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return f"Screenshot failed: {e}"

    def analyze_screenshot(self, filepath: str = "data/screenshot.png") -> str:
        try:
            self.take_screenshot(filepath)
            with open(filepath, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode()

            try:
                import ollama
                from jarvis.config import settings
                client = ollama.Client(host=settings.ollama_base_url)
                response = client.chat(
                    model="llava:7b",
                    messages=[{
                        "role": "user",
                        "content": "Describe everything you see on this screen in detail. What applications are open? What text is visible? What is the user working on?",
                        "images": [image_b64],
                    }],
                )
                description = response["message"]["content"].strip()
                logger.info(f"Screenshot analyzed: {description[:100]}...")
                return description
            except Exception as vision_err:
                logger.warning(f"Vision analysis failed: {vision_err}, returning file path")
                return f"Screenshot saved to {filepath}. Vision model not available for analysis."
        except Exception as e:
            return f"Screenshot analysis failed: {e}"

    def type_text(self, text: str, interval: float = 0.05) -> str:
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: {text[:50]}...")
            return f"Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
        except Exception as e:
            return f"Failed to type text: {e}"

    def click_at(self, x: int, y: int, clicks: int = 1, button: str = "left") -> str:
        try:
            pyautogui.click(x, y, clicks=clicks, button=button)
            logger.info(f"Clicked at ({x}, {y})")
            return f"Clicked at ({x}, {y})"
        except Exception as e:
            return f"Failed to click: {e}"

    def press_key(self, key: str) -> str:
        try:
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
            return f"Pressed {key}"
        except Exception as e:
            return f"Failed to press key: {e}"

    def hotkey(self, *keys: str) -> str:
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"Hotkey: {'+'.join(keys)}")
            return f"Pressed {'+'.join(keys)}"
        except Exception as e:
            return f"Failed to press hotkey: {e}"

    def scroll(self, clicks: int) -> str:
        try:
            pyautogui.scroll(clicks)
            logger.info(f"Scrolled {clicks} clicks")
            return f"Scrolled {clicks} clicks"
        except Exception as e:
            return f"Failed to scroll: {e}"

    def get_mouse_position(self) -> str:
        try:
            x, y = pyautogui.position()
            return f"Mouse position: ({x}, {y})"
        except Exception as e:
            return f"Failed to get mouse position: {e}"

    def move_mouse_to(self, x: int, y: int) -> str:
        try:
            pyautogui.moveTo(x, y, duration=0.3)
            return f"Moved mouse to ({x}, {y})"
        except Exception as e:
            return f"Failed to move mouse: {e}"

    def run_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout.strip() or result.stderr.strip()
            logger.info(f"Command executed: {command}")
            return output[:2000] if output else "Command completed with no output"
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return f"Command failed: {e}"

    def shutdown(self) -> str:
        try:
            if os.name == "nt":
                subprocess.run(["shutdown", "/s", "/t", "60"], capture_output=True, text=True)
            else:
                subprocess.run(["shutdown", "-h", "now"], capture_output=True, text=True)
            return "System shutting down in 60 seconds. Say 'cancel shutdown' to stop."
        except Exception as e:
            return f"Shutdown failed: {e}"

    def cancel_shutdown(self) -> str:
        try:
            if os.name == "nt":
                subprocess.run(["shutdown", "/a"], capture_output=True, text=True)
            return "Shutdown cancelled."
        except Exception as e:
            return f"Cancel shutdown failed: {e}"

    def set_volume(self, level: int) -> str:
        try:
            if os.name == "nt":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                return f"Volume set to {level}%"
            return "Volume control not supported on this platform"
        except Exception as e:
            return f"Volume control failed: {e}. Install pycaw for Windows volume control."

    def set_brightness(self, level: int) -> str:
        try:
            if os.name == "nt":
                import subprocess
                result = subprocess.run(
                    ["powershell", "-Command", f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return f"Brightness set to {level}%"
                return f"Brightness control failed: {result.stderr.strip()}"
            return "Brightness control not supported on this platform"
        except Exception as e:
            return f"Brightness control failed: {e}"

    def sleep_system(self) -> str:
        try:
            if os.name == "nt":
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], capture_output=True, text=True)
            else:
                subprocess.run(["systemctl", "suspend"], capture_output=True, text=True)
            return "System going to sleep."
        except Exception as e:
            return f"Sleep failed: {e}"

    def restart_system(self) -> str:
        try:
            if os.name == "nt":
                subprocess.run(["shutdown", "/r", "/t", "60"], capture_output=True, text=True)
            else:
                subprocess.run(["shutdown", "-r", "now"], capture_output=True, text=True)
            return "System restarting in 60 seconds."
        except Exception as e:
            return f"Restart failed: {e}"

    def cancel_restart(self) -> str:
        try:
            if os.name == "nt":
                subprocess.run(["shutdown", "/a"], capture_output=True, text=True)
            return "Restart cancelled."
        except Exception as e:
            return f"Cancel restart failed: {e}"

    def list_processes(self) -> str:
        try:
            if os.name == "nt":
                result = subprocess.run(
                    ["tasklist", "/FO", "CSV", "/NH"],
                    capture_output=True,
                    text=True,
                )
                processes = [line.split(",")[0].strip('"') for line in result.stdout.strip().split("\n") if line]
                return f"Running processes ({len(processes)}): {', '.join(processes[:20])}"
            return "Process listing not supported on this platform"
        except Exception as e:
            return f"Failed to list processes: {e}"

    def kill_process(self, process_name: str) -> str:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/IM", process_name], capture_output=True, text=True)
            else:
                subprocess.run(["pkill", "-f", process_name], capture_output=True, text=True)
            logger.info(f"Killed process: {process_name}")
            return f"Killed process {process_name}"
        except Exception as e:
            return f"Failed to kill process: {e}"

    def get_system_info(self) -> str:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            return f"CPU: {cpu}%, Memory: {memory.percent}% used ({memory.available / 1024**3:.1f}GB free)"
        except ImportError:
            return "System info requires psutil package"
        except Exception as e:
            return f"Failed to get system info: {e}"
