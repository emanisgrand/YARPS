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

        performance_count = self.singer_cache.get(name, {}).get('performance_count', 0)
        singer = Singer(name, song, self.entry_counter, performance_count)
        self.entry_counter += 1

        insert_position = len(self.queue)
        for i in range(1, len(self.queue)):
            if self.queue[i].performance_count > 0 and singer.performance_count == 0:
                insert_position = i
                break

        self.queue.insert(insert_position, singer)
        
        if name not in self.singer_cache:
            self.singer_cache[name] = {'songs': set(), 'performance_count': 0}
        self.singer_cache[name]['songs'].add(song)
        
        self.save_singer_cache()
        return singer

    def remove_from_queue(self):
        if self.queue:
            removed_singer = self.queue.pop(0)
            removed_singer.increment_performance_count()
            self.singer_cache[removed_singer.name]['performance_count'] = removed_singer.performance_count
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
        for singer in self.queue:
            singer.performance_count = 0
            singer.is_new = True
        for name in self.singer_cache:
            self.singer_cache[name]['performance_count'] = 0
        self.save_singer_cache()

    def load_singer_cache(self):
        data = self.file_handler.load_singer_cache()
        for name, info in data.items():
            self.singer_cache[name] = {
                'songs': set(info['songs']),
                'performance_count': info.get('performance_count', 0)
            }

    def save_singer_cache(self):
        data = {
            name: {
                'songs': list(info['songs']),
                'performance_count': info['performance_count']
            } for name, info in self.singer_cache.items()
        }
        try:
            self.file_handler.save_singer_cache(data)
            print(f"Singer cache saved successfully. Path: {self.file_handler.data_file_path}")
        except Exception as e:
            print(f"Error saving singer cache: {str(e)}")

    def get_songs_for_singer(self, name):
        return list(self.singer_cache.get(name, {'songs': set()})['songs'])

    def get_performance_count(self, name):
        return self.singer_cache.get(name, {}).get('performance_count', 0)