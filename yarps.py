import tkinter as tk
from file_handler import FileHandler
from queue_manager import QueueManager
from ticker_manager import TickerManager
from ui_components import InputFrame, QueueFrame, InfoFrame, TickerStateFrame

class TextTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YARPS - You Always Remove the Previous Singer")

        self.file_handler = FileHandler()
        self.queue_manager = QueueManager(self.file_handler)
        
        self.input_frame = InputFrame(root, self.add_to_queue)
        self.input_frame.pack(pady=10)

        self.queue_frame = QueueFrame(root, self.queue_manager, self)
        self.queue_frame.pack(pady=10)

        self.info_frame = InfoFrame(root, self.queue_manager, self)
        self.info_frame.pack(pady=10)

        self.ticker_manager = TickerManager(root, self.queue_manager)
        self.ticker_state_frame = TickerStateFrame(root, self.ticker_manager)
        self.ticker_state_frame.pack(pady=10)

        self.clear_counts_button = tk.Button(root, text="Clear Performance Counts", command=self.clear_performance_counts)
        self.clear_counts_button.pack(side="bottom", pady=10)

        self.info_frame.set_ticker_manager(self.ticker_manager)

        self.root.bind("<Button-1>", self.deselect_singer)

    def add_to_queue(self, name, song):
        singer = self.queue_manager.add_to_queue(name, song)
        self.queue_frame.update_listbox()
        self.ticker_manager.update_queue()

    def clear_performance_counts(self):
        if tk.messagebox.askyesno("Clear Performance Counts", "Are you sure you want to clear all performance counts?"):
            self.queue_manager.clear_performance_counts()
            self.queue_frame.update_listbox()

    def update_queue_frame(self):
        self.queue_frame.update_listbox()
        self.ticker_manager.update_queue()

    def update_info_frame(self, singer):
        self.info_frame.update_selected_singer(singer)

    def deselect_singer(self, event):
        if not (self.queue_frame.queue_listbox.winfo_containing(event.x_root, event.y_root) or 
                self.info_frame.song_dropdown.winfo_containing(event.x_root, event.y_root) or
                self.info_frame.new_song_entry.winfo_containing(event.x_root, event.y_root) or
                self.info_frame.add_song_button.winfo_containing(event.x_root, event.y_root)):
            self.update_info_frame(None)

    def on_close(self):
        self.queue_manager.save_singer_cache()
        self.ticker_manager.on_close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()