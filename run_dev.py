import os
import sys
import time
import subprocess
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class BotReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.last_restart = time.time()
        self.start_bot()

    def start_bot(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()

        logger.info("Starting bot process...")
        # Use python executable from current environment
        self.process = subprocess.Popen([sys.executable, "main.py"])
        self.last_restart = time.time()

    def on_modified(self, event):
        # Ignore directories and non-python files
        if event.is_directory or not event.src_path.endswith(".py"):
            return

        # Avoid restarting too frequently (debounce)
        if time.time() - self.last_restart < 2:
            return

        logger.info(f"Detected change in {event.src_path}, restarting bot...")
        self.start_bot()


def main():
    path = "."
    event_handler = BotReloader()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        logger.info(f"Watching for changes in {os.path.abspath(path)}")
        logger.info("Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping bot and watcher...")
        if event_handler.process and event_handler.process.poll() is None:
            event_handler.process.terminate()
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
