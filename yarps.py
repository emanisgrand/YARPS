import tkinter as tk
import os
import sys
from tkinter import ttk, messagebox
import threading
import time
import json
import shutil
from singer import Singer  # Import the Singer class from singer.py
from ticker_window import TickerWindow  # Import the TickerWindow class from ticker_window.py

class TextTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YARPS - You Always Remove the Previous Singer")

        # Singer data
        self.queue = []
        self.singer_cache = {}
        self.selected_singer = None
        self.running = True
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

        self.queue_listbox = tk.Listbox(self.queue_frame, width=70, font=("Courier", 10))
        self.queue_listbox.pack(side="left", fill="y")
        self.queue_listbox.bind("<<ListboxSelect>>", self.display_singer_info)
        self.queue_listbox.bind("<Button-1>", self.on_drag_start)
        self.queue_listbox.bind("<B1-Motion>", self.on_drag_motion)
        self.queue_listbox.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.queue_listbox.bind("<Double-1>", self.queue_listbox_double_click)

        self.scrollbar = ttk.Scrollbar(self.queue_frame, orient="vertical", command=self.queue_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.queue_listbox.config(yscrollcommand=self.scrollbar.set)

        # Frame for selected singer information
        self.info_frame = ttk.Frame(root)
        self.info_frame.pack(pady=10)

        self.selected_singer_label = ttk.Label(self.info_frame, text="Selected Singer:")
        self.selected_singer_label.pack()

        self.song_dropdown = ttk.Combobox(self.info_frame, state="readonly")
        self.song_dropdown.pack()
        self.song_dropdown.bind("<<ComboboxSelected>>", self.on_song_selected)

        self.new_song_entry = ttk.Entry(self.info_frame)
        self.new_song_entry.pack()

        self.add_song_button = ttk.Button(self.info_frame, text="Add Song", command=self.add_song_to_singer)
        self.add_song_button.pack()
        
        # Buttons for moving the selected singer
        self.remove_button = ttk.Button(self.info_frame, text="Remove", command=self.remove_from_queue)
        self.remove_button.pack()

        self.move_up_button = ttk.Button(self.info_frame, text="Move to Next in Queue", command=self.move_to_next_in_queue)
        self.move_up_button.pack()

        self.move_bottom_button = ttk.Button(self.info_frame, text="Move to Bottom of Queue", command=self.move_to_bottom_of_queue)
        self.move_bottom_button.pack()

        # Button for clearing performance counts
        self.clear_counts_button = ttk.Button(root, text="Clear Performance Counts", command=self.clear_performance_counts)
        self.clear_counts_button.pack(side="bottom", pady=10)

        self.load_singer_cache()

        # Frame for ticker state control
        self.ticker_state_frame = ttk.Frame(root)
        self.ticker_state_frame.pack(pady=10)

        self.state_label = ttk.Label(self.ticker_state_frame, text="Ticker State:")
        self.state_label.grid(row=0, column=0, padx=5)

        self.state_combobox = ttk.Combobox(self.ticker_state_frame, values=["auto", "current_singer_only", "full_queue_display"])
        self.state_combobox.grid(row=0, column=1, padx=5)
        self.state_combobox.bind("<<ComboboxSelected>>", self.change_ticker_state)

        # Launch Ticker Window
        self.ticker_window = TickerWindow(root)
        self.root.bind("<Button-1>", self.deselect_singer)

    def change_ticker_state(self, event):
        selected_state = self.state_combobox.get()
        self.ticker_window.set_state(selected_state)

    def get_data_file_path(self):
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            bundle_dir = sys._MEIPASS
        else:
            # Running as script
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Use a writable user data directory
        user_data_dir = os.path.join(os.path.expanduser('~'), '.yarps')
        os.makedirs(user_data_dir, exist_ok=True)
        
        user_file_path = os.path.join(user_data_dir, 'singer_cache.json')
        bundle_file_path = os.path.join(bundle_dir, 'singer_cache.json')
        
        if not os.path.exists(user_file_path) and os.path.exists(bundle_file_path):
            # Copy the bundled file to the user data directory if it doesn't exist
            shutil.copy2(bundle_file_path, user_file_path)
    
        return user_file_path
        
    def add_to_queue(self, event=None):
        entry_text = self.singer_entry.get()
        if entry_text:
            try:
                name, song = entry_text.split("-", 1)
                name = name.strip().title()
                song = song.strip()

                if name in self.singer_cache:
                    singer = self.singer_cache[name]
                    singer.add_song(song)
                    singer.set_current_song(song)
                else:
                    singer = Singer(name, song, self.entry_counter)
                    self.singer_cache[name] = singer
                    self.entry_counter += 1

                self.queue.append(singer)
                self.update_listbox()
                self.singer_entry.delete(0, tk.END)
                self.ticker_window.update_queue(self.queue)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter the singer and song in the format: 'Singer - Song'")

    def remove_from_queue(self):
        if self.queue:
            removed_singer = self.queue.pop(0)
            removed_singer.increment_performance_count()
            self.singer_cache[removed_singer.name] = removed_singer
            if self.selected_singer == removed_singer:
                self.selected_singer = None
                self.update_selected_singer_display()
            self.save_singer_cache()
            self.update_listbox()
            self.ticker_window.update_queue(self.queue)
        else:
            messagebox.showinfo("Queue Empty", "There are no singers in the queue to remove.")

    def clear_performance_counts(self):
        if messagebox.askyesno("Clear Performance Counts", "Are you sure you want to clear all performance counts?"):
            for singer in self.singer_cache.values():
                singer.performance_count = 0
                singer.is_new = True
            self.save_singer_cache()
            self.update_listbox()
    
    def queue_listbox_double_click(self, event):
        if self.queue:
            self.remove_from_queue()

    def update_listbox(self):
        self.queue_listbox.delete(0, tk.END)
        for i, singer in enumerate(self.queue, 1):
            prefix = "* " if singer.is_new else ""
            display_text = f"{prefix}{i}. {singer.name} - {singer.current_song} (Performances: {singer.performance_count})"
            self.queue_listbox.insert(tk.END, display_text)
            self.queue_listbox.itemconfig(tk.END, **singer.get_display_style())
        self.ticker_window.update_queue(self.queue)

    def display_singer_info(self, event):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            self.selected_singer = self.queue[selected_index[0]]
            self.update_selected_singer_display()
            print(f"Singer selected: {self.selected_singer.name}, Current song: {self.selected_singer.current_song}")
        else:
            print("No singer selected in display_singer_info")

    def add_song_to_singer(self):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            selected_singer = self.queue[selected_index[0]]
            new_song = self.new_song_entry.get()
            if new_song:
                selected_singer.add_song(new_song)
                self.song_dropdown['values'] = selected_singer.songs
                self.song_dropdown.set(new_song)
                selected_singer.set_current_song(new_song)
                self.new_song_entry.delete(0, tk.END)
                self.update_listbox()
                self.ticker_window.update_queue(self.queue)
                self.save_singer_cache()

    def on_song_selected(self, event):
        if self.selected_singer:
            new_song = self.song_dropdown.get()
            if new_song:
                self.selected_singer.set_current_song(new_song)
                self.update_listbox()
                self.ticker_window.update_queue(self.queue)
                self.save_singer_cache()
                print(f"Song selected for {self.selected_singer.name}: {new_song}")
            else:
                print("No song selected")
        else:
            print("No singer selected")
        print("on_song_selected called")

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
            self.move_singer(drag_index, drop_index)
            self.update_listbox()

    def move_singer(self, from_index, to_index):
        if self.queue and 0 <= from_index < len(self.queue):
            singer = self.queue.pop(from_index)
            if to_index > len(self.queue):
                to_index = len(self.queue)
            self.queue.insert(to_index, singer)
            self.update_listbox()
            if self.selected_singer == singer:
                self.queue_listbox.selection_clear(0, tk.END)
                self.queue_listbox.selection_set(to_index)
                self.queue_listbox.see(to_index)

    def move_to_next_in_queue(self):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.move_singer(index, 1)
            self.update_listbox()

    def move_to_bottom_of_queue(self):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.move_singer(index, len(self.queue) - 1)
            self.update_listbox()

    def deselect_singer(self, event):
        # Check if the click is outside of interactable elements
        if not (self.queue_listbox.winfo_containing(event.x_root, event.y_root) or 
                self.song_dropdown.winfo_containing(event.x_root, event.y_root) or
                self.new_song_entry.winfo_containing(event.x_root, event.y_root) or
                self.add_song_button.winfo_containing(event.x_root, event.y_root)):
            self.selected_singer = None
            self.update_selected_singer_display()
            print("Singer deselected")

    def update_selected_singer_display(self):
        if self.selected_singer:
            self.selected_singer_label.config(text=f"Selected Singer: {self.selected_singer.name}")
            self.song_dropdown['values'] = self.selected_singer.songs
            self.song_dropdown.set(self.selected_singer.current_song)
        else:
            self.selected_singer_label.config(text="Selected Singer: None")
            self.song_dropdown.set('')
            self.song_dropdown['values'] = []

    def update_listbox(self):
        self.queue_listbox.delete(0, tk.END)
        for i, singer in enumerate(self.queue, 1):
            prefix = "* " if singer.is_new else ""
            display_text = f"{prefix}{i:<3} {singer.name:<20} {singer.current_song:<30} {singer.performance_count:>3}"
            self.queue_listbox.insert(tk.END, display_text)
            self.queue_listbox.itemconfig(tk.END, **singer.get_display_style())
            print(f"Updated listbox: {singer.name}, Current song: {singer.current_song}")
        self.ticker_window.update_queue(self.queue)
        print("Listbox update completed")

    def load_singer_cache(self):
        try:
            with open(self.get_data_file_path(), 'r') as f:
                data = json.load(f)
                for name, info in data.items():
                    singer = Singer(name, info['current_song'], info['entry_number'])
                    singer.songs = info['songs']
                    singer.performance_count = info['performance_count']
                    singer.is_new = info['is_new']
                    self.singer_cache[name] = singer
        except FileNotFoundError:
            pass  # It's okay if the file doesn't exist yet

    def save_singer_cache(self):
        data = {name: {'songs': singer.songs, 
                       'current_song': singer.current_song, 
                       'entry_number': singer.entry_number,
                       'performance_count': singer.performance_count,
                       'is_new': singer.is_new} 
                for name, singer in self.singer_cache.items()}
        with open(self.get_data_file_path(), 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

    def on_close(self):
        self.save_singer_cache()
        self.running = False
        self.ticker_window.on_close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
