import tkinter as tk
from tkinter import ttk
import threading
import time
from singer import Singer

class TextTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Ticker App")

        # Entry number counter
        self.entry_counter = 1

        # Frame for input
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(pady=10)

        self.singer_label = ttk.Label(self.input_frame, text="Singer and Song:")
        self.singer_label.grid(row=0, column=0, padx=5)

        self.singer_entry = ttk.Entry(self.input_frame, width=40)
        self.singer_entry.grid(row=0, column=1, padx=5)
        self.singer_entry.bind("<Return>", self.add_to_queue)

        self.add_button = ttk.Button(self.input_frame, text="Add", command=self.add_to_queue)
        self.add_button.grid(row=0, column=2, padx=5)

        # Frame for ticker
        self.ticker_frame = ttk.Frame(root)
        self.ticker_frame.pack(pady=10, fill="x")

        self.ticker_label = ttk.Label(self.ticker_frame, text="", font=("Helvetica", 16))
        self.ticker_label.pack(side="left", padx=5)

        # Frame for queue
        self.queue_frame = ttk.Frame(root)
        self.queue_frame.pack(pady=10)

        self.queue_listbox = tk.Listbox(self.queue_frame, width=50)
        self.queue_listbox.pack(side="left", fill="y")
        self.queue_listbox.bind("<<ListboxSelect>>", self.display_singer_info)

        self.scrollbar = ttk.Scrollbar(self.queue_frame, orient="vertical", command=self.queue_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.queue_listbox.config(yscrollcommand=self.scrollbar.set)

        # Frame for selected singer information
        self.info_frame = ttk.Frame(root)
        self.info_frame.pack(pady=10)

        self.selected_singer_label = ttk.Label(self.info_frame, text="Selected Singer:")
        self.selected_singer_label.pack()

        self.info_text = tk.Text(self.info_frame, width=50, height=10, state="disabled")
        self.info_text.pack()

        self.remove_button = ttk.Button(self.info_frame, text="Remove", command=self.remove_from_queue)
        self.remove_button.pack()

        self.queue = []
        self.running = True
        self.start_ticker()

    def add_to_queue(self, event=None):
        entry_text = self.singer_entry.get()
        if entry_text:
            name, song = entry_text.split("-", 1)
            new_singer = Singer(name.strip(), song.strip(), self.entry_counter)
            self.queue.append(new_singer)
            self.queue_listbox.insert(tk.END, f"{self.entry_counter}. {new_singer}")
            self.entry_counter += 1
            self.singer_entry.delete(0, tk.END)

    def remove_from_queue(self):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            self.queue_listbox.delete(selected_index)
            del self.queue[selected_index[0]]

    def display_singer_info(self, event):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            selected_singer = self.queue[selected_index[0]]
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Name: {selected_singer.name}\nSong: {selected_singer.song}\nEntry Number: {selected_singer.entry_number}")
            self.info_text.config(state="disabled")

    def start_ticker(self):
        def run_ticker():
            while self.running:
                if self.queue:
                    current_text = str(self.queue[0])
                    self.queue.append(self.queue.pop(0))  # Re-add the text to the end of the queue for continuous scrolling
                    display_text = " " * 40 + current_text + "    "  # Initial spaces to start off-screen and add spaces to separate items
                    while len(display_text) > 0:
                        self.ticker_label.config(text=display_text)
                        display_text = display_text[1:]  # Remove the first character to scroll to the left
                        time.sleep(0.1)
                        self.root.update_idletasks()
                    display_text += " " * 40  # Ensure text loops back to the right
                else:
                    time.sleep(1)

        ticker_thread = threading.Thread(target=run_ticker, daemon=True)
        ticker_thread.start()

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
