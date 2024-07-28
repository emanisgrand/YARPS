import tkinter as tk
from tkinter import ttk
import threading
import time

class TickerWindow:
    def __init__(self, parent):
        self.parent = parent
        self.ticker_window = tk.Toplevel(parent)
        self.ticker_window.title("The Kings of Karaoke")
        
        # Set window to always be on top and make it slightly transparent
        self.ticker_window.attributes('-topmost', True, '-alpha', 0.9)

        # Create a style
        self.style = ttk.Style()
        self.style.configure('Ticker.TLabel', font=("Helvetica", 28), background='#2C3E50', foreground='#ECF0F1')

        # Create a frame to hold our content
        self.frame = ttk.Frame(self.ticker_window, style='Ticker.TFrame', padding=5)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.ticker_label = ttk.Label(self.frame, text="", style='Ticker.TLabel', font=("Helvetica", 28))
        self.ticker_label.pack(side="left", padx=5, fill=tk.BOTH, expand=True)

        self.running = True
        self.queue = []
        self.state = "current_singer_only"  # Initial state
        self.auto_state = False
        self.last_state_change = time.time()
        
        # Initialize borderless mode flag
        self.borderless = False

        # Create right-click menu
        self.menu = tk.Menu(self.ticker_window, tearoff=0)
        self.menu.add_command(label="Toggle Borderless", command=self.toggle_borderless)

        # Bind right-click event to show menu
        self.ticker_window.bind("<Button-3>", self.show_menu)

        # Bind left-click and drag events for moving the window
        self.ticker_window.bind("<ButtonPress-1>", self.start_move)
        self.ticker_window.bind("<ButtonRelease-1>", self.stop_move)
        self.ticker_window.bind("<B1-Motion>", self.do_move)

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
                        current_text = f"🎤 Now Singing: {self.queue[0].name} - {self.queue[0].current_song}"
                        display_text = " " * (self.ticker_window.winfo_width() // 10) + current_text + "    "
                    elif self.state == "full_queue_display" or (self.auto_state and self.state != "current_singer_only"):
                        display_text = " " * (self.ticker_window.winfo_width() // 10) + "🎶 Up Next: "
                        for i, singer in enumerate(self.queue[:5], 1):
                            display_text += f"{i}. {singer.name}    "
                    
                    while len(display_text) > 0 and self.running:
                        self.ticker_label.config(text=display_text)
                        display_text = display_text[1:]  # Remove the first character to scroll to the left
                        time.sleep(0.05)
                        self.ticker_window.update_idletasks()
                    display_text += " " * (self.ticker_window.winfo_width() // 10)  # Ensure text loops back to the right
                else:
                    self.ticker_label.config(text="🎵 Waiting for the next star... 🎵")
                    time.sleep(1)

        ticker_thread = threading.Thread(target=run_ticker, daemon=True)
        ticker_thread.start()

    def show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def toggle_borderless(self):
        self.borderless = not self.borderless
        if self.borderless:
            self.ticker_window.overrideredirect(True)
        else:
            self.ticker_window.overrideredirect(False)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.ticker_window.winfo_x() + deltax
        y = self.ticker_window.winfo_y() + deltay
        self.ticker_window.geometry(f"+{x}+{y}")

    def on_close(self):
        self.running = False
        self.ticker_window.destroy()