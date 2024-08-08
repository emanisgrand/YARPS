class Singer:
    def __init__(self, name, song, entry_number, performance_count=0):
        self.name = name.title()
        self.current_song = song
        self.entry_number = entry_number
        self.is_new = performance_count == 0
        self.performance_count = performance_count

    def __str__(self):
        return f"{self.name} - {self.current_song}"

    def ticker_str(self):
        return f"{self.name} - {self.current_song}"

    def get_display_style(self):
        return {"foreground": "green" if self.is_new else "black"}

    def increment_performance_count(self):
        self.performance_count += 1
        self.is_new = False