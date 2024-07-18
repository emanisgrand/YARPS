class Singer:
    def __init__(self, name, song, entry_number):
        self.name = name.title()
        self.songs = [song]
        self.current_song = song
        self.entry_number = entry_number
        self.performance_count = 0
        self.is_new = True

    def __str__(self):
        return f"{self.name} - {self.current_song}"

    def ticker_str(self):
        return f"{self.name} - {self.current_song}"

    def add_song(self, song):
        if song not in self.songs:
            self.songs.append(song)

    def set_current_song(self, song):
        if song in self.songs:
            self.current_song = song
        elif song:  # If the song is not in the list but is not empty, add it
            self.add_song(song)
            self.current_song = song

    def increment_performance_count(self):
        self.performance_count += 1
        self.is_new = False

    def get_display_style(self):
        if self.is_new:
            return {"foreground": "green"}
        else:
            return {"foreground": "black"}