import tkinter as tk
from tkinter import ttk, messagebox

class InputFrame(ttk.Frame):
    def __init__(self, parent, add_to_queue_callback):
        super().__init__(parent)
        self.add_to_queue_callback = add_to_queue_callback

        self.singer_label = ttk.Label(self, text="Singer and Song:")
        self.singer_label.grid(row=0, column=0, padx=5)

        self.singer_entry = ttk.Entry(self, width=40)
        self.singer_entry.grid(row=0, column=1, padx=5)
        self.singer_entry.bind("<Return>", self.add_to_queue)

        self.add_button = ttk.Button(self, text="Add", command=self.add_to_queue)
        self.add_button.grid(row=0, column=2, padx=5)

    def add_to_queue(self, event=None):
        entry_text = self.singer_entry.get()
        if entry_text:
            try:
                name, song = entry_text.split("-", 1)
                self.add_to_queue_callback(name, song)
                self.singer_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter the singer and song in the format: 'Singer - Song'")

class QueueFrame(ttk.Frame):
    def __init__(self, parent, queue_manager, app):
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.app = app
        self.drag_data = {'index': None, 'y': 0}
        self.selected_singer = None
        self.queue_listbox = tk.Listbox(self, width=70, font=("Courier", 10))
        self.queue_listbox.pack(side="left", fill="y")
        self.queue_listbox.bind("<<ListboxSelect>>", self.display_singer_info)
        self.queue_listbox.bind("<Button-1>", self.on_drag_start)
        self.queue_listbox.bind("<B1-Motion>", self.on_drag_motion)
        self.queue_listbox.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.queue_listbox.bind("<Double-1>", self.queue_listbox_double_click)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.queue_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.queue_listbox.config(yscrollcommand=self.scrollbar.set)

    def display_singer_info(self, event):
        selected_index = self.queue_listbox.curselection()
        if selected_index:
            self.selected_singer = self.queue_manager.queue[selected_index[0]]
            self.app.update_info_frame(self.selected_singer)
        else:
            self.selected_singer = None
            self.app.update_info_frame(None)
    
    def update_listbox(self):
        self.queue_listbox.delete(0, tk.END)
        for i, singer in enumerate(self.queue_manager.queue, 1):
            prefix = "* " if singer.is_new else ""
            display_text = f"{prefix}{i:<3} {singer.name:<20} {singer.current_song:<30} {singer.performance_count:>3}"
            self.queue_listbox.insert(tk.END, display_text)
            self.queue_listbox.itemconfig(tk.END, **singer.get_display_style())
    
    def on_drag_start(self, event):
        self.drag_data['index'] = self.queue_listbox.nearest(event.y)
        self.drag_data['y'] = event.y

    def on_drag_motion(self, event):
        if self.drag_data['index'] is not None:
            y = event.y
            if abs(y - self.drag_data['y']) > 5:  # Moved more than 5 pixels
                drag_index = self.drag_data['index']
                drop_index = self.queue_listbox.nearest(y)
                if drag_index != drop_index:
                    self.queue_listbox.delete(drag_index)
                    self.queue_listbox.insert(drop_index, self.queue_manager.queue[drag_index].ticker_str())
                    self.queue_listbox.selection_clear(0, tk.END)
                    self.queue_listbox.selection_set(drop_index)
                    self.queue_listbox.see(drop_index)
                    self.drag_data['index'] = drop_index
                    self.drag_data['y'] = y

    def on_drag_stop(self, event):
        if self.drag_data['index'] is not None:
            drop_index = self.queue_listbox.nearest(event.y)
            if self.drag_data['index'] != drop_index:
                self.queue_manager.move_singer(self.drag_data['index'], drop_index)
                self.update_listbox()
        self.drag_data['index'] = None
        self.drag_data['y'] = 0

    def queue_listbox_double_click(self, event):
        if self.queue_manager.queue:
            self.queue_manager.remove_from_queue()
            self.update_listbox()
            self.app.update_queue_frame()
            self.app.update_info_frame(None)

class InfoFrame(ttk.Frame):
    def __init__(self, parent, queue_manager, app):
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.app = app
        self.selected_singer = None
        self.ticker_manager = None

        self.selected_singer_label = ttk.Label(self, text="Selected Singer:")
        self.selected_singer_label.pack()

        self.song_dropdown = ttk.Combobox(self, state="readonly")
        self.song_dropdown.pack()
        self.song_dropdown.bind("<<ComboboxSelected>>", self.on_song_selected)

        self.new_song_entry = ttk.Entry(self)
        self.new_song_entry.pack()

        self.add_song_button = ttk.Button(self, text="Add Song", command=self.add_song_to_singer)
        self.add_song_button.pack()

        self.remove_button = ttk.Button(self, text="Remove", command=self.remove_from_queue)
        self.remove_button.pack()

        self.move_up_button = ttk.Button(self, text="Move to Next in Queue", command=self.move_to_next_in_queue)
        self.move_up_button.pack()

        self.move_bottom_button = ttk.Button(self, text="Move to Bottom of Queue", command=self.move_to_bottom_of_queue)
        self.move_bottom_button.pack()

    def update_selected_singer(self, singer):
        self.selected_singer = singer
        if singer:
            self.selected_singer_label.config(text=f"Selected Singer: {singer.name}")
            self.song_dropdown['values'] = singer.songs
            self.song_dropdown.set(singer.current_song)
        else:
            self.selected_singer_label.config(text="Selected Singer: None")
            self.song_dropdown.set('')
            self.song_dropdown['values'] = []
    
    def set_ticker_manager(self, ticker_manager):
        self.ticker_manager = ticker_manager
    
    def on_song_selected(self, event):
        if self.selected_singer:
            new_song = self.song_dropdown.get()
            if new_song:
                self.selected_singer.set_current_song(new_song)
                self.app.update_queue_frame()
                self.queue_manager.save_singer_cache()
                self.update_ticker()
                print(f"Song selected for {self.selected_singer.name}: {new_song}")
            else:
                print("No song selected")
        else:
            print("No singer selected")
            print("on_song_selected called")

    def add_song_to_singer(self):
        if self.selected_singer:
            new_song = self.new_song_entry.get()
            if new_song:
                self.selected_singer.add_song(new_song)
                self.song_dropdown['values'] = self.selected_singer.songs
                self.song_dropdown.set(new_song)
                self.selected_singer.set_current_song(new_song)
                self.new_song_entry.delete(0, tk.END)
                self.app.update_queue_frame()
                self.queue_manager.save_singer_cache()
        self.update_ticker()

    def remove_from_queue(self):
        removed_singer = self.queue_manager.remove_from_queue()
        if removed_singer:
            self.app.update_queue_frame()
            if self.selected_singer == removed_singer:
                self.update_selected_singer(None)
        else:
            messagebox.showinfo("Queue Empty", "There are no singers in the queue to remove.")
        self.update_ticker()

    def move_to_next_in_queue(self):
        if self.selected_singer:
            index = self.queue_manager.queue.index(self.selected_singer)
            self.queue_manager.move_singer(index, 1)
            self.app.update_queue_frame()
        self.update_ticker()

    def move_to_bottom_of_queue(self):
        if self.selected_singer:
            index = self.queue_manager.queue.index(self.selected_singer)
            self.queue_manager.move_singer(index, len(self.queue_manager.queue) - 1)
            self.app.update_queue_frame()
        self.update_ticker()

    def update_ticker(self):
        if self.ticker_manager:
            self.ticker_manager.update_queue()

class TickerStateFrame(ttk.Frame):
    def __init__(self, parent, ticker_manager):
        super().__init__(parent)
        self.ticker_manager = ticker_manager
        self.state_label = ttk.Label(self, text="Ticker State:")
        self.state_label.grid(row=0, column=0, padx=5)

        self.state_combobox = ttk.Combobox(self, values=["auto", "current_singer_only", "full_queue_display"])
        self.state_combobox.grid(row=0, column=1, padx=5)
        self.state_combobox.bind("<<ComboboxSelected>>", self.change_ticker_state)

    def change_ticker_state(self, event):
        selected_state = self.state_combobox.get()
        self.ticker_manager.set_state(selected_state)