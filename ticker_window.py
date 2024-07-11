import tkinter as tk
import threading
import time

class TickerWindow:
    def __init__(self, parent):
        self.parent = parent
        self.ticker_window = tk.Toplevel(parent)
        self.ticker_window.title("The Kings of Karaoke")

        self.ticker_label = tk.Label(self.ticker_window, text="", font=("Helvetica", 16))
        self.ticker_label.pack(side="left", padx=5)

        self.running = True
        self.queue = []
        self.state = "current_singer_only"  # Initial state
        self.start_ticker()

    def update_queue(self, queue):
        self.queue = queue

    def set_state(self, state):
        self.state = state

    def start_ticker(self):
        def run_ticker():
            while self.running:
                if self.queue:
                    if self.state == "current_singer_only":
                        current_text = str(self.queue[0])
                        display_text = " " * (self.ticker_window.winfo_width() // 10) + current_text + "    "  # Initial spaces to start off-screen and add spaces to separate items
                    elif self.state == "full_queue_display":
                        current_text = "Up next: " + self.queue[1].name if len(self.queue) > 1 else ""
                        following_singers = ["Followed by: " + singer.name for singer in self.queue[2:]]
                        display_text = " " * (self.ticker_window.winfo_width() // 10) + current_text + "    " + "    ".join(following_singers) + "    "
                    
                    while len(display_text) > 0:
                        self.ticker_label.config(text=display_text)
                        display_text = display_text[1:]  # Remove the first character to scroll to the left
                        time.sleep(0.1)
                        self.ticker_window.update_idletasks()
                    display_text += " " * (self.ticker_window.winfo_width() // 10)  # Ensure text loops back to the right
                else:
                    time.sleep(1)

        ticker_thread = threading.Thread(target=run_ticker, daemon=True)
        ticker_thread.start()

    def on_close(self):
        self.running = False
        self.ticker_window.destroy()
