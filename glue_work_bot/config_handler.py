import yaml

class ConfigHandler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.load_exception = None

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_excluded_users(self):
        return self.config.get('exclude_users', [])

    def get_load_exception(self):
        return self.load_exception