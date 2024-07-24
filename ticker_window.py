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
        self.auto_state = False
        self.last_state_change = time.time()
        self.start_ticker()

    def update_queue(self, queue):
        self.queue = queue

    def set_state(self, state):
        self.state = state
        self.last_state_change = time.time()
        self.auto_state = (state == "auto")

    def start_ticker(self):
        def run_ticker():
            while self.running:
                current_time = time.time()
                if self.auto_state and current_time - self.last_state_change >= 60:
                    self.state = "full_queue_display" if self.state == "current_singer_only" else "current_singer_only"
                    self.last_state_change = current_time

                if self.queue:
                    if self.state == "current_singer_only" or (self.auto_state and self.state != "full_queue_display"):
                        current_text = f"{self.queue[0].name} - {self.queue[0].current_song}"
                        display_text = " " * (self.ticker_window.winfo_width() // 10) + current_text + "    "
                    elif self.state == "full_queue_display" or (self.auto_state and self.state != "current_singer_only"):
                        display_text = " " * (self.ticker_window.winfo_width() // 10)
                        for i, singer in enumerate(self.queue):
                            display_text += f"{i+1}. {singer.name}    "
                    
                    while len(display_text) > 0 and self.running:
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