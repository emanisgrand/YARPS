from ticker_window import TickerWindow

class TickerManager:
    def __init__(self, root, queue_manager):
        self.ticker_window = TickerWindow(root)
        self.queue_manager = queue_manager

    def update_queue(self):
        self.ticker_window.update_queue(self.queue_manager.queue)

    def set_state(self, state):
        self.ticker_window.set_state(state)

    def on_close(self):
        self.ticker_window.on_close()