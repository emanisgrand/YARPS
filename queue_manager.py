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
        else:
            singer = Singer(name, song, self.entry_counter)
            self.singer_cache[name] = singer
            self.entry_counter += 1

        insert_position = len(self.queue)
        for i, queued_singer in enumerate(self.queue):
            if queued_singer.performance_count > 0 and singer.performance_count == 0:
                insert_position = i
                break

        self.queue.insert(insert_position, singer)
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
        self.entry_counter = 1
        for name, info in data.items():
            singer = Singer(name, info['songs'][0], self.entry_counter)
            singer.songs = info['songs']
            self.singer_cache[name] = singer
            self.entry_counter += 1

    def save_singer_cache(self):
        data = {name: {'songs': singer.songs} for name, singer in self.singer_cache.items()}
        try:
            self.file_handler.save_singer_cache(data)
            print(f"Singer cache saved successfully. Path: {self.file_handler.data_file_path}")
        except Exception as e:
            print(f"Error saving singer cache: {str(e)}")