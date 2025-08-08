import os
import yaml

class ConfigHandler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.load_exception = None

    def load_config(self): # Returns True if successful, otherwise returns False
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                return True
        except Exception as e:
            self.load_exception = e
            return False

    def get_urls(self):
        return self.config.get('urls', [])

    def get_load_exception(self):
        return self.load_exception