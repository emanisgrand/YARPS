from singer import Singer

class QueueManager:
    def __init__(self, file_handler):
        self.queue = []
        self.singer_cache = {}
        self.file_handler = file_handler
        self.entry_counter = 1
        self.load_singer_cache()

    def add_to_queue(self, name, song):
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
        self.save_singer_cache()
        return singer

    def remove_from_queue(self):
        if self.queue:
            removed_singer = self.queue.pop(0)
            removed_singer.increment_performance_count()
            self.singer_cache[removed_singer.name] = removed_singer
            self.save_singer_cache()
            return removed_singer
        return None

    def move_singer(self, from_index, to_index):
        if self.queue and 0 <= from_index < len(self.queue):
            singer = self.queue.pop(from_index)
            if to_index > len(self.queue):
                to_index = len(self.queue)
            self.queue.insert(to_index, singer)

    def clear_performance_counts(self):
        for singer in self.singer_cache.values():
            singer.performance_count = 0
            singer.is_new = True
        self.save_singer_cache()

    def load_singer_cache(self):
        data = self.file_handler.load_singer_cache()
        for name, info in data.items():
            singer = Singer(name, info['current_song'], info['entry_number'])
            singer.songs = info['songs']
            singer.performance_count = info['performance_count']
            singer.is_new = info['is_new']
            self.singer_cache[name] = singer

    def save_singer_cache(self):
        data = {name: {'songs': singer.songs, 
                       'current_song': singer.current_song, 
                       'entry_number': singer.entry_number,
                       'performance_count': singer.performance_count,
                       'is_new': singer.is_new} 
                for name, singer in self.singer_cache.items()}
        self.file_handler.save_singer_cache(data)