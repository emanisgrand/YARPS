import tkinter as tk
from tkinter import ttk
import threading
import time
from singer import Singer  # Import the Singer class from singer.py
from ticker_window import TickerWindow  # Import the TickerWindow class from ticker_window.py

class TextTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YARPS - You Always Remove the Previous Singer")

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

        # Frame for queue
        self.queue_frame = ttk.Frame(root)
        self.queue_frame.pack(pady=10)

        self.queue_listbox = tk.Listbox(self.queue_frame, width=50)
        self.queue_listbox.pack(side="left", fill="y")
        self.queue_listbox.bind("<<ListboxSelect>>", self.display_singer_info)
        self.queue_listbox.bind("<Button-1>", self.on_drag_start)
        self.queue_listbox.bind("<B1-Motion>", self.on_drag_motion)
        self.queue_listbox.bind("<ButtonRelease-1>", self.on_drag_stop)

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

        # Buttons for moving the selected singer
        self.move_up_button = ttk.Button(self.info_frame, text="Move to Next in Queue", command=self.move_to_next_in_queue)
        self.move_up_button.pack()

        self.move_bottom_button = ttk.Button(self.info_frame, text="Move to Bottom of Queue", command=self.move_to_bottom_of_queue)
        self.move_bottom_button.pack()

        # Frame for ticker state control
        self.ticker_state_frame = ttk.Frame(root)
        self.ticker_state_frame.pack(pady=10)

        self.state_label = ttk.Label(self.ticker_state_frame, text="Ticker State:")
        self.state_label.grid(row=0, column=0, padx=5)

        self.state_combobox = ttk.Combobox(self.ticker_state_frame, values=["current_singer_only", "full_queue_display"])
        self.state_combobox.grid(row=0, column=1, padx=5)
        self.state_combobox.bind("<<ComboboxSelected>>", self.change_ticker_state)

        self.queue = []
        self.running = True

        # Launch Ticker Window
        self.ticker_window = TickerWindow(root)

    def add_to_queue(self, event=None):
        entry_text = self.singer_entry.get()
        if entry_text:
            name, song = entry_text.split("-", 1)
            new_singer = Singer(name.strip(), song.strip(), self.entry_counter)
            self.queue.append(new_singer)
            self.queue_listbox.insert(tk.END, f"{self.entry_counter}. {new_singer}")
            self.entry_counter += 1
            self.singer_entry.delete(0, tk.END)
            self.ticker_window.update_queue(self.queue)

    def remove_from_queue(self):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            self.queue_listbox.delete(selected_index)
            del self.queue[selected_index[0]]
            self.ticker_window.update_queue(self.queue)

    def display_singer_info(self, event):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            selected_singer = self.queue[selected_index[0]]
            self.info_text.config(state="normal")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Name: {selected_singer.name}\nSong: {selected_singer.song}\nEntry Number: {selected_singer.entry_number}")
            self.info_text.config(state="disabled")

    def change_ticker_state(self, event):
        selected_state = self.state_combobox.get()
        self.ticker_window.set_state(selected_state)

    def on_drag_start(self, event):
        self.drag_data = {'index': self.queue_listbox.nearest(event.y)}

    def on_drag_motion(self, event):
        pass

    def on_drag_stop(self, event):
        drag_index = self.drag_data['index']
        drop_index = self.queue_listbox.nearest(event.y)
        if drag_index != drop_index:
            self.queue[drag_index], self.queue[drop_index] = self.queue[drop_index], self.queue[drag_index]
            self.update_listbox()

    def move_to_next_in_queue(self):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            singer = self.queue.pop(index)
            self.queue.insert(1, singer)
            self.update_listbox()

    def move_to_bottom_of_queue(self):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            singer = self.queue.pop(index)
            self.queue.append(singer)
            self.update_listbox()

    def update_listbox(self):
        self.queue_listbox.delete(0, tk.END)
        for i, singer in enumerate(self.queue, 1):
            self.queue_listbox.insert(tk.END, f"{i}. {singer}")
        self.ticker_window.update_queue(self.queue)

    def on_close(self):
        self.running = False
        self.ticker_window.on_close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
