class Singer:
    def __init__(self, name, song, entry_number):
        self.name = name.title()
        self.song = song
        self.entry_number = entry_number

    def __str__(self):
        return f"{self.name} - {self.song}"
