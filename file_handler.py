import os
import sys
import json
import shutil

class FileHandler:
    def __init__(self):
        self.data_file_path = self.get_data_file_path()

    def get_data_file_path(self):
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            bundle_dir = sys._MEIPASS
        else:
            # Running as script
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Use a writable user data directory
        user_data_dir = os.path.join(os.path.expanduser('~'), '.yarps')
        os.makedirs(user_data_dir, exist_ok=True)
        
        user_file_path = os.path.join(user_data_dir, 'singer_cache.json')
        bundle_file_path = os.path.join(bundle_dir, 'singer_cache.json')
        
        if not os.path.exists(user_file_path) and os.path.exists(bundle_file_path):
            # Copy the bundled file to the user data directory if it doesn't exist
            shutil.copy2(bundle_file_path, user_file_path)
    
        return user_file_path

    def load_singer_cache(self):
            print(f"Loading singer cache from: {self.data_file_path}")
            try:
                with open(self.data_file_path, 'r') as f:
                    data = json.load(f)
                print("Singer cache loaded successfully.")
                return data
            except FileNotFoundError:
                print("Singer cache file not found. Creating a new one.")
                return {}
            except json.JSONDecodeError:
                print("Error decoding singer cache file. Starting with an empty cache.")
                return {}

    def save_singer_cache(self, data):
        print(f"Saving singer cache to: {self.data_file_path}")
        try:
            with open(self.data_file_path, 'w') as f:
                json.dump(data, f, indent=4, sort_keys=True)
            print("Singer cache saved successfully.")
        except Exception as e:
            print(f"Error saving singer cache: {str(e)}")