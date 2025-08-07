from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from time import sleep
import subprocess
import os

class Watcher(FileSystemEventHandler):
    def on_deleted(self, event):
        if event.src_path.endswith("test.txt"):
            print("test.txt deleted, checking FullTokens.txt...")

            sleep(30)  # Initial delay before checking

            full_tokens_path = "./Accounts/FullTokens.txt"
            done_file_path = "./Accounts/done.txt"

            # Check if FullTokens.txt exists
            if not os.path.exists(full_tokens_path):
                print(f"File {full_tokens_path} does not exist. Skipping script execution.")
                return
            
            # Count the number of lines in FullTokens.txt
            with open(full_tokens_path, "r") as f:
                line_count = sum(1 for _ in f)

            print(f"FullTokens.txt contains {line_count} lines.")

            if line_count > 11:
                print("Line count is greater than 11, running script...")
                try:
                    subprocess.run(["python3", "allofallfn.py"], check=True)
                    print("Script executed successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Error executing script: {e}")
            else:
                print("Line count is 11 or less, deleting done.txt...")
                if os.path.exists(done_file_path):
                    os.remove(done_file_path)
                    print(f"{done_file_path} deleted.")
                    with open("./Accounts/test.txt", "w") as file:
                      file.write("Hello, World!")
                else:
                    print(f"{done_file_path} does not exist.")

# Set up the observer
path_to_watch = "./Accounts/"
event_handler = Watcher()
observer = Observer()
observer.schedule(event_handler, path_to_watch, recursive=False)
observer.start()

print(f"Watching directory: {path_to_watch}")

try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    observer.stop()
observer.join()