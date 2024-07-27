class Singer:
    def __init__(self, name, song, entry_number):
        self.name = name.title()
        self.songs = [song]
        self.current_song = song
        self.entry_number = entry_number
        self.is_new = True
        self.performance_count = 0

    def __str__(self):
        return f"{self.name} - {self.current_song}"

    def ticker_str(self):
        return f"{self.name} - {self.current_song}"

    def add_song(self, song):
        if song and song not in self.songs:
            self.songs.append(song)
            self.current_song = song
            return True
        return False

    def set_current_song(self, song):
        if song in self.songs:
            self.current_song = song
            return True
        return False

    def increment_performance_count(self):
        self.performance_count += 1
        self.is_new = False

    def get_display_style(self):
        return {"foreground": "green" if self.is_new else "black"}