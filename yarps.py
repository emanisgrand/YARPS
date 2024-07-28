import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
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

class ImprovedUITheme:
    def __init__(self, root):
        self.root = root
        self.set_theme()

    def set_theme(self):
        # Define color scheme
        bg_color = "#2C3E50"  # Dark blue-gray
        fg_color = "#ECF0F1"  # Light gray
        accent_color = "#3498DB"  # Bright blue
        
        # Configure root window
        self.root.configure(bg=bg_color)
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common elements
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=('Helvetica', 10))
        style.configure("TEntry", fieldbackground=fg_color, foreground=bg_color, font=('Helvetica', 10))
        style.configure("TButton", background=accent_color, foreground=fg_color, font=('Helvetica', 10, 'bold'))
        style.map("TButton", background=[('active', "#2980B9")])  # Darker blue when clicked
        
        # Configure Listbox
        self.root.option_add("*TListbox*Background", fg_color)
        self.root.option_add("*TListbox*Foreground", bg_color)
        self.root.option_add("*TListbox*Font", tkfont.Font(family="Helvetica", size=10))
        
        # Configure Combobox
        style.map('TCombobox', fieldbackground=[('readonly', fg_color)])
        style.map('TCombobox', selectbackground=[('readonly', accent_color)])
        style.map('TCombobox', selectforeground=[('readonly', fg_color)])

    def apply_layout(self, app):
        # Add padding to main frames
        for frame in (app.input_frame, app.queue_frame, app.info_frame, app.ticker_state_frame):
            frame.configure(padding="10 10 10 10")
        
        # Center align elements in input frame
        app.input_frame.singer_label.grid(row=0, column=0, padx=5, pady=5)
        app.input_frame.singer_entry.grid(row=0, column=1, padx=5, pady=5)
        app.input_frame.add_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Improve queue frame layout
        app.queue_frame.queue_listbox.configure(borderwidth=0, highlightthickness=0)
        app.queue_frame.scrollbar.pack(side="right", fill="y", padx=(0, 10))
        
        # Improve info frame layout
        for widget in app.info_frame.winfo_children():
            widget.pack_configure(pady=5)
        
        # Style the clear counts button
        app.clear_counts_button.configure(bg="#E74C3C", fg="white", font=('Helvetica', 10, 'bold'))

# Usage in your main application
if __name__ == "__main__":
    root = tk.Tk()
    app = TextTickerApp(root)
    
    # Apply the improved UI theme
    ui_theme = ImprovedUITheme(root)
    ui_theme.apply_layout(app)
    
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()